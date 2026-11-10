import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import IntegrityError

from app.modules.conteudo.domain.catalogo import (
    esta_disponivel,
    normalizar_nome_assunto,
    validar_status,
)
from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.area_enem import AreaEnem
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.assunto_transferencia import AssuntoTransferencia
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.services.alterar_status_catalogo_service import (
    AlterarStatusAssuntoService,
    AlterarStatusMateriaService,
)
from app.modules.conteudo.services.listar_catalogo_admin_service import (
    ListarAssuntosAdminService,
    ListarMateriasAdminService,
)
from app.modules.conteudo.services.atualizar_materia_service import AtualizarMateriaService
from app.modules.conteudo.services.impacto_catalogo_service import (
    ImpactoAssuntoService,
    ImpactoMateriaService,
)
from app.modules.conteudo.services.transferir_assunto_service import TransferirAssuntoService
from app.transaction_manager import TransactionManager


class CatalogoDomainTest(unittest.TestCase):
    def test_normalizacao_unicode_espacos_caixa_e_limites(self):
        self.assertEqual(
            normalizar_nome_assunto("  GEne\u0301tica\t\n molecular  "),
            "genética molecular",
        )
        for value in (None, " \t ", "x" * 151):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalizar_nome_assunto(value)

    def test_status_e_disponibilidade(self):
        self.assertEqual(validar_status("ativa"), "ativa")
        self.assertTrue(esta_disponivel(MagicMock(status="ativa")))
        self.assertFalse(esta_disponivel(MagicMock(status="inativa")))
        with self.assertRaises(ValueError):
            validar_status("apagada")

    def test_models_nao_possuem_cascade_destrutivo(self):
        self.assertNotIn("delete", Materia.assuntos.property.cascade)
        foreign_key = next(iter(Assunto.materia_id.property.columns[0].foreign_keys))
        self.assertEqual(foreign_key.ondelete, "RESTRICT")

    def test_novas_models_serializam_campos_estaveis(self):
        self.assertEqual(
            AreaEnem(id=1, codigo="linguagens", nome="Linguagens", ordem=1).to_dict(),
            {"id": 1, "codigo": "linguagens", "nome": "Linguagens", "ordem": 1},
        )
        transfer = AssuntoTransferencia(
            id=2,
            assunto_id=3,
            materia_origem_id=4,
            materia_destino_id=5,
            questoes_impactadas=6,
        ).to_dict()
        self.assertEqual(transfer["questoes_impactadas"], 6)


class TransactionManagerTest(unittest.TestCase):
    @patch("app.transaction_manager.db.session")
    def test_confirma_resultado(self, scoped):
        session = scoped.return_value
        session.in_transaction.return_value = False
        self.assertEqual(TransactionManager.executar(lambda: "ok"), "ok")
        session.begin.assert_called_once_with()
        session.commit.assert_called_once_with()

    @patch("app.transaction_manager.db.session")
    def test_reverte_falha(self, scoped):
        session = scoped.return_value
        session.in_transaction.return_value = True
        with self.assertRaisesRegex(RuntimeError, "falha"):
            TransactionManager.executar(
                lambda: (_ for _ in ()).throw(RuntimeError("falha"))
            )
        session.begin.assert_not_called()
        session.rollback.assert_called_once_with()


class AdminListingServiceTest(unittest.TestCase):
    def test_materias_paginadas(self):
        consulta = MagicMock()
        consulta.listar.return_value = (
            [{
                'id': 1,
                'area_enem': {'id': 3},
                'assuntos': 2,
                'questoes': 7
            }],
            21
        )
        result = ListarMateriasAdminService(consulta).executar(
            {"pagina": "2", "por_pagina": "10", "busca": " fisica ", "status": "ativa"}
        )
        self.assertEqual(result["total_paginas"], 3)
        self.assertEqual(result["itens"][0]["questoes"], 7)
        consulta.listar.assert_called_once_with(
            {
                'busca': 'fisica',
                'status': 'ativa',
                'area_enem_id': None
            },
            2,
            10
        )

    def test_assuntos_expoem_resumos_nulos(self):
        consulta = MagicMock()
        consulta.listar.return_value = (
            [{
                'id': 1,
                'materia': {'id': 2},
                'area_enem': {'id': 3},
                'questoes': 4
            }],
            1
        )
        result = ListarAssuntosAdminService(consulta).executar({})
        self.assertIsNone(result["itens"][0]["resumos"])

    def test_rejeita_paginacao_busca_status_e_ids_invalidos(self):
        invalid = [
            {"pagina": "x"},
            {"pagina": 0},
            {"por_pagina": 101},
            {"busca": "x" * 101},
            {"status": "apagada"},
            {"materia_id": "x"},
        ]
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(DadosInvalidosError):
                ListarAssuntosAdminService(MagicMock()).executar(params)


