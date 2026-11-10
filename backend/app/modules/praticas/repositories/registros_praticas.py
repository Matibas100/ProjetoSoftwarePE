"""Histórico de apresentação tipado, sem entidades ORM artificiais."""
from dataclasses import dataclass
from datetime import datetime

PRATICA = (
    'id',
    'usuario_id',
    'questao_versao_id',
    'chave_envio',
    'estado',
    'resposta_escolhida',
    'correta',
    'iniciada_em',
    'respondida_em',
    'assunto_id',
    'assunto_nome',
    'materia_id',
    'materia_nome'
)


@dataclass(frozen=True)
class PraticaHistoricoRegistro:
    id: int
    usuario_id: int
    questao_versao_id: int
    chave_envio: str
    estado: str
    resposta_escolhida: str
    correta: bool
    iniciada_em: datetime
    respondida_em: datetime
    assunto_id: int
    assunto_nome: str
    materia_id: int
    materia_nome: str

    def resumo(self):
        return {
            'id': self.id,
            'questao_versao_id': self.questao_versao_id,
            'resposta_escolhida': self.resposta_escolhida,
            'correta': self.correta,
            'respondida_em': self.respondida_em.isoformat()+'Z',
            'assunto': {'id': self.assunto_id, 'nome': self.assunto_nome},
            'materia': {'id': self.materia_id, 'nome': self.materia_nome}
        }
