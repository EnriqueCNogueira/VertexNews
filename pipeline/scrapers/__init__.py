# MÓDULO DE SCRAPERS
"""
Scrapers individuais para diferentes fontes de notícias
"""

from .mundo_do_marketing import scrape_mundo_do_marketing
from .meio_e_mensagem import scrape_meio_e_mensagem
from .exame import scrape_exame
from .gkpb import scrape_gkpb

__all__ = [
    'scrape_mundo_do_marketing',
    'scrape_meio_e_mensagem',
    'scrape_exame',
    'scrape_gkpb'
]
