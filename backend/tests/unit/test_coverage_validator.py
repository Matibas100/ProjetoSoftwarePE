import unittest
from pathlib import Path

from scripts.validate_backend_coverage import has_executable_statements, validate


class BackendCoverageValidatorTest(unittest.TestCase):
    fixtures = Path(__file__).resolve().parents[1] / "fixtures" / "coverage_project"
    statement_fixtures = Path(__file__).resolve().parents[1] / "fixtures" / "statements"

    def test_aceita_limites_atendidos(self):
        self.assertEqual(validate(self.fixtures / "coverage-valid.json", self.fixtures), [])

    def test_reprova_linhas_branches_arquivo_zerado_e_ausente(self):
        errors = validate(self.fixtures / "coverage-invalid.json", self.fixtures)
        self.assertTrue(any("zero linhas" in error for error in errors))
        self.assertTrue(any("linhas" in error and "abaixo" in error for error in errors))
        self.assertTrue(any("branches" in error and "abaixo" in error for error in errors))
        self.assertTrue(any("ausente" in error for error in errors))

    def test_considera_import_como_instrucao_executavel(self):
        self.assertTrue(
            has_executable_statements(self.statement_fixtures / "import_only.py")
        )
        self.assertFalse(
            has_executable_statements(self.statement_fixtures / "docstring_only.py")
        )


if __name__ == "__main__":
    unittest.main()
