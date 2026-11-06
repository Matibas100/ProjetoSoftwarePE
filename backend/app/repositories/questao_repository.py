from sqlalchemy import text, select, func

from app.extensions import db
from app.models.questao import Questao
from app.models.questao_versao import QuestaoVersao
from app.models.assunto import Assunto
from app.models.materia import Materia
from app.models.area_enem import AreaEnem


class QuestaoRepository:
    """Executa a consulta especializada de Questoes por Assunto."""

    @staticmethod
    def pares_elegiveis_plano(assunto_ids, bloquear=False):
        """Disponibilidade atual por classificação, sem expor conteúdo ou gabarito.

        Na geração, a leitura final compartilha locks com retirada/transferência.
        O vínculo atual deve coincidir também com o snapshot da versão publicada.
        """
        if not assunto_ids:
            return set()
        consulta = (select(QuestaoVersao.assunto_id, QuestaoVersao.materia_id)
            .join(Questao, Questao.id == QuestaoVersao.questao_id)
            .join(Assunto, Assunto.id == QuestaoVersao.assunto_id)
            .join(Materia, Materia.id == QuestaoVersao.materia_id)
            .where(QuestaoVersao.assunto_id.in_(assunto_ids), QuestaoVersao.estado == "publicada",
                Questao.status != "arquivada", Questao.versao_publicada_id == QuestaoVersao.id,
                Assunto.status == "ativa", Materia.status == "ativa", Assunto.materia_id == Materia.id))
        if bloquear:
            consulta = consulta.with_for_update(read=True)
        return set(db.session.execute(consulta).all())

    @staticmethod
    def contagens_dashboard(contexto):
        estados = dict(contexto.executar(select(Questao.status, func.count()).group_by(Questao.status)).all())
        return {"rascunhos": estados.get("rascunho", 0), "publicadas": estados.get("publicada", 0),
            "arquivadas": estados.get("arquivada", 0)}

    @staticmethod
    def projecao_classificacao_historica():
        """Contrato de leitura de classificação das versões publicadas imutáveis."""
        q = QuestaoVersao
        return select(q.id.label("questao_versao_id"), q.materia_id, q.materia_nome,
            q.assunto_id, q.assunto_nome).where(q.estado == "publicada")

    @staticmethod
    def bloquear(questao_id):
        return db.session.execute(select(Questao).where(Questao.id == questao_id)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def bloquear_classificacao(assunto_id):
        # A inativação/transferência também precisa dos locks InnoDB destas linhas.
        assunto = db.session.execute(select(Assunto).where(Assunto.id == assunto_id)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
        if assunto is None:
            return None
        materia = db.session.execute(select(Materia).where(Materia.id == assunto.materia_id)
            .with_for_update().execution_options(populate_existing=True)).scalar_one()
        area = AreaEnem.buscar_por_id(materia.area_enem_id)
        return assunto, materia, area

    @staticmethod
    def versoes(questao_id):
        return db.session.execute(select(QuestaoVersao).where(QuestaoVersao.questao_id == questao_id)
            .order_by(QuestaoVersao.numero)).scalars().all()

    @staticmethod
    def listar_admin(filtros, pagina, por_pagina):
        condicoes = []
        for campo in ("status", "dificuldade", "assunto_id"):
            if filtros.get(campo):
                condicoes.append(getattr(Questao, campo) == filtros[campo])
        if filtros.get("materia_id"):
            condicoes.append(Materia.id == filtros["materia_id"])
        if filtros.get("area_enem_id"):
            condicoes.append(AreaEnem.id == filtros["area_enem_id"])
        if filtros.get("busca"):
            condicoes.append(Questao.enunciado.contains(filtros["busca"], autoescape=True))
        base = select(Questao, Assunto, Materia, AreaEnem).join(Assunto, Questao.assunto_id == Assunto.id)
        base = base.join(Materia, Assunto.materia_id == Materia.id).join(AreaEnem, Materia.area_enem_id == AreaEnem.id)
        base = base.where(*condicoes)
        total = db.session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        linhas = db.session.execute(base.order_by(Questao.id.desc()).offset((pagina-1)*por_pagina)
            .limit(por_pagina)).all()
        return linhas, total

    @staticmethod
    def versao_elegivel(versao_id, bloquear=False):
        consulta = (select(QuestaoVersao).join(Questao, Questao.id == QuestaoVersao.questao_id)
            .join(Assunto, Assunto.id == QuestaoVersao.assunto_id)
            .join(Materia, Materia.id == QuestaoVersao.materia_id)
            .where(QuestaoVersao.id == versao_id, QuestaoVersao.estado == "publicada",
                Questao.status != "arquivada", Questao.versao_publicada_id == QuestaoVersao.id,
                Assunto.status == "ativa", Materia.status == "ativa"))
        if bloquear:
            consulta = consulta.with_for_update().execution_options(populate_existing=True)
        return db.session.execute(consulta).scalar_one_or_none()

    @staticmethod
    def listar_elegiveis(filtros, pagina, limite):
        base = select(QuestaoVersao).join(Questao, Questao.id == QuestaoVersao.questao_id)
        base = base.join(Assunto, Assunto.id == QuestaoVersao.assunto_id)
        base = base.join(Materia, Materia.id == QuestaoVersao.materia_id)
        base = base.where(QuestaoVersao.estado == "publicada", Questao.status != "arquivada",
            Questao.versao_publicada_id == QuestaoVersao.id, Assunto.status == "ativa", Materia.status == "ativa")
        for campo in ("assunto_id", "materia_id"):
            if filtros.get(campo):
                base = base.where(getattr(QuestaoVersao, campo) == filtros[campo])
        total = db.session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        linhas = db.session.execute(base.order_by(QuestaoVersao.questao_id)
            .offset((pagina - 1) * limite).limit(limite)).scalars().all()
        return linhas, total

    @staticmethod
    def versoes_elegiveis(ids):
        if not ids:
            return []
        consulta = (select(QuestaoVersao).join(Questao, Questao.id == QuestaoVersao.questao_id)
            .join(Assunto, Assunto.id == QuestaoVersao.assunto_id)
            .join(Materia, Materia.id == QuestaoVersao.materia_id)
            .where(QuestaoVersao.id.in_(ids), QuestaoVersao.estado == "publicada",
                Questao.status != "arquivada", Questao.versao_publicada_id == QuestaoVersao.id,
                Assunto.status == "ativa", Materia.status == "ativa"))
        return db.session.execute(consulta).scalars().all()

    @staticmethod
    def versoes_historicas(ids):
        if not ids:
            return []
        return db.session.execute(select(QuestaoVersao).where(
            QuestaoVersao.id.in_(ids), QuestaoVersao.estado == "publicada")).scalars().all()

    @staticmethod
    def buscar_por_assunto(assunto_id):
        resultado = db.session.execute(
            text("CALL sp_questoes_por_assunto(:assunto_id)"),
            {"assunto_id": assunto_id},
        )
        try:
            return [dict(linha) for linha in resultado.mappings().all()]
        finally:
            resultado.close()
