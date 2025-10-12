# INICIALIZAÇÃO DOS BANCOS DE DADOS SQLITE
"""
Módulo responsável pela inicialização dos bancos de dados SQLite
para o pipeline de notícias de marketing
"""

import sqlite3
import os
from typing import Optional


class DatabaseInitializer:
    """Classe para inicialização dos bancos de dados SQLite"""

    def __init__(self):
        """Inicializa o gerenciador de bancos de dados"""
        self.aux_db_path = "noticias_aux.db"
        self.main_db_path = "noticias.db"

    def init_auxiliary_database(self) -> bool:
        """
        Inicializa o banco de dados auxiliar (noticias_aux.db)

        Schema: id, titulo, link (UNIQUE), imagem (pode ser NULL), resumo, cluster

        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                cursor = conn.cursor()

                # Criar tabela de notícias auxiliares
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS noticias_aux (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        link TEXT UNIQUE NOT NULL,
                        imagem TEXT,
                        resumo TEXT,
                        cluster INTEGER
                    )
                """)

                # Criar índices para melhor performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_noticias_aux_link 
                    ON noticias_aux(link)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_noticias_aux_cluster 
                    ON noticias_aux(cluster)
                """)

                conn.commit()
                print(f"Banco auxiliar inicializado: {self.aux_db_path}")
                return True

        except Exception as e:
            print(f"Erro ao inicializar banco auxiliar: {e}")
            return False

    def init_main_database(self) -> bool:
        """
        Inicializa o banco de dados principal (noticias.db)

        Schema: id, titulo, link (UNIQUE), imagem, resumo, cluster, data_selecao (TIMESTAMP)

        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()

                # Criar tabela de notícias principais
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS noticias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        link TEXT UNIQUE NOT NULL,
                        imagem TEXT,
                        resumo TEXT,
                        cluster INTEGER,
                        data_selecao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Criar índices para melhor performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_noticias_link 
                    ON noticias(link)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_noticias_data_selecao 
                    ON noticias(data_selecao DESC)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_noticias_cluster 
                    ON noticias(cluster)
                """)

                conn.commit()
                print(f"Banco principal inicializado: {self.main_db_path}")
                return True

        except Exception as e:
            print(f"Erro ao inicializar banco principal: {e}")
            return False

    def init_all_databases(self) -> bool:
        """
        Inicializa todos os bancos de dados necessários

        Returns:
            True se todos foram inicializados com sucesso, False caso contrário
        """
        print("="*60)
        print("INICIALIZANDO BANCOS DE DADOS SQLITE")
        print("="*60)

        aux_success = self.init_auxiliary_database()
        main_success = self.init_main_database()

        if aux_success and main_success:
            print("\nTodos os bancos de dados foram inicializados com sucesso!")
            print(f"   - Banco auxiliar: {self.aux_db_path}")
            print(f"   - Banco principal: {self.main_db_path}")
            return True
        else:
            print("\nFalha na inicialização de alguns bancos de dados.")
            return False

    def check_database_exists(self, db_path: str) -> bool:
        """
        Verifica se um banco de dados existe

        Args:
            db_path: Caminho para o arquivo do banco de dados

        Returns:
            True se existe, False caso contrário
        """
        return os.path.exists(db_path)

    def get_database_info(self) -> dict:
        """
        Obtém informações sobre os bancos de dados

        Returns:
            Dicionário com informações dos bancos
        """
        info = {
            'aux_db': {
                'path': self.aux_db_path,
                'exists': self.check_database_exists(self.aux_db_path),
                'size_mb': 0
            },
            'main_db': {
                'path': self.main_db_path,
                'exists': self.check_database_exists(self.main_db_path),
                'size_mb': 0
            }
        }

        # Calcular tamanhos dos arquivos
        if info['aux_db']['exists']:
            info['aux_db']['size_mb'] = os.path.getsize(
                self.aux_db_path) / (1024 * 1024)

        if info['main_db']['exists']:
            info['main_db']['size_mb'] = os.path.getsize(
                self.main_db_path) / (1024 * 1024)

        return info


# Instância global para inicialização dos bancos
db_initializer = DatabaseInitializer()


def initialize_databases() -> bool:
    """
    Função de conveniência para inicializar todos os bancos de dados

    Returns:
        True se inicializados com sucesso, False caso contrário
    """
    return db_initializer.init_all_databases()


if __name__ == "__main__":
    # Teste da inicialização
    success = initialize_databases()
    if success:
        info = db_initializer.get_database_info()
        print("\nInformações dos bancos de dados:")
        print(
            f"Auxiliar: {info['aux_db']['path']} ({info['aux_db']['size_mb']:.2f} MB)")
        print(
            f"Principal: {info['main_db']['path']} ({info['main_db']['size_mb']:.2f} MB)")
    else:
        print("Falha na inicialização dos bancos de dados.")
