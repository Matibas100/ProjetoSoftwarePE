"""Registro explícito e reexportação das mesmas 21 classes canônicas."""
from app.modules.conteudo.models.area_enem import AreaEnem
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.assunto_transferencia import AssuntoTransferencia
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.models.questao import Questao
from app.modules.conteudo.models.questao_versao import QuestaoVersao
from app.modules.conteudo.models.questao_evento import QuestaoEvento
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from app.modules.contas.models.sessao import Sessao
from app.modules.contas.models.auth_limite import AuthLimite
from app.modules.praticas.models.pratica_tentativa import PraticaTentativa
from app.modules.plano_estudos.models.plano_estudo import PlanoEstudo, PlanoEstudoItem
from app.modules.simulados.models.simulado import (
    Simulado,
    SimuladoRascunhoItem,
    SimuladoVersao,
    SimuladoVersaoItem,
    SimuladoEvento,
    SimuladoTentativa,
    SimuladoResposta
)


__all__ = [
    'AreaEnem',
    'Assunto',
    'AssuntoTransferencia',
    'Materia',
    'Questao',
    'QuestaoVersao',
    'QuestaoEvento',
    'Usuario',
    'RegistroPrivacidade',
    'Sessao',
    'AuthLimite',
    'PraticaTentativa',
    'PlanoEstudo',
    'PlanoEstudoItem',
    'Simulado',
    'SimuladoRascunhoItem',
    'SimuladoVersao',
    'SimuladoVersaoItem',
    'SimuladoEvento',
    'SimuladoTentativa',
    'SimuladoResposta'
]
