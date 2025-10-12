# MÓDULO DE TRATAMENTO DE ERROS
"""
Sistema simples e eficiente para tratamento de erros no pipeline
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, Any


class PipelineErrorHandler:
    """Classe simples para tratamento centralizado de erros"""

    def __init__(self):
        self.setup_logging()
        self.error_count = 0
        self.warning_count = 0

    def setup_logging(self):
        """Configura logging básico"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    'errors/pipeline_errors.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error: Exception, context: str = "",
                     continue_execution: bool = True) -> bool:
        """
        Trata erros de forma centralizada

        Args:
            error: Exceção capturada
            context: Contexto onde o erro ocorreu
            continue_execution: Se deve continuar a execução

        Returns:
            True se deve continuar, False se deve parar
        """
        self.error_count += 1

        error_msg = f"ERRO em {context}: {str(error)}"
        self.logger.error(error_msg)

        # Log detalhado apenas para erros críticos
        if self.error_count <= 3:  # Limita logs detalhados
            self.logger.error(f"Traceback: {traceback.format_exc()}")

        print(f"ERRO: {error_msg}")

        if not continue_execution:
            print("Execução interrompida devido a erro crítico.")
            return False

        return True

    def handle_warning(self, message: str, context: str = ""):
        """Trata avisos"""
        self.warning_count += 1
        warning_msg = f"AVISO em {context}: {message}"
        self.logger.warning(warning_msg)
        print(f"AVISO: {warning_msg}")

    def validate_data(self, data: Any, data_type: str, context: str = "") -> bool:
        """
        Validação simples de dados

        Args:
            data: Dados para validar
            data_type: Tipo esperado ('list', 'dict', 'str', 'not_empty')
            context: Contexto da validação

        Returns:
            True se válido, False caso contrário
        """
        try:
            if data_type == 'list' and not isinstance(data, list):
                self.handle_warning(
                    f"Esperado lista, recebido {type(data)}", context)
                return False

            elif data_type == 'dict' and not isinstance(data, dict):
                self.handle_warning(
                    f"Esperado dicionário, recebido {type(data)}", context)
                return False

            elif data_type == 'str' and not isinstance(data, str):
                self.handle_warning(
                    f"Esperado string, recebido {type(data)}", context)
                return False

            elif data_type == 'not_empty':
                if not data or (hasattr(data, '__len__') and len(data) == 0):
                    self.handle_warning("Dados vazios encontrados", context)
                    return False

            return True

        except Exception as e:
            self.handle_error(e, f"Validação de dados em {context}")
            return False

    def get_summary(self) -> dict:
        """Retorna resumo dos erros e avisos"""
        return {
            'errors': self.error_count,
            'warnings': self.warning_count,
            'timestamp': datetime.now().isoformat()
        }


# Instância global para uso em todo o pipeline
error_handler = PipelineErrorHandler()
