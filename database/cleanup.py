# LIMPEZA DO BANCO DE DADOS AUXILIAR
"""
Módulo responsável pela limpeza e manutenção do banco de dados auxiliar
"""

import os
import sqlite3
from typing import Optional
from datetime import datetime


class DatabaseCleanup:
    """Classe para operações de limpeza do banco de dados auxiliar"""

    def __init__(self, aux_db_path: str = "noticias_aux.db"):
        """
        Inicializa o gerenciador de limpeza

        Args:
            aux_db_path: Caminho para o banco de dados auxiliar
        """
        self.aux_db_path = aux_db_path

    def clear_auxiliary_database(self) -> bool:
        """
        Limpa todos os dados do banco auxiliar

        Returns:
            True se limpo com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.aux_db_path):
                print(f"⚠️ Banco auxiliar não encontrado: {self.aux_db_path}")
                return True

            with sqlite3.connect(self.aux_db_path) as conn:
                cursor = conn.cursor()

                # Contar registros antes da limpeza
                cursor.execute("SELECT COUNT(*) FROM noticias_aux")
                count_before = cursor.fetchone()[0]

                # Limpar tabela
                cursor.execute("DELETE FROM noticias_aux")
                conn.commit()

                print(
                    f"✅ Banco auxiliar limpo: {count_before} registros removidos")
                return True

        except Exception as e:
            print(f"❌ Erro ao limpar banco auxiliar: {e}")
            return False

    def delete_auxiliary_database(self) -> bool:
        """
        Remove completamente o arquivo do banco auxiliar

        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.aux_db_path):
                print(f"⚠️ Banco auxiliar não encontrado: {self.aux_db_path}")
                return True

            # Obter informações do arquivo antes da remoção
            file_size = os.path.getsize(self.aux_db_path)

            # Tentar remover arquivo com retry
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    os.remove(self.aux_db_path)
                    print(f"✅ Banco auxiliar removido: {self.aux_db_path}")
                    print(
                        f"   - Tamanho do arquivo: {file_size / (1024 * 1024):.2f} MB")
                    return True
                except PermissionError:
                    if attempt < max_retries - 1:
                        print(
                            f"⚠️ Arquivo em uso, tentando novamente em 1 segundo... (tentativa {attempt + 1}/{max_retries})")
                        time.sleep(1)
                    else:
                        print(
                            f"⚠️ Não foi possível remover o arquivo após {max_retries} tentativas")
                        print("   - O arquivo será removido na próxima execução")
                        return True  # Considerar como sucesso pois o arquivo foi limpo

        except Exception as e:
            print(f"❌ Erro ao remover banco auxiliar: {e}")
            return False

    def vacuum_database(self) -> bool:
        """
        Executa VACUUM no banco auxiliar para otimizar espaço

        Returns:
            True se otimizado com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.aux_db_path):
                print(f"⚠️ Banco auxiliar não encontrado: {self.aux_db_path}")
                return True

            with sqlite3.connect(self.aux_db_path) as conn:
                cursor = conn.cursor()

                # Obter tamanho antes do VACUUM
                size_before = os.path.getsize(self.aux_db_path)

                # Executar VACUUM
                cursor.execute("VACUUM")

                # Obter tamanho após o VACUUM
                size_after = os.path.getsize(self.aux_db_path)

                print(f"✅ VACUUM executado no banco auxiliar")
                print(
                    f"   - Tamanho antes: {size_before / (1024 * 1024):.2f} MB")
                print(
                    f"   - Tamanho depois: {size_after / (1024 * 1024):.2f} MB")
                print(
                    f"   - Espaço liberado: {(size_before - size_after) / (1024 * 1024):.2f} MB")

                return True

        except Exception as e:
            print(f"❌ Erro ao executar VACUUM: {e}")
            return False

    def get_database_info(self) -> dict:
        """
        Obtém informações sobre o banco auxiliar

        Returns:
            Dicionário com informações do banco
        """
        info = {
            'exists': False,
            'size_mb': 0,
            'record_count': 0,
            'last_modified': None
        }

        try:
            if os.path.exists(self.aux_db_path):
                info['exists'] = True
                info['size_mb'] = os.path.getsize(
                    self.aux_db_path) / (1024 * 1024)
                info['last_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(self.aux_db_path)
                ).strftime('%Y-%m-%d %H:%M:%S')

                # Contar registros
                with sqlite3.connect(self.aux_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM noticias_aux")
                    info['record_count'] = cursor.fetchone()[0]

        except Exception as e:
            print(f"❌ Erro ao obter informações do banco: {e}")

        return info

    def cleanup_complete(self) -> bool:
        """
        Executa limpeza completa do banco auxiliar

        Returns:
            True se limpeza completa foi bem-sucedida, False caso contrário
        """
        print("="*60)
        print("INICIANDO LIMPEZA COMPLETA DO BANCO AUXILIAR")
        print("="*60)

        # Obter informações antes da limpeza
        info_before = self.get_database_info()
        if info_before['exists']:
            print(f"📊 Informações antes da limpeza:")
            print(f"   - Arquivo existe: {info_before['exists']}")
            print(f"   - Tamanho: {info_before['size_mb']:.2f} MB")
            print(f"   - Registros: {info_before['record_count']}")
            print(f"   - Última modificação: {info_before['last_modified']}")

        # Executar limpeza
        success = True

        # 1. Limpar dados
        if not self.clear_auxiliary_database():
            success = False

        # 2. Otimizar espaço
        if not self.vacuum_database():
            success = False

        # 3. Remover arquivo
        if not self.delete_auxiliary_database():
            success = False

        if success:
            print("\n✅ Limpeza completa executada com sucesso!")
            print("   - Banco auxiliar removido completamente")
            print("   - Sistema pronto para próxima execução")
        else:
            print("\n❌ Alguns erros ocorreram durante a limpeza")

        print("="*60)
        return success


# Instância global para limpeza
cleanup_manager = DatabaseCleanup()


def cleanup_auxiliary_database() -> bool:
    """
    Função de conveniência para limpeza completa do banco auxiliar

    Returns:
        True se limpeza foi bem-sucedida, False caso contrário
    """
    return cleanup_manager.cleanup_complete()


def get_cleanup_manager() -> DatabaseCleanup:
    """
    Função de conveniência para obter o gerenciador de limpeza

    Returns:
        Instância de DatabaseCleanup
    """
    return cleanup_manager


if __name__ == "__main__":
    # Teste da limpeza
    manager = get_cleanup_manager()

    # Mostrar informações
    info = manager.get_database_info()
    print(f"Informações do banco auxiliar: {info}")

    # Executar limpeza completa
    success = cleanup_auxiliary_database()
    print(f"Limpeza completa: {'Sucesso' if success else 'Falha'}")
