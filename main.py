# ORQUESTRADOR PRINCIPAL - PIPELINE INTELIGENTE DE NOTÍCIAS DE MARKETING
"""
Sistema automatizado para coletar, processar, analisar e apresentar 
notícias relevantes do setor de marketing digital.
"""

from pipeline.selector import selecionar_noticias_estrategicas
from pipeline.clustering import clusterizar_noticias, interpretar_clusters
from pipeline.summarizer import sumarizar_textos
from pipeline.extractor import extrair_textos_noticias
from pipeline.collectors import coletar_noticias
import pandas as pd
import sys
import os

# Adicionar o diretório pipeline ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))

# Importar módulos do pipeline


def executar_pipeline():
    """
    Executa o pipeline completo de processamento de notícias

    Returns:
        tuple: (df_noticias_completo, df_insights_finais)
    """
    print("="*80)
    print("           PIPELINE INTELIGENTE DE NOTÍCIAS DE MARKETING")
    print("="*80)
    print("Sistema automatizado para transformar dados brutos da web em insights estratégicos")
    print("="*80)

    try:
        # ETAPA 1: COLETA DE DADOS
        print("\n[ETAPA 1] COLETA DE DADOS")
        print("-" * 50)
        noticias_coletadas = coletar_noticias()

        if not noticias_coletadas:
            print("ERRO: Nenhuma notícia foi coletada. Verificando conectividade...")
            return None, None

        # Criar DataFrame
        df_noticias = pd.DataFrame(noticias_coletadas, columns=[
                                   'fonte', 'categoria', 'titulo', 'descricao', 'link'])
        print(f"\nOK {len(df_noticias)} notícias coletadas com sucesso!")
        print("\n--- Tabela Consolidada de Notícias Coletadas ---")
        print(df_noticias.head())

        # ETAPA 2: EXTRAÇÃO DE TEXTO
        print("\n[ETAPA 2] EXTRAÇÃO DE TEXTO")
        print("-" * 50)
        textos_para_sumarizar, indices_validos, stats = extrair_textos_noticias(
            df_noticias)

        if not textos_para_sumarizar:
            print("ERRO: Nenhum texto foi extraído com sucesso.")
            return df_noticias, None

        # ETAPA 3: SUMARIZAÇÃO
        print("\n[ETAPA 3] SUMARIZAÇÃO COM IA")
        print("-" * 50)
        df_noticias = sumarizar_textos(
            df_noticias, textos_para_sumarizar, indices_validos)

        if 'resumo' not in df_noticias.columns:
            print("ERRO: Falha na sumarização dos textos.")
            return df_noticias, None

        # ETAPA 4: CLUSTERIZAÇÃO
        print("\n[ETAPA 4] CLUSTERIZAÇÃO E ANÁLISE")
        print("-" * 50)
        df_noticias, kmeans, vectorizer = clusterizar_noticias(df_noticias)

        if kmeans is None:
            print("ERRO: Falha na clusterização.")
            return df_noticias, None

        # ETAPA 5: INTERPRETAÇÃO DOS CLUSTERS
        print("\n[ETAPA 5] INTERPRETAÇÃO DOS CLUSTERS")
        print("-" * 50)
        df_noticias = interpretar_clusters(df_noticias, kmeans, vectorizer)

        # ETAPA 6: SELEÇÃO ESTRATÉGICA
        print("\n[ETAPA 6] SELEÇÃO ESTRATÉGICA")
        print("-" * 50)

        # Preparar DataFrame para seleção
        df_cluster = df_noticias.dropna(subset=['resumo']).copy()
        df_cluster = df_cluster[~df_cluster['resumo'].str.startswith(
            'Falha na sumarização')]

        df_insights_finais = selecionar_noticias_estrategicas(
            df_noticias, df_cluster, top_n=15)

        # RESULTADO FINAL
        print("\n" + "="*80)
        print("           PIPELINE EXECUTADO COM SUCESSO!")
        print("="*80)
        print(f"Total de notícias processadas: {len(df_noticias)}")
        print(f"Notícias com resumos válidos: {len(df_cluster)}")
        print(
            f"Notícias estratégicas selecionadas: {len(df_insights_finais)}")
        print("="*80)

        return df_noticias, df_insights_finais

    except Exception as e:
        print(f"\nERRO CRÍTICO no pipeline: {e}")
        print("Verifique a conectividade com a internet e as dependências instaladas.")
        return None, None


def main():
    """Função principal do orquestrador"""
    print("Iniciando Pipeline Inteligente de Notícias de Marketing...")

    # Executar pipeline
    df_noticias, df_insights = executar_pipeline()

    if df_noticias is not None:
        print("\nRESUMO FINAL:")
        print(f"   - Notícias coletadas: {len(df_noticias)}")
        if df_insights is not None:
            print(f"   - Insights estratégicos: {len(df_insights)}")
            print(
                "\nAs 15 notícias mais estratégicas foram selecionadas para conteúdo de Instagram!")
        else:
            print("   - Insights estratégicos: Não disponíveis")
    else:
        print("\nPipeline não pôde ser executado completamente.")

    print("\nExecução finalizada.")


if __name__ == "__main__":
    main()
