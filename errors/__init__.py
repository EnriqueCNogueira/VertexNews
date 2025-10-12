# MÓDULO DE TRATAMENTO DE ERROS
"""
Sistema de tratamento de erros centralizado para o pipeline
"""

from .error_handler import PipelineErrorHandler, error_handler

__all__ = ['PipelineErrorHandler', 'error_handler']
