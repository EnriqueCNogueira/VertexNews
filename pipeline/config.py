# ETAPA 1: CONFIGURAÇÃO INICIAL
"""
Configurações globais do pipeline de notícias de marketing
"""

# Headers para requisições HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Configurações do modelo de sumarização
MODEL_CONFIG = {
    'model_name': "unicamp-dl/ptt5-small-portuguese-vocab",
    'max_length': 1024,
    'max_new_tokens': 150,
    'min_new_tokens': 40,
    'num_beams': 4,
    'early_stopping': True
}

# Configurações de clusterização
CLUSTERING_CONFIG = {
    'n_clusters': 5,
    'random_state': 42,
    'n_init': 10,
    'max_features': 1000
}

# Configurações de relevância
RELEVANCE_KEYWORDS = {
    'marcas_grandes': {
        'termos': [
            'google', 'apple', 'microsoft', 'amazon', 'samsung', 'coca-cola',
            'toyota', 'mercedes-benz', 'mcdonald\'s', 'disney', 'nike',
            'instagram', 'facebook', 'meta', 'itaú', 'bradesco', 'nubank',
            'banco do brasil', 'petrobras', 'vale', 'magalu', 'natura',
            'ambev', 'havaianas', 'renner', 'netflix', 'spotify', 'uber'
        ],
        'peso': 5
    },
    'campanhas_e_acoes': {
        'termos': [
            'campanha', 'lançamento', 'lança', 'anuncia', 'patrocina',
            'parceria', 'colaboração', 'ativação', 'evento', 'marketing',
            'publicidade', 'anúncio', 'branding', 'influenciadores'
        ],
        'peso': 3
    },
    'palavras_de_impacto': {
        'termos': [
            'revoluciona', 'transforma', 'inova', 'impacto', 'crescimento',
            'tendência', 'futuro', 'inteligência artificial', 'ia', 'novo'
        ],
        'peso': 2
    }
}

# Mapeamento de rótulos para clusters
MAPA_ROTULOS = {
    0: "Tema A (Ex: IA e Automação)",
    1: "Tema B (Ex: SEO e Buscas)",
    2: "Tema C (Ex: Marketing de Influência)",
    3: "Tema D (Ex: E-commerce e Varejo)",
    4: "Tema E (Ex: Branding e Campanhas)"
}
