from pathlib import Path
import subprocess
import sys


def test_main_demo_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "src/main.py"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "SRSim Minimal Battle Demo" in result.stdout
    assert "Winner: allies" in result.stdout
    assert "Event Counts:" in result.stdout
    assert "weakness_break" in result.stdout
    assert "[Shield]" in result.stdout
    assert "[Heal]" in result.stdout
    assert "Battle Log:" in result.stdout
