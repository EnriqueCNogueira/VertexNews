# CONFIGURAÇÃO DA API
"""
Configurações centralizadas para a API REST do Vertex News.
"""

import os
from typing import Dict, Any


class APIConfig:
    """Classe para configurações da API"""

    def __init__(self):
        """Inicializa as configurações da API"""

        # Configurações do servidor
        self.HOST = os.getenv("API_HOST", "0.0.0.0")
        self.PORT = int(os.getenv("API_PORT", "8000"))
        self.DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

        # Configurações de CORS
        self.CORS_ORIGINS = [
            "http://localhost:3000",  # React dev server
            "http://localhost:8080",  # Vue dev server
            "http://localhost:5173",  # Vite dev server
            "https://vertexnews.com",  # Produção
        ]

        # Configurações de cache
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutos
        self.CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))

        # Configurações de rate limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(
            os.getenv("RATE_LIMIT_WINDOW", "60"))  # 1 minuto

        # Configurações de dados
        self.DEFAULT_LIMIT = 15
        self.MAX_LIMIT = 50

        # Configurações de validação
        self.VALIDATION_CONFIG = {
            "strict_mode": True,
            "require_all_fields": False,
            "max_title_length": 500,
            "max_resumo_length": 2000,
        }

        # Configurações de logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def get_cors_origins(self) -> list:
        """Retorna as origens permitidas para CORS"""
        return self.CORS_ORIGINS.copy()

    def get_cache_config(self) -> Dict[str, Any]:
        """Retorna configurações de cache"""
        return {
            "ttl": self.CACHE_TTL,
            "max_size": self.CACHE_MAX_SIZE
        }

    def get_rate_limit_config(self) -> Dict[str, int]:
        """Retorna configurações de rate limiting"""
        return {
            "requests": self.RATE_LIMIT_REQUESTS,
            "window": self.RATE_LIMIT_WINDOW
        }

    def get_validation_config(self) -> Dict[str, Any]:
        """Retorna configurações de validação"""
        return self.VALIDATION_CONFIG.copy()


# Instância global da configuração
api_config = APIConfig()


def get_api_config() -> APIConfig:
    """
    Função de conveniência para obter a instância da configuração

    Returns:
        Instância de APIConfig
    """
    return api_config
