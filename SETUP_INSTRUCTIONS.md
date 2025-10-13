# 🚀 Instruções de Configuração - Pipeline Inteligente de Notícias

## 📋 Pré-requisitos

- **Python 3.8+** instalado no sistema
- **Git** para clonar o repositório
- **Conexão com internet** estável (para download de modelos de IA)
- **Mínimo 4GB RAM** recomendado (para processamento de IA)

## 🔧 Configuração Passo a Passo

### 1. Clonar o Repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd Vertex
```

### 2. Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Baixar recursos do NLTK (necessário para processamento de texto)
python -c "import nltk; nltk.download('stopwords')"
```

### 4. Verificar Instalação
```bash
# Testar se tudo está funcionando
python -c "import torch, transformers, sklearn, pandas, requests, bs4; print('✅ Todas as dependências instaladas com sucesso!')"
```

## 🎯 Primeira Execução

### Executar o Pipeline Completo
```bash
python main.py
```

**⚠️ IMPORTANTE:** Na primeira execução, o sistema irá:
- Baixar o modelo de IA `unicamp-dl/ptt5-small-portuguese-vocab` (pode demorar alguns minutos)
- Criar os bancos de dados SQLite automaticamente
- Processar notícias de 4 fontes diferentes

### O que Esperar na Primeira Execução
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
Coletando de: Meio & Mensagem
Coletando de: Mundo do Marketing  
Coletando de: Exame
Coletando de: GKPB
✅ 45 notícias coletadas no total

[ETAPA 2] EXTRAÇÃO DE TEXTO
--------------------------------------------------
Iniciando extração de conteúdo completo para 45 artigos...
✅ 38 textos extraídos com sucesso

[ETAPA 3] SUMARIZAÇÃO COM IA
--------------------------------------------------
Carregando modelo de IA... (Aguarde - primeira vez pode demorar)
Modelo carregado com sucesso!
✅ 38 textos sumarizados com sucesso

[ETAPA 4] CLUSTERIZAÇÃO E ANÁLISE
--------------------------------------------------
Executando vetorização TF-IDF...
Executando algoritmo K-Means...
✅ 38 clusters salvos no banco auxiliar

[ETAPA 5] INTERPRETAÇÃO DOS CLUSTERS
--------------------------------------------------
Extraindo palavras-chave principais de cada cluster...
✅ Clusters interpretados com sucesso

[ETAPA 6] SELEÇÃO ESTRATÉGICA
--------------------------------------------------
Calculando scores de relevância estratégica...
AS 15 NOTÍCIAS MAIS ESTRATÉGICAS PARA CONTEÚDO DE INSTAGRAM
🔄 Transferindo 15 notícias para o banco principal...

[ETAPA 7] LIMPEZA DO BANCO AUXILIAR
--------------------------------------------------
✅ Banco auxiliar limpo e removido com sucesso

================================================================================
           PIPELINE EXECUTADO COM SUCESSO!
================================================================================
Total de notícias no banco principal: 15
Notícias selecionadas nesta execução: 15
================================================================================
```

## 📁 Estrutura de Arquivos Após Execução

Após a primeira execução bem-sucedida, você terá:

```
Vertex/
├── 📁 database/              # ✅ Código fonte (versionado)
├── 📁 pipeline/              # ✅ Código fonte (versionado)  
├── 📁 config/                 # ✅ Código fonte (versionado)
├── 📁 errors/                 # ✅ Código fonte (versionado)
├── 📄 main.py                 # ✅ Código fonte (versionado)
├── 📄 requirements.txt        # ✅ Código fonte (versionado)
├── 📄 README.md               # ✅ Código fonte (versionado)
├── 📄 SETUP_INSTRUCTIONS.md   # ✅ Código fonte (versionado)
├── 🗄️ noticias.db            # 📊 Banco principal (criado automaticamente)
├── 📁 venv/                   # 🚫 Ambiente virtual (não versionado)
└── 📁 __pycache__/           # 🚫 Cache Python (não versionado)
```

## 🔍 Verificação de Funcionamento

### Verificar Bancos de Dados
```bash
# Verificar se os bancos foram criados
ls -la *.db
# Deve mostrar: noticias.db (banco principal)
```

### Verificar Logs de Erro
```bash
# Se houver problemas, verificar logs
cat errors/pipeline_errors.log
```

### Testar Componentes Individuais
```bash
# Testar inicialização dos bancos
python database/init_db.py

# Testar coleta de notícias
python -c "from pipeline.collectors import coletar_noticias; print(len(coletar_noticias()))"
```

## ⚠️ Solução de Problemas Comuns

### Erro: "ModuleNotFoundError"
```bash
# Verificar se o ambiente virtual está ativado
which python  # Deve apontar para venv/bin/python (Linux/Mac) ou venv\Scripts\python.exe (Windows)

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro: "CUDA out of memory" ou problemas com GPU
```bash
# O sistema funciona perfeitamente apenas com CPU
# Se aparecer erro de CUDA, pode ignorar - o modelo usará CPU automaticamente
```

### Erro: "Connection timeout" ou problemas de rede
```bash
# Verificar conexão com internet
ping google.com

# Alguns sites podem ter proteção anti-bot - isso é normal
# O sistema continuará com as outras fontes
```

### Erro: "NLTK data not found"
```bash
# Baixar dados do NLTK
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Erro: "Model download failed"
```bash
# Limpar cache e tentar novamente
rm -rf ~/.cache/huggingface/
python main.py
```

## 🚀 Execuções Subsequentes

Após a primeira execução bem-sucedida:

1. **O modelo de IA já estará em cache** - execuções futuras serão mais rápidas
2. **Os bancos de dados persistirão** - notícias acumularão ao longo do tempo
3. **Execute quando quiser** - `python main.py` processará novas notícias

## 📊 Monitoramento

### Verificar Estatísticas
```bash
# Ver quantas notícias estão no banco principal
python -c "
from database.main_operations import get_main_operations
ops = get_main_operations()
stats = ops.get_statistics()
print(f'Total: {stats[\"total\"]} notícias')
print(f'Últimos 7 dias: {stats[\"ultimos_7_dias\"]} notícias')
"
```

### Verificar Últimas Notícias
```bash
# Ver as últimas notícias selecionadas
python -c "
from database.main_operations import get_main_operations
ops = get_main_operations()
noticias = ops.get_recent_news(limit=5)
for n in noticias:
    print(f'📰 {n[\"titulo\"]}')
    print(f'🔗 {n[\"link\"]}')
    print('---')
"
```

## 🎯 Próximos Passos

Após configurar o ambiente:

1. **Execute o pipeline regularmente** para manter dados atualizados
2. **Monitore os logs** para identificar problemas
3. **Considere automatizar** com cron jobs (Linux/Mac) ou Task Scheduler (Windows)
4. **Desenvolva a API REST** usando os dados do banco principal
5. **Crie o frontend web** para visualizar as notícias

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** em `errors/pipeline_errors.log`
2. **Consulte o README.md** para documentação completa
3. **Execute os testes individuais** para identificar o componente com problema
4. **Verifique a conectividade** com as fontes de notícias

---

**✅ Configuração Completa!** Seu ambiente está pronto para processar notícias de marketing com IA.
