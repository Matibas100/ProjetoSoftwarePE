from datetime import date, datetime, time, timedelta
from collections.abc import Mapping
import re
from app.exceptions import DadosInvalidosError


def periodo(filtros, instante):
    if (not isinstance(filtros, Mapping) or set(filtros) - {"inicio", "fim"} or len(filtros) not in {0, 2}
        or (hasattr(filtros, "getlist") and any(len(filtros.getlist(k)) != 1 for k in filtros))):
        raise DadosInvalidosError("Informe início e fim juntos, sem filtros extras ou repetidos.")
    hoje = instante.date()
    if not filtros:
        inicio, fim = hoje - timedelta(days=29), hoje
    else:
        valores = []
        for campo in ("inicio", "fim"):
            valor = filtros.get(campo)
            try:
                if not isinstance(valor, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", valor):
                    raise ValueError()
                valores.append(date.fromisoformat(valor))
            except ValueError as erro:
                raise DadosInvalidosError("Datas devem usar YYYY-MM-DD.") from erro
        inicio, fim = valores
    if inicio > fim or (fim - inicio).days >= 366 or fim > hoje:
        raise DadosInvalidosError("Período deve ter de 1 a 366 dias e não pode terminar no futuro UTC.")
    return {"inicio": inicio.isoformat(), "fim": fim.isoformat(), "timezone": "UTC"}, datetime.combine(inicio, time()), datetime.combine(fim + timedelta(days=1), time())
