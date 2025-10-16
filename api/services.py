# SERVIÇOS DE DADOS PARA API
"""
Serviços para integração com banco de dados e lógica de negócio da API.
"""

from .cache import get_api_cache
from .models import NewsItem, NewsResponse, ErrorResponse
from database.db_manager import get_db_manager
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Adicionar o diretório raiz ao path para importar módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NewsService:
    """Serviço para operações com notícias"""

    def __init__(self):
        """Inicializa o serviço"""
        self.db_manager = get_db_manager()
        self.cache = get_api_cache()

    def get_posted_news(self, limit: int = 15) -> NewsResponse:
        """
        Obtém notícias com status 'postada' do banco de dados

        Args:
            limit: Número máximo de notícias a retornar

        Returns:
            NewsResponse com as notícias encontradas
        """
        try:
            # Verificar cache primeiro
            cache_key = f"posted_news_{limit}"
            cached_data = self.cache.get(cache_key)

            if cached_data:
                cached_data["cached"] = True
                return NewsResponse(**cached_data)

            # Buscar no banco de dados
            raw_news = self._get_posted_news_from_db(limit)

            if not raw_news:
                return NewsResponse(
                    success=True,
                    data=[],
                    total=0,
                    cached=False,
                    timestamp=datetime.now().isoformat()
                )

            # Converter para modelos Pydantic
            news_items = []
            for news in raw_news:
                try:
                    news_item = NewsItem(**news)
                    news_items.append(news_item)
                except Exception as e:
                    print(
                        f"[AVISO] Erro ao converter notícia {news.get('id', 'unknown')}: {e}")
                    continue

            # Preparar resposta
            response_data = {
                "success": True,
                "data": [item.dict() for item in news_items],
                "total": len(news_items),
                "cached": False,
                "timestamp": datetime.now().isoformat()
            }

            # Armazenar no cache
            self.cache.set(cache_key, response_data)

            return NewsResponse(**response_data)

        except Exception as e:
            print(f"[ERRO] Erro ao obter notícias postadas: {e}")
            return NewsResponse(
                success=False,
                data=[],
                total=0,
                cached=False,
                timestamp=datetime.now().isoformat()
            )

    def _get_posted_news_from_db(self, limit: int) -> List[Dict[str, Any]]:
        """
        Busca notícias com status 'postada' diretamente do banco

        Args:
            limit: Número máximo de notícias

        Returns:
            Lista de dicionários com dados das notícias
        """
        try:
            # Usar a função existente do db_manager que já filtra por status
            all_news = self.db_manager.get_api_data(
                limit=limit * 2)  # Buscar mais para filtrar

            # Filtrar apenas notícias com status 'postada'
            posted_news = [
                news for news in all_news
                if news.get('status') == 'postada'
            ]

            # Limitar ao número solicitado
            return posted_news[:limit]

        except Exception as e:
            print(f"[ERRO] Erro ao buscar notícias do banco: {e}")
            return []

    def get_news_by_id(self, news_id: int) -> Optional[NewsItem]:
        """
        Obtém uma notícia específica por ID

        Args:
            news_id: ID da notícia

        Returns:
            NewsItem ou None se não encontrada
        """
        try:
            # Verificar cache
            cache_key = f"news_{news_id}"
            cached_data = self.cache.get(cache_key)

            if cached_data:
                return NewsItem(**cached_data)

            # Buscar no banco
            news = self._get_news_by_id_from_db(news_id)

            if not news:
                return None

            # Converter para modelo
            news_item = NewsItem(**news)

            # Armazenar no cache
            self.cache.set(cache_key, news_item.dict())

            return news_item

        except Exception as e:
            print(f"[ERRO] Erro ao obter notícia por ID {news_id}: {e}")
            return None

    def _get_news_by_id_from_db(self, news_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca uma notícia específica no banco de dados

        Args:
            news_id: ID da notícia

        Returns:
            Dicionário com dados da notícia ou None
        """
        try:
            import sqlite3

            main_db_path = self.db_manager.main_db_path

            with sqlite3.connect(main_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, fonte, 
                           data_selecao, score, status
                    FROM noticias
                    WHERE id = ? AND status = 'postada'
                """, (news_id,))

                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None

        except Exception as e:
            print(f"[ERRO] Erro ao buscar notícia no banco: {e}")
            return None

    def clear_cache(self) -> bool:
        """
        Limpa o cache da API

        Returns:
            True se limpo com sucesso
        """
        try:
            self.cache.clear()
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao limpar cache: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache

        Returns:
            Dicionário com estatísticas do cache
        """
        return self.cache.get_stats()


# Instância global do serviço
news_service = NewsService()


def get_news_service() -> NewsService:
    """
    Função de conveniência para obter a instância do serviço

    Returns:
        Instância de NewsService
    """
    return news_service
