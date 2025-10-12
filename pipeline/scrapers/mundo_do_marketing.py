# SCRAPER MUNDO DO MARKETING
"""
Scraper específico para o site Mundo do Marketing
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_mundo_do_marketing(lista_noticias):
    """Coleta notícias do site Mundo do Marketing"""
    url_base = 'https://mundodomarketing.com.br/noticias'
    print(f"  Conectando ao site...")
    links_adicionados = set()
    count = 0

    try:
        response = requests.get(url_base, headers=HEADERS, timeout=15)
        if response.status_code == 200:
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
                                lista_noticias.append({
                                    'fonte': 'Mundo do Marketing',
                                    'categoria': categoria_tag.get_text(strip=True),
                                    'titulo': titulo_tag.get_text(strip=True),
                                    'descricao': "Sem descrição",
                                    'link': link_completo
                                })
                                links_adicionados.add(link_completo)
                                count += 1
                except Exception as e:
                    error_handler.handle_error(
                        e, f"Mundo do Marketing - processamento de artigo")

            print(f"  Sucesso: {count} notícias coletadas")
        else:
            error_handler.handle_warning(
                f"Status HTTP {response.status_code}", "Mundo do Marketing")
    except requests.RequestException as e:
        error_handler.handle_error(e, "Mundo do Marketing - conexão")
