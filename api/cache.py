# CACHE EM MEMÓRIA PARA API
"""
Sistema de cache em memória para otimizar performance da API.
"""

import time
from typing import Dict, Any, Optional, List
from threading import Lock
from .config import get_api_config


class APICache:
    """Cache em memória thread-safe para a API"""

    def __init__(self):
        """Inicializa o cache"""
        self.config = get_api_config()
        cache_config = self.config.get_cache_config()

        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._max_size = cache_config["max_size"]
        self._ttl = cache_config["ttl"]

    def _is_expired(self, timestamp: float) -> bool:
        """Verifica se um item do cache expirou"""
        return time.time() - timestamp > self._ttl

    def _cleanup_expired(self):
        """Remove itens expirados do cache"""
        current_time = time.time()
        expired_keys = []

        for key, data in self._cache.items():
            if current_time - data["timestamp"] > self._ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

    def _evict_oldest(self):
        """Remove o item mais antigo quando o cache está cheio"""
        if not self._cache:
            return

        oldest_key = min(self._cache.keys(),
                         key=lambda k: self._cache[k]["timestamp"])
        del self._cache[oldest_key]

    def get(self, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache

        Args:
            key: Chave do cache

        Returns:
            Valor armazenado ou None se não encontrado/expirado
        """
        with self._lock:
            if key not in self._cache:
                return None

            data = self._cache[key]

            # Verificar se expirou
            if self._is_expired(data["timestamp"]):
                del self._cache[key]
                return None

            return data["value"]

    def set(self, key: str, value: Any) -> None:
        """
        Armazena um valor no cache

        Args:
            key: Chave do cache
            value: Valor a ser armazenado
        """
        with self._lock:
            # Limpar itens expirados primeiro
            self._cleanup_expired()

            # Se o cache está cheio, remover o mais antigo
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_oldest()

            # Armazenar o novo item
            self._cache[key] = {
                "value": value,
                "timestamp": time.time()
            }

    def delete(self, key: str) -> bool:
        """
        Remove um item do cache

        Args:
            key: Chave do cache

        Returns:
            True se o item foi removido, False se não existia
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache

        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            current_time = time.time()
            expired_count = sum(1 for data in self._cache.values()
                                if self._is_expired(data["timestamp"]))

            return {
                "total_items": len(self._cache),
                "expired_items": expired_count,
                "active_items": len(self._cache) - expired_count,
                "max_size": self._max_size,
                "ttl": self._ttl
            }


# Instância global do cache
api_cache = APICache()


def get_api_cache() -> APICache:
    """
    Função de conveniência para obter a instância do cache

    Returns:
        Instância de APICache
    """
    return api_cache
