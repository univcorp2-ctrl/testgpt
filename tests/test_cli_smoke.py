from click.testing import CliRunner

from app.cli import app


def test_doctor_smoke() -> None:
    result = CliRunner().invoke(app, ["doctor"])
    assert result.exit_code == 0
