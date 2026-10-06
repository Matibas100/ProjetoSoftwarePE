"""Consultas especificas, JOINs, relatorios e Stored Procedures.

CRUD simples permanece nas Models. Repositories serao adicionados apenas quando
um caso de uso exigir uma operacao de banco especializada.
"""
from app.repositories.catalogo_repository import CatalogoRepository

__all__ = ["CatalogoRepository"]
