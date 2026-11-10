import unittest

from app.exceptions import DadosInvalidosError
from app.core.paginacao import envelope_paginado, inteiro_filtro


class InteiroFiltroTest(unittest.TestCase):
    def test_ausencia_e_vazio_retornam_none(self):
        for valor in (None, ""):
            with self.subTest(valor=valor):
                self.assertIsNone(inteiro_filtro(valor, "pagina"))

    def test_preserva_conversoes_aceitas_por_int(self):
        for valor, esperado in (
            (2, 2),
            ("2", 2),
            (" +02 ", 2),
            (True, 1),
            (2.9, 2),
            ("１２", 12),
            (b"3", 3)
        ):
            with self.subTest(valor=valor):
                self.assertEqual(inteiro_filtro(valor, "pagina"), esperado)

    def test_limites_inclusivos_e_maximo_opcional(self):
        self.assertEqual(inteiro_filtro("1", "pagina"), 1)
        self.assertEqual(inteiro_filtro("100", "por_pagina", maximo=100), 100)
        self.assertEqual(inteiro_filtro("0", "indice", minimo=0), 0)
        self.assertEqual(inteiro_filtro("-2", "indice", minimo=-2, maximo=0), -2)
        self.assertEqual(inteiro_filtro("2147483648", "pagina"), 2147483648)

    def test_conversao_invalida_preserva_mensagem_e_causa(self):
        for valor, causa in (
            ("abc", ValueError),
            ("1.5", ValueError),
            (" ", ValueError),
            ([], TypeError),
            ({}, TypeError)
        ):
            with self.subTest(valor=valor):
                with self.assertRaises(DadosInvalidosError) as erro:
                    inteiro_filtro(valor, "materia_id")
                self.assertEqual(str(erro.exception), "materia_id deve ser um inteiro valido.")
                self.assertIsInstance(erro.exception.__cause__, causa)

    def test_fora_do_intervalo_preserva_mensagem(self):
        for valor in (0, -1, False, "101"):
            with self.subTest(valor=valor):
                with self.assertRaises(DadosInvalidosError) as erro:
                    inteiro_filtro(valor, "por_pagina", maximo=100)
                self.assertEqual(
                    str(erro.exception),
                    "por_pagina esta fora do intervalo permitido."
                )


class EnvelopePaginadoTest(unittest.TestCase):
    def test_total_zero_envelope_vazio(self):
        self.assertEqual(
            envelope_paginado([], 1, 20, 0),
            {
                "itens": [],
                "pagina": 1,
                "por_pagina": 20,
                "total_itens": 0,
                "total_paginas": 0,
            }
        )

    def test_total_exato_e_parcial_preserva_lista_e_ordem(self):
        itens = [{"id": 3}, {"id": 1}]
        for total, paginas in ((20, 2), (21, 3)):
            with self.subTest(total=total):
                resultado = envelope_paginado(itens, 2, 10, total)
                self.assertEqual(
                    resultado,
                    {
                        "itens": [{"id": 3}, {"id": 1}],
                        "pagina": 2,
                        "por_pagina": 10,
                        "total_itens": total,
                        "total_paginas": paginas,
                    }
                )
                self.assertIs(resultado["itens"], itens)

    def test_pagina_apos_a_ultima_preserva_pagina_e_total(self):
        itens = []
        resultado = envelope_paginado(itens, 9, 10, 21)
        self.assertEqual(
            resultado,
            {
                "itens": [],
                "pagina": 9,
                "por_pagina": 10,
                "total_itens": 21,
                "total_paginas": 3,
            }
        )
        self.assertIs(resultado["itens"], itens)

    def test_nao_introduz_validacao_de_zero_por_pagina(self):
        self.assertEqual(envelope_paginado([], 1, 0, 0)["total_paginas"], 0)
        with self.assertRaises(ZeroDivisionError):
            envelope_paginado([], 1, 0, 1)
