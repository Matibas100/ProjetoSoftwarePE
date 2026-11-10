"""Executa as integracoes apenas com opt-in explicito no processo."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    os.environ['GEMINI_API_KEY'] = ''
    os.environ['TUTOR_IA_ENABLED'] = 'false'
    if os.getenv("RUN_MYSQL_INTEGRATION") != "1":
        print(
            "Integracoes MySQL bloqueadas. Defina RUN_MYSQL_INTEGRATION=1 "
            "somente no processo de teste.",
            file=sys.stderr,
        )
        return 2
    sys.path.insert(0, str(BACKEND_ROOT))
    suite = unittest.defaultTestLoader.discover(
        str(BACKEND_ROOT / "tests"),
        pattern="*_integration.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
