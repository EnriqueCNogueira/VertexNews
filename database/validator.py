# VALIDAÇÃO SIMPLIFICADA DE DADOS
"""
Módulo responsável pela validação básica de segurança dos dados
antes de inserir nos bancos de dados do pipeline de notícias
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
from .config import get_db_config


class DataValidator:
    """Classe simplificada para validação de dados essenciais"""

    def __init__(self):
        """Inicializa o validador de dados"""
        self.config = get_db_config().get_validation_config()
        self.allowed_sources = self.config['allowed_sources']

    def validate_title(self, titulo: str) -> Tuple[bool, str]:
        """
        Valida o título da notícia

        Args:
            titulo: Título da notícia

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not titulo or not isinstance(titulo, str):
            return False, "Título é obrigatório e deve ser uma string"

        titulo = titulo.strip()

        if len(titulo) == 0:
            return False, "Título não pode estar vazio"

        if len(titulo) > self.config['max_title_length']:
            return False, f"Título muito longo (máximo {self.config['max_title_length']} caracteres)"

        # Verificar caracteres problemáticos básicos (apenas caracteres perigosos para HTML/XML)
        if re.search(r'[<>"\']', titulo):
            return False, "Título contém caracteres inválidos"

        return True, ""

    def validate_link(self, link: str) -> Tuple[bool, str]:
        """
        Valida o link da notícia

        Args:
            link: Link da notícia

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not link or not isinstance(link, str):
            return False, "Link é obrigatório e deve ser uma string"

        link = link.strip()

        if len(link) == 0:
            return False, "Link não pode estar vazio"

        if len(link) > self.config['max_link_length']:
            return False, f"Link muito longo (máximo {self.config['max_link_length']} caracteres)"

        # Validar formato de URL
        try:
            parsed = urlparse(link)
            if not parsed.scheme or not parsed.netloc:
                return False, "Link deve ser uma URL válida"

            if parsed.scheme not in ['http', 'https']:
                return False, "Link deve usar protocolo HTTP ou HTTPS"
        except Exception:
            return False, "Link deve ser uma URL válida"

        return True, ""

    def validate_image(self, imagem: Optional[str]) -> Tuple[bool, str]:
        """
        Valida a URL da imagem

        Args:
            imagem: URL da imagem (pode ser None)

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if imagem is None:
            return True, ""  # Imagem é opcional

        if not isinstance(imagem, str):
            return False, "Imagem deve ser uma string ou None"

        imagem = imagem.strip()

        if len(imagem) == 0:
            return True, ""  # String vazia é tratada como None

        if len(imagem) > self.config['max_link_length']:
            return False, f"URL da imagem muito longa (máximo {self.config['max_link_length']} caracteres)"

        # Validar formato de URL
        try:
            parsed = urlparse(imagem)
            if not parsed.scheme or not parsed.netloc:
                return False, "URL da imagem deve ser válida"

            if parsed.scheme not in ['http', 'https']:
                return False, "URL da imagem deve usar protocolo HTTP ou HTTPS"
        except Exception:
            return False, "URL da imagem deve ser válida"

        return True, ""

    def validate_resumo(self, resumo: str) -> Tuple[bool, str]:
        """
        Valida o resumo da notícia

        Args:
            resumo: Resumo da notícia

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not resumo or not isinstance(resumo, str):
            return False, "Resumo é obrigatório e deve ser uma string"

        resumo = resumo.strip()

        if len(resumo) == 0:
            return False, "Resumo não pode estar vazio"

        if len(resumo) > self.config['max_resumo_length']:
            return False, f"Resumo muito longo (máximo {self.config['max_resumo_length']} caracteres)"

        # Verificar se não é uma mensagem de erro de sumarização
        if resumo.startswith('Falha na sumarização'):
            return False, "Resumo contém erro de sumarização"

        return True, ""

    def validate_cluster(self, cluster: Optional[int]) -> Tuple[bool, str]:
        """
        Valida o número do cluster

        Args:
            cluster: Número do cluster

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if cluster is None:
            return True, ""  # Cluster pode ser None inicialmente

        if not isinstance(cluster, int):
            return False, "Cluster deve ser um número inteiro ou None"

        if cluster < 0:
            return False, "Cluster deve ser um número não negativo"

        if cluster > 10:  # Assumindo máximo de 10 clusters
            return False, "Cluster deve ser menor que 10"

        return True, ""

    def validate_fonte(self, fonte: str) -> Tuple[bool, str]:
        """
        Valida a fonte da notícia

        Args:
            fonte: Fonte da notícia

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not fonte or not isinstance(fonte, str):
            return False, "Fonte é obrigatória e deve ser uma string"

        fonte = fonte.strip()

        if len(fonte) == 0:
            return False, "Fonte não pode estar vazia"

        if fonte not in self.allowed_sources:
            return False, f"Fonte deve ser uma das seguintes: {', '.join(self.allowed_sources)}"

        return True, ""

    def validate_score(self, score: Optional[float]) -> Tuple[bool, str]:
        """
        Valida o score de relevância

        Args:
            score: Score de relevância

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if score is None:
            return True, ""  # Score pode ser None

        if not isinstance(score, (int, float)):
            return False, "Score deve ser um número ou None"

        if score < 0:
            return False, "Score deve ser não negativo"

        if score > 100:  # Assumindo score máximo de 100
            return False, "Score deve ser menor que 100"

        return True, ""

    def validate_status(self, status: str) -> Tuple[bool, str]:
        """
        Valida o status da notícia

        Args:
            status: Status da notícia

        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not status or not isinstance(status, str):
            return True, ""  # Status é opcional, pode ser None ou vazio

        status = status.strip().lower()

        if status not in ['postada', 'arquivada']:
            return False, "Status deve ser 'postada' ou 'arquivada'"

        return True, ""

    def validate_basic_news(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida dados básicos de uma notícia (após scraping)

        Args:
            data: Dicionário com os dados básicos da notícia

        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        errors = []

        # Validar campos obrigatórios básicos
        required_fields = ['titulo', 'link', 'fonte']
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo obrigatório '{field}' não encontrado")
            elif data[field] is None or (isinstance(data[field], str) and data[field].strip() == ''):
                errors.append(
                    f"Campo obrigatório '{field}' não pode estar vazio")

        if errors:
            return False, errors

        # Validar cada campo individualmente
        validations = {
            'titulo': lambda: self.validate_title(data.get('titulo', '')),
            'link': lambda: self.validate_link(data.get('link', '')),
            'imagem': lambda: self.validate_image(data.get('imagem')),
            'fonte': lambda: self.validate_fonte(data.get('fonte', ''))
        }

        for field, validation_func in validations.items():
            if field in data:
                try:
                    is_valid, error_msg = validation_func()
                    if not is_valid:
                        errors.append(f"{field}: {error_msg}")
                except Exception as e:
                    errors.append(f"{field}: Erro na validação - {str(e)}")

        return len(errors) == 0, errors

    def validate_complete_news(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida dados completos de uma notícia (pronta para seleção)

        Args:
            data: Dicionário com os dados completos da notícia

        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        errors = []

        # Validar campos obrigatórios completos
        required_fields = ['titulo', 'link', 'resumo', 'cluster', 'fonte']
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo obrigatório '{field}' não encontrado")
            elif data[field] is None or (isinstance(data[field], str) and data[field].strip() == ''):
                errors.append(
                    f"Campo obrigatório '{field}' não pode estar vazio")

        if errors:
            return False, errors

        # Validar cada campo individualmente
        validations = {
            'titulo': lambda: self.validate_title(data.get('titulo', '')),
            'link': lambda: self.validate_link(data.get('link', '')),
            'imagem': lambda: self.validate_image(data.get('imagem')),
            'resumo': lambda: self.validate_resumo(data.get('resumo', '')),
            'cluster': lambda: self.validate_cluster(data.get('cluster')),
            'fonte': lambda: self.validate_fonte(data.get('fonte', '')),
            'score': lambda: self.validate_score(data.get('score')),
            'status': lambda: self.validate_status(data.get('status', ''))
        }

        for field, validation_func in validations.items():
            if field in data:
                try:
                    is_valid, error_msg = validation_func()
                    if not is_valid:
                        errors.append(f"{field}: {error_msg}")
                except Exception as e:
                    errors.append(f"{field}: Erro na validação - {str(e)}")

        return len(errors) == 0, errors

    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza os dados removendo caracteres problemáticos

        Args:
            data: Dicionário com os dados

        Returns:
            Dicionário com dados sanitizados
        """
        sanitized = data.copy()

        # Sanitizar strings
        string_fields = ['titulo', 'link',
                         'imagem', 'resumo', 'fonte', 'status']
        for field in string_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                # Remover caracteres de controle e normalizar espaços
                sanitized[field] = re.sub(
                    r'\s+', ' ', sanitized[field].strip())

                # Remover caracteres problemáticos para HTML/XML
                sanitized[field] = sanitized[field].replace(
                    '<', '&lt;').replace('>', '&gt;')

        # Converter imagem vazia para None
        if 'imagem' in sanitized and sanitized['imagem'] == '':
            sanitized['imagem'] = None

        return sanitized


