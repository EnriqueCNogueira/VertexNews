# SCRAPER MEIO & MENSAGEM
"""
Scraper específico para o site Meio & Mensagem
"""

import requests
from bs4 import BeautifulSoup
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_meio_e_mensagem(lista_noticias):
    """Coleta notícias do site Meio & Mensagem"""
    url = 'https://www.meioemensagem.com.br/marketing'
    print(f"  Conectando ao site...")

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            artigos = soup.find_all('article', class_='post')

            for artigo in artigos:
                link_tag = artigo.find('a')
                titulo_tag = artigo.find('h3', class_='titulo')
                descricao_tag = artigo.find('p')
                categoria_tag = artigo.find('span', class_='categoria')

                if link_tag and titulo_tag:
                    lista_noticias.append({
                        'fonte': 'Meio & Mensagem',
                        'categoria': categoria_tag.get_text(strip=True) if categoria_tag else "Sem categoria",
                        'titulo': titulo_tag.get_text(strip=True),
                        'descricao': descricao_tag.get_text(strip=True) if descricao_tag else "Sem descrição",
                        'link': link_tag['href']
                    })

            print(f"  Sucesso: {len(artigos)} notícias coletadas")
        else:
            print(f"  Erro: Status HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"  Erro de conexão: {e}")
