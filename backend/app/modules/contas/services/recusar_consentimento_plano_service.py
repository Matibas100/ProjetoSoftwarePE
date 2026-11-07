from typing import Callable
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository as Repo
from app.modules.contas.services.privacidade_validacao import validar_corpo, validar_versao, validar_revisao, resposta_reenvio, resposta_nova
from app.transaction_manager import TransactionManager


class RecusarConsentimentoPlanoService:
    def __init__(self, eliminar_planos: Callable[[int], None]):
        self._eliminar_planos = eliminar_planos

    def executar(self, usuario_id, dados):
        validar_corpo(dados, negativa=True)
        def registrar():
            Repo.bloquear_usuario(usuario_id)
            anterior = Repo.por_chave(usuario_id, dados["chave_envio"])
            registros = Repo.ultimas(usuario_id)
            if anterior is not None:
                return resposta_reenvio(anterior, dados, "plano", "recusar", registros)
            doc = validar_versao("plano", dados["versao"])
            atual = registros["plano"]
            validar_revisao(atual, dados["revisao"])
            if atual is not None and atual.acao == "aceitar":
                raise AutenticacaoError("Use revogar para retirar uma aceitação existente.", 400, "decisao_invalida")
            registro = RegistroPrivacidade(usuario_id=usuario_id, tipo="plano", acao="recusar",
                versao=doc["versao"], documento_sha256=doc["sha256"],
                chave_envio=dados["chave_envio"], revisao_base=dados["revisao"]).salvar(confirmar=False)
            self._eliminar_planos(usuario_id)
            return resposta_nova(registro, registros)
        return TransactionManager.executar(registrar)
