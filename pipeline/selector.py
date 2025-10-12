# ETAPA 6: SELEÇÃO POR RELEVÂNCIA ESTRATÉGICA
"""
Módulo responsável pela seleção das notícias mais estratégicas para conteúdo
Refatorado para usar banco auxiliar e principal
"""

import pandas as pd
import re
from config.config import RELEVANCE_KEYWORDS
from database.aux_operations import get_aux_operations
from database.main_operations import get_main_operations


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
    e transfere para o banco principal

    Args:
        top_n: Número de notícias a selecionar

    Returns:
        Lista de notícias selecionadas
    """
    # Obter instâncias dos gerenciadores
    aux_ops = get_aux_operations()
    main_ops = get_main_operations()

    # Obter notícias prontas para seleção
    noticias_prontas = aux_ops.get_news_with_resumos()

    if not noticias_prontas:
        print("ERRO: Nenhuma notícia pronta para seleção encontrada.")
        return []

    print("="*70)
    print("INICIANDO SELEÇÃO POR RELEVÂNCIA ESTRATÉGICA")
    print("="*70)

    # Calcular scores de relevância
    print("Calculando scores de relevância estratégica...")
    for noticia in noticias_prontas:
        texto_completo = noticia['titulo'] + ' ' + noticia['resumo']
        score = calcular_score(texto_completo)
        noticia['relevance_score'] = score

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

    print("\n--- Ranking de Relevância dos Clusters ---")
    print("Clusters ordenados pelo potencial de gerar conteúdo atrativo:")
    for cluster, avg_score in sorted(cluster_avg_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"Cluster {cluster}: {avg_score:.2f} (média)")
    print("-" * 50)

    # Selecionar as top N notícias
    noticias_selecionadas = noticias_prontas[:top_n]

    print("\n" + "="*70)
    print(f"AS {top_n} NOTÍCIAS MAIS ESTRATÉGICAS PARA CONTEÚDO DE INSTAGRAM")
    print("="*70)
    print("Notícias selecionadas com base na menção a grandes marcas, campanhas e impacto.")

    # Mostrar notícias selecionadas
    for i, noticia in enumerate(noticias_selecionadas, 1):
        print(f"\n{i}. Score: {noticia['relevance_score']:.1f}")
        print(f"   Título: {noticia['titulo']}")
        print(f"   Cluster: {noticia['cluster']}")
        print(f"   Resumo: {noticia['resumo'][:100]}...")

    # Transferir notícias selecionadas para o banco principal
    print(
        f"\n🔄 Transferindo {len(noticias_selecionadas)} notícias para o banco principal...")
    stats_transferencia = main_ops.transfer_selected_news(
        noticias_selecionadas)

    print(f"\n✅ Seleção estratégica concluída!")
    print(f"   - Notícias novas: {stats_transferencia['novas']}")
    print(f"   - Timestamps atualizados: {stats_transferencia['atualizadas']}")
    print(f"   - Falhas: {stats_transferencia['falhas']}")

    return noticias_selecionadas
