# ETAPA 2: COLETORES DE DADOS
"""
Módulo responsável pela coleta de notícias de diferentes fontes web
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .config import HEADERS


def scrape_mundo_do_marketing(lista_noticias):
    """Coleta notícias do site Mundo do Marketing"""
    url_base = 'https://mundodomarketing.com.br/noticias'
    print(f"Executando scraper para: Mundo do Marketing")
    links_adicionados = set()
    count = 0

    try:
        response = requests.get(url_base, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            artigos = soup.find_all('div', class_='framer-11hhesp-container')

            for artigo in artigos:
                link_tag = artigo.find('a', class_='framer-1wh61m0')
                container_texto = artigo.find('div', class_='framer-1r5yzu2')

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

            print(f" -> Concluído. {count} notícias novas adicionadas.")
        else:
            print(
                f" -> Falha ao acessar o site. Status: {response.status_code}")
    except requests.RequestException as e:
        print(f" -> Erro de conexão: {e}")


def scrape_meio_e_mensagem(lista_noticias):
    """Coleta notícias do site Meio & Mensagem"""
    url = 'https://www.meioemensagem.com.br/marketing'
    print(f"[EXECUTANDO] Scraper para: Meio & Mensagem")

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

            print(f"  -> Concluído. {len(artigos)} notícias adicionadas.")
        else:
            print(f"  -> Falha. Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"  -> Erro de conexão: {e}")


def scrape_exame(lista_noticias):
    """Coleta notícias do site Exame"""
    url_base = 'https://exame.com'
    url = f'{url_base}/marketing/'
    print(f"[DEFINIÇÃO] Lendo scraper para: Exame")

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

            print(f" -> Concluído. {count} notícias adicionadas.")
            return count
        return 0
    except requests.RequestException:
        print(" -> Erro de conexão")
        return 0


def coletar_noticias():
    """Executa todos os scrapers e retorna lista consolidada de notícias"""
    print("--- Iniciando processo de coleta de dados de múltiplas fontes ---")
    noticias_coletadas = []

    scrape_meio_e_mensagem(noticias_coletadas)
    scrape_mundo_do_marketing(noticias_coletadas)
    scrape_exame(noticias_coletadas)

    print("\n--- Processo de coleta finalizado ---")
    print(
        f"Total de notícias coletadas de todas as fontes: {len(noticias_coletadas)}")

    return noticias_coletadas
