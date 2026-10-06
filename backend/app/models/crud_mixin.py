from app.extensions import db


class CrudMixin(db.Model):
    """Operacoes simples compartilhadas pelas Models do dominio."""

    __abstract__ = True

    def salvar(self, confirmar=True):
        try:
            db.session.add(self)
            if confirmar:
                db.session.commit()
            else:
                db.session.flush()
        except Exception:
            if confirmar:
                db.session.rollback()
            raise
        return self

    def atualizar(self, confirmar=True, **dados):
        for campo, valor in dados.items():
            if campo in self.campos_atualizaveis:
                setattr(self, campo, valor)
        try:
            if confirmar:
                db.session.commit()
            else:
                db.session.flush()
        except Exception:
            if confirmar:
                db.session.rollback()
            raise
        return self

    def deletar(self, confirmar=True):
        try:
            db.session.delete(self)
            if confirmar:
                db.session.commit()
            else:
                db.session.flush()
        except Exception:
            if confirmar:
                db.session.rollback()
            raise

    @classmethod
    def listar_todos(cls):
        return db.session.execute(db.select(cls)).scalars().all()

    @classmethod
    def buscar_por_id(cls, registro_id):
        return db.session.get(cls, registro_id)
