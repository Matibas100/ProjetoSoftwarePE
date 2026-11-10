"""Locks de geração/propriedade e consulta ordenada, sem CRUD duplicado."""
from sqlalchemy import select, text
from app.core.procedures_mysql import executar_resultados, conferir_resultados
from app.contexto_leitura import ContextoLeitura
from app.extensions import db
from app.modules.contas.api import bloquear_usuario
from app.modules.plano_estudos.models.plano_estudo import (
    PlanoEstudo as Plano,
    PlanoEstudoItem as Item,
)


class PlanoEstudoRepository:
    bloquear_usuario = staticmethod(bloquear_usuario)

    @staticmethod
    def contexto(instante):
        return ContextoLeitura(db.session.connection(), instante)

    @staticmethod
    def atual(usuario_id, bloquear=False):
        db.session.flush()
        consulta = select(Plano).from_statement(text('CALL sp_plano_atual(:usuario_id,:bloquear)')
            .columns(*Plano.__table__.columns))
        if bloquear:
            consulta = consulta.execution_options(populate_existing=True)
        resultado = db.session.execute(
            consulta,
            {
                'usuario_id': usuario_id,
                'bloquear': int(bloquear)
            }
        )
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def por_chave(usuario_id, chave):
        db.session.flush()
        resultado = db.session.execute(
            select(Plano).from_statement(
                text('CALL sp_plano_por_chave(:usuario_id,:chave)').columns(*Plano.__table__.columns))
            .execution_options(populate_existing=True),
            {'usuario_id': usuario_id, 'chave': chave}
        )
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def itens(plano_id):
        db.session.flush()
        resultado = db.session.execute(
            select(Item).from_statement(
                text('CALL sp_plano_itens(:plano_id)').columns(*Item.__table__.columns))
            .execution_options(populate_existing=True),
            {'plano_id': plano_id}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def item_proprio(usuario_id, item_id):
        db.session.flush()
        resultado = db.session.execute(
            select(Item, Plano).from_statement(
                text('CALL sp_plano_item_proprio(:usuario_id,:item_id)')
                .columns(*Item.__table__.columns, *Plano.__table__.columns))
            .execution_options(populate_existing=True),
            {
                'usuario_id': usuario_id,
                'item_id': item_id
            }
        )
        try:
            return resultado.one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def eliminar_planos_proprios(usuario_id):
        # O chamador mantém o lock do usuário até o único commit da negativa.
        db.session.flush()
        afetadas = []
        for entidade in list(db.session.identity_map.values()):
            if isinstance(entidade, Plano):
                plano = entidade
            elif isinstance(entidade, Item):
                # Busca básica por PK somente para identificar o dono de item já carregado.
                plano = Plano.buscar_por_id(entidade.plano_id)
            else:
                continue
            if plano is not None and plano.usuario_id == usuario_id:
                afetadas.append(entidade)
        resultados = executar_resultados(
            db.session.connection(),
            'CALL sp_eliminar_planos_proprios(%s)',
            (usuario_id,)
        )
        contagens, = conferir_resultados(resultados, [('planos_eliminados', 'itens_eliminados')])
        linha, = contagens
        # Expiração seletiva conserva a negativa pendente e permite rollback externo.
        for entidade in afetadas:
            db.session.expire(entidade)
