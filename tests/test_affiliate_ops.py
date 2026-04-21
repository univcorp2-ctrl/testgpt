from pathlib import Path
import json

from click.testing import CliRunner

from app.cli import app
from app.services.affiliate_ops import (
    build_content_spec,
    canonicalize_url,
    dedupe_items,
    normalize_item,
    run_deterministic_pipeline,
    SourceItem,
)


def test_canonicalize_url_strips_tracking_params() -> None:
    raw = "https://Example.com/path/?utm_source=x&a=1&fbclid=abc"
    assert canonicalize_url(raw) == "https://example.com/path?a=1"


def test_dedupe_items_by_canonical_url() -> None:
    rules = {"buffer": ["buffer"]}
    a = normalize_item(
        SourceItem(
            url="https://buffer.com/blog?utm_source=x",
            title="Buffer post",
            description="desc",
            body="",
            source="rss",
            published_at="2026-01-01",
        ),
        rules,
    )
    b = normalize_item(
        SourceItem(
            url="https://buffer.com/blog",
            title="Buffer post updated",
            description="desc",
            body="",
            source="rss",
            published_at="2026-01-01",
        ),
        rules,
    )

    assert len(dedupe_items([a, b])) == 1


def test_run_deterministic_pipeline_generates_outputs(tmp_path: Path) -> None:
    input_file = tmp_path / "input.jsonl"
    rows = [
        {
            "url": "https://buffer.com/library/ai-posting?utm_source=x",
            "title": "Buffer update",
            "description": "new scheduling",
            "body": "",
            "source": "manual",
            "published_at": "2026-03-01",
        },
        {
            "url": "https://buffer.com/library/ai-posting",
            "title": "Buffer update duplicate",
            "description": "new scheduling",
            "body": "",
            "source": "manual",
        },
    ]
    input_file.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    result = run_deterministic_pipeline(input_file, tmp_path / "out")

    assert result["input_count"] == 2
    assert result["deduped_count"] == 1
    assert Path(str(result["specs_path"])).exists()


def test_build_content_spec_flags_hype() -> None:
    item = normalize_item(
        SourceItem(
            url="https://example.com/a",
            title="最強の運用",
            description="",
            body="",
            source="manual",
            published_at=None,
        ),
        {},
    )
    spec = build_content_spec(item)
    assert "hype_claim_in_title" in spec.risk_flags
    assert "publish_date_missing" in spec.unresolved_facts


def test_cli_run_affiliate_deterministic(tmp_path: Path) -> None:
    input_file = tmp_path / "input.jsonl"
    input_file.write_text(
        json.dumps(
            {
                "url": "https://runpod.io/blog/new",
                "title": "RunPod update",
                "description": "GPU",
                "body": "",
                "source": "rss",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run-affiliate-deterministic",
            "--input-jsonl",
            str(input_file),
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )

    assert result.exit_code == 0
    assert "spec_count" in result.output
