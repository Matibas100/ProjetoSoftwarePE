from app.extensions import db


class ModeloBase(db.Model):
    """Persistência e leitura; salvar respeita os invariantes da entidade."""

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

    @classmethod
    def listar_todos(cls):
        return db.session.execute(db.select(cls)).scalars().all()

    @classmethod
    def buscar_por_id(cls, registro_id):
        return db.session.get(cls, registro_id)


class ModeloAtualizavel(ModeloBase):
    """Acrescenta atualização dos campos permitidos pela Model."""

    __abstract__ = True

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


class CrudMixin(ModeloAtualizavel):
    """CRUD completo; mantém o caminho de importação legado."""

    __abstract__ = True

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
