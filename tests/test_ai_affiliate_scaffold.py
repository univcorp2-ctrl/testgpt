from pathlib import Path

from click.testing import CliRunner

from app.cli import app
from app.services.ai_affiliate_scaffold import bootstrap_ai_affiliate_workspace


def test_bootstrap_ai_affiliate_workspace_creates_expected_structure(tmp_path: Path) -> None:
    result = bootstrap_ai_affiliate_workspace(tmp_path)

    root = tmp_path / "ai_affiliate_automation"
    assert result.root == root
    assert (root / "ingest").exists()
    assert (root / "normalize").exists()
    assert (root / "docs" / "business_background.md").exists()
    assert (root / "docs" / "prompt_library.md").exists()
    assert (root / "docs" / "implementation_guide.md").exists()
    assert (root / "automation_config.yaml").exists()


def test_bootstrap_ai_affiliate_cli(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["bootstrap-ai-affiliate", "--base-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "workspace:" in result.output
    assert (tmp_path / "ai_affiliate_automation" / "prompts" / "prompt_index.yaml").exists()
