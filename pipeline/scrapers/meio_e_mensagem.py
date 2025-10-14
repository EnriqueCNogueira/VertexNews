# SCRAPER MEIO & MENSAGEM
"""
Scraper específico para o site Meio & Mensagem
Refatorado para usar seletores específicos e extração de imagens com fallbacks
"""

import requests
from bs4 import BeautifulSoup
import re
from config.config import HEADERS
from errors.error_handler import error_handler


def scrape_meio_e_mensagem(lista_noticias):
    """Coleta notícias do site Meio & Mensagem usando seletores específicos"""
    url = 'https://www.meioemensagem.com.br/marketing'
    print(f"  Conectando ao site Meio & Mensagem...")

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            # Garantir encoding correto para caracteres especiais
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            # Usar seletores específicos para o Meio & Mensagem baseados na análise HTML
            artigos = soup.find_all('article')

            count = 0
            for artigo in artigos:
                try:
                    # Buscar link principal do artigo
                    link_tag = artigo.find('a')
                    if not link_tag:
                        continue

                    link = link_tag.get('href')
                    if not link:
                        continue

                    # Buscar título específico (h2 ou h3)
                    titulo_tag = artigo.find(['h2', 'h3'], class_='titulo')
                    if not titulo_tag:
                        continue

                    titulo = titulo_tag.get_text(strip=True)

                    # Buscar categoria específica
                    categoria_tag = artigo.find('span', class_='categoria')
                    categoria = categoria_tag.get_text(
                        strip=True) if categoria_tag else "Marketing"

                    # Buscar descrição específica
                    descricao_tag = artigo.find('p')
                    descricao = descricao_tag.get_text(
                        strip=True) if descricao_tag else "Sem descrição"

                    # Buscar data específica (span com tempo)
                    data = "Sem data"
                    spans = artigo.find_all('span')
                    for span in spans:
                        text = span.get_text(strip=True)
                        if text and any(word in text.lower() for word in ['minutos', 'horas', 'dias', 'atrás']):
                            data = text
                            break

                    # Buscar imagem específica para Meio & Mensagem (usando data-src)
                    foto_url = ""

                    # Procurar por img com data-src (método principal)
                    img_tag = artigo.find('img')
                    if img_tag:
                        foto_url = img_tag.get('data-src', '')

                    # Fallback: procurar por src tradicional
                    if not foto_url and img_tag:
                        foto_url = img_tag.get('src', '')

                    # Fallback: procurar por source dentro de picture
                    if not foto_url:
                        picture = artigo.find('picture')
                        if picture:
                            source_tag = picture.find('source')
                            if source_tag:
                                srcset = source_tag.get('srcset', '')
                                if srcset:
                                    # Pegar a primeira URL do srcset
                                    foto_url = srcset.split(
                                        ',')[0].strip().split(' ')[0]

                    lista_noticias.append({
                        'fonte': 'Meio e Mensagem',
                        'categoria': categoria,
                        'titulo': titulo,
                        'descricao': descricao,
                        'link': link,
                        'foto': foto_url,
                        'data': data
                    })
                    count += 1

                except Exception as e:
                    error_handler.handle_error(
                        e, f"Erro ao processar artigo Meio & Mensagem")
                    continue

            print(f"  Sucesso: {count} notícias coletadas do Meio & Mensagem")
        else:
            print(f"  Erro: Status HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"  Erro de conexão Meio & Mensagem: {e}")
