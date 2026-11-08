"""Representação técnica das consultas administrativas existentes."""
from app.contracts.catalogo import AssuntoAdminRegistro, FiltrosCatalogo, MateriaAdminRegistro
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository


class ConsultaMateriasMySQL:
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[MateriaAdminRegistro], int]:
        return CatalogoRepository.listar_materias_admin(filtros, pagina, limite)


class ConsultaAssuntosMySQL:
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[AssuntoAdminRegistro], int]:
        return CatalogoRepository.listar_assuntos_admin(filtros, pagina, limite)
