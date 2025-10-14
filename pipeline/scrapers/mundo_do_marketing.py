# SCRAPER MUNDO DO MARKETING
"""
Scraper específico para o site Mundo do Marketing
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_mundo_do_marketing(lista_noticias):
    """Coleta notícias do site Mundo do Marketing com extração de imagens"""
    url_base = 'https://mundodomarketing.com.br/noticias'
    print(f"  Conectando ao site Mundo do Marketing...")
    links_adicionados = set()
    count = 0

    try:
        response = requests.get(url_base, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            # Garantir encoding correto para caracteres especiais
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            artigos = soup.find_all('div', class_='framer-11hhesp-container')

            for artigo in artigos:
                try:
                    link_tag = artigo.find('a', class_='framer-1wh61m0')
                    container_texto = artigo.find(
                        'div', class_='framer-1r5yzu2')

                    if link_tag and container_texto:
                        titulo_tag = container_texto.find(
                            'h2', class_='framer-text')
                        categoria_tag = container_texto.find(
                            'p', class_='framer-text')

                        if titulo_tag and categoria_tag:
                            link_relativo = link_tag['href']
                            link_completo = urljoin(url_base, link_relativo)

                            if link_completo not in links_adicionados:
                                # Extrair imagem seguindo o padrão do GKPB
                                foto_url = _extrair_imagem_mundo_marketing(
                                    artigo, url_base)

                                # Buscar data de forma genérica
                                data_tag = (artigo.find('time') or
                                            artigo.find('span', {'class': lambda x: x and 'date' in x.lower()}) or
                                            artigo.find('div', {'class': lambda x: x and 'date' in x.lower()}))
                                data = data_tag.get_text(
                                    strip=True) if data_tag else "Sem data"

                                lista_noticias.append({
                                    'fonte': 'Mundo do Marketing',
                                    'categoria': categoria_tag.get_text(strip=True),
                                    'titulo': titulo_tag.get_text(strip=True),
                                    'descricao': "Sem descrição",
                                    'link': link_completo,
                                    'foto': foto_url,
                                    'data': data
                                })
                                links_adicionados.add(link_completo)
                                count += 1
                except Exception as e:
                    error_handler.handle_error(
                        e, f"Mundo do Marketing - processamento de artigo")

            print(
                f"  Sucesso: {count} notícias coletadas do Mundo do Marketing")
        else:
            print(f"  Erro: Status HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"  Erro de conexão Mundo do Marketing: {e}")


def _extrair_imagem_mundo_marketing(artigo, url_base):
    """
    Extrai imagem do artigo seguindo o padrão do GKPB com fallbacks
    Baseado na análise HTML: imagem está em div com data-framer-name="Image"
    """
    foto_url = ""

    try:
        # Método 1: Procurar pela div específica com data-framer-name="Image"
        image_div = artigo.find('div', {'data-framer-name': 'Image'})
        if image_div:
            img_tag = image_div.find('img')
            if img_tag:
                foto_url = img_tag.get('src', '')
                if foto_url:
                    # Converter URL relativa para absoluta se necessário
                    foto_url = urljoin(url_base, foto_url)

        # Método 2: Fallback - procurar por qualquer tag img no artigo
        if not foto_url:
            img_tag = artigo.find('img')
            if img_tag:
                foto_url = img_tag.get('src', '')
                if foto_url:
                    foto_url = urljoin(url_base, foto_url)

        # Método 3: Fallback - procurar por divs com data-bg (caso mude no futuro)
        if not foto_url:
            img_divs = artigo.find_all(attrs={'data-bg': True})
            if img_divs:
                foto_url = img_divs[0].get('data-bg', '')
                if foto_url:
                    foto_url = urljoin(url_base, foto_url)

        # Método 4: Fallback - procurar por divs com background-image no style
        if not foto_url:
            img_divs = artigo.find_all(
                'div', {'class': lambda x: x and 'thumb' in x.lower()})
            for div in img_divs:
                style = div.get('style', '')
                if 'background-image' in style:
                    match = re.search(r'url\("?([^"]+)"?\)', style)
                    if match:
                        foto_url = match.group(1)
                        foto_url = urljoin(url_base, foto_url)
                        break

        return foto_url

    except Exception as e:
        error_handler.handle_error(
            e, "Mundo do Marketing - extração de imagem")
        return ""
