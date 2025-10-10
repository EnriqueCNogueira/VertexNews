# ETAPA 5: VETORIZAÇÃO E CLUSTERIZAÇÃO (K-MEANS)
"""
Módulo responsável pela vetorização e clusterização das notícias
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
import numpy as np
from .config import CLUSTERING_CONFIG


def preparar_stopwords():
    """Baixa e prepara as stopwords em português"""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("O recurso 'stopwords' não foi encontrado. Tentando baixar...")
        nltk.download('stopwords')
        print("Download concluído.")

    return stopwords.words('portuguese')


def clusterizar_noticias(df_noticias):
    """
    Realiza a vetorização e clusterização das notícias

    Args:
        df_noticias: DataFrame com notícias e resumos

    Returns:
        tuple: (df_noticias_atualizado, kmeans, vectorizer)
    """
    if 'resumo' not in df_noticias.columns:
        print("ERRO: Coluna 'resumo' não encontrada no DataFrame.")
        return df_noticias, None, None

    print("="*60)
    print("           INICIANDO ETAPA 4 E 5: VETORIZAÇÃO E CLUSTERIZAÇÃO")
    print("="*60)

    # Preparar stopwords
    portuguese_stopwords = preparar_stopwords()

    # Filtrar notícias com resumos válidos
    df_cluster = df_noticias.dropna(subset=['resumo']).copy()
    df_cluster = df_cluster[~df_cluster['resumo'].str.startswith(
        'Falha na sumarização')]

    if df_cluster.empty:
        print("Nenhum resumo válido encontrado para a clusterização.")
        return df_noticias, None, None

    print(
        f"\nPreparando para clusterizar {len(df_cluster)} notícias com resumos válidos...")

    # Vetorização TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=CLUSTERING_CONFIG['max_features'],
        stop_words=portuguese_stopwords
    )
    X = vectorizer.fit_transform(df_cluster['resumo'])

    # Clusterização K-Means
    kmeans = KMeans(
        n_clusters=CLUSTERING_CONFIG['n_clusters'],
        random_state=CLUSTERING_CONFIG['random_state'],
        n_init=CLUSTERING_CONFIG['n_init']
    )

    df_cluster['cluster'] = kmeans.fit_predict(X)

    # Adicionar clusters ao DataFrame original
    df_noticias['cluster'] = df_cluster['cluster']
    df_noticias['cluster'] = df_noticias['cluster'].astype('Int64')

    print("\n--- Processo de Clusterização Concluído! ---")
    print("\n" + "="*60)
    print("                   AMOSTRA DO RESULTADO DA CLUSTERIZAÇÃO")
    print("="*60)
    print(df_noticias[['titulo', 'resumo', 'cluster']].head())

    print("\n" + "="*60)
    print("                   DISTRIBUIÇÃO DE NOTÍCIAS POR CLUSTER")
    print("="*60)
    print(df_noticias['cluster'].value_counts().sort_index())

    return df_noticias, kmeans, vectorizer


def interpretar_clusters(df_noticias, kmeans, vectorizer):
    """
    Interpreta e analisa os clusters formados

    Args:
        df_noticias: DataFrame com notícias e clusters
        kmeans: Modelo K-Means treinado
        vectorizer: Vetorizador TF-IDF treinado

    Returns:
        DataFrame com rótulos dos temas
    """
    if kmeans is None or vectorizer is None:
        print("ERRO: Modelos de clusterização não encontrados.")
        return df_noticias

    print("="*70)
    print("           INICIANDO ETAPA 6: INTERPRETAÇÃO E ANÁLISE DOS CLUSTERS")
    print("="*70)

    print(
        "\n--- [Análise 1] Extraindo as palavras-chave principais de cada cluster ---\n")

    termos = vectorizer.get_feature_names_out()
    centroides = kmeans.cluster_centers_
    termos_ordenados_por_centroide = centroides.argsort()[:, ::-1]

    for i in range(CLUSTERING_CONFIG['n_clusters']):
        palavras_chave = [termos[ind]
                          for ind in termos_ordenados_por_centroide[i, :10]]
        print(f"Cluster {i}:")
        print(f"  -> Palavras-chave: {', '.join(palavras_chave)}")

    print("\n" + "="*70)
    print(
        "\n--- [Análise 2] Revisando amostras de notícias de cada cluster ---\n")

    for i in range(CLUSTERING_CONFIG['n_clusters']):
        print(f"--- Amostras do Cluster {i} ---")
        amostras = df_noticias[df_noticias['cluster']
                               == i][['titulo', 'resumo']].head(3)
        for index, row in amostras.iterrows():
            print(f"  - Título: {row['titulo']}")
        print("-"*(len(f"--- Amostras do Cluster {i} ---")))

    # Adicionar rótulos dos temas
    from .config import MAPA_ROTULOS
    df_noticias['tema_cluster'] = df_noticias['cluster'].map(MAPA_ROTULOS)

    print("\n" + "="*70)
    print("\n--- DataFrame final com os rótulos dos temas ---")
    print(df_noticias[['titulo', 'cluster', 'tema_cluster']].head())

    return df_noticias
