# SCRAPER GKPB
"""
Scraper específico para o site GKPB (gkpb.com.br)
"""

import requests
from bs4 import BeautifulSoup
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_gkpb(lista_noticias):
    """Coleta notícias do site GKPB"""
    url = 'https://gkpb.com.br/category/publicidade/'
    print(f"  Conectando ao site GKPB...")

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar todos os artigos na página
            artigos = soup.find_all('div', class_='tdb_module_loop')

            for artigo in artigos:
                try:
                    # Extrair título e link
                    titulo_tag = artigo.find(
                        'h3', class_='entry-title td-module-title')
                    if not titulo_tag:
                        continue

                    link_tag = titulo_tag.find('a')
                    if not link_tag:
                        continue

                    titulo = link_tag.get_text(strip=True)
                    link = link_tag.get('href')

                    # Extrair categoria
                    categoria_tag = artigo.find('a', class_='td-post-category')
                    categoria = categoria_tag.get_text(
                        strip=True) if categoria_tag else "Sem categoria"

                    # Extrair foto
                    foto_tag = artigo.find(
                        'span', class_='entry-thumb td-thumb-css')
                    foto_url = ""
                    if foto_tag:
                        foto_url = foto_tag.get('data-bg', '')
                        if not foto_url:
                            # Tentar buscar em style background-image
                            style = foto_tag.get('style', '')
                            if 'background-image' in style:
                                import re
                                match = re.search(r'url\("?([^"]+)"?\)', style)
                                if match:
                                    foto_url = match.group(1)

                    # Extrair data
                    data_tag = artigo.find(
                        'time', class_='entry-date updated td-module-date')
                    data = data_tag.get_text(
                        strip=True) if data_tag else "Sem data"

                    # Extrair texto completo da notícia
                    texto_completo = extrair_texto_noticia(link)

                    lista_noticias.append({
                        'fonte': 'GKPB',
                        'categoria': categoria,
                        'titulo': titulo,
                        'descricao': texto_completo[:200] + "..." if len(texto_completo) > 200 else texto_completo,
                        'link': link,
                        'foto': foto_url,
                        'data': data,
                        'texto_completo': texto_completo
                    })

                except Exception as e:
                    error_handler.handle_error(
                        e, f"Erro ao processar artigo GKPB: {titulo}")
                    continue

            print(f"  Sucesso: {len(artigos)} notícias coletadas do GKPB")
        else:
            print(f"  Erro: Status HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"  Erro de conexão GKPB: {e}")


def extrair_texto_noticia(url_noticia):
    """Extrai o texto completo de uma notícia específica"""
    try:
        response = requests.get(url_noticia, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar o container principal do texto
            container_texto = soup.find('div', class_='tdb_single_content')
            if not container_texto:
                return "Texto não encontrado"

            # Extrair todos os parágrafos
            paragrafos = container_texto.find_all('p')
            texto_completo = ""

            for p in paragrafos:
                texto_paragrafo = p.get_text(strip=True)
                # Filtrar parágrafos muito curtos
                if texto_paragrafo and len(texto_paragrafo) > 10:
                    texto_completo += texto_paragrafo + " "

            return texto_completo.strip()
        else:
            return f"Erro ao acessar notícia: HTTP {response.status_code}"
    except Exception as e:
        error_handler.handle_error(
            e, f"Erro ao extrair texto da notícia: {url_noticia}")
        return "Erro ao extrair texto"
