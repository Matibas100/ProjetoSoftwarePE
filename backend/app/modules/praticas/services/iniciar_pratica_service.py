from sqlalchemy.exc import IntegrityError
from app.core.relogio import agora_utc
from app.exceptions import ConflitoError
from app.modules.praticas.models.pratica_tentativa import PraticaTentativa
from app.modules.praticas.repositories.pratica_repository import PraticaRepository
from app.modules.praticas.services.consultar_pratica_service import detalhe
from app.modules.conteudo.api import ConsultarVersaoElegivelService
from app.modules.praticas.services.pratica_validacao import inicio
from app.transaction_manager import TransactionManager


class IniciarPraticaService:
    @staticmethod
    def executar(usuario_id, dados):
        versao_id, chave = inicio(dados)

        def replay(tentativa):
            if tentativa.questao_versao_id != versao_id:
                raise ConflitoError("Chave já utilizada para outra versão.")
            return detalhe(tentativa), 200

        def criar():
            versao = ConsultarVersaoElegivelService.executar(versao_id)
            tentativa = PraticaTentativa(
                usuario_id=usuario_id,
                questao_versao_id=versao_id,
                chave_envio=chave,
                estado="em_andamento",
                iniciada_em=agora_utc(),
                assunto_id=versao["assunto"]["id"],
                assunto_nome=versao["assunto"]["nome"],
                materia_id=versao["materia"]["id"],
                materia_nome=versao["materia"]["nome"]
            )
            tentativa.salvar(confirmar=False)
            return detalhe(tentativa), 201

        existente = PraticaRepository.por_chave(usuario_id, chave)
        if existente is not None:
            return TransactionManager.executar(lambda: replay(existente))
        try:
            return TransactionManager.executar(criar)
        except IntegrityError:
            # UNIQUE resolve a disputa. A transação falha já foi revertida.
            def recuperar():
                existente = PraticaRepository.por_chave(usuario_id, chave, bloquear=True)
                if existente is None:
                    raise
                return replay(existente)
            return TransactionManager.executar(recuperar)
