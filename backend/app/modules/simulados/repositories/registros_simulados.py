"""Registros das páginas de apresentação; escrita permanece nas Models."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

SIMULADO = ('id', 'titulo', 'estado', 'revisao', 'autor_id', 'criado_em',
            'atualizado_em', 'simulado_versao_id')
TENTATIVA = ('id', 'usuario_id', 'simulado_versao_id', 'estado', 'revisao',
    'chave_envio', 'iniciada_em', 'finalizada_em', 'total', 'respondidas',
    'acertos', 'erros', 'em_branco', 'percentual_acerto', 'em_andamento_marcador')


@dataclass(frozen=True)
class SimuladoRegistro:
    id: int
    titulo: str
    estado: str
    revisao: int
    autor_id: int
    criado_em: datetime
    atualizado_em: datetime
    simulado_versao_id: int | None


@dataclass(frozen=True)
class TentativaHistoricoRegistro:
    id: int
    usuario_id: int
    simulado_versao_id: int
    estado: str
    revisao: int
    chave_envio: str
    iniciada_em: datetime
    finalizada_em: datetime
    total: int
    respondidas: int
    acertos: int
    erros: int
    em_branco: int
    percentual_acerto: Decimal
    em_andamento_marcador: int | None

    def resultado(self):
        return {**{c: getattr(self, c) for c in ('total', 'respondidas', 'acertos', 'erros', 'em_branco')},
            'percentual_acerto': float(self.percentual_acerto),
            'finalizada_em': self.finalizada_em.isoformat()+'Z'}
