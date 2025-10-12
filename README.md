# Pipeline Inteligente de Notícias de Marketing

Sistema automatizado para coletar, processar, analisar e apresentar notícias relevantes do setor de marketing digital, utilizando banco de dados SQLite e cache em memória.

## 🏗️ Arquitetura Atual

### Sistema Implementado (v2.0)
- **Banco Auxiliar (noticias_aux.db)**: Temporário, usado durante o processamento
- **Banco Principal (noticias.db)**: Persistente, usado para armazenar notícias selecionadas
- **Cache em Memória**: Armazena textos completos durante o processamento
- **Pipeline de Processamento**: Sistema completo de coleta até seleção estratégica

### Fluxo de Dados Implementado
1. **Scraping** → Banco Auxiliar + Cache
2. **Extração de Texto** → Cache
3. **Sumarização** → Cache → Banco Auxiliar
4. **Clusterização** → Banco Auxiliar
5. **Seleção Estratégica** → Banco Auxiliar → Banco Principal
6. **Limpeza** → Remove Banco Auxiliar

## 📁 Estrutura do Projeto

```
Vertex/
├── database/                 # Módulos de banco de dados ✅
│   ├── init_db.py          # Inicialização dos bancos
│   ├── aux_operations.py   # Operações no banco auxiliar
│   ├── main_operations.py  # Operações no banco principal
│   ├── cleanup.py          # Limpeza do banco auxiliar
│   └── text_cache.py       # Cache em memória
├── pipeline/                # Módulos do pipeline ✅
│   ├── collectors.py       # Coleta de notícias
│   ├── extractor.py        # Extração de texto
│   ├── summarizer.py       # Sumarização com IA
│   ├── clustering.py       # Clusterização
│   ├── selector.py         # Seleção estratégica
│   └── scrapers/           # Scrapers específicos
│       ├── gkpb.py         # ✅ Completo (com imagens)
│       ├── exame.py        # ⚠️ Falta extração de imagens
│       ├── meio_e_mensagem.py # ⚠️ Falta extração de imagens
│       └── mundo_do_marketing.py # ⚠️ Falta extração de imagens
├── config/                  # Configurações ✅
│   └── config.py           # Configurações do sistema
├── errors/                  # Tratamento de erros ✅
│   └── error_handler.py    # Sistema de logs e erros
├── main.py                  # Orquestrador principal ✅
└── requirements.txt         # Dependências ✅
```

## 🚀 Como Usar

