from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
}

DEFAULT_RULES: dict[str, list[str]] = {
    "elevenlabs": ["elevenlabs", "voice", "tts", "text to speech"],
    "jasper": ["jasper", "marketing ai", "copywriting"],
    "lovable": ["lovable", "ai app builder"],
    "replit": ["replit", "repl"],
    "buffer": ["buffer", "social scheduling"],
    "kit": ["kit", "convertkit", "creator email"],
    "getresponse": ["getresponse", "email automation"],
    "runpod": ["runpod", "gpu"],
    "conoha": ["conoha", "wing"],
    "xserver": ["xserver", "wordpress hosting"],
    "freee": ["freee", "accounting"],
}


@dataclass(frozen=True)
class SourceItem:
    url: str
    title: str
    description: str
    body: str
    source: str
    published_at: str | None


@dataclass(frozen=True)
class NormalizedItem:
    canonical_url: str
    source_domain: str
    title: str
    description: str
    body: str
    source: str
    published_at: str | None
    content_hash: str
    merchants: list[str]


@dataclass(frozen=True)
class ContentSpec:
    topic: str
    angle: str
    audience_persona: str
    merchant: str | None
    confirmed_facts: list[str]
    unresolved_facts: list[str]
    required_disclosure: bool
    primary_cta: str
    secondary_cta: str
    risk_flags: list[str]
    source_url: str


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    host = parsed.netloc.lower()
    clean_query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in TRACKING_QUERY_KEYS]
    query = urlencode(clean_query, doseq=True)
    path = parsed.path.rstrip("/")
    canonical = urlunparse((scheme, host, path, "", query, ""))
    return canonical


def hash_content(title: str, description: str, canonical_url: str) -> str:
    payload = "\n".join([title.strip(), description.strip(), canonical_url])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def detect_merchants(text: str, rules: dict[str, list[str]]) -> list[str]:
    lower = text.lower()
    matches: list[str] = []
    for merchant, keywords in rules.items():
        if any(word in lower for word in keywords):
            matches.append(merchant)
    return sorted(set(matches))


def normalize_item(item: SourceItem, rules: dict[str, list[str]]) -> NormalizedItem:
    canonical_url = canonicalize_url(item.url)
    source_domain = urlparse(canonical_url).netloc
    merchants = detect_merchants("\n".join([item.title, item.description, item.body]), rules)
    return NormalizedItem(
        canonical_url=canonical_url,
        source_domain=source_domain,
        title=item.title.strip(),
        description=item.description.strip(),
        body=item.body.strip(),
        source=item.source.strip(),
        published_at=item.published_at,
        content_hash=hash_content(item.title, item.description, canonical_url),
        merchants=merchants,
    )


def dedupe_items(items: list[NormalizedItem]) -> list[NormalizedItem]:
    seen: set[str] = set()
    deduped: list[NormalizedItem] = []
    for item in items:
        key = item.canonical_url or item.content_hash
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def build_content_spec(item: NormalizedItem) -> ContentSpec:
    merchant = item.merchants[0] if item.merchants else None
    title_lower = item.title.lower()
    angle = "comparison" if " vs " in title_lower else "update"
    unresolved: list[str] = []
    if item.published_at is None:
        unresolved.append("publish_date_missing")

    risk_flags: list[str] = []
    risky_terms = ["最強", "絶対", "誰でも"]
    if any(term in item.title for term in risky_terms):
        risk_flags.append("hype_claim_in_title")

    topic = merchant or "general_ai_automation"
    confirmed_facts = [f"source={item.source}", f"domain={item.source_domain}"]
    if item.published_at:
        confirmed_facts.append(f"published_at={item.published_at}")

    return ContentSpec(
        topic=topic,
        angle=angle,
        audience_persona="ai_affiliate_operator",
        merchant=merchant,
        confirmed_facts=confirmed_facts,
        unresolved_facts=unresolved,
        required_disclosure=merchant is not None,
        primary_cta="owned_lp",
        secondary_cta="lead_magnet",
        risk_flags=risk_flags,
        source_url=item.canonical_url,
    )


def _read_jsonl(path: Path) -> list[SourceItem]:
    rows: list[SourceItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        rows.append(
            SourceItem(
                url=str(obj.get("url", "")),
                title=str(obj.get("title", "")),
                description=str(obj.get("description", "")),
                body=str(obj.get("body", "")),
                source=str(obj.get("source", "manual")),
                published_at=(str(obj["published_at"]) if obj.get("published_at") else None),
            )
        )
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_deterministic_pipeline(input_jsonl: Path, output_dir: Path) -> dict[str, int | str]:
    sources = _read_jsonl(input_jsonl)
    normalized = [normalize_item(item, DEFAULT_RULES) for item in sources]
    deduped = dedupe_items(normalized)
    specs = [build_content_spec(item) for item in deduped]

    normalized_rows = [item.__dict__ for item in deduped]
    spec_rows = [spec.__dict__ for spec in specs]

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    normalized_path = output_dir / f"normalized_{timestamp}.jsonl"
    specs_path = output_dir / f"content_specs_{timestamp}.jsonl"

    _write_jsonl(normalized_path, normalized_rows)
    _write_jsonl(specs_path, spec_rows)

    return {
        "input_count": len(sources),
        "normalized_count": len(normalized),
        "deduped_count": len(deduped),
        "spec_count": len(specs),
        "normalized_path": str(normalized_path),
        "specs_path": str(specs_path),
    }
