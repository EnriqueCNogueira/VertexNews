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
from database import initialize_databases, cleanup_auxiliary_database, get_db_manager
from database.text_cache import get_text_cache
from errors.error_handler import error_handler
from scripts.test_database_integrity import run_database_integrity_test
import sys
import os
import time


def main(skip_integrity_test: bool = False):
    """
    Função principal que executa o pipeline completo de notícias

    Args:
        skip_integrity_test: Se True, pula o teste de integridade do banco de dados
    """
    start_time = time.time()

    # Teste de integridade do banco de dados (obrigatório antes do pipeline)
    if not skip_integrity_test:
        print("=" * 60)
        print("[TEST] EXECUTANDO TESTE DE INTEGRIDADE DO BANCO DE DADOS")
        print("=" * 60)

        if not run_database_integrity_test():
            print(
                "\n[ERRO] ERRO CRÍTICO: Teste de integridade do banco de dados falhou!")
            print("   O pipeline não pode ser executado com segurança.")
            print("   Corrija os problemas do banco de dados antes de continuar.")
            return None, None

        print("\n[OK] Teste de integridade do banco de dados passou!")
        print("   Pipeline pode ser executado com segurança.")
        print("=" * 60)
    else:
        print(
            "[AVISO] Teste de integridade do banco de dados pulado por solicitação do usuário.")

    # Inicializar sistema
    if not _initialize_system():
        return None, None

    # Obter instâncias dos gerenciadores
    db_manager = get_db_manager()
    text_cache = get_text_cache()

    # Executar etapas do pipeline
    pipeline_steps = [
        ("Coleta de notícias", _execute_data_collection),
        ("Extração de conteúdo", _execute_text_extraction),
        ("Sumarização de textos", _execute_summarization),
        ("Clusterização de notícias", _execute_clustering),
        ("Análise de clusters", _execute_cluster_interpretation),
        ("Seleção de 15 notícias", _execute_strategic_selection),
        ("Limpeza de dados temporários", _execute_cleanup),
    ]

    for step_name, step_function in pipeline_steps:
        print(f"\n[INICIANDO] {step_name}...")

        try:
            result = step_function(db_manager, text_cache)
            if result is False:  # Falha crítica
                return None, None
            print(f"{step_name.split()[0].capitalize()} concluída")
        except Exception as e:
            if not error_handler.handle_error(e, step_name):
                return None, None

    # Retornar dados finais
    try:
        stats_finais = db_manager.get_statistics()
        api_data = db_manager.get_api_data(limit=15)

        # Calcular tempo total
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)

        print(f"\nPipeline concluído com sucesso!")
        print(f"Tempo total de execução: {minutes}m {seconds}s")

        return api_data, stats_finais
    except Exception as e:
        error_handler.handle_error(e, "Relatório final")
        return None, None


def _initialize_system() -> bool:
    """Inicializa o sistema verificando bancos de dados"""
    if not os.path.exists("noticias.db") or not os.path.exists("noticias_aux.db"):
        print("[INICIANDO] Inicializando bancos de dados...")
        if not initialize_databases():
            print("ERRO: Falha na inicialização dos bancos de dados.")
            return False
        print("Bancos de dados inicializados")
    return True


def _execute_data_collection(db_manager, text_cache) -> bool:
    """Executa coleta de dados"""
    try:
        noticias_coletadas = coletar_noticias()
        if not error_handler.validate_data(noticias_coletadas, 'not_empty', "Coleta de notícias"):
            print("ERRO: Nenhuma notícia foi coletada.")
            return False
        return True
    except Exception as e:
        error_handler.handle_error(
            e, "Coleta de notícias", continue_execution=False)
        return False


def _execute_text_extraction(db_manager, text_cache) -> bool:
    """Executa extração de texto"""
    try:
        textos_para_sumarizar, indices_validos, stats = extrair_textos_noticias()
        if not error_handler.validate_data(textos_para_sumarizar, 'not_empty', "Extração de textos"):
            print("ERRO: Nenhum texto foi extraído com sucesso.")
            return False
        return True
    except Exception as e:
        error_handler.handle_error(e, "Extração de textos")
        return False


