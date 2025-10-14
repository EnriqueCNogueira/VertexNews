# UTILITÁRIOS UNIFICADOS PARA SCRAPING
"""
Módulo unificado com funções utilitárias para scraping
Substitui os arquivos utils/ criados anteriormente
"""

import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def detect_source_from_url(url: str) -> str:
    """
    Detecta a fonte baseada na URL da notícia

    Args:
        url: URL da notícia

    Returns:
        Nome da fonte detectada
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Mapeamento de domínios para fontes
        domain_mapping = {
            'exame.com': 'Exame',
            'gkpb.com.br': 'GKPB',
            'meioemensagem.com.br': 'Meio e Mensagem',
            'mundodomarketing.com.br': 'Mundo do Marketing'
        }

        # Verificar mapeamento direto
        for domain_key, source in domain_mapping.items():
            if domain_key in domain:
                return source

        return 'Desconhecida'

    except Exception:
        return 'Desconhecida'


def extract_image_url(article_element, base_url: str = "") -> str:
    """
    Extrai URL da imagem de um elemento de artigo com múltiplos fallbacks

    Args:
        article_element: Elemento BeautifulSoup do artigo
        base_url: URL base para converter URLs relativas

    Returns:
        URL da imagem ou string vazia se não encontrada
    """
    if not article_element:
        return ""

    # Lista de métodos de extração em ordem de prioridade
    extraction_methods = [
        _extract_from_data_bg,
        _extract_from_img_src,
        _extract_from_data_src,
        _extract_from_background_style,
        _extract_from_srcset,
        _extract_from_placeholder_image
    ]

    for method in extraction_methods:
        try:
            image_url = method(article_element)
            if image_url:
                # Converter URL relativa para absoluta se necessário
                if base_url and not image_url.startswith(('http://', 'https://')):
                    image_url = urljoin(base_url, image_url)
                return image_url
        except Exception:
            continue

    return ""


def validate_url(url: str) -> bool:
    """
    Valida se uma string é uma URL válida

    Args:
        url: String para validar

    Returns:
        True se é URL válida, False caso contrário
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url.strip())
        return bool(parsed.scheme and parsed.netloc and
                    parsed.scheme in ['http', 'https'])
    except Exception:
        return False


def extract_content_meio_mensagem(soup: BeautifulSoup) -> str:
    """
    Extrai conteúdo específico para o site Meio e Mensagem
    Corrige o problema de extração que estava falhando

    Args:
        soup: BeautifulSoup object da página

    Returns:
        Texto extraído ou None se falhar
    """
    try:
        # Método 1: Procurar por div com classe 'content' ou 'post-content'
        content_selectors = [
            'div.content',
            'div.post-content',
            'article .content',
            'div.entry-content',
            'div.article-content',
            'main .content',
            'div.texto'
        ]

        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                paragraphs = content_div.find_all('p')
                if paragraphs:
                    texto = ' '.join([p.get_text(strip=True)
                                     for p in paragraphs])
                    if len(texto.strip()) > 100:
                        return texto

        # Método 2: Procurar por qualquer div com texto longo
        all_divs = soup.find_all('div')
        for div in all_divs:
            paragraphs = div.find_all('p')
            if len(paragraphs) >= 3:  # Pelo menos 3 parágrafos
                texto = ' '.join([p.get_text(strip=True) for p in paragraphs])
                if len(texto.strip()) > 200:  # Texto substancial
                    return texto

        # Método 3: Fallback - extrair todos os parágrafos da página
        all_paragraphs = soup.find_all('p')
        if len(all_paragraphs) >= 2:
            texto = ' '.join([p.get_text(strip=True) for p in all_paragraphs])
            if len(texto.strip()) > 150:
                return texto

        # Método 4: Último recurso - extrair texto visível
        visible_text = soup.get_text(separator=' ', strip=True)
        if len(visible_text) > 300:
            return visible_text

    except Exception as e:
        print(f"[AVISO] Erro na extração Meio e Mensagem: {e}")

    return None


# Funções auxiliares para extração de imagem
def _extract_from_data_bg(element) -> str:
    """Extrai imagem de atributo data-bg"""
    img_divs = element.find_all(attrs={'data-bg': True})
    if img_divs:
        return img_divs[0].get('data-bg', '')
    return ""


def _extract_from_img_src(element) -> str:
    """Extrai imagem de tag img src"""
    img_tag = element.find('img')
    if img_tag:
        src = img_tag.get('src', '')
        # Pular placeholders
        if src and not src.startswith('data:image/gif'):
            return src
    return ""


def _extract_from_data_src(element) -> str:
    """Extrai imagem de atributo data-src"""
    img_tag = element.find('img')
    if img_tag:
        return img_tag.get('data-src', '')
    return ""


def _extract_from_background_style(element) -> str:
    """Extrai imagem de background-image no style"""
    # Procurar em divs com classes relacionadas a thumb/image
    for class_name in ['thumb', 'image', 'photo', 'picture']:
        divs = element.find_all(
            'div', {'class': lambda x: x and class_name in x.lower()})
        for div in divs:
            style = div.get('style', '')
            if 'background-image' in style:
                match = re.search(r'url\("?([^"]+)"?\)', style)
                if match:
                    return match.group(1)
    return ""


def _extract_from_srcset(element) -> str:
    """Extrai imagem de srcset"""
    picture = element.find('picture')
    if picture:
        source_tag = picture.find('source')
        if source_tag:
            srcset = source_tag.get('srcset', '')
            if srcset:
                # Pegar a primeira URL do srcset
                return srcset.split(',')[0].strip().split(' ')[0]
    return ""


def _extract_from_placeholder_image(element) -> str:
    """Extrai imagem de tags img com classe placeholder-image"""
    img_tags = element.find_all('img', class_='placeholder-image')
    for img_tag in img_tags:
        src = img_tag.get('src', '')
        if src and not src.startswith('data:image/gif'):
            return src
    return ""
