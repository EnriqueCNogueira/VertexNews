# TESTE ROBUSTO DOS SCRAPERS
"""
Teste robusto para detectar mudanças nos sites e verificar se os scrapers estão funcionando corretamente.
Este teste deve ser executado manualmente para verificar se os scrapers estão funcionando antes de executar o pipeline.
"""

from pipeline.scrapers.mundo_do_marketing import scrape_mundo_do_marketing
from pipeline.scrapers.meio_e_mensagem import scrape_meio_e_mensagem
from pipeline.scrapers.gkpb import scrape_gkpb
from pipeline.scrapers.exame import scrape_exame
from config.config import HEADERS
import requests
import time
import sys
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime
from bs4 import BeautifulSoup

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ScraperRobustTest:
    """Classe para testes robustos dos scrapers"""

    def __init__(self):
        """Inicializa o teste dos scrapers"""
        self.scrapers = {
            'Exame': {
                'url': 'https://exame.com/marketing/',
                'function': scrape_exame,
                'expected_selectors': ['div.sc-dbce6183-0', 'h3.headline-extra-small'],
                'min_articles': 5
            },
            'GKPB': {
                'url': 'https://gkpb.com.br/category/publicidade/',
                'function': scrape_gkpb,
                'expected_selectors': ['div.tdb_module_header', 'h3.entry-title'],
                'min_articles': 5
            },
            'Meio e Mensagem': {
                'url': 'https://www.meioemensagem.com.br/marketing',
                'function': scrape_meio_e_mensagem,
                'expected_selectors': ['article', 'h2.titulo', 'h3.titulo'],
                'min_articles': 5
            },
            'Mundo do Marketing': {
                'url': 'https://mundodomarketing.com.br/noticias',
                'function': scrape_mundo_do_marketing,
                'expected_selectors': ['div.framer-11hhesp-container', 'h2.framer-text'],
                'min_articles': 5
            }
        }

        self.results = {}
        self.errors = []
        self.warnings = []

    def run_all_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Executa todos os testes dos scrapers

        Returns:
            Tupla (sucesso_geral, resultados_detalhados)
        """
        print("[INFO] Iniciando testes robustos dos scrapers...")
        print(f"   Testando {len(self.scrapers)} sites...")

        # Limpar resultados anteriores
        self.results = {}
        self.errors = []
        self.warnings = []

        # Executar testes para cada scraper
        for site_name, config in self.scrapers.items():
            print(f"\n[NEWS] Testando {site_name}...")
            self._test_single_scraper(site_name, config)

        # Determinar sucesso geral
        success = len(self.errors) == 0

        # Exibir resultados
        self._display_results()

        return success, self.results

    def _test_single_scraper(self, site_name: str, config: Dict[str, Any]):
        """Testa um único scraper"""
        site_results = {
            'site': site_name,
            'url': config['url'],
            'success': False,
            'articles_found': 0,
            'response_time': 0,
            'status_code': 0,
            'errors': [],
            'warnings': [],
            'html_analysis': {},
            'selector_analysis': {}
        }

        try:
            # Teste 1: Conectividade básica
            print(f"  [NET] Testando conectividade...")
            connectivity_success, response_time, status_code = self._test_connectivity(
                config['url'])
            site_results['response_time'] = response_time
            site_results['status_code'] = status_code

            if not connectivity_success:
                site_results['errors'].append(
                    f"Falha na conectividade: Status {status_code}")
                self.results[site_name] = site_results
                return

            # Teste 2: Análise HTML
            print(f"  [HTML] Analisando estrutura HTML...")
            html_analysis = self._analyze_html_structure(config['url'])
            site_results['html_analysis'] = html_analysis

            # Teste 3: Análise de seletores
            print(f"  [SELECTOR] Verificando seletores...")
            selector_analysis = self._analyze_selectors(
                config['url'], config['expected_selectors'])
            site_results['selector_analysis'] = selector_analysis

            # Teste 4: Execução do scraper
            print(f"  [SCRAPER] Executando scraper...")
            scraper_success, articles_count = self._test_scraper_execution(
                config['function'])
            site_results['articles_found'] = articles_count

            if not scraper_success:
                site_results['errors'].append("Falha na execução do scraper")

            # Teste 5: Validação de resultados
            print(f"  [VALIDATE] Validando resultados...")
            validation_results = self._validate_scraper_results(
                articles_count, config['min_articles'])
            site_results['warnings'].extend(validation_results['warnings'])

            # Determinar sucesso geral do site
            site_results['success'] = (
                connectivity_success and
                scraper_success and
                articles_count >= config['min_articles'] and
                len(site_results['errors']) == 0
            )

        except Exception as e:
            site_results['errors'].append(f"Erro inesperado: {str(e)}")
            site_results['success'] = False

        # Adicionar resultados ao resultado geral
        self.results[site_name] = site_results

        # Adicionar erros e avisos globais
        self.errors.extend(
            [f"{site_name}: {error}" for error in site_results['errors']])
        self.warnings.extend(
            [f"{site_name}: {warning}" for warning in site_results['warnings']])

    def _test_connectivity(self, url: str) -> Tuple[bool, float, int]:
        """Testa a conectividade com um site"""
        try:
            start_time = time.time()
            response = requests.get(url, headers=HEADERS, timeout=10)
            response_time = time.time() - start_time

            success = response.status_code == 200

            if not success:
                self.warnings.append(
                    f"Status HTTP {response.status_code} para {url}")

            return success, response_time, response.status_code

        except requests.RequestException as e:
            self.errors.append(f"Erro de conexão com {url}: {str(e)}")
            return False, 0, 0

    def _analyze_html_structure(self, url: str) -> Dict[str, Any]:
        """Analisa a estrutura HTML do site"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                return {'error': f'Status HTTP {response.status_code}'}

            soup = BeautifulSoup(response.content, 'html.parser')

            # Análise básica da estrutura
            analysis = {
                'title': soup.title.string if soup.title else 'Sem título',
                'total_elements': len(soup.find_all()),
                'article_elements': len(soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in x.lower())),
                'heading_elements': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'link_elements': len(soup.find_all('a')),
                'image_elements': len(soup.find_all('img')),
                'common_classes': self._get_common_classes(soup),
                'meta_info': self._get_meta_info(soup)
            }

            return analysis

        except Exception as e:
            return {'error': f'Erro na análise HTML: {str(e)}'}

    def _analyze_selectors(self, url: str, expected_selectors: List[str]) -> Dict[str, Any]:
        """Analisa se os seletores esperados estão presentes"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                return {'error': f'Status HTTP {response.status_code}'}

            soup = BeautifulSoup(response.content, 'html.parser')

            analysis = {
                'expected_selectors': {},
                'found_selectors': {},
                'recommendations': []
            }

            for selector in expected_selectors:
                elements = soup.select(selector)
                analysis['expected_selectors'][selector] = len(elements)

                if len(elements) == 0:
                    analysis['recommendations'].append(
                        f"Seletor '{selector}' não encontrado")
                elif len(elements) < 5:
                    analysis['recommendations'].append(
                        f"Seletor '{selector}' encontrou poucos elementos: {len(elements)}")

            # Buscar seletores alternativos
            analysis['alternative_selectors'] = self._find_alternative_selectors(
                soup)

            return analysis

        except Exception as e:
            return {'error': f'Erro na análise de seletores: {str(e)}'}

    def _test_scraper_execution(self, scraper_function) -> Tuple[bool, int]:
        """Testa a execução do scraper"""
        try:
            # Lista para coletar notícias
            lista_noticias = []

            # Executar scraper
            articles_count = scraper_function(lista_noticias)

            # Validar resultados
            if articles_count is None or articles_count < 0:
                return False, 0

            # Verificar se as notícias foram coletadas corretamente
            valid_articles = 0
            for noticia in lista_noticias:
                if (noticia.get('titulo') and
                    noticia.get('link') and
                        noticia.get('fonte')):
                    valid_articles += 1

            success = valid_articles > 0

            return success, valid_articles

        except Exception as e:
            self.errors.append(f"Erro na execução do scraper: {str(e)}")
            return False, 0

    def _validate_scraper_results(self, articles_count: int, min_expected: int) -> Dict[str, List[str]]:
        """Valida os resultados do scraper"""
        warnings = []

        if articles_count == 0:
            warnings.append("Nenhuma notícia coletada")
        elif articles_count < min_expected:
            warnings.append(
                f"Poucas notícias coletadas: {articles_count} (esperado: {min_expected}+)")
        elif articles_count > 50:
            warnings.append(
                f"Muitas notícias coletadas: {articles_count} (pode indicar problema)")

        return {'warnings': warnings}

    def _get_common_classes(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Encontra classes CSS comuns"""
        class_counts = {}

        for element in soup.find_all(class_=True):
            for class_name in element.get('class', []):
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Retornar as 10 classes mais comuns
        return dict(sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:10])

    def _get_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai informações meta do site"""
        meta_info = {}

        # Meta tags importantes
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')

            if name and content:
                meta_info[name] = content

        return meta_info

    def _find_alternative_selectors(self, soup: BeautifulSoup) -> List[str]:
        """Encontra seletores alternativos para artigos"""
        alternatives = []

        # Buscar por elementos que podem conter artigos
        potential_selectors = [
            'div[class*="article"]',
            'div[class*="post"]',
            'div[class*="news"]',
            'div[class*="item"]',
            'article',
            'div[class*="card"]',
            'div[class*="content"]'
        ]

        for selector in potential_selectors:
            elements = soup.select(selector)
            if len(elements) >= 3:  # Pelo menos 3 elementos
                alternatives.append(f"{selector} ({len(elements)} elementos)")

        return alternatives[:5]  # Retornar apenas os 5 melhores

    def _display_results(self):
        """Exibe os resultados dos testes"""
        print(f"\n[RESULTADO] Resultados dos testes dos scrapers:")

        # Resumo geral
        total_sites = len(self.scrapers)
        successful_sites = sum(
            1 for result in self.results.values() if result['success'])

        print(f"   [NET] Sites testados: {total_sites}")
        print(f"   [OK] Sites funcionando: {successful_sites}")
        print(
            f"   [ERRO] Sites com problemas: {total_sites - successful_sites}")
        print(f"   [AVISO] Avisos: {len(self.warnings)}")

        # Detalhes por site
        print(f"\n[NEWS] Detalhes por site:")
        for site_name, result in self.results.items():
            status = "[OK]" if result['success'] else "[ERRO]"
            print(f"   {status} {site_name}:")
            print(
                f"      [ARTICLES] Artigos encontrados: {result['articles_found']}")
            print(
                f"      [TIME] Tempo de resposta: {result['response_time']:.2f}s")
            print(f"      [HTTP] Status HTTP: {result['status_code']}")

            if result['errors']:
                print(f"      [ERRO] Erros:")
                for error in result['errors']:
                    print(f"         • {error}")

            if result['warnings']:
                print(f"      [AVISO] Avisos:")
                for warning in result['warnings']:
                    print(f"         • {warning}")

        # Recomendações gerais
        if self.warnings or self.errors:
            print(f"\n[TIPS] Recomendações:")

            if self.errors:
                print(f"   [ERRO] Problemas críticos encontrados:")
                for error in self.errors:
                    print(f"      • {error}")

            if self.warnings:
                print(f"   [AVISO] Pontos de atenção:")
                for warning in self.warnings:
                    print(f"      • {warning}")

        if successful_sites == total_sites:
            print(f"\n[SUCESSO] Todos os scrapers estão funcionando corretamente!")
        else:
            print(
                f"\n[AVISO] Alguns scrapers precisam de atenção antes de executar o pipeline.")


def run_scraper_robust_test() -> bool:
    """
    Função principal para executar o teste robusto dos scrapers

    Returns:
        True se todos os scrapers estão funcionando, False caso contrário
    """
    test = ScraperRobustTest()
    success, results = test.run_all_tests()

    if success:
        print(f"\n[SUCESSO] Teste dos scrapers concluído com sucesso!")
        print(f"   Todos os scrapers estão funcionando corretamente.")
    else:
        print(f"\n[ERRO] Teste dos scrapers encontrou problemas!")
        print(f"   Verifique os erros antes de executar o pipeline.")

    return success


if __name__ == "__main__":
    # Executar teste quando chamado diretamente
    success = run_scraper_robust_test()
    sys.exit(0 if success else 1)
