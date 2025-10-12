# MÓDULO DE BANCO DE DADOS
"""
Operações de banco de dados para o pipeline de notícias
"""

from .init_db import DatabaseInitializer, db_initializer, initialize_databases
from .aux_operations import AuxiliaryOperations, aux_ops, get_aux_operations
from .main_operations import MainOperations, main_ops, get_main_operations
from .cleanup import DatabaseCleanup, cleanup_manager, cleanup_auxiliary_database
from .text_cache import NewsTextCache, text_cache, get_text_cache

__all__ = [
    'DatabaseInitializer', 'db_initializer', 'initialize_databases',
    'AuxiliaryOperations', 'aux_ops', 'get_aux_operations',
    'MainOperations', 'main_ops', 'get_main_operations',
    'DatabaseCleanup', 'cleanup_manager', 'cleanup_auxiliary_database',
    'NewsTextCache', 'text_cache', 'get_text_cache'
]
