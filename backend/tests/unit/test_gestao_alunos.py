import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError, OperationalError
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.domain.gestao_alunos import email_mascarado, validar_id, exigir_aluno
from app.modules.contas.services.listar_alunos_admin_service import ListarAlunosAdminService
from app.modules.contas.services.gestao_alunos_validacao import confirmar_acao, executar_mutacao
from app.modules.contas.services.atualizar_aluno_admin_service import AtualizarAlunoAdminService
from app.modules.contas.services.criar_aluno_admin_service import CriarAlunoAdminService


class GestaoAlunosTest(unittest.TestCase):
    def test_ids_confirmacao_e_mascara_segura(self):
        for valor in [None,True,False,'1',0,-1,2147483648,1.2]:
            with self.subTest(valor=valor),self.assertRaises(AutenticacaoError): validar_id(valor)
        self.assertEqual(validar_id(2147483647),2147483647)
        for email in [None,'invalido','a@@teste.local','à@teste.local']:
            self.assertEqual(email_mascarado(email),'***')
        self.assertEqual(email_mascarado(' Aluno@TESTE.local '),'a***@teste.local')
        for dados in [None,[],{}, {'confirmar':1},{'confirmar':False},{'confirmar':True,'ator':1}]:
            with self.assertRaises(AutenticacaoError): confirmar_acao(dados)
        confirmar_acao({'confirmar':True})
        for alvo in [None,SimpleNamespace(perfil='administrador')]:
            with self.assertRaises(AutenticacaoError) as erro: exigir_aluno(alvo)
            self.assertEqual(erro.exception.codigo,'usuario_nao_encontrado')

    def test_query_validada_antes_da_consulta_e_total_independente(self):
        consulta=Mock()
        consulta.listar.return_value=([],42)
        service=ListarAlunosAdminService(consulta)
        invalidos=[{'pagina':None},{'pagina':True},{'pagina':'١'},{'pagina':''},{'pagina':'0'},
            {'por_pagina':101},{'pagina':1.2},{'busca':None},{'busca':'a'*255},{'status':None},
            {'perfil':'aluno'},{'pagina':'2147483648'},{'por_pagina':'abc'}]
        for parametros in invalidos:
            with self.subTest(parametros=parametros),self.assertRaises(AutenticacaoError): service.executar(parametros)
        consulta.listar.assert_not_called()
        envelope=service.executar({'pagina':'4','por_pagina':'20','busca':' %_\\ ','status':'inativo'})
        consulta.listar.assert_called_once_with('%_\\',False,4,20)
        self.assertEqual(envelope,{'itens':[],'pagina':4,'por_pagina':20,'total_itens':42,'total_paginas':3})
        consulta.listar.return_value=([{'id':1,'nome':'Aluno','email':'aluno@teste.local','perfil':'aluno',
            'ativo':1,'criado_em':datetime(2026,11,9)}],1)
        envelope=service.executar({})
        self.assertEqual(envelope['itens'][0]['email_mascarado'],'a***@teste.local')
        self.assertNotIn('email',envelope['itens'][0])

    def test_mapeia_somente_erros_especificos_apos_fronteira(self):
        with patch('app.modules.contas.services.gestao_alunos_validacao.TransactionManager.executar') as transacao:
            for numero,chave,codigo in [(1062,'uq_usuarios_email','email_em_uso'),(1451,'fk','usuario_com_vinculos'),
                (1205,'lock','operacao_concorrente'),(1213,'lock','operacao_concorrente')]:
                transacao.side_effect=OperationalError(None,None,Exception(numero,chave))
                with self.assertRaises(AutenticacaoError) as erro: executar_mutacao(Mock())
                self.assertEqual(erro.exception.codigo,codigo)
                self.assertNotIn(chave,str(erro.exception))
            for original in [Exception(1062,'outra_chave'),Exception(1234,'erro'),Exception()]:
                transacao.side_effect=IntegrityError(None,None,original)
                with self.assertRaises(IntegrityError): executar_mutacao(Mock())
            transacao.side_effect=Exception(1205,'Falha crua de cursor')
            with self.assertRaises(AutenticacaoError) as erro: executar_mutacao(Mock())
            self.assertEqual(erro.exception.codigo,'operacao_concorrente')

    def test_criacao_perfil_fixo_hash_sem_mutar_entrada(self):
        with patch('app.modules.contas.services.criar_aluno_admin_service.executar_mutacao',side_effect=lambda op:op()), \
             patch('app.modules.contas.services.autenticacao_service.Usuario') as model:
            usuario=model.return_value
            usuario.salvar.return_value=usuario
            usuario.id=1;usuario.nome='Aluno';usuario.email='aluno@teste.local';usuario.perfil='aluno';usuario.ativo=True;usuario.criado_em=datetime(2026,11,9)
            dados={'nome':' Aluno ','email':' ALUNO@teste.local ','senha':'Senha 123','senha_confirmacao':'Senha 123'}
            retorno=CriarAlunoAdminService.executar(dados)
            self.assertEqual(model.call_args.kwargs['perfil'],'aluno')
            self.assertTrue(model.call_args.kwargs['senha_hash'].startswith('scrypt:'))
            self.assertNotIn('senha_hash',retorno)
            self.assertEqual(dados['email'],' ALUNO@teste.local ')
            usuario.salvar.assert_called_once_with(confirmar=False)

    def test_edicao_noop_nome_e_email_revogam_somente_quando_necessario(self):
        with patch('app.modules.contas.services.atualizar_aluno_admin_service.executar_mutacao',side_effect=lambda op:op()), \
             patch('app.modules.contas.services.atualizar_aluno_admin_service.UsuarioRepository.bloquear') as lock, \
             patch('app.modules.contas.services.atualizar_aluno_admin_service.AutenticacaoRepository.revogar_usuario') as revogar:
            u=Mock(id=1,nome='Aluno',email='aluno@teste.local',perfil='aluno',ativo=False,criado_em=datetime(2026,11,9))
            lock.return_value=u
            AtualizarAlunoAdminService.executar(1,{'nome':'Aluno','email':'ALUNO@teste.local'})
            u.atualizar.assert_not_called();revogar.assert_not_called()
            AtualizarAlunoAdminService.executar(1,{'nome':'Corrigido','email':'aluno@teste.local'})
            revogar.assert_not_called()
            AtualizarAlunoAdminService.executar(1,{'nome':'Corrigido','email':'novo@teste.local'})
            self.assertEqual(revogar.call_count,1)
            for dados in [{'nome':'X','email':'novo@teste.local'},{'nome':'Nome','email':'invalido'}, {'nome':'Nome','email':'a@teste.local','perfil':'aluno'}]:
                with self.assertRaises(AutenticacaoError): AtualizarAlunoAdminService.executar(1,dados)
