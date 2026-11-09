"""Lock e permissão pública de Contas, sem exposição de identidade ORM."""
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository as _Privacidade
from app.modules.contas.services.validar_permissao_plano_service import ValidarPermissaoPlanoService as _Permissao
from app.modules.contas.services.validar_permissao_tutoria_service import ValidarPermissaoTutoriaService as _Tutoria

ValidarPermissaoPlanoService = _Permissao
ValidarPermissaoTutoriaService = _Tutoria


def bloquear_usuario(usuario_id):
    return _Privacidade.bloquear_usuario(usuario_id)


__all__ = ['bloquear_usuario', 'ValidarPermissaoPlanoService', 'ValidarPermissaoTutoriaService']
