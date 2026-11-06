"""Capacidades e falhas da persistência, sem conexão ao banco."""
import unittest
from unittest.mock import patch

from sqlalchemy.orm import configure_mappers

from app.extensions import db
from app.models.crud_mixin import CrudMixin, ModeloAtualizavel, ModeloBase
from app.models.materia import Materia
from app.models.questao_versao import QuestaoVersao
from app.models.questao_evento import QuestaoEvento
from app.models.simulado import SimuladoVersao, SimuladoVersaoItem, SimuladoEvento
from app.models.plano_estudo import PlanoEstudo, PlanoEstudoItem


class PersistenciaCapacidadesTest(unittest.TestCase):
    def test_bases_abstratas_com_um_caminho_ate_model(self):
        configure_mappers()
        self.assertEqual(len(list(db.Model.registry.mappers)), 20)
        self.assertEqual(len(db.metadata.tables), 20)
        self.assertEqual(CrudMixin.__bases__, (ModeloAtualizavel,))
        self.assertEqual(ModeloAtualizavel.__bases__, (ModeloBase,))
        self.assertEqual(ModeloBase.__bases__, (db.Model,))
        for base in (ModeloBase, ModeloAtualizavel, CrudMixin):
            self.assertTrue(base.__abstract__)
            self.assertNotIn('__tablename__', base.__dict__)
        self.assertFalse(hasattr(ModeloBase, 'atualizar'))
        self.assertFalse(hasattr(ModeloBase, 'deletar'))
        self.assertFalse(hasattr(ModeloAtualizavel, 'deletar'))

    def test_capacidades_das_vinte_models(self):
        imutaveis = {QuestaoVersao, QuestaoEvento, SimuladoVersao,
                     SimuladoVersaoItem, SimuladoEvento}
        planos = {PlanoEstudo, PlanoEstudoItem}
        for mapper in db.Model.registry.mappers:
            model = mapper.class_
            self.assertTrue(hasattr(model, 'salvar'))
            self.assertEqual(hasattr(model, 'atualizar'), model not in imutaveis)
            self.assertEqual(hasattr(model, 'deletar'), model not in imutaveis | planos)
            base = ModeloBase if model in imutaveis else ModeloAtualizavel if model in planos else CrudMixin
            self.assertEqual(model.__bases__, (base,))

    @patch('app.models.crud_mixin.db.session')
    def test_flush_falho_deixa_rollback_ao_caso_composto(self, session):
        session.flush.side_effect = RuntimeError('falha controlada')
        materia = Materia(nome='Antes')
        for operacao in (lambda: materia.salvar(confirmar=False),
                         lambda: materia.atualizar(confirmar=False, nome='Depois'),
                         lambda: materia.deletar(confirmar=False)):
            with self.assertRaises(RuntimeError):
                operacao()
        session.rollback.assert_not_called()
        session.commit.assert_not_called()
