from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.area_enem import AreaEnem
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository


DESTINOS = {"inativar": "inativa", "arquivar": "arquivada", "reativar": "ativa"}
TRANSICOES = {
    "ativa": {"inativa", "arquivada"},
    "inativa": {"ativa", "arquivada"},
    "arquivada": {"ativa"},
}


def _validar_transicao(registro, acao):
    destino = DESTINOS.get(acao)
    if destino is None or destino not in TRANSICOES.get(registro.status, set()):
        raise DadosInvalidosError("Transicao de status nao permitida.")
    return destino


class AlterarStatusMateriaService:
    @staticmethod
    def executar(materia_id, acao):
        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")
        destino = _validar_transicao(materia, acao)
        if destino == "arquivada":
            pendentes = CatalogoRepository.contar_assuntos_nao_arquivados(materia_id)
            if pendentes:
                raise ConflitoError(
                    "A materia possui assuntos ativos ou inativos.",
                    detalhes={"assuntos_nao_arquivados": pendentes},
                )
        if destino == "ativa" and AreaEnem.buscar_por_id(materia.area_enem_id) is None:
            raise ConflitoError("A materia nao possui uma Area do ENEM valida.")
        materia.atualizar(status=destino)
        return materia.to_dict()


class AlterarStatusAssuntoService:
    @staticmethod
    def executar(assunto_id, acao):
        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")
        destino = _validar_transicao(assunto, acao)
        if destino == "ativa":
            materia = Materia.buscar_por_id(assunto.materia_id)
            if materia is None or materia.status != "ativa":
                raise ConflitoError("A materia precisa estar ativa para reativar o assunto.")
            if CatalogoRepository.existe_assunto_equivalente(
                assunto.materia_id, assunto.nome_normalizado, ignorar_id=assunto.id
            ):
                raise ConflitoError("Ja existe um assunto equivalente nesta materia.")
        assunto.atualizar(status=destino)
        return assunto.to_dict()
