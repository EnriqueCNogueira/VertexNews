# ETAPA 3: EXTRAÇÃO DE TEXTO
"""
Módulo responsável pela extração do conteúdo completo dos artigos
Refatorado para usar cache em memória e banco auxiliar
"""

import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from config.config import HEADERS
from errors.error_handler import error_handler
from database.aux_operations import get_aux_operations
from database.text_cache import get_text_cache


def extrair_fallback_exame(soup):
    """
    Função de fallback para extrair conteúdo básico do Exame quando há paywall
    """
    try:
        # Extrair título
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else ""

        # Extrair meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        desc_text = meta_desc.get('content', '') if meta_desc else ""

        # Extrair qualquer texto visível que possa ser útil
        visible_text = ""
        for tag in soup.find_all(['p', 'div', 'span'], limit=10):
            text = tag.get_text(strip=True)
            if len(text) > 20 and len(text) < 500:  # Filtrar textos muito curtos ou longos
                visible_text += text + " "

        # Combinar tudo
        fallback_content = f"{title_text}. {desc_text}. {visible_text}".strip()

        # Retornar apenas se tiver conteúdo suficiente
        if len(fallback_content) > 100:
            return fallback_content

    except Exception:
        pass

    return None


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
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            error_handler.handle_warning(
                f"Status HTTP {response.status_code} para {url}", fonte)
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = None

        # Seletores específicos para cada fonte
        if fonte == 'Meio & Mensagem':
            content_div = soup.find('div', class_='content') or soup.find(
                'article') or soup.find('div', class_='post-content')
        elif fonte == 'Mundo do Marketing':
            content_div = soup.find('div', class_='content') or soup.find(
                'article') or soup.find('div', class_='post-content')
        elif fonte == 'GKPB':
            # Seletores específicos para o GKPB
            content_div = (soup.find('div', class_='tdb_single_content') or
                           soup.find('div', class_='td-post-content') or
                           soup.find('article') or
                           soup.find('div', class_='content') or
                           soup.find('div', {'class': lambda x: x and 'content' in x.lower()}))
        elif fonte == 'Exame':
            # Tentar múltiplos seletores para o Exame devido a mudanças no layout
            content_div = (soup.find('div', class_='article-content') or
                           soup.find('article') or
                           soup.find('div', class_='content') or
                           soup.find('div', {'class': lambda x: x and 'content' in x.lower()}) or
                           soup.find('div', {'class': lambda x: x and 'article' in x.lower()}) or
                           soup.find('main') or
                           soup.find('div', {'class': lambda x: x and 'text' in x.lower()}))

            # Se não encontrou conteúdo principal, tentar extrair resumo/lead
            if not content_div:
                content_div = (soup.find('div', {'class': lambda x: x and 'lead' in x.lower()}) or
                               soup.find('div', {'class': lambda x: x and 'summary' in x.lower()}) or
                               soup.find('div', {'class': lambda x: x and 'excerpt' in x.lower()}))

        if content_div:
            paragraphs = content_div.find_all('p')
            if paragraphs:
                texto_completo = ' '.join(
                    [p.get_text(strip=True) for p in paragraphs])
                if len(texto_completo.strip()) > 50:  # Validação mínima de conteúdo
                    return texto_completo
                else:
                    error_handler.handle_warning(
                        f"Conteúdo muito curto extraído de {url}", fonte)
            else:
                error_handler.handle_warning(
                    f"Nenhum parágrafo encontrado em {url}", fonte)
        else:
            # Última tentativa: extrair título e meta description como fallback
            if fonte == 'Exame':
                fallback_text = extrair_fallback_exame(soup)
                if fallback_text:
                    error_handler.handle_warning(
                        f"Usando conteúdo fallback para {url}", fonte)
                    return fallback_text

            error_handler.handle_warning(
                f"Seletor de conteúdo não encontrado em {url}", fonte)

        return None
    except requests.RequestException as e:
        error_handler.handle_error(e, f"Extração de texto de {fonte}")
        return None


def extrair_textos_noticias():
    """
    Extrai textos completos de todas as notícias no banco auxiliar
    e armazena no cache em memória

    Returns:
        tuple: (textos_para_sumarizar, indices_validos, stats)
    """
    # Obter instâncias dos gerenciadores
    aux_ops = get_aux_operations()
    text_cache = get_text_cache()

    # Obter notícias do banco auxiliar
    noticias = aux_ops.get_all_news()

    if not noticias:
        print("Nenhuma notícia encontrada no banco auxiliar.")
        return [], [], {}

    textos_para_sumarizar = []
    indices_validos = []
    stats = defaultdict(lambda: {'success': 0, 'fail': 0})
    total_artigos = len(noticias)

    print(
        f"Iniciando extração de conteúdo completo para {total_artigos} artigos...")

    for i, noticia in enumerate(noticias):
        link = noticia['link']

        # Detectar fonte baseada no domínio
        if 'meioemensagem.com.br' in link:
            fonte = 'Meio & Mensagem'
        elif 'mundodomarketing.com.br' in link:
            fonte = 'Mundo do Marketing'
        elif 'exame.com' in link:
            fonte = 'Exame'
        elif 'gkpb.com.br' in link:
            fonte = 'GKPB'
        else:
            fonte = 'Desconhecida'

        print(f"[{i + 1}/{total_artigos}] Extraindo conteúdo de '{fonte}'...")

        texto = extrair_texto_completo(link, fonte)

        if texto:
            stats[fonte]['success'] += 1
            textos_para_sumarizar.append("summarize: " + texto)
            indices_validos.append(i)

            # Armazenar no cache
            text_cache.store_text(link, texto)
        else:
            stats[fonte]['fail'] += 1

        time.sleep(0.5)  # Evitar sobrecarga nos servidores

    # Exibir diagnóstico
    print("\n" + "="*50)
    print("      DIAGNÓSTICO DA EXTRAÇÃO DE CONTEÚDO")
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
    print("\nTextos extraídos estão prontos para sumarização.")

    return textos_para_sumarizar, indices_validos, stats
