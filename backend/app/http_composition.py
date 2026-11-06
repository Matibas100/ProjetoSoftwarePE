"""Acesso à composição restrito à adaptação HTTP."""
from flask import current_app
from app.composition import Composicao


def servicos() -> Composicao:
    return current_app.extensions['servicos']
