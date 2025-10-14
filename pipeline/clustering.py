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
from database import get_db_manager


def preparar_stopwords():
    """Baixa e prepara as stopwords em português"""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    return stopwords.words('portuguese')


def clusterizar_noticias():
    """
    Realiza a vetorização e clusterização das notícias do banco auxiliar
    Versão otimizada com melhor tratamento de erros

    Returns:
        tuple: (kmeans, vectorizer, noticias_processadas)
    """
    db_manager = get_db_manager()
    noticias = db_manager.get_news_for_clustering()

    if not noticias:
        print("ERRO: Nenhuma notícia com resumo válido encontrada.")
        return None, None, []

    try:
        # Preparar dados
        portuguese_stopwords = preparar_stopwords()
        resumos = [noticia['resumo'] for noticia in noticias]

        # Vetorização TF-IDF otimizada
        vectorizer = TfidfVectorizer(
            max_features=CLUSTERING_CONFIG['max_features'],
            stop_words=portuguese_stopwords,
            ngram_range=(1, 2)  # Adicionar bigramas para melhor clustering
        )
        X = vectorizer.fit_transform(resumos)

        # Clusterização K-Means otimizada
        kmeans = KMeans(
            n_clusters=CLUSTERING_CONFIG['n_clusters'],
            random_state=CLUSTERING_CONFIG['random_state'],
            n_init=CLUSTERING_CONFIG['n_init'],
            max_iter=300  # Aumentar iterações para melhor convergência
        )

        clusters = kmeans.fit_predict(X)

        # Atualizar clusters em batch para melhor performance
        clusters_salvos = _update_clusters_batch(
            db_manager, noticias, clusters)

        return kmeans, vectorizer, noticias

    except Exception as e:
        print(f"[ERRO] Falha na clusterização: {e}")
        return None, None, []


def _update_clusters_batch(db_manager, noticias, clusters):
    """Atualiza clusters em batch para melhor performance"""
    clusters_salvos = 0
    for i, noticia in enumerate(noticias):
        if db_manager.update_news_with_cluster(noticia['link'], int(clusters[i])):
            clusters_salvos += 1
    return clusters_salvos


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

    # Obter instância do gerenciador unificado
    db_manager = get_db_manager()

    return db_manager.get_news_for_selection()
