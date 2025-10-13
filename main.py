# ORQUESTRADOR PRINCIPAL - PIPELINE INTELIGENTE DE NOTÍCIAS DE MARKETING
"""
Sistema automatizado para coletar, processar, analisar e apresentar 
notícias relevantes do setor de marketing digital.
Refatorado para usar banco de dados SQLite e cache em memória
"""

from pipeline.selector import selecionar_noticias_estrategicas
from pipeline.clustering import clusterizar_noticias, interpretar_clusters
from pipeline.summarizer import sumarizar_textos
from pipeline.extractor import extrair_textos_noticias
from pipeline.collectors import coletar_noticias
from database.init_db import initialize_databases
from database.cleanup import cleanup_auxiliary_database
from database.aux_operations import get_aux_operations
from database.main_operations import get_main_operations
from database.text_cache import get_text_cache
from errors.error_handler import error_handler
import sys
import os

# Adicionar o diretório pipeline ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))


def executar_pipeline():
    """
    Executa o pipeline completo de processamento de notícias
    usando banco de dados SQLite e cache em memória

    Returns:
        tuple: (noticias_processadas, noticias_selecionadas)
    """
    print("="*80)
    print("           PIPELINE INTELIGENTE DE NOTÍCIAS DE MARKETING")
    print("="*80)
    print("Sistema automatizado para transformar dados brutos da web em insights estratégicos")
    print("Arquitetura: SQLite + Cache em Memória")
    print("="*80)

    try:
        # INICIALIZAÇÃO DOS BANCOS DE DADOS
        print("\n[INICIALIZAÇÃO] BANCOS DE DADOS SQLITE")
        print("-" * 50)

        if not initialize_databases():
            print("ERRO: Falha na inicialização dos bancos de dados.")
            return None, None

        # Obter instâncias dos gerenciadores
        aux_ops = get_aux_operations()
        main_ops = get_main_operations()
        text_cache = get_text_cache()

        # ETAPA 1: COLETA DE DADOS
        print("\n[ETAPA 1] COLETA DE DADOS")
        print("-" * 50)

        try:
            noticias_coletadas = coletar_noticias()
        except Exception as e:
            if not error_handler.handle_error(e, "Coleta de notícias", continue_execution=False):
                return None, None

        if not error_handler.validate_data(noticias_coletadas, 'not_empty', "Coleta de notícias"):
            print("ERRO: Nenhuma notícia foi coletada. Verificando conectividade...")
            return None, None

        print(
            f"SUCESSO: {len(noticias_coletadas)} notícias coletadas de todas as fontes")

        # Verificar estatísticas do banco auxiliar
        counts = aux_ops.count_news()
        print(
            f"BANCO AUXILIAR: {counts['total']} notícias, {counts['com_resumos']} com resumos")

        # ETAPA 2: EXTRAÇÃO DE TEXTO
        print("\n[ETAPA 2] EXTRAÇÃO DE TEXTO")
        print("-" * 50)

        try:
            textos_para_sumarizar, indices_validos, stats = extrair_textos_noticias()
        except Exception as e:
            error_handler.handle_error(e, "Extração de textos")
            return None, None

        if not error_handler.validate_data(textos_para_sumarizar, 'not_empty', "Extração de textos"):
            print("ERRO: Nenhum texto foi extraído com sucesso.")
            return None, None

        # Verificar estatísticas do cache
        cache_stats = text_cache.get_cache_stats()
        print(
            f"CACHE: {cache_stats['total_texts']} textos armazenados em memória")

        # ETAPA 3: SUMARIZAÇÃO
        print("\n[ETAPA 3] SUMARIZAÇÃO COM IA")
        print("-" * 50)

        try:
            textos_sumarizados = sumarizar_textos()
        except Exception as e:
            error_handler.handle_error(e, "Sumarização com IA")
            return None, None

        if textos_sumarizados == 0:
            print("ERRO: Falha na sumarização dos textos.")
            return None, None

        print(f"✅ {textos_sumarizados} textos sumarizados com sucesso")

        # ETAPA 4: CLUSTERIZAÇÃO
        print("\n[ETAPA 4] CLUSTERIZAÇÃO E ANÁLISE")
        print("-" * 50)

        try:
            kmeans, vectorizer, noticias_processadas = clusterizar_noticias()
        except Exception as e:
            error_handler.handle_error(e, "Clusterização")
            return None, None

        if kmeans is None:
            print("ERRO: Falha na clusterização.")
            return None, None

        # ETAPA 5: INTERPRETAÇÃO DOS CLUSTERS
        print("\n[ETAPA 5] INTERPRETAÇÃO DOS CLUSTERS")
        print("-" * 50)

        try:
            noticias_finais = interpretar_clusters(kmeans, vectorizer)
        except Exception as e:
            error_handler.handle_error(e, "Interpretação de clusters")
            # Continua execução mesmo com erro nesta etapa

        # ETAPA 6: SELEÇÃO ESTRATÉGICA
        print("\n[ETAPA 6] SELEÇÃO ESTRATÉGICA")
        print("-" * 50)

        try:
            noticias_selecionadas = selecionar_noticias_estrategicas(top_n=15)
        except Exception as e:
            error_handler.handle_error(e, "Seleção estratégica")
            noticias_selecionadas = []

        # ETAPA 7: LIMPEZA
        print("\n[ETAPA 7] LIMPEZA DO BANCO AUXILIAR")
        print("-" * 50)

        try:
            cleanup_success = cleanup_auxiliary_database()
            if cleanup_success:
                print("✅ Banco auxiliar limpo e removido com sucesso")
            else:
                print("⚠️ Alguns problemas na limpeza do banco auxiliar")
        except Exception as e:
            error_handler.handle_error(e, "Limpeza do banco auxiliar")

        # RESULTADO FINAL
        print("\n" + "="*80)
        print("           PIPELINE EXECUTADO COM SUCESSO!")
        print("="*80)

        # Estatísticas finais
        main_stats = main_ops.get_statistics()
        print(
            f"Total de notícias no banco principal: {main_stats.get('total', 0)}")
        print(
            f"Notícias selecionadas nesta execução: {len(noticias_selecionadas)}")
        print(
            f"Notícias dos últimos 7 dias: {main_stats.get('ultimos_7_dias', 0)}")

        # Resumo de erros e avisos
        error_summary = error_handler.get_summary()
        if error_summary['errors'] > 0 or error_summary['warnings'] > 0:
            print(f"\nRESUMO DE PROBLEMAS ENCONTRADOS:")
            print(f"   - Erros encontrados: {error_summary['errors']}")
            print(f"   - Avisos gerados: {error_summary['warnings']}")
            print(f"   - Log salvo em: pipeline_errors.log")

        print("="*80)

        return noticias_coletadas, noticias_selecionadas

    except Exception as e:
        error_handler.handle_error(
            e, "Pipeline principal", continue_execution=False)
        print("ERRO CRÍTICO: Pipeline interrompido.")
        print("Verifique a conectividade com a internet e as dependências instaladas.")
        return None, None


def main():
    """Função principal do orquestrador"""
    print("Iniciando Pipeline Inteligente de Notícias de Marketing...")
    print("Nova arquitetura: SQLite + Cache em Memória")

    # Executar pipeline
    noticias_coletadas, noticias_selecionadas = executar_pipeline()

    if noticias_coletadas is not None:
        print("\nRESUMO FINAL:")
        print(f"   - Notícias coletadas: {len(noticias_coletadas)}")
        if noticias_selecionadas:
            print(f"   - Insights estratégicos: {len(noticias_selecionadas)}")
            print(
                "\nAs 15 notícias mais estratégicas foram selecionadas e salvas no banco principal!")
            print("Dados prontos para consumo pela API do site.")
        else:
            print("   - Insights estratégicos: Não disponíveis")
    else:
        print("\nPipeline não pôde ser executado completamente.")

    print("\nExecução finalizada.")


if __name__ == "__main__":
    main()