def _execute_summarization(db_manager, text_cache) -> bool:
    """Executa sumarização"""
    try:
        textos_sumarizados = sumarizar_textos()
        if textos_sumarizados == 0:
            print("ERRO: Falha na sumarização dos textos.")
            return False
        return True
    except Exception as e:
        error_handler.handle_error(e, "Sumarização com IA")
        return False


def _execute_clustering(db_manager, text_cache) -> bool:
    """Executa clusterização"""
    try:
        kmeans, vectorizer, noticias_processadas = clusterizar_noticias()
        if kmeans is None:
            print("ERRO: Falha na clusterização.")
            return False

        # Armazenar modelos para uso posterior
        text_cache.store_models(kmeans, vectorizer)
        return True
    except Exception as e:
        error_handler.handle_error(e, "Clusterização")
        return False


def _execute_cluster_interpretation(db_manager, text_cache) -> bool:
    """Executa interpretação de clusters"""
    try:
        # Recuperar modelos do cache
        kmeans, vectorizer = text_cache.get_models()
        if kmeans is None or vectorizer is None:
            print(
                "AVISO: Modelos de clusterização não encontrados. Pulando interpretação.")
            return True

        interpretar_clusters(kmeans, vectorizer)
        return True
    except Exception as e:
        error_handler.handle_error(e, "Interpretação de clusters")
        return True  # Não é crítico


def _execute_strategic_selection(db_manager, text_cache) -> bool:
    """Executa seleção estratégica"""
    try:
        selecionar_noticias_estrategicas(top_n=15)
        return True
    except Exception as e:
        error_handler.handle_error(e, "Seleção estratégica")
        return True  # Não é crítico


def _execute_cleanup(db_manager, text_cache) -> bool:
    """Executa limpeza do banco auxiliar"""
    try:
        cleanup_success = cleanup_auxiliary_database()
        return True
    except Exception as e:
        error_handler.handle_error(e, "Limpeza do banco auxiliar")
        return True  # Não é crítico


def run_pipeline(skip_integrity_test: bool = False):
    """
    Executa o pipeline completo e exibe resultados

    Args:
        skip_integrity_test: Se True, pula o teste de integridade do banco de dados
    """
    try:
        # Executar pipeline
        api_data, stats = main(skip_integrity_test)

        if api_data is None:
            print("\n[ERRO] Pipeline falhou. Verifique os logs acima.")
            return False

        return True

    except KeyboardInterrupt:
        print("\n\n[INFO] Pipeline interrompido pelo usuário.")
        return False
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha inesperada no pipeline: {e}")
        error_handler.handle_error(e, "Pipeline principal")
        return False


if __name__ == "__main__":
    # Verificar argumentos da linha de comando
    skip_integrity_test = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("PIPELINE DE NOTÍCIAS DE MARKETING")
            print("Uso: python main.py")
            print("Opções:")
            print("  --help                    Exibe esta ajuda")
            print("  --test                    Executa pipeline em modo de teste")
            print(
                "  --skip-integrity-test     Pula o teste de integridade do banco de dados")
            print(
                "  --force                   Força execução mesmo com problemas de integridade")
            sys.exit(0)
        elif sys.argv[1] == "--test":
            print("[MODO TESTE] Executando pipeline com configurações de teste...")
            # Aqui poderiam ser aplicadas configurações de teste
        elif sys.argv[1] == "--skip-integrity-test":
            print(
                "[AVISO] Modo de execução sem teste de integridade do banco de dados.")
            skip_integrity_test = True
        elif sys.argv[1] == "--force":
            print("[AVISO] Modo de execução forçada - pulando teste de integridade.")
            skip_integrity_test = True

    # Executar pipeline
    success = run_pipeline(skip_integrity_test)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
