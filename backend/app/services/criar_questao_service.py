from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.models.assunto import Assunto
from app.models.questao import Questao


class CriarQuestaoService:
    DIFICULDADES_VALIDAS = {"facil", "media", "dificil"}
    RESPOSTAS_VALIDAS = {"A", "B", "C", "D", "E"}
    CAMPOS_TEXTO_OBRIGATORIOS = (
        "enunciado",
        "alternativa_a",
        "alternativa_b",
        "alternativa_c",
        "alternativa_d",
        "alternativa_e",
    )

    @classmethod
    def executar(cls, dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados da questao em formato JSON.")

        valores = {}
        for campo in cls.CAMPOS_TEXTO_OBRIGATORIOS:
            valor = dados.get(campo)
            if not isinstance(valor, str) or not valor.strip():
                raise DadosInvalidosError(
                    f"O campo {campo} e obrigatorio e nao pode ser vazio."
                )
            valores[campo] = valor.strip()

        resposta_correta = dados.get("resposta_correta")
        if not isinstance(resposta_correta, str):
            raise DadosInvalidosError("A resposta_correta e obrigatoria.")
        resposta_correta = resposta_correta.strip()
        if resposta_correta not in cls.RESPOSTAS_VALIDAS:
            raise DadosInvalidosError(
                "resposta_correta deve ser A, B, C, D ou E."
            )

        dificuldade = dados.get("dificuldade")
        if not isinstance(dificuldade, str):
            raise DadosInvalidosError("A dificuldade e obrigatoria.")
        dificuldade = dificuldade.strip()
        if dificuldade not in cls.DIFICULDADES_VALIDAS:
            raise DadosInvalidosError(
                "dificuldade deve ser facil, media ou dificil."
            )

        assunto_id = dados.get("assunto_id")
        if (
            not isinstance(assunto_id, int)
            or isinstance(assunto_id, bool)
            or assunto_id <= 0
        ):
            raise DadosInvalidosError("assunto_id deve ser um numero inteiro valido.")

        if Assunto.buscar_por_id(assunto_id) is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        explicacao = dados.get("explicacao")
        if explicacao is not None and not isinstance(explicacao, str):
            raise DadosInvalidosError("A explicacao deve ser um texto ou nula.")

        questao = Questao(
            **valores,
            resposta_correta=resposta_correta,
            explicacao=explicacao.strip() if isinstance(explicacao, str) else None,
            dificuldade=dificuldade,
            assunto_id=assunto_id,
        )

        try:
            questao.salvar()
        except IntegrityError as erro:
            raise ConflitoError(
                "Nao foi possivel cadastrar a questao por conflito de integridade."
            ) from erro

        return questao.to_dict()
