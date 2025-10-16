# APLICAÇÃO PRINCIPAL DA API
"""
Aplicação FastAPI principal para o Vertex News.
Configuração completa com CORS, middleware e tratamento de erros.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
from datetime import datetime

from .config import get_api_config
from .routes import router
from .models import ErrorResponse


# Configuração da API
api_config = get_api_config()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, api_config.LOG_LEVEL),
    format=api_config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Vertex News API",
    description="API REST para fornecer dados das notícias de marketing para o frontend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições"""
    start_time = time.time()

    # Log da requisição
    logger.info(f"Iniciando requisição: {request.method} {request.url}")

    # Processar requisição
    response = await call_next(request)

    # Calcular tempo de processamento
    process_time = time.time() - start_time

    # Log da resposta
    logger.info(
        f"Requisição concluída: {request.method} {request.url} "
        f"- Status: {response.status_code} - Tempo: {process_time:.3f}s"
    )

    # Adicionar header de tempo de processamento
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Middleware para tratamento de erros
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    logger.error(f"Erro HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação"""
    logger.error(f"Erro de validação: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            error="Erro de validação dos parâmetros da requisição",
            error_code="VALIDATION_ERROR",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler para exceções do Starlette"""
    logger.error(f"Erro Starlette {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=str(exc.detail),
            error_code=f"STARLETTE_{exc.status_code}",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Erro inesperado: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Erro interno do servidor",
            error_code="INTERNAL_ERROR",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


# Incluir rotas
app.include_router(router, prefix="/api/v1", tags=["news"])


# Rota raiz
@app.get("/")
async def root():
    """
    Rota raiz da API

    Returns:
        Informações básicas da API
    """
    return {
        "message": "Vertex News API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health",
        "timestamp": datetime.now().isoformat()
    }


# Evento de startup
@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    logger.info("Iniciando Vertex News API...")
    logger.info(
        f"Configurações: Host={api_config.HOST}, Port={api_config.PORT}")
    logger.info(f"CORS Origins: {api_config.get_cors_origins()}")
    logger.info("API iniciada com sucesso!")


# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação"""
    logger.info("Encerrando Vertex News API...")


# Função para executar a aplicação
def run_app():
    """Executa a aplicação FastAPI"""
    import uvicorn

    uvicorn.run(
        "api.app:app",
        host=api_config.HOST,
        port=api_config.PORT,
        reload=api_config.DEBUG,
        log_level=api_config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    run_app()
