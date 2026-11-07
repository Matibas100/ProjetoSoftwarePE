"""Compatibilidade estática: mesma identidade das bases e de db."""
from app.core.persistencia import ModeloBase, ModeloAtualizavel, CrudMixin, db

__all__ = ["ModeloBase", "ModeloAtualizavel", "CrudMixin", "db"]
