"""Valida cobertura agregada do backend e arquivos Python sem exercicio."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "coverage-backend.json"
MIN_LINES = 90.0
MIN_BRANCHES = 85.0


def production_files(root: Path = ROOT) -> list[Path]:
    return (
        sorted((root / "backend" / "app").rglob("*.py"))
        + sorted((root / "backend" / "database").glob("*.py"))
        + [root / "backend" / "run.py"]
    )


def has_executable_statements(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        isinstance(node, ast.stmt)
        and not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        for node in tree.body
    )


def _normalized_files(report: dict) -> dict[str, dict]:
    return {
        Path(name).as_posix().lower(): details
        for name, details in report.get("files", {}).items()
    }


def validate(report_path: Path, root: Path = ROOT) -> list[str]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    reported = _normalized_files(report)
    errors: list[str] = []
    covered_lines = total_lines = covered_branches = total_branches = 0

    for path in production_files(root):
        relative = path.relative_to(root).as_posix()
        details = reported.get(relative.lower())
        if details is None:
            errors.append(f"Arquivo ausente do relatorio: {relative}")
            continue

        summary = details.get("summary", {})
        statements = int(summary.get("num_statements", 0))
        lines = int(summary.get("covered_lines", 0))
        branches = int(summary.get("num_branches", 0))
        branches_covered = int(summary.get("covered_branches", 0))
        total_lines += statements
        covered_lines += lines
        total_branches += branches
        covered_branches += branches_covered

        if has_executable_statements(path) and statements > 0 and lines == 0:
            errors.append(f"Arquivo executavel com zero linhas cobertas: {relative}")

    line_percent = 100.0 if total_lines == 0 else covered_lines * 100 / total_lines
    branch_percent = (
        100.0 if total_branches == 0 else covered_branches * 100 / total_branches
    )
    if line_percent < MIN_LINES:
        errors.append(
            f"Cobertura agregada de linhas {line_percent:.2f}% abaixo de {MIN_LINES:.0f}%"
        )
    if branch_percent < MIN_BRANCHES:
        errors.append(
            "Cobertura agregada de branches "
            f"{branch_percent:.2f}% abaixo de {MIN_BRANCHES:.0f}%"
        )

    print(
        f"Backend: linhas {line_percent:.2f}% "
        f"({covered_lines}/{total_lines}); branches {branch_percent:.2f}% "
        f"({covered_branches}/{total_branches})."
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", nargs="?", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    if not args.report.is_file():
        print(f"Relatorio nao encontrado: {args.report}", file=sys.stderr)
        return 1
    errors = validate(args.report)
    for error in errors:
        print(f"ERRO: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
