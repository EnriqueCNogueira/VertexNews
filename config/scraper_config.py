# CONFIGURAÇÃO DE SCRAPERS
"""
Configuração centralizada para URLs e seletores CSS dos scrapers
Elimina configurações hardcoded espalhadas pelo código
"""

# URLs base dos sites
SCRAPER_URLS = {
    'exame': {
        'base_url': 'https://exame.com',
        'category_url': 'https://exame.com/marketing/',
        'name': 'Exame'
    },
    'gkpb': {
        'base_url': 'https://gkpb.com.br',
        'category_url': 'https://gkpb.com.br/category/publicidade/',
        'name': 'GKPB'
    },
    'meio_mensagem': {
        'base_url': 'https://www.meioemensagem.com.br',
        'category_url': 'https://www.meioemensagem.com.br/marketing',
        'name': 'Meio e Mensagem'
    },
    'mundo_marketing': {
        'base_url': 'https://mundodomarketing.com.br',
        'category_url': 'https://mundodomarketing.com.br/noticias',
        'name': 'Mundo do Marketing'
    }
}

# Seletores CSS específicos por site
SCRAPER_SELECTORS = {
    'exame': {
        'articles': 'div.sc-dbce6183-0',
        'title': 'h3.headline-extra-small a',
        'category': 'span.label-small',
        'image': 'img.placeholder-image',
        'date': 'time, span[class*="date"], div[class*="date"]'
    },
    'gkpb': {
        'articles': 'div[class*="tdb_module_header"][class*="td_module_wrap"]',
        'title': 'h3[class*="entry-title"] a',
        'category': 'span[class*="category"], a[class*="category"], span[class*="tag"]',
        'image': 'div[data-bg]',
        'date': 'time, span[class*="date"], div[class*="date"]'
    },
    'meio_mensagem': {
        'articles': 'article',
        'title': 'h2.titulo, h3.titulo',
        'category': 'span.categoria',
        'image': 'img[data-src], img[src]',
        'date': 'span'
    },
    'mundo_marketing': {
        'articles': 'div.framer-11hhesp-container',
        'title': 'h2.framer-text',
        'category': 'p.framer-text',
        'image': 'div[data-framer-name="Image"] img',
        'date': 'time, span[class*="date"], div[class*="date"]'
    }
}

# Configurações de timeout e retry
SCRAPER_CONFIG = {
    'timeout': 5,
    'retry_attempts': 3,
    'delay_between_requests': 0.5,
    'max_articles_per_site': 50
}
