"""Executa testes unitarios sem carregar .env nem conectar ao MySQL."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["DATABASE_URL"] = "mysql+pymysql://unit:unit@127.0.0.1:9/unit"
os.environ["AUTH_SECRET_KEY"] = "ab" * 32  # Chave ficticia, exclusiva dos testes sem banco.
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    suite = unittest.defaultTestLoader.discover(
        str(BACKEND_ROOT / "tests" / "unit"), pattern="test_*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
