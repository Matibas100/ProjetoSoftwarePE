"""Capacidades e falhas da persistência, sem conexão ao banco."""
import unittest
from unittest.mock import patch

from sqlalchemy.orm import configure_mappers

from app.extensions import db
from app.core import persistencia
from app.models.crud_mixin import CrudMixin, ModeloAtualizavel, ModeloBase
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.models.questao_versao import QuestaoVersao
from app.modules.conteudo.models.questao_evento import QuestaoEvento
from app.modules.simulados.models.simulado import SimuladoVersao, SimuladoVersaoItem, SimuladoEvento
from app.modules.plano_estudos.models.plano_estudo import PlanoEstudo, PlanoEstudoItem
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade


class PersistenciaCapacidadesTest(unittest.TestCase):
    def test_bases_abstratas_com_um_caminho_ate_model(self):
        from app.models import crud_mixin
        self.assertIs(crud_mixin.db, db)
        for nome in ('ModeloBase', 'ModeloAtualizavel', 'CrudMixin'):
            self.assertIs(getattr(crud_mixin, nome), getattr(persistencia, nome))
        configure_mappers()
        self.assertEqual(len(list(db.Model.registry.mappers)), 21)
        self.assertEqual(len(db.metadata.tables), 21)
        self.assertEqual(CrudMixin.__bases__, (ModeloAtualizavel,))
        self.assertEqual(ModeloAtualizavel.__bases__, (ModeloBase,))
        self.assertEqual(ModeloBase.__bases__, (db.Model,))
        for base in (ModeloBase, ModeloAtualizavel, CrudMixin):
            self.assertTrue(base.__abstract__)
            self.assertNotIn('__tablename__', base.__dict__)
        self.assertFalse(hasattr(ModeloBase, 'atualizar'))
        self.assertFalse(hasattr(ModeloBase, 'deletar'))
        self.assertFalse(hasattr(ModeloAtualizavel, 'deletar'))

    def test_capacidades_das_vinte_e_uma_models(self):
        imutaveis = {
            QuestaoVersao,
            QuestaoEvento,
            SimuladoVersao,
            SimuladoVersaoItem,
            SimuladoEvento,
            RegistroPrivacidade
        }
        planos = {PlanoEstudo, PlanoEstudoItem}
        for mapper in db.Model.registry.mappers:
            model = mapper.class_
            self.assertTrue(hasattr(model, 'salvar'))
            self.assertEqual(hasattr(model, 'atualizar'), model not in imutaveis)
            self.assertEqual(hasattr(model, 'deletar'), model not in imutaveis | planos)
            base = ModeloBase if model in imutaveis else ModeloAtualizavel if model in planos else CrudMixin
            self.assertEqual(model.__bases__, (base,))

    @patch('app.core.persistencia.db.session')
    def test_flush_falho_deixa_rollback_ao_caso_composto(self, session):
        session.flush.side_effect = RuntimeError('falha controlada')
        materia = Materia(nome='Antes')
        for operacao in (
            lambda: materia.salvar(confirmar=False),
            lambda: materia.atualizar(confirmar=False, nome='Depois'),
            lambda: materia.deletar(confirmar=False)
        ):
            with self.assertRaises(RuntimeError):
                operacao()
        session.rollback.assert_not_called()
        session.commit.assert_not_called()
