"""Contratos editoriais, concorrência e rollback com MySQL real."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

from sqlalchemy import text
from app.core.relogio import agora_utc
from app.extensions import db
from app.modules.conteudo.models.questao_versao import QuestaoVersao
from app.modules.conteudo.services.gestao_questao_service import (
    ConsultarVersaoElegivelService,
    ConsultarVersaoHistoricaService,
    ConsultarVersoesElegiveisService,
    ConsultarVersoesHistoricasService,
    PublicarQuestaoService,
    EditarQuestaoService,
)
from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from tests.integration_support import MySQLIntegrationTestCase


class QuestoesVersionadasIntegrationTest(MySQLIntegrationTestCase):
    def setUp(self):
        materia=self.client.post(
            '/api/materias',
            json={
                'nome': 'Matéria '+uuid4().hex,
                'area_enem_id': 4
            }
        ).get_json()
        assunto=self.client.post(
            '/api/assuntos',
            json={
                'nome': 'Assunto '+uuid4().hex,
                'materia_id': materia['id']
            }
        ).get_json()
        self.materia_id=materia['id']
        self.assunto_id=assunto['id']
        self.dados={campo: 'Texto '+campo for campo in (
            'enunciado',
            'alternativa_a',
            'alternativa_b',
            'alternativa_c',
            'alternativa_d',
            'alternativa_e'
        )}
        self.dados.update(
            resposta_correta='A',
            dificuldade='media',
            explicacao=None,
            assunto_id=self.assunto_id
        )
        self.questao=self.client.post('/api/questoes', json=self.dados).get_json()
        self.path='/api/questoes/'+str(self.questao['id'])
        self.ator=self.client.get('/api/auth/sessao').get_json()['usuario']['id']
        with self.app.app_context():
            db.session.execute(
                text('UPDATE sessoes SET reautenticada_em=:data WHERE usuario_id=:id'),
                {'data': agora_utc(), 'id': self.ator}
            )
            db.session.commit()

    def publicar(self, revisao=1):
        return self.client.post(
            self.path+'/publicar',
            json={
                'revisao': revisao,
                'confirmar': True,
                'motivo': 'Revisado pelo teste'
            }
        )

    def detalhe(self):
        return self.client.get(self.path).get_json()

    def test_fluxo_versions_replay_arquivamento_e_procedure_legada(self):
        self.assertEqual(set(self.questao), {'id', *self.dados.keys()})
        self.assertEqual(self.detalhe()['status'], 'rascunho')
        self.assertEqual(self.detalhe()['versoes'], [])
        primeira=self.publicar()
        self.assertEqual(primeira.status_code, 200)
        versao=primeira.get_json()['versao_publicada_id']
        self.assertEqual(self.publicar().get_json()['versao_publicada_id'], versao)
        with self.app.app_context():
            seguro=ConsultarVersaoElegivelService.executar(versao)
            self.assertNotIn('resposta_correta', seguro)
            self.assertNotIn('explicacao', seguro)
            original=ConsultarVersaoHistoricaService.executar(versao, correcao=True)
            self.assertEqual(original['resposta_correta'], 'A')
            self.assertEqual(ConsultarVersoesElegiveisService.executar([versao]), {versao: seguro})
            self.assertEqual(
                ConsultarVersoesHistoricasService.executar(
                    [versao],
                    True
                ),
                {versao: original}
            )
            self.assertEqual(ConsultarVersoesHistoricasService.executar([]), {})
            with self.assertRaises(RecursoNaoEncontradoError):
                ConsultarVersoesHistoricasService.executar([versao, 2147483647])
        editada=self.client.put(
            self.path,
            json={
                'revisao': 1,
                'enunciado': 'Novo enunciado',
                'resposta_correta': 'B'
            }
        )
        self.assertEqual(editada.status_code, 200)
        self.assertEqual(editada.get_json()['versao_publicada_id'], versao)
        nova=self.publicar(2).get_json()['versao_publicada_id']
        self.assertNotEqual(nova, versao)
        with self.app.app_context():
            self.assertEqual(ConsultarVersaoHistoricaService.executar(versao, True), original)
            with self.assertRaises(ConflitoError):
                ConsultarVersaoElegivelService.executar(versao)
            self.assertEqual(set(ConsultarVersoesElegiveisService.executar([versao, nova])), {nova})
        corpo={'revisao': 2, 'confirmar': True, 'motivo': 'Retirada revisada'}
        self.assertEqual(self.client.post(self.path+'/arquivar', json=corpo).status_code, 200)
        self.assertEqual(self.client.post(self.path+'/arquivar', json=corpo).status_code, 200)
        self.assertEqual(
            self.client.put(
                self.path,
                json={
                    'revisao': 2,
                    'enunciado': 'x'
                }
            ).status_code,
            409
        )
        self.assertEqual(self.publicar(2).status_code, 409)
        with self.app.app_context():
            with self.assertRaises(ConflitoError):
                ConsultarVersaoElegivelService.executar(nova)
            self.assertEqual(ConsultarVersoesElegiveisService.executar([versao, nova]), {})
            self.assertEqual(
                ConsultarVersoesHistoricasService.executar(
                    [versao],
                    True
                ),
                {versao: original}
            )
            self.assertEqual(ConsultarVersaoHistoricaService.executar(versao, True), original)
            rows=db.session.execute(
                text('SELECT acao,ator_id FROM questao_eventos WHERE questao_id=:id'),
                {'id': self.questao['id']}
            ).all()
            self.assertEqual([r.acao for r in rows].count('publicacao'), 2)
            self.assertEqual([r.acao for r in rows].count('arquivamento'), 1)
            self.assertTrue(all(r.ator_id==self.ator for r in rows))
        legado=self.client.get(
            '/api/questoes/por-assunto',
            query_string={'assunto_id': self.assunto_id}
        ).get_json()
        self.assertEqual(legado[0]['enunciado'], 'Novo enunciado')
        self.assertEqual(self.client.delete(self.path).status_code, 405)

    def test_filtros_paginacao_head_erros_e_permissoes(self):
        url='/api/admin/questoes'
        consulta={
            'assunto_id': self.assunto_id,
            'materia_id': self.materia_id,
            'area_enem_id': 4,
            'status': 'rascunho',
            'dificuldade': 'media',
            'busca': 'Texto',
            'por_pagina': 1
        }
        dados=self.client.get(url, query_string=consulta).get_json()
        self.assertEqual(dados['total_itens'], 1)
        self.assertEqual(dados['itens'][0]['id'], self.questao['id'])
        self.assertEqual(self.client.head(self.path).status_code, 200)
        self.assertEqual(self.client.head(self.path).data, b'')
        self.assertEqual(self.client.get(self.path).headers['Cache-Control'], 'no-store')
        for filtro in (
            {'pagina': 0},
            {'pagina': ''},
            {'por_pagina': 101},
            {'materia_id': 'x'},
            {'dificuldade': 'alta'},
            {'status': 'ativa'},
            {'busca': 'x'*101},
            {'usuario_id': 2}
        ):
            self.assertEqual(self.client.get(url, query_string=filtro).status_code, 400)
        consulta['busca']='Inexistente'
        self.assertEqual(self.client.get(url, query_string=consulta).get_json()['itens'], [])
        self.assertEqual(self.client.get('/api/questoes/2147483647').status_code, 404)
        anonimo=self.app.test_client()
        self.assertEqual(anonimo.get(url).status_code, 401)
        self.assertEqual(anonimo.get(self.path).status_code, 401)
        token=anonimo.get('/api/auth/csrf').get_json()['csrf_token']
        email=uuid4().hex+'@teste.local'
        senha='Senha teste segura 123'
        headers={'Origin': 'http://frontend.test', 'X-CSRF-Token': token}
        self.assertEqual(
            anonimo.post(
                '/api/auth/cadastro',
                json={
                    'nome': 'Aluno',
                    'email': email,
                    'senha': senha,
                    'senha_confirmacao': senha,
                    'termos_uso': {
                        'versao': "2.0",
                        'aceito': True
                    }
                },
                headers=headers
            ).status_code,
            201
        )
        self.assertEqual(
            anonimo.post(
                '/api/auth/login',
                json={
                    'email': email,
                    'senha': senha
                },
                headers=headers
            ).status_code,
            200
        )
        self.assertEqual(anonimo.get(url).status_code, 403)
        self.assertEqual(anonimo.get(self.path).status_code, 403)

    def test_edicao_e_confirmacao_invalidas_sem_alteracao(self):
        for corpo, esperado in (
            (None, 400),
            ({}, 400),
            ({'revisao': True, 'enunciado': 'x'}, 400),
            ({'revisao': 1}, 400),
            ({'revisao': 1, 'status': 'publicada'}, 400),
            ({'revisao': 2, 'enunciado': 'x'}, 409),
            ({'revisao': 1, 'alternativa_a': ''}, 400)
        ):
            self.assertEqual(self.client.put(self.path, json=corpo).status_code, esperado)
        for corpo in (
            {'revisao': 1, 'confirmar': False, 'motivo': 'Teste'},
            {'revisao': 1, 'confirmar': True, 'motivo': 'x'},
            {'revisao': 1, 'confirmar': True, 'motivo': None},
            {'revisao': 1, 'confirmar': True, 'motivo': 'Teste', 'ator_id': 2}
        ):
            self.assertEqual(self.client.post(self.path+'/publicar', json=corpo).status_code, 400)
        self.assertEqual(self.detalhe()['revisao'], 1)
        self.assertEqual(self.detalhe()['versoes'], [])
        with self.app.app_context():
            for service in (ConsultarVersaoElegivelService, ConsultarVersaoHistoricaService):
                with self.assertRaises(RecursoNaoEncontradoError):
                    service.executar(2147483647)

    def test_snapshot_e_evento_append_only_inclusive_flush_orm(self):
        versao_id=self.publicar().get_json()['versao_publicada_id']
        from app.modules.conteudo.models.questao_evento import QuestaoEvento
        with self.app.app_context():
            versao=QuestaoVersao.buscar_por_id(versao_id)
            evento=db.session.execute(db.select(QuestaoEvento).where(QuestaoEvento.questao_id==self.questao['id'])).scalars().first()
            for registro in (versao, evento):
                self.assertFalse(hasattr(registro, 'atualizar'))
                self.assertFalse(hasattr(registro, 'deletar'))
                db.session.delete(registro)
                with self.assertRaises(ConflitoError):
                    db.session.flush()
                db.session.rollback()
            versao.enunciado='Mutação proibida'
            with self.assertRaises(ConflitoError):
                versao.salvar()
            evento=db.session.get(QuestaoEvento, evento.id)
            evento.motivo='Mutação proibida'
            with self.assertRaises(ConflitoError):
                evento.salvar()
            self.assertEqual(
                ConsultarVersaoHistoricaService.executar(versao_id)['enunciado'],
                self.dados['enunciado']
            )

    def test_catalogo_inativo_retira_elegibilidade_sem_mudar_snapshot(self):
        v=self.publicar().get_json()['versao_publicada_id']
        self.assertEqual(
            self.client.post(f'/api/assuntos/{self.assunto_id}/inativar').status_code,
            200
        )
        self.assertEqual(
            self.client.put(
                self.path,
                json={
                    'revisao': 1,
                    'enunciado': 'x'
                }
            ).status_code,
            400
        )
        with self.app.app_context():
            with self.assertRaises(ConflitoError):
                ConsultarVersaoElegivelService.executar(v)
            self.assertEqual(
                ConsultarVersaoHistoricaService.executar(
                    v,
                    True
                )['enunciado'],
                self.dados['enunciado']
            )
        self.assertEqual(
            self.client.post(f'/api/assuntos/{self.assunto_id}/reativar').status_code,
            200
        )
        self.assertEqual(
            self.client.put(
                self.path,
                json={
                    'revisao': 1,
                    'enunciado': 'x'
                }
            ).status_code,
            200
        )
        self.assertEqual(
            self.client.post(f'/api/materias/{self.materia_id}/inativar').status_code,
            200
        )
        self.assertEqual(self.publicar(2).status_code, 409)

    def test_publicacao_concorrente_e_edicao_obsoleta(self):
        barrier=Barrier(2)

        def publicar():
            with self.app.app_context():
                barrier.wait(timeout=10)
                return PublicarQuestaoService.executar(
                    self.questao['id'],
                    {'revisao': 1, 'confirmar': True, 'motivo': 'Revisão concorrente'},
                    self.ator
                )
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(publicar) for _ in range(2)]
            resultados=[f.result(timeout=20) for f in futures]
        self.assertEqual(resultados[0]['versao_publicada_id'], resultados[1]['versao_publicada_id'])
        self.assertEqual(len(resultados[0]['versoes']), 1)
        barrier=Barrier(2)

        def editar():
            with self.app.app_context():
                barrier.wait(timeout=10)
                try:
                    EditarQuestaoService.executar(
                        self.questao['id'],
                        {
                            'revisao': 1,
                            'enunciado': 'Novo'
                        },
                        self.ator
                    )
                    return 200
                except ConflitoError:
                    return 409
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(editar) for _ in range(2)]
            self.assertEqual(sorted(f.result(timeout=20) for f in futures), [200, 409])

    def test_rollback_real_na_ultima_gravacao_de_publicacao_e_cadastro(self):
        # Falha injetada pelo próprio MySQL; não simula o acesso ao banco.
        with self.app.app_context():
            db.session.execute(text("CREATE TRIGGER falha_publicacao BEFORE UPDATE ON questoes "
                "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Falha controlada de teste'"))
            db.session.commit()
        try:
            self.assertEqual(self.publicar().status_code, 500)
            self.assertEqual(self.detalhe()['versoes'], [])
            self.assertIsNone(self.detalhe()['versao_publicada_id'])
            with self.app.app_context():
                count=db.session.execute(
                    text('SELECT COUNT(*) FROM questao_eventos WHERE questao_id=:id'),
                    {'id': self.questao['id']}
                ).scalar_one()
                self.assertEqual(count, 1)
        finally:
            with self.app.app_context():
                db.session.execute(text('DROP TRIGGER falha_publicacao'))
                db.session.commit()
        with self.app.app_context():
            db.session.execute(text("CREATE TRIGGER falha_evento BEFORE INSERT ON questao_eventos "
                "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Falha controlada de teste'"))
            db.session.commit()
        try:
            novos=dict(self.dados, enunciado='Rollback '+uuid4().hex)
            self.assertEqual(self.client.post('/api/questoes', json=novos).status_code, 500)
            lista=self.client.get(
                '/api/admin/questoes',
                query_string={'busca': novos['enunciado']}
            ).get_json()
            self.assertEqual(lista['total_itens'], 0)
        finally:
            with self.app.app_context():
                db.session.execute(text('DROP TRIGGER falha_evento'))
                db.session.commit()

    def test_reautenticacao_csrf_origem_e_arquivamento_obsoleto(self):
        with self.app.app_context():
            db.session.execute(
                text('UPDATE sessoes SET reautenticada_em=:data WHERE usuario_id=:id'),
                {'data': agora_utc()-timedelta(minutes=15), 'id': self.ator}
            )
            db.session.commit()
        self.assertEqual(self.publicar().status_code, 403)
        self.assertEqual(self.publicar().get_json()['codigo'], 'reautenticacao_necessaria')
        with self.app.app_context():
            db.session.execute(
                text('UPDATE sessoes SET reautenticada_em=:data WHERE usuario_id=:id'),
                {'data': agora_utc(), 'id': self.ator}
            )
            db.session.commit()
        self.assertEqual(
            self.client.post(
                self.path+'/publicar',
                json={},
                headers={'Origin': 'http://indevida.test'}
            ).status_code,
            403
        )
        self.assertEqual(
            self.client.post(
                self.path+'/publicar',
                json={},
                headers={'X-CSRF-Token': 'invalido'}
            ).status_code,
            403
        )
        self.assertEqual(
            self.client.post(
                self.path+'/arquivar',
                json={
                    'revisao': 2,
                    'confirmar': True,
                    'motivo': 'Teste'
                }
            ).status_code,
            409
        )
