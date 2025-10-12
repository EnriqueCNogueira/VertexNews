# ETAPA 5: VETORIZAÇÃO E CLUSTERIZAÇÃO (K-MEANS)
"""
Módulo responsável pela vetorização e clusterização das notícias
Refatorado para usar banco auxiliar
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
import numpy as np
from config.config import CLUSTERING_CONFIG
from database.aux_operations import get_aux_operations


def preparar_stopwords():
    """Baixa e prepara as stopwords em português"""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("O recurso 'stopwords' não foi encontrado. Tentando baixar...")
        nltk.download('stopwords')
        print("Download concluído.")

    return stopwords.words('portuguese')


def clusterizar_noticias():
    """
    Realiza a vetorização e clusterização das notícias do banco auxiliar

    Returns:
        tuple: (kmeans, vectorizer, noticias_processadas)
    """
    # Obter instância das operações auxiliares
    aux_ops = get_aux_operations()

    # Obter notícias com resumos válidos
    noticias = aux_ops.get_news_with_resumos()

    if not noticias:
        print("ERRO: Nenhuma notícia com resumo válido encontrada no banco auxiliar.")
        return None, None, []

    print("="*60)
    print("INICIANDO VETORIZAÇÃO E CLUSTERIZAÇÃO")
    print("="*60)

    # Preparar stopwords
    portuguese_stopwords = preparar_stopwords()

    print(
        f"\nPreparando clusterização de {len(noticias)} notícias com resumos válidos...")

    # Preparar dados para clusterização
    resumos = [noticia['resumo'] for noticia in noticias]

    # Vetorização TF-IDF
    print("Executando vetorização TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=CLUSTERING_CONFIG['max_features'],
        stop_words=portuguese_stopwords
    )
    X = vectorizer.fit_transform(resumos)

    # Clusterização K-Means
    print("Executando algoritmo K-Means...")
    kmeans = KMeans(
        n_clusters=CLUSTERING_CONFIG['n_clusters'],
        random_state=CLUSTERING_CONFIG['random_state'],
        n_init=CLUSTERING_CONFIG['n_init']
    )

    clusters = kmeans.fit_predict(X)

    # Atualizar clusters no banco auxiliar
    print("Salvando clusters no banco auxiliar...")
    clusters_salvos = 0
    for i, noticia in enumerate(noticias):
        success = aux_ops.update_cluster(noticia['link'], int(clusters[i]))
        if success:
            clusters_salvos += 1

    print(f"✅ {clusters_salvos} clusters salvos no banco auxiliar")

    print("\nClusterização concluída com sucesso!")
    print("\n" + "="*60)
    print("DISTRIBUIÇÃO DE NOTÍCIAS POR CLUSTER")
    print("="*60)

    # Mostrar distribuição dos clusters
    cluster_counts = {}
    for cluster in clusters:
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1

    for cluster_id in sorted(cluster_counts.keys()):
        print(f"Cluster {cluster_id}: {cluster_counts[cluster_id]} notícias")

    return kmeans, vectorizer, noticias


def interpretar_clusters(kmeans, vectorizer):
    """
    Interpreta e analisa os clusters formados

    Args:
        kmeans: Modelo K-Means treinado
        vectorizer: Vetorizador TF-IDF treinado

    Returns:
        Lista de notícias com interpretação dos clusters
    """
    if kmeans is None or vectorizer is None:
        print("ERRO: Modelos de clusterização não encontrados.")
        return []

    print("="*70)
    print("INICIANDO INTERPRETAÇÃO E ANÁLISE DOS CLUSTERS")
    print("="*70)

    print("\nExtraindo palavras-chave principais de cada cluster...\n")

    termos = vectorizer.get_feature_names_out()
    centroides = kmeans.cluster_centers_
    termos_ordenados_por_centroide = centroides.argsort()[:, ::-1]

    for i in range(CLUSTERING_CONFIG['n_clusters']):
        palavras_chave = [termos[ind]
                          for ind in termos_ordenados_por_centroide[i, :10]]
        print(f"Cluster {i}:")
        print(f"  -> Palavras-chave: {', '.join(palavras_chave)}")

    print("\n" + "="*70)
    print("\nRevisando amostras de notícias de cada cluster...\n")

    # Obter instância das operações auxiliares
    aux_ops = get_aux_operations()

    for i in range(CLUSTERING_CONFIG['n_clusters']):
        print(f"--- Amostras do Cluster {i} ---")
        amostras = aux_ops.get_news_by_cluster(i)

        for j, amostra in enumerate(amostras[:3]):  # Mostrar apenas 3 amostras
            print(f"  - Título: {amostra['titulo']}")

        print("-"*(len(f"--- Amostras do Cluster {i} ---")))

    print("\n" + "="*70)
    print("Interpretação dos clusters concluída!")
    print("="*70)

    return aux_ops.get_all_news()
