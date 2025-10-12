# SCRAPER EXAME
"""
Scraper específico para o site Exame
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_exame(lista_noticias):
    """Coleta notícias do site Exame"""
    url_base = 'https://exame.com'
    url = f'{url_base}/marketing/'
    print(f"  Conectando ao site...")

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            artigos = soup.find_all('div', class_='sc-dbce6183-0')
            count = 0

            for artigo in artigos:
                h3_tag = artigo.find('h3', class_='headline-extra-small')
                categoria_tag = artigo.find('span', class_='label-small')

                if h3_tag and h3_tag.a:
                    link_relativo = h3_tag.a['href']
                    link_completo = urljoin(url_base, link_relativo)

                    lista_noticias.append({
                        'fonte': 'Exame',
                        'categoria': categoria_tag.get_text(strip=True) if categoria_tag else "Marketing",
                        'titulo': h3_tag.a.get_text(strip=True),
                        'descricao': "Sem descrição",
                        'link': link_completo
                    })
                    count += 1

            print(f"  Sucesso: {count} notícias coletadas")
            return count
        return 0
    except requests.RequestException:
        print("  Erro de conexão")
        return 0
