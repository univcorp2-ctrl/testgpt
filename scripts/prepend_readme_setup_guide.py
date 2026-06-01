from __future__ import annotations

import os
from pathlib import Path

START = "<!-- AI_README_SETUP_GUIDE_START -->"
END = "<!-- AI_README_SETUP_GUIDE_END -->"

repo = os.environ.get("GITHUB_REPOSITORY", "this repository").split("/")[-1]

BLOCK = f"""{START}
## 🧭 画像付き初期設定ガイド

![README 画像付き初期設定ガイド](docs/assets/readme-setup-guide.svg)

このリポジトリ **{repo}** を初めて開いた人は、まずここだけ見れば初期設定から実行、成果物確認まで進められます。

### 最初にやること

1. 必要なSecretや外部サービス設定を確認します。
2. GitHub Actions または README の実行手順に沿って動かします。
3. 実行ログと成果物を確認します。
4. エラー時は Actions の失敗ステップと Secret名を確認します。

### 詳しい画像付きガイド

- [docs/setup-visual-guide.md](docs/setup-visual-guide.md)
- [docs/image-generation-prompts.md](docs/image-generation-prompts.md)

> SecretやAPIキーの実値は、README、Issue、ログ、画像に絶対に貼らないでください。例では `********` または `YOUR_SECRET_HERE` を使います。

{END}
"""

readme = Path("README.md")
original = readme.read_text(encoding="utf-8") if readme.exists() else f"# {repo}\n"

if START in original and END in original:
    before = original.split(START, 1)[0]
    rest = original.split(START, 1)[1].split(END, 1)[1]
    updated = before + BLOCK + rest.lstrip("\n")
else:
    updated = BLOCK + "\n\n" + original

if updated != original:
    readme.write_text(updated, encoding="utf-8")
    print("README.md updated with visual setup guide block")
else:
    print("README.md already up to date")
