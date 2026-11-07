from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository as Repo
from app.modules.contas.services.privacidade_validacao import validar_corpo, validar_versao, validar_revisao, resposta_reenvio, resposta_nova
from app.transaction_manager import TransactionManager


class AceitarTermosUsoService:
    @staticmethod
    def executar(usuario_id, dados):
        validar_corpo(dados)
        def registrar():
            Repo.bloquear_usuario(usuario_id)
            anterior = Repo.por_chave(usuario_id, dados["chave_envio"])
            registros = Repo.ultimas(usuario_id)
            if anterior is not None:
                return resposta_reenvio(anterior, dados, "uso", "aceitar", registros)
            doc = validar_versao("uso", dados["versao"])
            validar_revisao(registros["uso"], dados["revisao"])
            registro = RegistroPrivacidade(usuario_id=usuario_id, tipo="uso", acao="aceitar",
                versao=doc["versao"], documento_sha256=doc["sha256"],
                chave_envio=dados["chave_envio"], revisao_base=dados["revisao"]).salvar(confirmar=False)
            return resposta_nova(registro, registros)
        return TransactionManager.executar(registrar)
