"""Adaptação pequena dos conflitos de banco após rollback do caso de uso."""
from app.modules.contas.domain.autenticacao import AutenticacaoError, validar_dados
from app.transaction_manager import TransactionManager


def confirmar_acao(dados):
    validar_dados(dados, {'confirmar'})
    if dados['confirmar'] is not True:
        raise AutenticacaoError('Confirme explicitamente a ação.')


def executar_mutacao(operacao):
    try:
        return TransactionManager.executar(operacao)
    except Exception as erro:
        # CALL com cursor participante pode propagar o erro original do driver;
        # a Model/consulta ORM propaga o mesmo código em .orig. Sem SQL no Service.
        original = getattr(erro, 'orig', erro)
        args = getattr(original, 'args', ())
        numero = args[0] if args else None
        if numero == 1062 and 'uq_usuarios_email' in str(original):
            raise AutenticacaoError('Este e-mail já está em uso.',409,'email_em_uso') from None
        if numero == 1451:
            raise AutenticacaoError('A conta possui vínculos. Considere desativá-la.',409,'usuario_com_vinculos') from None
        if numero in {1205,1213}:
            raise AutenticacaoError('Operação concorrente. Confirme novamente.',409,'operacao_concorrente') from None
        raise
