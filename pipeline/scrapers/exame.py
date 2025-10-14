# SCRAPER EXAME
"""
Scraper específico para o site Exame
Refatorado para usar seletores específicos e extração de imagens
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.config import HEADERS
from errors.error_handler import error_handler
from ..scraper_utils import extract_image_url


def scrape_exame(lista_noticias):
    """Coleta notícias do site Exame usando seletores específicos"""
    url_base = 'https://exame.com'
    url = f'{url_base}/marketing/'
    print(f"  Conectando ao site Exame...")

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            # Garantir encoding correto para caracteres especiais
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            # Usar seletores específicos para o Exame baseados na análise HTML
            artigos = soup.find_all('div', class_='sc-dbce6183-0')

            count = 0
            for artigo in artigos:
                try:
                    # Buscar título e link específicos para Exame
                    h3_tag = artigo.find('h3', class_='headline-extra-small')
                    if not h3_tag or not h3_tag.a:
                        continue

                    titulo = h3_tag.a.get_text(strip=True)
                    link_relativo = h3_tag.a['href']
                    link_completo = urljoin(url_base, link_relativo)

                    if not titulo or not link_completo:
                        continue

                    # Buscar categoria específica para Exame
                    categoria_tag = artigo.find('span', class_='label-small')
                    categoria = categoria_tag.get_text(
                        strip=True) if categoria_tag else "Marketing"

                    # Extrair imagem usando função utilitária
                    foto_url = extract_image_url(artigo, url_base)

                    # Buscar data de forma genérica
                    data_tag = (artigo.find('time') or
                                artigo.find('span', {'class': lambda x: x and 'date' in x.lower()}) or
                                artigo.find('div', {'class': lambda x: x and 'date' in x.lower()}))
                    data = data_tag.get_text(
                        strip=True) if data_tag else "Sem data"

                    lista_noticias.append({
                        'fonte': 'Exame',
                        'categoria': categoria,
                        'titulo': titulo,
                        'descricao': "Sem descrição",  # Será extraído depois no extractor
                        'link': link_completo,
                        'foto': foto_url,
                        'data': data
                    })
                    count += 1

                except Exception as e:
                    error_handler.handle_error(
                        e, f"Erro ao processar artigo Exame")
                    continue

            print(f"  Sucesso: {count} notícias coletadas do Exame")
            return count
        else:
            print(f"  Erro: Status HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"  Erro de conexão Exame: {e}")
        return 0
