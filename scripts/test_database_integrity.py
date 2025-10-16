# TESTE RÁPIDO DE INTEGRIDADE DO BANCO DE DADOS
"""
Teste rápido para verificar a integridade dos bancos de dados antes da execução do pipeline.
Este teste deve ser executado sempre antes do pipeline para evitar corrupção de dados.
"""

from database.db_manager import get_db_manager
from database.config import get_db_config
import sqlite3
import os
import sys
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DatabaseIntegrityTest:
    """Classe para testes rápidos de integridade do banco de dados"""

    def __init__(self):
        """Inicializa o teste de integridade"""
        self.config = get_db_config()
        self.db_manager = get_db_manager()
        self.errors = []
        self.warnings = []

    def run_all_tests(self) -> Tuple[bool, List[str], List[str]]:
        """
        Executa todos os testes de integridade

        Returns:
            Tupla (sucesso, erros, avisos)
        """
        print("[INFO] Iniciando testes de integridade do banco de dados...")

        # Limpar resultados anteriores
        self.errors = []
        self.warnings = []

        # Executar testes
        self._test_database_files()
        self._test_database_structure()
        self._test_database_connectivity()
        self._test_data_integrity()
        self._test_performance_indicators()

        # Determinar sucesso
        success = len(self.errors) == 0

        # Exibir resultados
        self._display_results()

        return success, self.errors, self.warnings

    def _test_database_files(self):
        """Testa a existência e integridade dos arquivos de banco"""
        print("  [INFO] Verificando arquivos de banco...")

        aux_path = self.config.get_aux_db_path()
        main_path = self.config.get_main_db_path()

        # Verificar existência dos arquivos
        if not os.path.exists(aux_path):
            self.warnings.append(f"Banco auxiliar não encontrado: {aux_path}")
        else:
            # Verificar se o arquivo não está corrompido
            if not self._is_valid_sqlite_file(aux_path):
                self.errors.append(f"Banco auxiliar corrompido: {aux_path}")
            else:
                size_mb = os.path.getsize(aux_path) / (1024 * 1024)
                if size_mb > 100:  # Aviso se muito grande
                    self.warnings.append(
                        f"Banco auxiliar muito grande: {size_mb:.2f} MB")

        if not os.path.exists(main_path):
            self.warnings.append(
                f"Banco principal não encontrado: {main_path}")
        else:
            if not self._is_valid_sqlite_file(main_path):
                self.errors.append(f"Banco principal corrompido: {main_path}")
            else:
                size_mb = os.path.getsize(main_path) / (1024 * 1024)
                if size_mb > 500:  # Aviso se muito grande
                    self.warnings.append(
                        f"Banco principal muito grande: {size_mb:.2f} MB")

    def _test_database_structure(self):
        """Testa a estrutura das tabelas"""
        print("  [INFO] Verificando estrutura das tabelas...")

        # Testar banco auxiliar
        if os.path.exists(self.config.get_aux_db_path()):
            self._test_table_structure(self.config.get_aux_db_path(), 'noticias_aux', [
                'id', 'titulo', 'link', 'imagem', 'fonte', 'resumo',
                'cluster', 'data_coleta', 'data_processamento', 'status'
            ])

        # Testar banco principal
        if os.path.exists(self.config.get_main_db_path()):
            self._test_table_structure(self.config.get_main_db_path(), 'noticias', [
                'id', 'titulo', 'link', 'imagem', 'resumo', 'cluster',
                'fonte', 'score', 'status', 'data_selecao'
            ])

    def _test_database_connectivity(self):
        """Testa a conectividade com os bancos"""
        print("  [INFO] Testando conectividade...")

        # Testar banco auxiliar
        if os.path.exists(self.config.get_aux_db_path()):
            if not self._test_connection(self.config.get_aux_db_path()):
                self.errors.append("Falha na conexão com banco auxiliar")

        # Testar banco principal
        if os.path.exists(self.config.get_main_db_path()):
            if not self._test_connection(self.config.get_main_db_path()):
                self.errors.append("Falha na conexão com banco principal")

    def _test_data_integrity(self):
        """Testa a integridade dos dados"""
        print("  [INFO] Verificando integridade dos dados...")

        # Testar banco auxiliar
        if os.path.exists(self.config.get_aux_db_path()):
            self._test_data_consistency(
                self.config.get_aux_db_path(), 'noticias_aux')

        # Testar banco principal
        if os.path.exists(self.config.get_main_db_path()):
            self._test_data_consistency(
                self.config.get_main_db_path(), 'noticias')

    def _test_performance_indicators(self):
        """Testa indicadores de performance"""
        print("  [INFO] Verificando indicadores de performance...")

        # Testar banco auxiliar
        if os.path.exists(self.config.get_aux_db_path()):
            self._test_performance(
                self.config.get_aux_db_path(), 'noticias_aux')

        # Testar banco principal
        if os.path.exists(self.config.get_main_db_path()):
            self._test_performance(self.config.get_main_db_path(), 'noticias')

    def _is_valid_sqlite_file(self, file_path: str) -> bool:
        """Verifica se um arquivo é um SQLite válido"""
        try:
            with sqlite3.connect(file_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return len(tables) > 0
        except Exception:
            return False

    def _test_table_structure(self, db_path: str, table_name: str, expected_columns: List[str]):
        """Testa a estrutura de uma tabela"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Verificar se a tabela existe
                cursor.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if not cursor.fetchone():
                    self.errors.append(
                        f"Tabela '{table_name}' não encontrada em {db_path}")
                    return

                # Verificar colunas
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [row[1] for row in cursor.fetchall()]

                missing_columns = set(expected_columns) - set(columns)
                if missing_columns:
                    self.errors.append(
                        f"Colunas ausentes em {table_name}: {missing_columns}")

                # Verificar índices
                cursor.execute(f"PRAGMA index_list({table_name});")
                indexes = cursor.fetchall()
                if len(indexes) < 3:  # Esperamos pelo menos alguns índices
                    self.warnings.append(
                        f"Poucos índices em {table_name}: {len(indexes)} encontrados")

        except Exception as e:
            self.errors.append(
                f"Erro ao verificar estrutura de {table_name}: {str(e)}")

    def _test_connection(self, db_path: str) -> bool:
        """Testa a conexão com um banco"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1;")
                return cursor.fetchone()[0] == 1
        except Exception:
            return False

    def _test_data_consistency(self, db_path: str, table_name: str):
        """Testa a consistência dos dados"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Verificar registros órfãos ou inconsistentes
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                total_records = cursor.fetchone()[0]

                if total_records == 0:
                    self.warnings.append(f"Tabela {table_name} está vazia")
                    return

                # Verificar links duplicados
                cursor.execute(
                    f"SELECT link, COUNT(*) FROM {table_name} GROUP BY link HAVING COUNT(*) > 1;")
                duplicates = cursor.fetchall()
                if duplicates:
                    self.errors.append(
                        f"Links duplicados em {table_name}: {len(duplicates)} encontrados")

                # Verificar registros com campos obrigatórios vazios
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE titulo IS NULL OR titulo = '';")
                empty_titles = cursor.fetchone()[0]
                if empty_titles > 0:
                    self.errors.append(
                        f"Títulos vazios em {table_name}: {empty_titles}")

                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE link IS NULL OR link = '';")
                empty_links = cursor.fetchone()[0]
                if empty_links > 0:
                    self.errors.append(
                        f"Links vazios em {table_name}: {empty_links}")

                # Verificar datas inválidas
                if 'data_coleta' in [row[1] for row in cursor.execute(f"PRAGMA table_info({table_name});").fetchall()]:
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {table_name} WHERE data_coleta IS NULL;")
                    null_dates = cursor.fetchone()[0]
                    if null_dates > 0:
                        self.warnings.append(
                            f"Datas de coleta nulas em {table_name}: {null_dates}")

        except Exception as e:
            self.errors.append(
                f"Erro ao verificar consistência de {table_name}: {str(e)}")

    def _test_performance(self, db_path: str, table_name: str):
        """Testa indicadores de performance"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Verificar se os índices estão sendo usados
                cursor.execute(f"PRAGMA index_list({table_name});")
                indexes = cursor.fetchall()

                if len(indexes) == 0:
                    self.warnings.append(
                        f"Nenhum índice encontrado em {table_name}")

                # Verificar estatísticas de uso dos índices
                cursor.execute(f"PRAGMA index_info({table_name});")
                index_info = cursor.fetchall()

                # Verificar tamanho da tabela
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                record_count = cursor.fetchone()[0]

                if record_count > 10000:
                    self.warnings.append(
                        f"Tabela {table_name} muito grande: {record_count} registros")

        except Exception as e:
            self.warnings.append(
                f"Erro ao verificar performance de {table_name}: {str(e)}")

    def _display_results(self):
        """Exibe os resultados dos testes"""
        print(f"\n[RESULTADO] Resultados dos testes de integridade:")
        print(f"   [OK] Sucesso: {len(self.errors) == 0}")
        print(f"   [ERRO] Erros: {len(self.errors)}")
        print(f"   [AVISO] Avisos: {len(self.warnings)}")

        if self.errors:
            print(f"\n[ERRO] Erros encontrados:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")

        if self.warnings:
            print(f"\n[AVISO] Avisos:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        if not self.errors:
            if not self.warnings:
                print(
                    f"\n[SUCESSO] Todos os testes passaram! Banco de dados íntegro.")
            else:
                print(
                    f"\n[SUCESSO] Testes passaram com avisos. Banco de dados funcional.")


def run_database_integrity_test() -> bool:
    """
    Função principal para executar o teste de integridade

    Returns:
        True se todos os testes passaram, False caso contrário
    """
    test = DatabaseIntegrityTest()
    success, errors, warnings = test.run_all_tests()

    if success:
        if warnings:
            print(f"\n[SUCESSO] Teste de integridade concluído com avisos!")
            print(f"   Pipeline pode ser executado. Verifique os avisos acima.")
        else:
            print(f"\n[SUCESSO] Teste de integridade concluído com sucesso!")
            print(f"   Pipeline pode ser executado com segurança.")
    else:
        print(f"\n[ERRO] Teste de integridade falhou!")
        print(f"   Corrija os erros antes de executar o pipeline.")

    return success


if __name__ == "__main__":
    # Executar teste quando chamado diretamente
    success = run_database_integrity_test()
    sys.exit(0 if success else 1)
