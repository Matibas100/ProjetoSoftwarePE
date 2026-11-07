"""Participa da negativa; o chamador conserva lock e commit/rollback."""
from app.modules.plano_estudos.repositories.plano_estudo_repository import PlanoEstudoRepository


class EliminarPlanosPropriosService:
    def executar(self, usuario_id):
        PlanoEstudoRepository.eliminar_planos_proprios(usuario_id)