# Instância global do validador
data_validator = DataValidator()


def get_validator() -> DataValidator:
    """
    Função de conveniência para obter a instância do validador

    Returns:
        Instância de DataValidator
    """
    return data_validator


def validate_basic_news(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Função de conveniência para validar dados básicos

    Args:
        data: Dados da notícia para validar

    Returns:
        Tupla (é_válido, lista_de_erros)
    """
    return data_validator.validate_basic_news(data)


def validate_complete_news(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Função de conveniência para validar dados completos

    Args:
        data: Dados da notícia para validar

    Returns:
        Tupla (é_válido, lista_de_erros)
    """
    return data_validator.validate_complete_news(data)


def sanitize_news_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função de conveniência para sanitizar dados

    Args:
        data: Dados da notícia para sanitizar

    Returns:
        Dados sanitizados
    """
    return data_validator.sanitize_data(data)


if __name__ == "__main__":
    # Teste do validador
    validator = get_validator()

    # Dados de teste válidos básicos
    valid_basic = {
        'titulo': 'Teste de notícia válida',
        'link': 'https://exame.com/teste',
        'imagem': 'https://exame.com/imagem.jpg',
        'fonte': 'Exame'
    }

    # Dados de teste válidos completos
    valid_complete = {
        'titulo': 'Teste de notícia válida',
        'link': 'https://exame.com/teste',
        'imagem': 'https://exame.com/imagem.jpg',
        'resumo': 'Este é um resumo válido da notícia',
        'cluster': 1,
        'fonte': 'Exame',
        'score': 15.5
    }

    # Dados de teste inválidos
    invalid_data = {
        'titulo': '',  # Vazio
        'link': 'url-invalida',  # URL inválida
        'fonte': 'Fonte Desconhecida',  # Fonte não permitida
        'score': -5  # Score negativo
    }

    print("Testando validação de dados básicos válidos:")
    is_valid, errors = validator.validate_basic_news(valid_basic)
    print(f"Válido: {is_valid}")
    if errors:
        print(f"Erros: {errors}")

    print("\nTestando validação de dados completos válidos:")
    is_valid, errors = validator.validate_complete_news(valid_complete)
    print(f"Válido: {is_valid}")
    if errors:
        print(f"Erros: {errors}")

    print("\nTestando validação de dados inválidos:")
    is_valid, errors = validator.validate_basic_news(invalid_data)
    print(f"Válido: {is_valid}")
    if errors:
        print(f"Erros: {errors}")

    print("\nTestando sanitização:")
    dirty_data = {
        'titulo': '  Título com   espaços   extras  ',
        'link': 'https://teste.com',
        'resumo': 'Resumo com <tags> problemáticas'
    }
    clean_data = validator.sanitize_data(dirty_data)
    print(f"Dados limpos: {clean_data}")
