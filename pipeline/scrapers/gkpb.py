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
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Usar seletores mais genéricos para encontrar artigos
            artigos = (soup.find_all('article') or
                       soup.find_all('div', {'class': lambda x: x and 'post' in x.lower()}) or
                       soup.find_all('div', {'class': lambda x: x and 'item' in x.lower()}) or
                       soup.find_all('div', {'class': lambda x: x and 'card' in x.lower()}) or
                       soup.find_all('div', class_='tdb_module_loop'))

            count = 0
            for artigo in artigos:
                try:
                    # Buscar título e link de forma genérica
                    titulo_tag = (artigo.find('h1') or
                                  artigo.find('h2') or
                                  artigo.find('h3') or
                                  artigo.find('h4'))

                    if not titulo_tag:
                        continue

                    link_tag = titulo_tag.find('a')
                    if not link_tag:
                        # Tentar encontrar link em outros lugares do artigo
                        link_tag = artigo.find('a')
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

                    # Buscar imagem de forma genérica
                    foto_url = ""
                    img_tag = (artigo.find('img') or
                               artigo.find('div', {'class': lambda x: x and 'image' in x.lower()}) or
                               artigo.find('div', {'class': lambda x: x and 'thumb' in x.lower()}))

                    if img_tag:
                        if img_tag.name == 'img':
                            foto_url = img_tag.get('src', '')
                        else:
                            # Para divs com imagem de fundo
                            foto_url = img_tag.get('data-bg', '')
                            if not foto_url:
                                style = img_tag.get('style', '')
                                if 'background-image' in style:
                                    import re
                                    match = re.search(
                                        r'url\("?([^"]+)"?\)', style)
                                    if match:
                                        foto_url = match.group(1)

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