### 1. Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Baixar recursos do NLTK
python -c "import nltk; nltk.download('stopwords')"
```

### 2. Executar Pipeline
```bash
python main.py
```

O pipeline processará automaticamente:
- Coleta de notícias de 4 fontes
- Extração de textos completos
- Sumarização com IA
- Clusterização por temas
- Seleção das 15 mais estratégicas
- Armazenamento no banco principal

## 📊 Bancos de Dados

### Banco Auxiliar (noticias_aux.db)
- **Schema**: `id, titulo, link (UNIQUE), imagem, resumo, cluster`
- **Uso**: Processamento temporário durante execução
- **Limpeza**: Removido automaticamente ao final do pipeline

### Banco Principal (noticias.db)
- **Schema**: `id, titulo, link (UNIQUE), imagem, resumo, cluster, data_selecao`
- **Uso**: Dados persistentes das notícias selecionadas
- **Persistência**: Mantido entre execuções

## 🔄 Fluxo de Processamento Implementado

1. **Inicialização**: Criação dos bancos de dados
2. **Coleta**: Scraping de múltiplas fontes
3. **Extração**: Obtenção de textos completos
4. **Sumarização**: Geração de resumos com IA
5. **Clusterização**: Agrupamento por similaridade
6. **Seleção**: Escolha das 15 mais estratégicas
7. **Transferência**: Movimentação para banco principal
8. **Limpeza**: Remoção do banco auxiliar

## 🎯 Características Implementadas

- **Cache Inteligente**: Textos completos nunca salvos em banco
- **Processamento Incremental**: Suporte a execuções múltiplas
- **Segurança**: Proteção contra SQL Injection com consultas parametrizadas
- **Monitoramento**: Estatísticas e logs detalhados
- **Limpeza Automática**: Remoção de dados temporários
- **Tratamento de Erros**: Sistema robusto de tratamento de exceções

## 🛠️ Configuração

### Modelos de IA Implementados
- **Sumarização**: `unicamp-dl/ptt5-small-portuguese-vocab`
- **Clusterização**: K-Means com TF-IDF

### Fontes de Dados Implementadas
- **GKPB**: ✅ Completo (inclui extração de imagens)
- **Exame**: ⚠️ Básico (falta extração de imagens)
- **Meio & Mensagem**: ⚠️ Básico (falta extração de imagens)
- **Mundo do Marketing**: ⚠️ Básico (falta extração de imagens)

## 📈 Critérios de Seleção Implementados

As notícias são pontuadas baseadas em:

1. **Marcas Grandes** (peso 5) - Google, Apple, Microsoft, etc.
2. **Campanhas e Ações** (peso 3) - Lançamentos, parcerias, eventos
3. **Palavras de Impacto** (peso 2) - Inovação, tendências, futuro

## 🔧 Desenvolvimento

### Melhorias Pendentes

#### 1. Extração de Imagens
- **Exame**: Implementar extração de imagens dos artigos
- **Meio & Mensagem**: Implementar extração de imagens dos artigos
- **Mundo do Marketing**: Implementar extração de imagens dos artigos

#### 2. API REST (Não Implementada)
- Criar `api.py` com endpoints Flask
- Implementar endpoints:
  - `GET /api/news` - notícias mais recentes
  - `GET /api/news/search` - busca por termo
  - `GET /api/news/stats` - estatísticas
  - `GET /api/news/{id}` - notícia específica
  - `GET /api/health` - saúde da API

#### 3. Frontend Web (Não Implementado)
- Interface para visualização das notícias
- Dashboard com estatísticas
- Sistema de busca e filtros
- Exibição dos clusters e temas

### Adicionar Nova Fonte
1. Criar scraper em `pipeline/scrapers/`
2. Adicionar chamada em `pipeline/collectors.py`
3. Configurar seletores CSS em `pipeline/extractor.py`

### Modificar Critérios de Seleção
Editar `config/config.py` → `RELEVANCE_KEYWORDS`

### Ajustar Clusterização
Modificar `config/config.py` → `CLUSTERING_CONFIG`

## 🤖 Tecnologias Utilizadas

### Web Scraping
- `requests` - Requisições HTTP
- `BeautifulSoup` - Parsing de HTML

### Processamento de Dados
- `pandas` - Manipulação de DataFrames
- `numpy` - Operações numéricas

### Machine Learning & NLP
- `scikit-learn` - Clusterização K-Means e vetorização TF-IDF
- `nltk` - Processamento de linguagem natural
- `transformers` - Modelos de IA para sumarização
- `torch` - Framework de deep learning

### Banco de Dados
- `sqlite3` - Banco de dados SQLite

### Modelo de IA
- **unicamp-dl/ptt5-small-portuguese-vocab** - Modelo especializado em português para sumarização

## 📝 Notas Importantes

- Os textos completos das notícias **nunca** são salvos em banco de dados
- O banco auxiliar é **sempre** removido após o processamento
- Todas as operações de banco usam **consultas parametrizadas**
- O sistema suporta **execuções múltiplas** sem conflitos
- **API e Frontend ainda não foram implementados**

## 🔧 Solução de Problemas

### Erro de Conexão
- Verifique sua conexão com a internet
- Alguns sites podem ter proteção anti-bot

### Erro de Memória
- Feche outros programas
- Use um computador com mais RAM

### Erro de Dependências
- Certifique-se de que o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

### Modelo de IA não carrega
- Verifique se há espaço suficiente em disco
- O primeiro download pode demorar alguns minutos

### Banco de dados não encontrado
- Execute o pipeline primeiro: `python main.py`
- Verifique se os arquivos `noticias.db` e `noticias_aux.db` foram criados

## 📝 Exemplo de Saída

```
================================================================================
           PIPELINE INTELIGENTE DE NOTÍCIAS DE MARKETING
================================================================================
Sistema automatizado para transformar dados brutos da web em insights estratégicos
Arquitetura: SQLite + Cache em Memória
================================================================================

[INICIALIZAÇÃO] BANCOS DE DADOS SQLITE
--------------------------------------------------
✅ Banco auxiliar inicializado: noticias_aux.db
✅ Banco principal inicializado: noticias.db