class LifecycleServiceTest(unittest.TestCase):
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Materia")
    def test_materia_inexistente(self, matter_class):
        matter_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            AlterarStatusMateriaService.executar(1, "inativar")

    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.AreaEnem")
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Materia")
    def test_materia_inativa_e_rejeita_reativacao_sem_area(self, matter_class, area_class):
        matter = MagicMock(status="ativa", area_enem_id=3)
        matter.to_dict.return_value = {"status": "inativa"}
        matter_class.buscar_por_id.return_value = matter
        self.assertEqual(
            AlterarStatusMateriaService.executar(1, "inativar"),
            {"status": "inativa"}
        )
        matter.status = "inativa"
        area_class.buscar_por_id.return_value = None
        with self.assertRaises(ConflitoError):
            AlterarStatusMateriaService.executar(1, "reativar")

    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Materia")
    def test_materia_bloqueia_arquivamento_com_filhos(self, matter_class, repository):
        matter_class.buscar_por_id.return_value = MagicMock(status="ativa")
        repository.contar_assuntos_nao_arquivados.return_value = 2
        with self.assertRaises(ConflitoError) as error:
            AlterarStatusMateriaService.executar(1, "arquivar")
        self.assertEqual(error.exception.detalhes["assuntos_nao_arquivados"], 2)

    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Materia")
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Assunto")
    def test_assunto_reativa_em_materia_ativa(self, subject_class, matter_class, repository):
        subject = MagicMock(status="arquivada", materia_id=2, id=1, nome_normalizado="x")
        subject.to_dict.return_value = {"status": "ativa"}
        subject_class.buscar_por_id.return_value = subject
        matter_class.buscar_por_id.return_value = MagicMock(status="ativa")
        repository.existe_assunto_equivalente.return_value = False
        self.assertEqual(
            AlterarStatusAssuntoService.executar(1, "reativar"),
            {"status": "ativa"}
        )
        subject.atualizar.assert_called_once_with(status="ativa")

    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Assunto")
    def test_rejeita_transicao_invalida(self, subject_class):
        subject_class.buscar_por_id.return_value = MagicMock(status="arquivada")
        with self.assertRaises(DadosInvalidosError):
            AlterarStatusAssuntoService.executar(1, "arquivar")

    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Materia")
    @patch("app.modules.conteudo.services.alterar_status_catalogo_service.Assunto")
    def test_assunto_inexistente_materia_inativa_e_duplicidade(
        self,
        subject_class,
        matter_class,
        repository
    ):
        subject_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            AlterarStatusAssuntoService.executar(1, "reativar")

        subject = MagicMock(status="arquivada", materia_id=2, id=1, nome_normalizado="x")
        subject_class.buscar_por_id.return_value = subject
        matter_class.buscar_por_id.return_value = MagicMock(status="inativa")
        with self.assertRaises(ConflitoError):
            AlterarStatusAssuntoService.executar(1, "reativar")

        matter_class.buscar_por_id.return_value = MagicMock(status="ativa")
        repository.existe_assunto_equivalente.return_value = True
        with self.assertRaises(ConflitoError):
            AlterarStatusAssuntoService.executar(1, "reativar")


