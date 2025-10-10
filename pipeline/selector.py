# ETAPA 6: SELEÇÃO POR RELEVÂNCIA ESTRATÉGICA
"""
Módulo responsável pela seleção das notícias mais estratégicas para conteúdo
"""

import pandas as pd
import re
from .config import RELEVANCE_KEYWORDS


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


def selecionar_noticias_estrategicas(df_noticias, df_cluster, top_n=15):
    """
    Seleciona as notícias mais estratégicas para conteúdo de Instagram

    Args:
        df_noticias: DataFrame completo com notícias
        df_cluster: DataFrame filtrado com notícias válidas
        top_n: Número de notícias a selecionar

    Returns:
        DataFrame com as notícias mais estratégicas
    """
    if df_cluster.empty:
        print("ERRO: DataFrame 'df_cluster' vazio.")
        return pd.DataFrame()

    print("="*70)
    print("           INICIANDO ETAPA 7: SELEÇÃO POR RELEVÂNCIA ESTRATÉGICA")
    print("="*70)

    # Calcular scores de relevância
    df_cluster['relevance_score'] = df_cluster.apply(
        lambda row: calcular_score(row['titulo'] + ' ' + row['resumo']), axis=1
    )

    # Análise de relevância por cluster
    cluster_scores = df_cluster.groupby(
        'cluster')['relevance_score'].mean().sort_values(ascending=False)

    print("\n--- [Análise] Ranking de Relevância dos Clusters ---")
    print("Clusters ordenados pelo potencial de gerar conteúdo atrativo:")
    print(cluster_scores)
    print("-" * 50)

    # Selecionar as top N notícias
    df_insights_finais = df_cluster.nlargest(top_n, 'relevance_score')

    print("\n" + "="*70)
    print(
        f"           AS {top_n} NOTÍCIAS MAIS ESTRATÉGICAS PARA CONTEÚDO DE INSTAGRAM")
    print("="*70)
    print("Notícias selecionadas com base na menção a grandes marcas, campanhas e impacto.")

    # Adicionar tema do cluster se disponível
    if 'tema_cluster' in df_noticias.columns:
        from .config import MAPA_ROTULOS
        df_insights_finais['tema_cluster'] = df_insights_finais['cluster'].map(
            MAPA_ROTULOS)
        print(df_insights_finais[[
              'cluster', 'tema_cluster', 'relevance_score', 'titulo', 'resumo']])
    else:
        print(
            df_insights_finais[['cluster', 'relevance_score', 'titulo', 'resumo']])

    return df_insights_finais
