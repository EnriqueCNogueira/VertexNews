# ETAPA 2: COLETORES DE DADOS
"""
Módulo responsável pela coleta de notícias de diferentes fontes web
Refatorado para usar banco de dados SQLite e cache em memória
"""

from .scrapers import scrape_mundo_do_marketing, scrape_meio_e_mensagem, scrape_exame, scrape_gkpb
from database.aux_operations import get_aux_operations
from database.text_cache import get_text_cache


def coletar_noticias():
    """
    Executa todos os scrapers e salva dados no banco auxiliar
    Os textos completos são armazenados no cache em memória
    """
    print("Iniciando coleta de notícias de múltiplas fontes...")
    print("Dados serão salvos no banco auxiliar e cache em memória")

    # Obter instâncias dos gerenciadores
    aux_ops = get_aux_operations()
    text_cache = get_text_cache()

    # Limpar cache anterior
    text_cache.clear_cache()

    noticias_coletadas = []
    noticias_salvas = 0

    print("\nColetando de: Meio & Mensagem")
    scrape_meio_e_mensagem(noticias_coletadas)

    print("\nColetando de: Mundo do Marketing")
    scrape_mundo_do_marketing(noticias_coletadas)

    print("\nColetando de: Exame")
    scrape_exame(noticias_coletadas)

    print("\nColetando de: GKPB")
    scrape_gkpb(noticias_coletadas)

    print(
        f"\nColeta finalizada: {len(noticias_coletadas)} notícias coletadas no total")

    # Salvar notícias no banco auxiliar e textos no cache
    print("\nSalvando notícias no banco auxiliar...")
    for noticia in noticias_coletadas:
        # Salvar dados básicos no banco auxiliar
        success = aux_ops.insert_news_basic(
            titulo=noticia['titulo'],
            link=noticia['link'],
            imagem=noticia.get('foto')
        )

        if success:
            noticias_salvas += 1

        # Armazenar texto completo no cache (se disponível)
        if 'texto_completo' in noticia and noticia['texto_completo']:
            text_cache.store_text(noticia['link'], noticia['texto_completo'])

    print(f"✅ {noticias_salvas} notícias salvas no banco auxiliar")

    # Mostrar estatísticas do cache
    cache_stats = text_cache.get_cache_stats()
    print(
        f"📊 Cache em memória: {cache_stats['total_texts']} textos armazenados")

    return noticias_coletadas
