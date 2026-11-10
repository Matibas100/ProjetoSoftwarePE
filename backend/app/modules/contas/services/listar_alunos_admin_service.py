from app.contracts.usuarios import ConsultaAlunosAdmin
from app.core.paginacao import envelope_paginado, inteiro_filtro
from app.exceptions import DadosInvalidosError
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.domain.gestao_alunos import apresentar_linha


class ListarAlunosAdminService:
    def __init__(self, consulta: ConsultaAlunosAdmin):
        self._consulta = consulta

    def executar(self, parametros):
        if set(parametros)-{'busca', 'status', 'pagina', 'por_pagina'}:
            raise AutenticacaoError('Filtros inválidos.')
        numeros = []
        for campo, padrao, maximo in [('pagina', 1, 2147483647), ('por_pagina', 20, 100)]:
            valor = parametros.get(campo, padrao)
            if type(valor) not in (
                str,
                int
            ) or valor == '' or (isinstance(
                valor,
                str
            ) and not valor.isascii()):
                raise AutenticacaoError('Paginação inválida.')
            try:
                numero = inteiro_filtro(valor, campo, maximo=maximo)
            except DadosInvalidosError:
                raise AutenticacaoError('Paginação inválida.') from None
            numeros.append(numero)
        busca = parametros.get('busca', '')
        if not isinstance(busca, str) or len(busca.strip())>254:
            raise AutenticacaoError('Busca inválida.')
        status = parametros.get('status', '')
        if status not in ('', 'ativo', 'inativo'):
            raise AutenticacaoError('Status inválido.')
        pagina, limite = numeros
        linhas, total = self._consulta.listar(
            busca.strip(),
            None if status=='' else status=='ativo',
            pagina,
            limite
        )
        return envelope_paginado(
            [apresentar_linha(linha) for linha in linhas],
            pagina,
            limite,
            total
        )
