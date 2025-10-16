# MODELOS DE DADOS PARA API
"""
Modelos Pydantic para validação e serialização de dados da API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class NewsItem(BaseModel):
    """Modelo para uma notícia individual"""

    id: int = Field(..., description="ID único da notícia")
    titulo: str = Field(..., description="Título da notícia", max_length=500)
    link: str = Field(..., description="URL da notícia", max_length=1000)
    imagem: Optional[str] = Field(
        None, description="URL da imagem", max_length=1000)
    resumo: str = Field(..., description="Resumo da notícia", max_length=2000)
    fonte: str = Field(..., description="Fonte da notícia", max_length=100)
    score: Optional[float] = Field(
        None, description="Score de relevância", ge=0.0)
    cluster: int = Field(..., description="Número do cluster", ge=0)
    data_selecao: str = Field(..., description="Data de seleção da notícia")
    status: str = Field(..., description="Status da notícia")

    @validator('titulo')
    def validate_titulo(cls, v):
        if not v or not v.strip():
            raise ValueError('Título não pode ser vazio')
        return v.strip()

    @validator('link')
    def validate_link(cls, v):
        if not v or not v.strip():
            raise ValueError('Link não pode ser vazio')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Link deve começar com http:// ou https://')
        return v.strip()

    @validator('resumo')
    def validate_resumo(cls, v):
        if not v or not v.strip():
            raise ValueError('Resumo não pode ser vazio')
        return v.strip()

    @validator('fonte')
    def validate_fonte(cls, v):
        if not v or not v.strip():
            raise ValueError('Fonte não pode ser vazia')
        return v.strip()

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['postada', 'arquivada']
        if v not in allowed_statuses:
            raise ValueError(
                f'Status deve ser um dos seguintes: {allowed_statuses}')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NewsResponse(BaseModel):
    """Modelo para resposta da API com lista de notícias"""

    success: bool = Field(
        True, description="Indica se a requisição foi bem-sucedida")
    data: List[NewsItem] = Field(..., description="Lista de notícias")
    total: int = Field(..., description="Total de notícias retornadas")
    cached: bool = Field(
        False, description="Indica se os dados vieram do cache")
    timestamp: str = Field(..., description="Timestamp da resposta")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Modelo para resposta de erro da API"""

    success: bool = Field(
        False, description="Indica se a requisição foi bem-sucedida")
    error: str = Field(..., description="Mensagem de erro")
    error_code: str = Field(..., description="Código do erro")
    timestamp: str = Field(..., description="Timestamp do erro")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """Modelo para resposta de health check"""

    status: str = Field(..., description="Status da API")
    version: str = Field(..., description="Versão da API")
    database_connected: bool = Field(...,
                                     description="Status da conexão com banco")
    cache_stats: dict = Field(..., description="Estatísticas do cache")
    timestamp: str = Field(..., description="Timestamp da verificação")
