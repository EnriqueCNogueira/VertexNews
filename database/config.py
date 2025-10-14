# CONFIGURAÇÃO CENTRALIZADA DOS BANCOS DE DADOS
"""
Módulo responsável pela configuração centralizada dos caminhos e parâmetros
dos bancos de dados SQLite do pipeline de notícias de marketing
"""

import os
from typing import Dict, Any


class DatabaseConfig:
    """Classe para configuração centralizada dos bancos de dados"""

    def __init__(self):
        """Inicializa as configurações dos bancos de dados"""
        # Caminhos dos bancos de dados
        self.AUX_DB_PATH = "noticias_aux.db"
        self.MAIN_DB_PATH = "noticias.db"

        # Configurações de performance do SQLite
        self.SQLITE_PRAGMAS = {
            'journal_mode': 'OFF',
            'synchronous': 'OFF',
            'temp_store': 'MEMORY',
            'cache_size': 10000,
            'page_size': 4096
        }

        # Configurações de validação de dados
        self.VALIDATION_CONFIG = {
            'validate_on_insert': True,
            'validate_on_update': True,
            'strict_mode': False,
            'max_title_length': 500,
            'max_resumo_length': 2000,
            'max_link_length': 1000,
            'allowed_sources': ['Exame', 'GKPB', 'Meio e Mensagem', 'Mundo do Marketing', 'Desconhecida']
        }

        # Configurações de índices
        self.INDEX_CONFIG = {
            'create_indexes': True,
            'indexes': {
                'noticias_aux': [
                    'idx_noticias_aux_link',
                    'idx_noticias_aux_cluster',
                    'idx_noticias_aux_fonte',
                    'idx_noticias_aux_data'
                ],
                'noticias': [
                    'idx_noticias_link',
                    'idx_noticias_data_selecao',
                    'idx_noticias_cluster',
                    'idx_noticias_fonte',
                    'idx_noticias_score'
                ]
            }
        }

    def get_aux_db_path(self) -> str:
        """
        Retorna o caminho do banco de dados auxiliar

        Returns:
            Caminho do banco auxiliar
        """
        return self.AUX_DB_PATH

    def get_main_db_path(self) -> str:
        """
        Retorna o caminho do banco de dados principal

        Returns:
            Caminho do banco principal
        """
        return self.MAIN_DB_PATH

    def get_sqlite_pragmas(self) -> Dict[str, str]:
        """
        Retorna as configurações de performance do SQLite

        Returns:
            Dicionário com as configurações PRAGMA
        """
        return self.SQLITE_PRAGMAS.copy()

    def get_validation_config(self) -> Dict[str, Any]:
        """
        Retorna as configurações de validação

        Returns:
            Dicionário com as configurações de validação
        """
        return self.VALIDATION_CONFIG.copy()

    def get_index_config(self) -> Dict[str, Any]:
        """
        Retorna as configurações de índices

        Returns:
            Dicionário com as configurações de índices
        """
        return self.INDEX_CONFIG.copy()

    def set_custom_paths(self, aux_path: str = None, main_path: str = None):
        """
        Define caminhos customizados para os bancos de dados

        Args:
            aux_path: Caminho customizado para o banco auxiliar
            main_path: Caminho customizado para o banco principal
        """
        if aux_path:
            self.AUX_DB_PATH = aux_path
        if main_path:
            self.MAIN_DB_PATH = main_path

    def validate_paths(self) -> bool:
        """
        Valida se os caminhos dos bancos são válidos

        Returns:
            True se os caminhos são válidos, False caso contrário
        """
        try:
            # Verificar se os diretórios pai existem
            aux_dir = os.path.dirname(os.path.abspath(self.AUX_DB_PATH))
            main_dir = os.path.dirname(os.path.abspath(self.MAIN_DB_PATH))

            if not os.path.exists(aux_dir):
                os.makedirs(aux_dir, exist_ok=True)

            if not os.path.exists(main_dir):
                os.makedirs(main_dir, exist_ok=True)

            return True
        except Exception as e:
            print(f"Erro ao validar caminhos dos bancos: {e}")
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre os bancos de dados

        Returns:
            Dicionário com informações dos bancos
        """
        info = {
            'aux_db': {
                'path': self.AUX_DB_PATH,
                'exists': os.path.exists(self.AUX_DB_PATH),
                'size_mb': 0
            },
            'main_db': {
                'path': self.MAIN_DB_PATH,
                'exists': os.path.exists(self.MAIN_DB_PATH),
                'size_mb': 0
            },
            'config': {
                'validation_enabled': self.VALIDATION_CONFIG['validate_on_insert'],
                'indexes_enabled': self.INDEX_CONFIG['create_indexes']
            }
        }

        # Calcular tamanhos dos arquivos
        if info['aux_db']['exists']:
            info['aux_db']['size_mb'] = os.path.getsize(
                self.AUX_DB_PATH) / (1024 * 1024)

        if info['main_db']['exists']:
            info['main_db']['size_mb'] = os.path.getsize(
                self.MAIN_DB_PATH) / (1024 * 1024)

        return info


# Instância global da configuração
db_config = DatabaseConfig()


def get_db_config() -> DatabaseConfig:
    """
    Função de conveniência para obter a instância da configuração

    Returns:
        Instância de DatabaseConfig
    """
    return db_config


def set_database_paths(aux_path: str = None, main_path: str = None):
    """
    Função de conveniência para definir caminhos customizados

    Args:
        aux_path: Caminho customizado para o banco auxiliar
        main_path: Caminho customizado para o banco principal
    """
    db_config.set_custom_paths(aux_path, main_path)


if __name__ == "__main__":
    # Teste da configuração
    config = get_db_config()

    print("Configuração dos Bancos de Dados:")
    print(f"Banco auxiliar: {config.get_aux_db_path()}")
    print(f"Banco principal: {config.get_main_db_path()}")
    print(f"Pragmas SQLite: {config.get_sqlite_pragmas()}")
    print(
        f"Validação de dados: {config.get_validation_config()['validate_on_insert']}")

    # Validar caminhos
    if config.validate_paths():
        print("Caminhos dos bancos validados com sucesso")
    else:
        print("Erro na validação dos caminhos")

    # Informações dos bancos
    info = config.get_database_info()
    print(f"\nInformações dos bancos:")
    print(
        f"Auxiliar: {info['aux_db']['path']} ({info['aux_db']['size_mb']:.2f} MB)")
    print(
        f"Principal: {info['main_db']['path']} ({info['main_db']['size_mb']:.2f} MB)")
