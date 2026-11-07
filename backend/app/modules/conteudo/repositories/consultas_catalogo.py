"""Representação técnica das consultas administrativas existentes."""
from app.contracts.catalogo import AssuntoAdminRegistro, FiltrosCatalogo, MateriaAdminRegistro
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository


class ConsultaMateriasMySQL:
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[MateriaAdminRegistro], int]:
        linhas, total = CatalogoRepository.listar_materias_admin(filtros, pagina, limite)
        return [{**m.to_dict(), 'area_enem': a.to_dict(), 'assuntos': assuntos,
                 'questoes': questoes} for m, a, assuntos, questoes in linhas], total


class ConsultaAssuntosMySQL:
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[AssuntoAdminRegistro], int]:
        linhas, total = CatalogoRepository.listar_assuntos_admin(filtros, pagina, limite)
        return [{**s.to_dict(), 'materia': m.to_dict(), 'area_enem': a.to_dict(),
                 'questoes': questoes} for s, m, a, questoes in linhas], total
