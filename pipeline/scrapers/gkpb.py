# SCRAPER GKPB
"""
Scraper específico para o site GKPB (gkpb.com.br)
Refatorado para usar seletores genéricos e extração de texto no módulo extractor
"""

import requests
from bs4 import BeautifulSoup
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_gkpb(lista_noticias):
    """Coleta notícias do site GKPB usando seletores genéricos"""
    url = 'https://gkpb.com.br/category/publicidade/'
    print(f"  Conectando ao site GKPB...")

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            # Garantir encoding correto para caracteres especiais
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            # Usar seletores específicos para o GKPB baseados na análise HTML
            artigos = soup.find_all(
                'div', {'class': lambda x: x and 'tdb_module_header' in x and 'td_module_wrap' in x})

            count = 0
            for artigo in artigos:
                try:
                    # Buscar título e link específicos para GKPB
                    titulo_tag = artigo.find(
                        'h3', {'class': lambda x: x and 'entry-title' in x})
                    if not titulo_tag:
                        continue

                    link_tag = titulo_tag.find('a')
                    if not link_tag:
                        continue

                    titulo = link_tag.get_text(strip=True)
                    link = link_tag.get('href')

                    if not titulo or not link:
                        continue

                    # Buscar categoria de forma genérica
                    categoria_tag = (artigo.find('span', {'class': lambda x: x and 'category' in x.lower()}) or
                                     artigo.find('a', {'class': lambda x: x and 'category' in x.lower()}) or
                                     artigo.find('span', {'class': lambda x: x and 'tag' in x.lower()}))
                    categoria = categoria_tag.get_text(
                        strip=True) if categoria_tag else "Marketing"

                    # Buscar imagem específica para GKPB (usando data-bg)
                    foto_url = ""

                    # Procurar por qualquer div com data-bg (método que funciona)
                    img_divs = artigo.find_all(attrs={'data-bg': True})
                    if img_divs:
                        foto_url = img_divs[0].get('data-bg', '')

                    # Fallback: procurar por outras divs com background-image
                    if not foto_url:
                        img_divs = artigo.find_all(
                            'div', {'class': lambda x: x and 'thumb' in x.lower()})
                        for div in img_divs:
                            style = div.get('style', '')
                            if 'background-image' in style:
                                import re
                                match = re.search(r'url\("?([^"]+)"?\)', style)
                                if match:
                                    foto_url = match.group(1)
                                    break

                    # Fallback: procurar por tags img tradicionais
                    if not foto_url:
                        img_tag = artigo.find('img')
                        if img_tag:
                            foto_url = img_tag.get('src', '')

                    # Buscar data de forma genérica
                    data_tag = (artigo.find('time') or
                                artigo.find('span', {'class': lambda x: x and 'date' in x.lower()}) or
                                artigo.find('div', {'class': lambda x: x and 'date' in x.lower()}))
                    data = data_tag.get_text(
                        strip=True) if data_tag else "Sem data"

                    lista_noticias.append({
                        'fonte': 'GKPB',
                        'categoria': categoria,
                        'titulo': titulo,
                        'descricao': "Sem descrição",  # Será extraído depois no extractor
                        'link': link,
                        'foto': foto_url,
                        'data': data
                    })
                    count += 1

                except Exception as e:
                    error_handler.handle_error(
                        e, f"Erro ao processar artigo GKPB")
                    continue

            print(f"  Sucesso: {count} notícias coletadas do GKPB")
        else:
            print(f"  Erro: Status HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"  Erro de conexão GKPB: {e}")
