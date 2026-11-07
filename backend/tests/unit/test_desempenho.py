from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import Mock
from werkzeug.datastructures import MultiDict
from app.contexto_leitura import ContextoLeitura, utc
from app.exceptions import DadosInvalidosError
from app.modules.desempenho.services.desempenho_validacao import periodo
from app.modules.desempenho.services.consultar_desempenho_service import metrica, ConsultarDesempenhoService
from app.modules.praticas.repositories.pratica_repository import PraticaRepository
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository


class DesempenhoUnitTest(unittest.TestCase):
    def test_periodo_utc_limites_e_inputs_ambiguos(self):
        agora=datetime(2026,10,24,0,0,1)
        p,inicio,fim=periodo({},agora)
        self.assertEqual((fim-inicio).days,30);self.assertEqual(p['timezone'],'UTC')
        self.assertEqual(periodo({'inicio':'2025-10-24','fim':'2026-10-24'},agora)[0]['inicio'],'2025-10-24')
        for filtros in [[],None,{'inicio':None,'fim':'2026-10-24'},{'inicio':'2025-10-23','fim':'2026-10-24'},
            {'inicio':'2026-10-24','fim':'2026-10-25'},MultiDict([('inicio','2026-10-24'),('fim','2026-10-24'),('fim','2026-10-24')])]:
            with self.assertRaises(DadosInvalidosError):periodo(filtros,agora)
        self.assertEqual(utc(datetime(2026,10,23,21,tzinfo=timezone(timedelta(hours=-3)))),datetime(2026,10,24))
        with self.assertRaises(ValueError):utc('2026-10-24')

    def test_amostra_formula_e_denominador_ponderado(self):
        for total,estado in [(0,'sem_dados'),(1,'amostra_pequena'),(4,'amostra_pequena'),(5,'dados_disponiveis')]:
            d=metrica({'total_respostas':total,'acertos':0,'pratica':total,'simulado':0})
            self.assertEqual(d['estado_amostra'],estado);self.assertEqual(d['percentual_acerto'],0.0 if total else None)
        self.assertEqual(metrica({'total_respostas':3,'acertos':1,'pratica':2,'simulado':1})['percentual_acerto'],33.33)

    def test_contexto_e_usuario_obrigatorios_sem_fallback(self):
        with self.assertRaises(ValueError):ConsultarDesempenhoService(Mock(), Mock()).executar(None)
        with self.assertRaises(ValueError):
            with ContextoLeitura.usar(object()):pass
        for repo in [PraticaRepository,SimuladoRepository]:
            for args in [(None,datetime.now(),datetime.now()),(1,None,datetime.now()),(1,datetime.now(),None)]:
                with self.assertRaises(ValueError):repo.projecao_desempenho(*args)
                with self.assertRaises(ValueError):repo.projecao_atividades(*args)