[ETAPA 1] COLETA DE DADOS
--------------------------------------------------
Iniciando coleta de notícias de múltiplas fontes...
Dados serão salvos no banco auxiliar e cache em memória

Coletando de: Meio & Mensagem
Coletando de: Mundo do Marketing
Coletando de: Exame
Coletando de: GKPB

Coleta finalizada: 45 notícias coletadas no total
✅ 45 notícias salvas no banco auxiliar
📊 Cache em memória: 45 textos armazenados

[ETAPA 2] EXTRAÇÃO DE TEXTO
--------------------------------------------------
Iniciando extração de conteúdo completo para 45 artigos...
[1/45] Extraindo conteúdo de 'https://exemplo.com'...
...

[ETAPA 3] SUMARIZAÇÃO COM IA
--------------------------------------------------
INICIANDO SUMARIZAÇÃO COM INTELIGÊNCIA ARTIFICIAL
Dispositivo detectado: CPU
Carregando modelo de IA... (Aguarde)
Modelo carregado com sucesso!

Iniciando sumarização de 38 textos...
Progresso: 5/38 textos sumarizados. (Tempo: 45.2s)
...
✅ 38 textos sumarizados com sucesso

[ETAPA 4] CLUSTERIZAÇÃO E ANÁLISE
--------------------------------------------------
INICIANDO VETORIZAÇÃO E CLUSTERIZAÇÃO
Preparando clusterização de 38 notícias com resumos válidos...
Executando vetorização TF-IDF...
Executando algoritmo K-Means...
✅ 38 clusters salvos no banco auxiliar

[ETAPA 5] INTERPRETAÇÃO DOS CLUSTERS
--------------------------------------------------
INICIANDO INTERPRETAÇÃO E ANÁLISE DOS CLUSTERS
Extraindo palavras-chave principais de cada cluster...

Cluster 0:
  -> Palavras-chave: marketing, digital, campanha, marca, cliente
...

[ETAPA 6] SELEÇÃO ESTRATÉGICA
--------------------------------------------------
INICIANDO SELEÇÃO POR RELEVÂNCIA ESTRATÉGICA
Calculando scores de relevância estratégica...

--- Ranking de Relevância dos Clusters ---
Clusters ordenados pelo potencial de gerar conteúdo atrativo:
Cluster 2: 8.5 (média)
Cluster 0: 7.2 (média)
...

AS 15 NOTÍCIAS MAIS ESTRATÉGICAS PARA CONTEÚDO DE INSTAGRAM
Notícias selecionadas com base na menção a grandes marcas, campanhas e impacto.

🔄 Transferindo 15 notícias para o banco principal...
📊 Estatísticas da transferência:
   - Novas notícias: 12
   - Timestamps atualizados: 3
   - Falhas: 0

[ETAPA 7] LIMPEZA DO BANCO AUXILIAR
--------------------------------------------------
INICIANDO LIMPEZA COMPLETA DO BANCO AUXILIAR
✅ Banco auxiliar limpo: 45 registros removidos
✅ VACUUM executado no banco auxiliar
✅ Banco auxiliar removido: noticias_aux.db
✅ Limpeza completa executada com sucesso!

================================================================================
           PIPELINE EXECUTADO COM SUCESSO!
================================================================================
Total de notícias no banco principal: 127
Notícias selecionadas nesta execução: 15
Notícias dos últimos 7 dias: 23
================================================================================
```

## 📈 Status do Projeto

### ✅ Implementado (100%)
- Pipeline de processamento completo
- Sistema de banco de dados dual
- Cache inteligente em memória
- Sumarização com IA
- Clusterização e análise
- Seleção estratégica
- Tratamento de erros robusto
- Sistema de logs

### ⚠️ Parcialmente Implementado
- **Scrapers**: GKPB completo, outros precisam de extração de imagens

### ❌ Não Implementado
- **API REST**: Endpoints para acesso aos dados
- **Frontend Web**: Interface de usuário
- **Testes Automatizados**: Suite de testes
- **Deploy**: Configuração de produção

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Teste completamente
5. Submeta um pull request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Verifique a seção de solução de problemas
- Consulte a documentação dos módulos

---

**Desenvolvido com ❤️ para transformar dados em insights estratégicos**

**Status**: Pipeline completo ✅ | API pendente ❌ | Frontend pendente ❌