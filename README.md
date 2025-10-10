# Pipeline Inteligente de Notícias de Marketing

Sistema automatizado para coletar, processar, analisar e apresentar notícias relevantes do setor de marketing digital, transformando dados brutos da web em insights estratégicos para criação de conteúdo.

## 🎯 Objetivo

Transformar um grande volume de informações dispersas na web em insights valiosos, facilitando a criação de conteúdo estratégico para redes sociais, como o Instagram.

## 🏗️ Arquitetura do Sistema

O pipeline é composto por 6 etapas principais:

1. **Coleta de Dados** - Web scraping de múltiplas fontes
2. **Extração de Texto** - Obtenção do conteúdo completo dos artigos
3. **Sumarização** - Geração de resumos usando IA (Transformers)
4. **Clusterização** - Agrupamento de notícias por temas similares
5. **Interpretação** - Análise e rotulagem dos clusters
6. **Seleção Estratégica** - Escolha das 15 notícias mais relevantes

## 📁 Estrutura do Projeto

```
Vertex/
├── main.py                 # Orquestrador principal
├── requirements.txt        # Dependências do projeto
├── README.md              # Documentação
├── prompt.txt             # Definição original do projeto
└── pipeline/              # Módulos organizados por etapa
    ├── __init__.py
    ├── config.py          # Configurações globais
    ├── collectors.py      # Coleta de dados (scrapers)
    ├── extractor.py       # Extração de texto
    ├── summarizer.py      # Sumarização com IA
    ├── clustering.py      # Vetorização e clusterização
    └── selector.py        # Seleção estratégica
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Conexão com a internet
- 4GB de RAM mínimo (recomendado 8GB para melhor performance)

### Instalação

1. **Clone ou baixe o projeto**
   ```bash
   # Se usando git
   git clone <url-do-repositorio>
   cd Vertex
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Como Usar

### Execução Completa

```bash
python main.py
```

### Saída Esperada

O sistema irá:
- Coletar notícias de múltiplas fontes
- Extrair conteúdo completo dos artigos
- Gerar resumos usando IA
- Agrupar notícias por temas
- Selecionar as 15 mais estratégicas
- Exibir relatório final com estatísticas

## 📊 Fontes de Dados

O sistema coleta notícias das seguintes fontes:

- **Mundo do Marketing** - mundodomarketing.com.br
- **Meio & Mensagem** - meioemensagem.com.br
- **Exame** - exame.com/marketing

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

### Modelo de IA
- **unicamp-dl/ptt5-small-portuguese-vocab** - Modelo especializado em português para sumarização

## ⚙️ Configurações

As configurações principais estão no arquivo `pipeline/config.py`:

- **Headers HTTP** - Para requisições web
- **Parâmetros do modelo** - Configurações de sumarização
- **Configurações de clusterização** - Número de clusters, features, etc.
- **Palavras-chave de relevância** - Critérios para seleção estratégica

## 📈 Critérios de Seleção

As notícias são pontuadas baseadas em:

1. **Marcas Grandes** (peso 5) - Google, Apple, Microsoft, etc.
2. **Campanhas e Ações** (peso 3) - Lançamentos, parcerias, eventos
3. **Palavras de Impacto** (peso 2) - Inovação, tendências, futuro

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

## 📝 Exemplo de Saída

```
================================================================================
           PIPELINE INTELIGENTE DE NOTÍCIAS DE MARKETING
================================================================================
Sistema automatizado para transformar dados brutos da web em insights estratégicos
================================================================================

🔄 ETAPA 1: COLETA DE DADOS
--------------------------------------------------
Executando scraper para: Mundo do Marketing
 -> Concluído. 15 notícias novas adicionadas.

✅ 45 notícias coletadas com sucesso!

🔄 ETAPA 2: EXTRAÇÃO DE TEXTO
--------------------------------------------------
--- Iniciando extração de texto para 45 artigos ---
[1/45] Tentando extrair de 'Mundo do Marketing'...
...

🎉 PIPELINE EXECUTADO COM SUCESSO!
📊 Total de notícias processadas: 45
📈 Notícias com resumos válidos: 38
🎯 Notícias estratégicas selecionadas: 15
```

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
