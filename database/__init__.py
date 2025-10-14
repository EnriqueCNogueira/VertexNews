# MÓDULO DE BANCO DE DADOS REFATORADO
"""
Sistema de banco de dados simplificado para o pipeline de notícias.
Estrutura refatorada com 3 módulos essenciais mantendo funcionalidade completa.
"""

from .db_manager import DatabaseManager, db_manager, get_db_manager
from .config import DatabaseConfig, db_config, get_db_config
from .validator import DataValidator, data_validator, get_validator
from .text_cache import NewsTextCache, text_cache, get_text_cache

__all__ = [
    # Gerenciador principal unificado
    'DatabaseManager', 'db_manager', 'get_db_manager',

    # Configuração centralizada
    'DatabaseConfig', 'db_config', 'get_db_config',

    # Validação simplificada
    'DataValidator', 'data_validator', 'get_validator',

    # Cache em memória
    'NewsTextCache', 'text_cache', 'get_text_cache'
]

# Funções de conveniência para compatibilidade


def initialize_databases() -> bool:
    """
    Função de conveniência para inicializar os bancos de dados

    Returns:
        True se inicializado com sucesso
    """
    return db_manager.initialize_databases()


def cleanup_auxiliary_database() -> bool:
    """
    Função de conveniência para limpar o banco auxiliar

    Returns:
        True se limpo com sucesso
    """
    return db_manager.clear_auxiliary_database()
