# Vertex News API

API REST desenvolvida com FastAPI para fornecer dados das notícias de marketing para o frontend.

## Instalação

As dependências estão no `requirements.txt` principal do projeto:

```bash
pip install -r requirements.txt
```

## Uso

### Executar a API
```bash
python api/manage.py run
```

### Testar a API
```bash
python api/manage.py test
```

### Verificar configuração
```bash
python api/manage.py setup
```

### Exemplo de uso
```bash
python api/manage.py example
```

## Endpoints

- **GET /api/v1/news**: Obtém notícias com status 'postada' (máximo 15 por padrão)
- **GET /api/v1/news/{id}**: Obtém uma notícia específica por ID
- **GET /api/v1/health**: Health check da API
- **POST /api/v1/cache/clear**: Limpa o cache da API
- **GET /api/v1/cache/stats**: Obtém estatísticas do cache

## Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuração

As configurações podem ser alteradas através de variáveis de ambiente:

- `API_HOST`: Host do servidor (padrão: 0.0.0.0)
- `API_PORT`: Porta do servidor (padrão: 8000)
- `API_DEBUG`: Modo debug (padrão: false)
- `CACHE_TTL`: TTL do cache em segundos (padrão: 300)
- `CACHE_MAX_SIZE`: Tamanho máximo do cache (padrão: 100)
- `LOG_LEVEL`: Nível de log (padrão: INFO)