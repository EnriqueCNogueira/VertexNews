# ETAPA 6: SELEÇÃO POR RELEVÂNCIA ESTRATÉGICA
"""
Módulo responsável pela seleção das notícias mais estratégicas para conteúdo
Refatorado para usar banco auxiliar e principal
"""

import pandas as pd
import re
from config.config import RELEVANCE_KEYWORDS
from database import get_db_manager


def calcular_score(texto):
    """
    Calcula o score de relevância de um texto baseado nas palavras-chave

    Args:
        texto: Texto para análise

    Returns:
        Score de relevância
    """
    if not isinstance(texto, str):
        return 0

    score = 0
    texto_lower = texto.lower()

    for categoria in RELEVANCE_KEYWORDS.values():
        peso = categoria['peso']
        for termo in categoria['termos']:
            if re.search(r'\b' + re.escape(termo) + r'\b', texto_lower):
                score += peso

    return score


def selecionar_noticias_estrategicas(top_n=15):
    """
    Seleciona as notícias mais estratégicas para conteúdo de Instagram
    e transfere para o banco principal com controle de postagem

    Args:
        top_n: Número de notícias a selecionar

    Returns:
        Lista de notícias selecionadas
    """
    # Obter instância do gerenciador unificado
    db_manager = get_db_manager()

    # ETAPA 1: Obter notícias prontas para seleção
    noticias_prontas = db_manager.get_news_for_selection()

    if not noticias_prontas:
        print("ERRO: Nenhuma notícia pronta para seleção encontrada.")
        return []

    # Calcular scores de relevância
    for noticia in noticias_prontas:
        texto_completo = noticia['titulo'] + ' ' + noticia['resumo']
        score = calcular_score(texto_completo)
        noticia['relevance_score'] = score
        noticia['score'] = score  # Adicionar score para transferência

    # Ordenar por score de relevância
    noticias_prontas.sort(key=lambda x: x['relevance_score'], reverse=True)

    # Análise de relevância por cluster
    cluster_scores = {}
    for noticia in noticias_prontas:
        cluster = noticia['cluster']
        if cluster not in cluster_scores:
            cluster_scores[cluster] = []
        cluster_scores[cluster].append(noticia['relevance_score'])

    # Calcular média por cluster
    cluster_avg_scores = {}
    for cluster, scores in cluster_scores.items():
        cluster_avg_scores[cluster] = sum(scores) / len(scores)

    # Selecionar as top N notícias
    noticias_selecionadas = noticias_prontas[:top_n]

    # ETAPA 2: Arquivar notícias postadas que NÃO foram re-selecionadas
    # Obter links das notícias selecionadas
    links_selecionados = [noticia['link'] for noticia in noticias_selecionadas]

    # Arquivar apenas as notícias postadas que não foram re-selecionadas
    archived_count = db_manager.archive_posted_news(
        keep_selected_links=links_selecionados)

    # Transferir notícias selecionadas para o banco principal
    stats_transferencia = db_manager.transfer_selected_news(
        noticias_selecionadas)

    return noticias_selecionadas
