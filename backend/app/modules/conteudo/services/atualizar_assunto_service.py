from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.domain.catalogo import normalizar_nome_assunto
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository
from app.modules.conteudo.services.catalogo_validacao import validar_descricao, validar_id, validar_nome
from app.modules.conteudo.services.transferir_assunto_service import TransferirAssuntoService


class AtualizarAssuntoService:
    @staticmethod
    def executar(assunto_id, dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados do assunto em formato JSON.")

        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        campos_permitidos = {"nome", "descricao", "materia_id"}
        if not campos_permitidos.intersection(dados):
            raise DadosInvalidosError(
                "Informe nome, descricao ou materia_id para atualizar."
            )

        dados_atualizacao = {}

        if "nome" in dados:
            nome = validar_nome(dados["nome"], "do assunto", 150)
            dados_atualizacao["nome"] = nome
            dados_atualizacao["nome_normalizado"] = normalizar_nome_assunto(nome)

        if "descricao" in dados:
            dados_atualizacao["descricao"] = validar_descricao(dados["descricao"])

        if "materia_id" in dados:
            materia_id = validar_id(dados["materia_id"], "materia_id")
            materia = Materia.buscar_por_id(materia_id)
            if materia is None:
                raise RecursoNaoEncontradoError("Materia nao encontrada.")
            if materia_id != assunto.materia_id:
                previa = TransferirAssuntoService.previa(assunto_id, materia_id)
                return TransferirAssuntoService.executar(
                    assunto_id,
                    {
                        "materia_destino_id": materia_id,
                        "impacto_esperado": previa["impacto"],
                    },
                    atualizacoes=dados_atualizacao,
                )

        materia_final = dados.get("materia_id", assunto.materia_id)
        normalizado_final = dados_atualizacao.get(
            "nome_normalizado", assunto.nome_normalizado
        )
        if CatalogoRepository.existe_assunto_equivalente(
            materia_final, normalizado_final, ignorar_id=assunto_id
        ):
            raise ConflitoError("Ja existe um assunto equivalente nesta materia.")

        try:
            assunto.atualizar(**dados_atualizacao)
        except IntegrityError as erro:
            raise ConflitoError(
                "Ja existe um assunto equivalente nesta materia."
            ) from erro

        return assunto.to_dict()
