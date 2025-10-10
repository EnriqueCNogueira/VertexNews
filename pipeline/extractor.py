# ETAPA 3: EXTRAÇÃO DE TEXTO
"""
Módulo responsável pela extração do conteúdo completo dos artigos
"""

import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from .config import HEADERS


def extrair_texto_completo(url: str, fonte: str) -> str:
    """
    Extrai o texto completo de um artigo baseado na fonte

    Args:
        url: URL do artigo
        fonte: Nome da fonte para determinar o seletor CSS

    Returns:
        Texto completo do artigo ou None se falhar
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = None

        # Seletores específicos para cada fonte
        if fonte == 'Meio & Mensagem':
            content_div = soup.find('div', class_='__content')
        elif fonte == 'Mundo do Marketing':
            content_div = soup.find('div', class_='framer-1ga874m')
        elif fonte == 'Marketing Week':
            content_div = soup.find('div', class_='content')
        elif fonte == 'Exame':
            content_div = soup.find('div', id='news-body')

        if content_div:
            return ' '.join([p.get_text(strip=True) for p in content_div.find_all('p')])

        return None
    except requests.RequestException:
        return None


def extrair_textos_noticias(df_noticias):
    """
    Extrai textos completos de todas as notícias no DataFrame

    Args:
        df_noticias: DataFrame com as notícias coletadas

    Returns:
        tuple: (textos_para_sumarizar, indices_validos, stats)
    """
    if df_noticias.empty:
        print("DataFrame de notícias está vazio.")
        return [], [], {}

    textos_para_sumarizar = []
    indices_validos = []
    stats = defaultdict(lambda: {'success': 0, 'fail': 0})
    total_artigos = len(df_noticias)

    print(f"--- Iniciando extração de texto para {total_artigos} artigos ---")

    for index, row in df_noticias.iterrows():
        fonte = row['fonte']
        print(f"[{index + 1}/{total_artigos}] Tentando extrair de '{fonte}'...")

        texto = extrair_texto_completo(row['link'], fonte)

        if texto:
            stats[fonte]['success'] += 1
            textos_para_sumarizar.append("summarize: " + texto)
            indices_validos.append(index)
        else:
            stats[fonte]['fail'] += 1

        time.sleep(0.5)  # Evitar sobrecarga nos servidores

    # Exibir diagnóstico
    print("\n" + "="*50)
    print("      DIAGNÓSTICO DA EXTRAÇÃO DE TEXTO")
    print("="*50)

    total_success = 0
    total_fail = 0

    for fonte, resultados in sorted(stats.items()):
        s = resultados['success']
        f = resultados['fail']
        total_fonte = s + f

        print(f"\nFonte: {fonte}")
        print(f"  - SUCESSO: {s} / {total_fonte}")
        print(
            f"  - FALHAS:  {f} / {total_fonte} (Causa provável: paywall, login ou layout diferente)")

        total_success += s
        total_fail += f

    print("\n" + "="*50)
    print("RESUMO GERAL:")
    print(f"  - Total de textos extraídos com sucesso: {total_success}")
    print(f"  - Total de falhas na extração: {total_fail}")
    print(f"  - Total de artigos processados: {total_artigos}")
    print("="*50)
    print("\nAs listas 'textos_para_sumarizar' e 'indices_validos' estão prontas para a próxima etapa.")

    return textos_para_sumarizar, indices_validos, stats