class CatalogoValidationServiceTest(unittest.TestCase):
    @patch("app.modules.conteudo.services.atualizar_materia_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.atualizar_materia_service.AreaEnem")
    @patch("app.modules.conteudo.services.atualizar_materia_service.Materia")
    def test_atualizacao_valida_area_arquivamento_e_integridade(
        self,
        matter_class,
        area_class,
        repository
    ):
        matter = MagicMock()
        matter.to_dict.return_value = {"id": 1}
        matter_class.buscar_por_id.return_value = matter
        area_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            AtualizarMateriaService.executar(1, {"area_enem_id": 3})

        area_class.buscar_por_id.return_value = MagicMock()
        repository.contar_assuntos_nao_arquivados.return_value = 1
        with self.assertRaises(ConflitoError):
            AtualizarMateriaService.executar(
                1,
                {"area_enem_id": 3, "status": "arquivada"}
            )

        repository.contar_assuntos_nao_arquivados.return_value = 0
        matter.atualizar.side_effect = IntegrityError("update", {}, Exception("uq"))
        with self.assertRaises(ConflitoError):
            AtualizarMateriaService.executar(
                1,
                {"nome": "Fisica", "descricao": None, "status": "inativa"}
            )

    @patch("app.modules.conteudo.services.impacto_catalogo_service.Materia")
    @patch("app.modules.conteudo.services.impacto_catalogo_service.Assunto")
    def test_impactos_rejeitam_recursos_inexistentes(self, subject_class, matter_class):
        matter_class.buscar_por_id.return_value = None
        subject_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            ImpactoMateriaService.executar(1)
        with self.assertRaises(RecursoNaoEncontradoError):
            ImpactoAssuntoService.executar(1)


