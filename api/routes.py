# ROTAS DA API REST
"""
Definição das rotas e endpoints da API REST para Vertex News.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

from .models import NewsResponse, ErrorResponse, HealthResponse
from .services import get_news_service, NewsService
from .config import get_api_config


# Router principal da API
router = APIRouter()

# Configuração da API
api_config = get_api_config()


@router.get("/news", response_model=NewsResponse)
async def get_news(
    limit: int = Query(
        default=api_config.DEFAULT_LIMIT,
        ge=1,
        le=api_config.MAX_LIMIT,
        description="Número de notícias a retornar (máximo 50)"
    ),
    service: NewsService = Depends(get_news_service)
):
    """
    Endpoint principal para obter notícias com status 'postada'.

    Retorna as 15 notícias mais recentes com status 'postada' do banco de dados.
    As notícias com status 'arquivada' são ignoradas.

    Args:
        limit: Número de notícias a retornar (padrão: 15, máximo: 50)
        service: Instância do serviço de notícias

    Returns:
        NewsResponse com lista de notícias

    Raises:
        HTTPException: Em caso de erro interno do servidor
    """
    try:
        response = service.get_posted_news(limit=limit)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao buscar notícias"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] Erro inesperado no endpoint /news: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news_by_id(
    news_id: int,
    service: NewsService = Depends(get_news_service)
):
    """
    Obtém uma notícia específica por ID.

    Args:
        news_id: ID da notícia
        service: Instância do serviço de notícias

    Returns:
        NewsResponse com a notícia encontrada

    Raises:
        HTTPException: Se a notícia não for encontrada ou erro interno
    """
    try:
        news_item = service.get_news_by_id(news_id)

        if not news_item:
            raise HTTPException(
                status_code=404,
                detail=f"Notícia com ID {news_id} não encontrada"
            )

        # Converter para formato de resposta
        response_data = {
            "success": True,
            "data": [news_item.dict()],
            "total": 1,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }

        return NewsResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] Erro inesperado no endpoint /news/{news_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(service: NewsService = Depends(get_news_service)):
    """
    Endpoint de health check para verificar status da API.

    Args:
        service: Instância do serviço de notícias

    Returns:
        HealthResponse com status da API e componentes
    """
    try:
        # Verificar conexão com banco de dados
        db_connected = True
        try:
            # Tentar uma operação simples no banco
            service.db_manager.get_statistics()
        except Exception:
            db_connected = False

        # Obter estatísticas do cache
        cache_stats = service.get_cache_stats()

        return HealthResponse(
            status="healthy" if db_connected else "degraded",
            version="1.0.0",
            database_connected=db_connected,
            cache_stats=cache_stats,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        print(f"[ERRO] Erro no health check: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            database_connected=False,
            cache_stats={},
            timestamp=datetime.now().isoformat()
        )


@router.post("/cache/clear")
async def clear_cache(service: NewsService = Depends(get_news_service)):
    """
    Limpa o cache da API.

    Args:
        service: Instância do serviço de notícias

    Returns:
        JSON com resultado da operação
    """
    try:
        success = service.clear_cache()

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Cache limpo com sucesso",
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Erro ao limpar cache"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] Erro ao limpar cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.get("/cache/stats")
async def get_cache_stats(service: NewsService = Depends(get_news_service)):
    """
    Obtém estatísticas do cache.

    Args:
        service: Instância do serviço de notícias

    Returns:
        JSON com estatísticas do cache
    """
    try:
        stats = service.get_cache_stats()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": stats,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        print(f"[ERRO] Erro ao obter estatísticas do cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )
