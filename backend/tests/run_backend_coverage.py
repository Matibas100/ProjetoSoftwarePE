"""Coleta cobertura backend em processos unitario e de integracao."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    try:
        run(sys.executable, "-m", "coverage", "erase")
        run(
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--parallel-mode",
            "backend/tests/run_unit.py",
        )
        run(
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--parallel-mode",
            "backend/tests/run_integration.py",
        )
        run(sys.executable, "-m", "coverage", "combine")
        run(sys.executable, "-m", "coverage", "json")
        run(sys.executable, "scripts/validate_backend_coverage.py")
    except subprocess.CalledProcessError as error:
        return error.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
