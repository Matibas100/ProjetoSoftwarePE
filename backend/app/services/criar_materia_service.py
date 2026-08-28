from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError
from app.models.materia import Materia


class CriarMateriaService:
    @staticmethod
    def executar(dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados da materia em formato JSON.")

        nome = dados.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            raise DadosInvalidosError("O nome da materia e obrigatorio.")

        nome = nome.strip()
        if len(nome) > 100:
            raise DadosInvalidosError("O nome deve possuir no maximo 100 caracteres.")

        descricao = dados.get("descricao")
        if descricao is not None and not isinstance(descricao, str):
            raise DadosInvalidosError("A descricao deve ser um texto ou nula.")

        materia = Materia(
            nome=nome,
            descricao=descricao.strip() if isinstance(descricao, str) else None,
        )

        try:
            materia.salvar()
        except IntegrityError as erro:
            raise ConflitoError("Ja existe uma materia com esse nome.") from erro

        return materia.to_dict()
