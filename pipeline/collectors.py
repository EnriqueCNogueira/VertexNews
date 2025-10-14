# ETAPA 2: COLETORES DE DADOS
"""
Módulo responsável pela coleta de notícias de diferentes fontes web
Refatorado para usar banco de dados SQLite e cache em memória
"""

from .scrapers import scrape_mundo_do_marketing, scrape_meio_e_mensagem, scrape_exame, scrape_gkpb
from database import get_db_manager
from database.text_cache import get_text_cache


def coletar_noticias():
    """
    Executa todos os scrapers e salva dados no banco auxiliar
    Os textos completos são armazenados no cache em memória
    """
    # Obter instância do gerenciador unificado
    db_manager = get_db_manager()
    text_cache = get_text_cache()

    # Limpar cache anterior
    text_cache.clear_cache()

    noticias_coletadas = []
    noticias_salvas = 0

    scrape_meio_e_mensagem(noticias_coletadas)
    scrape_mundo_do_marketing(noticias_coletadas)
    scrape_exame(noticias_coletadas)
    scrape_gkpb(noticias_coletadas)

    # Salvar notícias no banco auxiliar e textos no cache
    for noticia in noticias_coletadas:
        # Salvar dados básicos no banco auxiliar
        success = db_manager.insert_news_basic(
            titulo=noticia['titulo'],
            link=noticia['link'],
            imagem=noticia.get('foto'),
            fonte=noticia.get('fonte', 'Desconhecida')
        )

        if success:
            noticias_salvas += 1

        # Armazenar texto completo no cache (se disponível)
        if 'texto_completo' in noticia and noticia['texto_completo']:
            text_cache.store_text(noticia['link'], noticia['texto_completo'])

    return noticias_coletadas