class TransferServiceTest(unittest.TestCase):
    @patch("app.modules.conteudo.services.transferir_assunto_service.Materia")
    @patch("app.modules.conteudo.services.transferir_assunto_service.Assunto")
    @patch("app.modules.conteudo.services.transferir_assunto_service.CatalogoRepository")
    def test_previa_rejeita_recursos_destino_e_conflito(
        self,
        repository,
        subject_class,
        matter_class
    ):
        subject_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            TransferirAssuntoService.previa(1, 3)

        subject = MagicMock(id=1, materia_id=2, nome_normalizado="x")
        subject_class.buscar_por_id.return_value = subject
        origin = MagicMock(id=2)
        matter_class.buscar_por_id.side_effect = [origin, None]
        with self.assertRaises(RecursoNaoEncontradoError):
            TransferirAssuntoService.previa(1, 3)

        for destination, error in [
            (MagicMock(id=2, status="ativa"), DadosInvalidosError),
            (MagicMock(id=3, status="inativa"), DadosInvalidosError),
            (MagicMock(id=3, status="ativa"), ConflitoError),
        ]:
            with self.subTest(error=error):
                matter_class.buscar_por_id.side_effect = [origin, destination]
                repository.existe_assunto_equivalente.return_value = error is ConflitoError
                with self.assertRaises(error):
                    TransferirAssuntoService.previa(1, 3)

    def test_transferencia_rejeita_payload_e_impacto_invalidos(self):
        with self.assertRaises(DadosInvalidosError):
            TransferirAssuntoService.executar(1, None)
        for impact in (None, {}, {"questoes": True}, {"questoes": -1}):
            with self.subTest(impact=impact), self.assertRaises(DadosInvalidosError):
                TransferirAssuntoService.executar(
                    1,
                    {"materia_destino_id": 3, "impacto_esperado": impact}
                )

    @patch("app.modules.conteudo.services.transferir_assunto_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.transferir_assunto_service.TransactionManager")
    def test_transferencia_revalida_registros_sob_lock(self, manager, repository):
        manager.executar.side_effect = lambda operation: operation()
        data = {"materia_destino_id": 3, "impacto_esperado": {"questoes": 0}}

        repository.buscar_assunto_para_atualizacao.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            TransferirAssuntoService.executar(1, data)

        subject = MagicMock(id=1, materia_id=2, nome_normalizado="x")
        origin = MagicMock(id=2)
        repository.buscar_assunto_para_atualizacao.return_value = subject
        repository.buscar_materias_para_atualizacao.return_value = [origin]
        with self.assertRaises(RecursoNaoEncontradoError):
            TransferirAssuntoService.executar(1, data)

        same_data = {"materia_destino_id": 2, "impacto_esperado": {"questoes": 0}}
        with self.assertRaises(DadosInvalidosError):
            TransferirAssuntoService.executar(1, same_data)

        destination = MagicMock(id=3, status="inativa")
        repository.buscar_materias_para_atualizacao.return_value = [origin, destination]
        with self.assertRaises(DadosInvalidosError):
            TransferirAssuntoService.executar(1, data)

        destination.status = "ativa"
        repository.existe_assunto_equivalente.return_value = True
        with self.assertRaises(ConflitoError):
            TransferirAssuntoService.executar(1, data)

    @patch("app.modules.conteudo.services.transferir_assunto_service.Materia")
    @patch("app.modules.conteudo.services.transferir_assunto_service.Assunto")
    @patch("app.modules.conteudo.services.transferir_assunto_service.CatalogoRepository")
    def test_previa_valida_e_retorna_impacto(self, repository, subject_class, matter_class):
        subject = MagicMock(id=1, materia_id=2, nome_normalizado="mecanica")
        subject_class.buscar_por_id.return_value = subject
        origin = MagicMock(id=2, to_dict=lambda: {"id": 2})
        destination = MagicMock(id=3, status="ativa", to_dict=lambda: {"id": 3})
        matter_class.buscar_por_id.side_effect = [origin, destination]
        repository.existe_assunto_equivalente.return_value = False
        repository.impacto_assunto.return_value = {"questoes": 8, "transferencias": 0}
        result = TransferirAssuntoService.previa(1, 3)
        self.assertEqual(result["impacto"], {"questoes": 8})

    @patch("app.modules.conteudo.services.transferir_assunto_service.AssuntoTransferencia")
    @patch("app.modules.conteudo.services.transferir_assunto_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.transferir_assunto_service.TransactionManager")
    def test_transferencia_atualiza_e_registra(self, manager, repository, transfer_class):
        manager.executar.side_effect = lambda operation: operation()
        subject = MagicMock(id=1, materia_id=2, nome_normalizado="mecanica")
        subject.to_dict.return_value = {"id": 1, "materia_id": 3}
        origin = MagicMock(id=2, to_dict=lambda: {"id": 2})
        destination = MagicMock(id=3, status="ativa", to_dict=lambda: {"id": 3})
        repository.buscar_assunto_para_atualizacao.return_value = subject
        repository.buscar_materias_para_atualizacao.return_value = [origin, destination]
        repository.existe_assunto_equivalente.return_value = False
        repository.impacto_assunto.return_value = {"questoes": 1, "transferencias": 0}
        result = TransferirAssuntoService.executar(
            1,
            {
                "materia_destino_id": 3,
                "impacto_esperado": {"questoes": 1},
                "nome": " Mecanica ",
                "descricao": "Movimento",
            }
        )
        self.assertEqual(result["materia_id"], 3)
        subject.atualizar.assert_called_once_with(
            confirmar=False,
            materia_id=3,
            nome="Mecanica",
            nome_normalizado="mecanica",
            descricao="Movimento",
        )
        transfer_class.return_value.salvar.assert_called_once_with(confirmar=False)

    @patch("app.modules.conteudo.services.transferir_assunto_service.CatalogoRepository")
    @patch("app.modules.conteudo.services.transferir_assunto_service.TransactionManager")
    def test_transferencia_detecta_impacto_alterado(self, manager, repository):
        manager.executar.side_effect = lambda operation: operation()
        subject = MagicMock(id=1, materia_id=2, nome_normalizado="x")
        origin = MagicMock(id=2, to_dict=lambda: {"id": 2})
        destination = MagicMock(id=3, status="ativa", to_dict=lambda: {"id": 3})
        repository.buscar_assunto_para_atualizacao.return_value = subject
        repository.buscar_materias_para_atualizacao.return_value = [origin, destination]
        repository.existe_assunto_equivalente.return_value = False
        repository.impacto_assunto.return_value = {"questoes": 2, "transferencias": 0}
        with self.assertRaises(ConflitoError) as error:
            TransferirAssuntoService.executar(
                1,
                {"materia_destino_id": 3, "impacto_esperado": {"questoes": 1}}
            )
        self.assertEqual(error.exception.detalhes["previa"]["impacto"]["questoes"], 2)

    @patch("app.modules.conteudo.services.transferir_assunto_service.TransactionManager")
    def test_transferencia_traduz_conflito_de_integridade(self, manager):
        manager.executar.side_effect = IntegrityError("transferir", {}, Exception("fk"))
        with self.assertRaises(ConflitoError):
            TransferirAssuntoService.executar(
                1,
                {"materia_destino_id": 3, "impacto_esperado": {"questoes": 0}}
            )


if __name__ == "__main__":
    unittest.main()
