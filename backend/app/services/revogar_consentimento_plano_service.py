from app.domain.autenticacao import AutenticacaoError
from app.models.registro_privacidade import RegistroPrivacidade
from app.repositories.privacidade_repository import PrivacidadeRepository as Repo
from app.services.privacidade_validacao import validar_corpo, validar_revisao, resposta_reenvio, resposta_nova
from app.transaction_manager import TransactionManager


class RevogarConsentimentoPlanoService:
    @staticmethod
    def executar(usuario_id, dados):
        validar_corpo(dados, negativa=True)
        def registrar():
            Repo.bloquear_usuario(usuario_id)
            anterior = Repo.por_chave(usuario_id, dados["chave_envio"])
            registros = Repo.ultimas(usuario_id)
            if anterior is not None:
                return resposta_reenvio(anterior, dados, "plano", "revogar", registros)
            atual = registros["plano"]
            validar_revisao(atual, dados["revisao"])
            if atual is None or atual.acao != "aceitar":
                raise AutenticacaoError("Só é possível revogar a última aceitação do plano.", 400, "decisao_invalida")
            if dados["versao"] != atual.versao:
                raise AutenticacaoError("Confirme a versão da aceitação que deseja revogar.", 409, "termo_desatualizado")
            registro = RegistroPrivacidade(usuario_id=usuario_id, tipo="plano", acao="revogar",
                versao=atual.versao, documento_sha256=atual.documento_sha256,
                chave_envio=dados["chave_envio"], revisao_base=dados["revisao"]).salvar(confirmar=False)
            Repo.eliminar_planos_proprios(usuario_id)
            return resposta_nova(registro, registros)
        return TransactionManager.executar(registrar)
