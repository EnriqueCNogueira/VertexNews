# CACHE EM MEMÓRIA PARA TEXTOS COMPLETOS
"""
Módulo responsável pelo cache em memória dos textos completos das notícias
durante o processamento do pipeline
"""

from typing import Dict, Optional, List
import threading


class NewsTextCache:
    """Classe para cache em memória dos textos completos das notícias"""

    def __init__(self):
        """Inicializa o cache em memória"""
        self._cache: Dict[str, str] = {}
        self._lock = threading.Lock()

    def store_text(self, link: str, text: str) -> bool:
        """
        Armazena texto completo no cache

        Args:
            link: Link da notícia (chave única)
            text: Texto completo da notícia

        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        try:
            with self._lock:
                self._cache[link] = text
                return True
        except Exception as e:
            print(f"❌ Erro ao armazenar texto no cache: {e}")
            return False

    def get_text(self, link: str) -> Optional[str]:
        """
        Obtém texto completo do cache

        Args:
            link: Link da notícia

        Returns:
            Texto completo ou None se não encontrado
        """
        try:
            with self._lock:
                return self._cache.get(link)
        except Exception as e:
            print(f"❌ Erro ao obter texto do cache: {e}")
            return None

    def remove_text(self, link: str) -> bool:
        """
        Remove texto do cache

        Args:
            link: Link da notícia

        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            with self._lock:
                if link in self._cache:
                    del self._cache[link]
                    return True
                return False
        except Exception as e:
            print(f"❌ Erro ao remover texto do cache: {e}")
            return False

    def get_all_texts(self) -> Dict[str, str]:
        """
        Obtém todos os textos do cache

        Returns:
            Dicionário com todos os textos armazenados
        """
        try:
            with self._lock:
                return self._cache.copy()
        except Exception as e:
            print(f"❌ Erro ao obter todos os textos: {e}")
            return {}

    def get_texts_for_summarization(self) -> List[tuple]:
        """
        Obtém textos formatados para sumarização

        Returns:
            Lista de tuplas (link, texto_formatado)
        """
        try:
            with self._lock:
                texts = []
                for link, text in self._cache.items():
                    formatted_text = f"summarize: {text}"
                    texts.append((link, formatted_text))
                return texts
        except Exception as e:
            print(f"❌ Erro ao obter textos para sumarização: {e}")
            return []

    def clear_cache(self) -> bool:
        """
        Limpa todo o cache

        Returns:
            True se limpo com sucesso, False caso contrário
        """
        try:
            with self._lock:
                self._cache.clear()
                return True
        except Exception as e:
            print(f"❌ Erro ao limpar cache: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Obtém estatísticas do cache

        Returns:
            Dicionário com estatísticas
        """
        try:
            with self._lock:
                total_texts = len(self._cache)
                total_chars = sum(len(text) for text in self._cache.values())

                return {
                    'total_texts': total_texts,
                    'total_characters': total_chars,
                    'average_length': total_chars // total_texts if total_texts > 0 else 0
                }
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas do cache: {e}")
            return {}

    def has_text(self, link: str) -> bool:
        """
        Verifica se um texto existe no cache

        Args:
            link: Link da notícia

        Returns:
            True se existe, False caso contrário
        """
        try:
            with self._lock:
                return link in self._cache
        except Exception as e:
            print(f"❌ Erro ao verificar existência no cache: {e}")
            return False


# Instância global do cache
text_cache = NewsTextCache()


def get_text_cache() -> NewsTextCache:
    """
    Função de conveniência para obter a instância do cache

    Returns:
        Instância de NewsTextCache
    """
    return text_cache


def store_news_text(link: str, text: str) -> bool:
    """
    Função de conveniência para armazenar texto no cache

    Args:
        link: Link da notícia
        text: Texto completo

    Returns:
        True se armazenado com sucesso
    """
    return text_cache.store_text(link, text)


def get_news_text(link: str) -> Optional[str]:
    """
    Função de conveniência para obter texto do cache

    Args:
        link: Link da notícia

    Returns:
        Texto completo ou None
    """
    return text_cache.get_text(link)


def clear_news_cache() -> bool:
    """
    Função de conveniência para limpar o cache

    Returns:
        True se limpo com sucesso
    """
    return text_cache.clear_cache()


if __name__ == "__main__":
    # Teste do cache
    cache = get_text_cache()

    # Teste de armazenamento
    success = cache.store_text("https://teste.com", "Texto de teste")
    print(f"Armazenamento: {'Sucesso' if success else 'Falha'}")

    # Teste de obtenção
    text = cache.get_text("https://teste.com")
    print(f"Texto obtido: {text}")

    # Teste de estatísticas
    stats = cache.get_cache_stats()
    print(f"Estatísticas: {stats}")

    # Teste de limpeza
    cleared = cache.clear_cache()
    print(f"Cache limpo: {'Sucesso' if cleared else 'Falha'}")
