from sqlalchemy.exc import IntegrityError
from app.core.relogio import agora_utc
from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.modules.simulados.models.simulado import (
    SimuladoVersao,
    SimuladoTentativa,
    SimuladoResposta,
)
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository as Repo
from app.modules.simulados.services.consultar_simulado_service import detalhe
from app.modules.simulados.services.gestao_simulado_service import elegiveis
from app.modules.simulados.services.simulado_validacao import inicio_simulado
from app.transaction_manager import TransactionManager


class IniciarSimuladoService:
    @staticmethod
    def executar(usuario_id, dados):
        versao_id, chave = inicio_simulado(dados)

        def replay(t):
            if t.simulado_versao_id != versao_id:
                raise ConflitoError("Chave já utilizada para outra versão.")
            return detalhe(t, bloquear=True), 200

        def operacao():
            v = SimuladoVersao.buscar_por_id(versao_id)
            if v is None:
                raise RecursoNaoEncontradoError("Versão de simulado não encontrada.")
            s = Repo.bloquear(v.simulado_id)
            existente = Repo.por_chave(usuario_id, chave)
            if existente:
                return replay(existente)
            em_andamento = Repo.andamento(usuario_id, versao_id)
            if em_andamento:
                return detalhe(em_andamento, bloquear=True), 200
            if s.estado != "publicado" or s.simulado_versao_id != versao_id:
                raise ConflitoError("Simulado indisponível para novo início.")
            itens = Repo.itens(versao_id=versao_id)
            elegiveis([i.questao_versao_id for i in itens])
            t = SimuladoTentativa(
                usuario_id=usuario_id,
                simulado_versao_id=versao_id,
                chave_envio=chave,
                estado="em_andamento",
                revisao=1,
                iniciada_em=agora_utc()
            ).salvar(confirmar=False)
            for i in itens:
                SimuladoResposta(tentativa_id=t.id, item_id=i.id).salvar(confirmar=False)
            return detalhe(t, bloquear=True), 201
        try:
            return TransactionManager.executar(operacao)
        except IntegrityError:
            # UNIQUE resolve inclusive inícios da mesma chave em versões diferentes.
            def recuperar():
                t = Repo.por_chave(usuario_id, chave)
                if t is None:
                    raise
                return replay(t)
            return TransactionManager.executar(recuperar)
