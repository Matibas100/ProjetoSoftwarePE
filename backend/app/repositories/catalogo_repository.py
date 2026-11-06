from sqlalchemy import distinct, func, or_, select

from app.extensions import db
from app.models.area_enem import AreaEnem
from app.models.assunto import Assunto
from app.models.assunto_transferencia import AssuntoTransferencia
from app.models.materia import Materia
from app.models.questao import Questao


class CatalogoRepository:
    """Consultas especializadas, agregacoes e locks do catalogo."""

    @staticmethod
    def listar_assuntos_ativos(materia_id=None):
        consulta = select(Assunto).join(Assunto.materia).where(
            Assunto.status == "ativa", Materia.status == "ativa"
        )
        if materia_id is not None:
            consulta = consulta.where(Assunto.materia_id == materia_id)
        return db.session.execute(
            consulta.order_by(Assunto.nome_normalizado, Assunto.id)
        ).scalars().all()

    @staticmethod
    def contagens_dashboard(contexto):
        return {"materias_ativas": contexto.executar(select(func.count()).select_from(Materia)
            .where(Materia.status == "ativa")).scalar_one(),
            "assuntos_ativos": contexto.executar(select(func.count()).select_from(Assunto)
            .where(Assunto.status == "ativa")).scalar_one()}

    @staticmethod
    def listar_materias_admin(filtros, pagina, por_pagina):
        condicoes = []
        if filtros.get("busca"):
            termo = f"%{filtros['busca']}%"
            condicoes.append(or_(Materia.nome.like(termo), Materia.descricao.like(termo)))
        if filtros.get("status"):
            condicoes.append(Materia.status == filtros["status"])
        if filtros.get("area_enem_id"):
            condicoes.append(Materia.area_enem_id == filtros["area_enem_id"])

        total = db.session.execute(
            select(func.count(Materia.id)).where(*condicoes)
        ).scalar_one()
        consulta = (
            select(
                Materia,
                AreaEnem,
                func.count(distinct(Assunto.id)).label("assuntos"),
                func.count(distinct(Questao.id)).label("questoes"),
            )
            .join(AreaEnem, Materia.area_enem_id == AreaEnem.id)
            .outerjoin(Assunto, Assunto.materia_id == Materia.id)
            .outerjoin(Questao, Questao.assunto_id == Assunto.id)
            .where(*condicoes)
            .group_by(Materia.id, AreaEnem.id)
            .order_by(Materia.nome, Materia.id)
            .offset((pagina - 1) * por_pagina)
            .limit(por_pagina)
        )
        return db.session.execute(consulta).all(), total

    @staticmethod
    def listar_assuntos_admin(filtros, pagina, por_pagina):
        condicoes = []
        if filtros.get("busca"):
            termo = f"%{filtros['busca']}%"
            condicoes.append(or_(Assunto.nome.like(termo), Assunto.descricao.like(termo)))
        if filtros.get("status"):
            condicoes.append(Assunto.status == filtros["status"])
        if filtros.get("area_enem_id"):
            condicoes.append(Materia.area_enem_id == filtros["area_enem_id"])
        if filtros.get("materia_id"):
            condicoes.append(Assunto.materia_id == filtros["materia_id"])

        base = select(Assunto.id).join(Materia).where(*condicoes).subquery()
        total = db.session.execute(select(func.count()).select_from(base)).scalar_one()
        consulta = (
            select(Assunto, Materia, AreaEnem, func.count(Questao.id).label("questoes"))
            .join(Materia, Assunto.materia_id == Materia.id)
            .join(AreaEnem, Materia.area_enem_id == AreaEnem.id)
            .outerjoin(Questao, Questao.assunto_id == Assunto.id)
            .where(*condicoes)
            .group_by(Assunto.id, Materia.id, AreaEnem.id)
            .order_by(Assunto.nome_normalizado, Assunto.id)
            .offset((pagina - 1) * por_pagina)
            .limit(por_pagina)
        )
        return db.session.execute(consulta).all(), total

    @staticmethod
    def impacto_materia(materia_id):
        assuntos = db.session.execute(
            select(func.count(Assunto.id)).where(Assunto.materia_id == materia_id)
        ).scalar_one()
        questoes = db.session.execute(
            select(func.count(Questao.id))
            .join(Assunto, Questao.assunto_id == Assunto.id)
            .where(Assunto.materia_id == materia_id)
        ).scalar_one()
        transferencias = db.session.execute(
            select(func.count(AssuntoTransferencia.id)).where(
                or_(
                    AssuntoTransferencia.materia_origem_id == materia_id,
                    AssuntoTransferencia.materia_destino_id == materia_id,
                )
            )
        ).scalar_one()
        return {"assuntos": assuntos, "questoes": questoes, "transferencias": transferencias}

    @staticmethod
    def impacto_assunto(assunto_id):
        questoes = db.session.execute(
            select(func.count(Questao.id)).where(Questao.assunto_id == assunto_id)
        ).scalar_one()
        transferencias = db.session.execute(
            select(func.count(AssuntoTransferencia.id)).where(
                AssuntoTransferencia.assunto_id == assunto_id
            )
        ).scalar_one()
        return {"questoes": questoes, "transferencias": transferencias}

    @staticmethod
    def contar_assuntos_nao_arquivados(materia_id):
        return db.session.execute(
            select(func.count(Assunto.id)).where(
                Assunto.materia_id == materia_id, Assunto.status != "arquivada"
            )
        ).scalar_one()

    @staticmethod
    def buscar_assunto_para_atualizacao(assunto_id):
        return db.session.execute(
            select(Assunto).where(Assunto.id == assunto_id).with_for_update()
        ).scalar_one_or_none()

    @staticmethod
    def buscar_materias_para_atualizacao(ids):
        return db.session.execute(
            select(Materia).where(Materia.id.in_(sorted(ids))).order_by(Materia.id).with_for_update()
        ).scalars().all()

    @staticmethod
    def existe_assunto_equivalente(materia_id, nome_normalizado, ignorar_id=None):
        consulta = select(Assunto.id).where(
            Assunto.materia_id == materia_id,
            Assunto.nome_normalizado == nome_normalizado,
        )
        if ignorar_id is not None:
            consulta = consulta.where(Assunto.id != ignorar_id)
        return db.session.execute(consulta.limit(1)).scalar_one_or_none() is not None
