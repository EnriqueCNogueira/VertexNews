# OPERAÇÕES NO BANCO DE DADOS AUXILIAR
"""
Módulo responsável pelas operações no banco de dados auxiliar (noticias_aux.db)
usado durante o processamento do pipeline
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class AuxiliaryOperations:
    """Classe para operações no banco de dados auxiliar"""

    def __init__(self, db_path: str = "noticias_aux.db"):
        """
        Inicializa as operações auxiliares

        Args:
            db_path: Caminho para o banco de dados auxiliar
        """
        self.db_path = db_path

    def insert_news_basic(self, titulo: str, link: str, imagem: Optional[str] = None) -> bool:
        """
        Insere notícia básica (após scraping) no banco auxiliar

        Args:
            titulo: Título da notícia
            link: Link da notícia (deve ser único)
            imagem: URL da imagem (opcional)

        Returns:
            True se inserido com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO noticias_aux (titulo, link, imagem)
                    VALUES (?, ?, ?)
                """, (titulo, link, imagem))

                conn.commit()
                return True

        except sqlite3.IntegrityError:
            # Link já existe - não é erro crítico
            print(f"Link já existe no banco auxiliar: {link}")
            return False
        except Exception as e:
            print(f"Erro ao inserir notícia básica: {e}")
            return False

    def update_resumo(self, link: str, resumo: str) -> bool:
        """
        Atualiza o resumo de uma notícia no banco auxiliar

        Args:
            link: Link da notícia
            resumo: Resumo gerado pela IA

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias_aux 
                    SET resumo = ? 
                    WHERE link = ?
                """, (resumo, link))

                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print(f"Nenhuma notícia encontrada com link: {link}")
                    return False

        except Exception as e:
            print(f"Erro ao atualizar resumo: {e}")
            return False

    def update_cluster(self, link: str, cluster: int) -> bool:
        """
        Atualiza o cluster de uma notícia no banco auxiliar

        Args:
            link: Link da notícia
            cluster: Número do cluster

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias_aux 
                    SET cluster = ? 
                    WHERE link = ?
                """, (cluster, link))

                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print(f"Nenhuma notícia encontrada com link: {link}")
                    return False

        except Exception as e:
            print(f"Erro ao atualizar cluster: {e}")
            return False

    def get_all_news(self) -> List[Dict]:
        """
        Obtém todas as notícias do banco auxiliar

        Returns:
            Lista de dicionários com as notícias
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster
                    FROM noticias_aux
                    ORDER BY id
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"Erro ao obter notícias: {e}")
            return []

    def get_news_with_resumos(self) -> List[Dict]:
        """
        Obtém notícias que possuem resumos válidos

        Returns:
            Lista de dicionários com notícias que têm resumos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster
                    FROM noticias_aux
                    WHERE resumo IS NOT NULL 
                    AND resumo != ''
                    AND resumo NOT LIKE 'Falha na sumarização%'
                    ORDER BY id
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"Erro ao obter notícias com resumos: {e}")
            return []

    def get_news_without_resumos(self) -> List[Dict]:
        """
        Obtém notícias que ainda não possuem resumos

        Returns:
            Lista de dicionários com notícias sem resumos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster
                    FROM noticias_aux
                    WHERE resumo IS NULL OR resumo = ''
                    ORDER BY id
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"Erro ao obter notícias sem resumos: {e}")
            return []

    def get_news_without_clusters(self) -> List[Dict]:
        """
        Obtém notícias que ainda não possuem clusters

        Returns:
            Lista de dicionários com notícias sem clusters
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster
                    FROM noticias_aux
                    WHERE cluster IS NULL
                    AND resumo IS NOT NULL 
                    AND resumo != ''
                    AND resumo NOT LIKE 'Falha na sumarização%'
                    ORDER BY id
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"Erro ao obter notícias sem clusters: {e}")
            return []

    def get_news_by_cluster(self, cluster: int) -> List[Dict]:
        """
        Obtém notícias de um cluster específico

        Args:
            cluster: Número do cluster

        Returns:
            Lista de dicionários com notícias do cluster
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster
                    FROM noticias_aux
                    WHERE cluster = ?
                    ORDER BY id
                """, (cluster,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"Erro ao obter notícias do cluster {cluster}: {e}")
            return []

    def get_top_news_by_relevance(self, top_n: int = 15) -> List[Dict]:
        """
        Obtém as top N notícias ordenadas por relevância (simulado)
        Para uso na seleção estratégica

        Args:
            top_n: Número de notícias a retornar

        Returns:
            Lista de dicionários com as top notícias
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster
                    FROM noticias_aux
                    WHERE resumo IS NOT NULL 
                    AND resumo != ''
                    AND resumo NOT LIKE 'Falha na sumarização%'
                    AND cluster IS NOT NULL
                    ORDER BY id
                    LIMIT ?
                """, (top_n,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"Erro ao obter top notícias: {e}")
            return []

    def count_news(self) -> Dict[str, int]:
        """
        Conta notícias por diferentes critérios

        Returns:
            Dicionário com contadores
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total de notícias
                cursor.execute("SELECT COUNT(*) FROM noticias_aux")
                total = cursor.fetchone()[0]

                # Notícias com resumos
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias_aux 
                    WHERE resumo IS NOT NULL AND resumo != ''
                """)
                com_resumos = cursor.fetchone()[0]

                # Notícias com clusters
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias_aux 
                    WHERE cluster IS NOT NULL
                """)
                com_clusters = cursor.fetchone()[0]

                # Notícias prontas para seleção
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias_aux 
                    WHERE resumo IS NOT NULL 
                    AND resumo != ''
                    AND resumo NOT LIKE 'Falha na sumarização%'
                    AND cluster IS NOT NULL
                """)
                prontas = cursor.fetchone()[0]

                return {
                    'total': total,
                    'com_resumos': com_resumos,
                    'com_clusters': com_clusters,
                    'prontas_selecao': prontas
                }

        except Exception as e:
            print(f"Erro ao contar notícias: {e}")
            return {}

    def clear_database(self) -> bool:
        """
        Limpa todos os dados do banco auxiliar

        Returns:
            True se limpo com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("DELETE FROM noticias_aux")
                conn.commit()

                print("Banco auxiliar limpo com sucesso")
                return True

        except Exception as e:
            print(f"Erro ao limpar banco auxiliar: {e}")
            return False


# Instância global para operações auxiliares
aux_ops = AuxiliaryOperations()


def get_aux_operations() -> AuxiliaryOperations:
    """
    Função de conveniência para obter a instância das operações auxiliares

    Returns:
        Instância de AuxiliaryOperations
    """
    return aux_ops


if __name__ == "__main__":
    # Teste das operações auxiliares
    ops = get_aux_operations()

    # Teste de inserção
    success = ops.insert_news_basic(
        "Teste", "https://teste.com", "https://imagem.com")
    print(f"Inserção teste: {'Sucesso' if success else 'Falha'}")

    # Teste de contagem
    counts = ops.count_news()
    print(f"Contadores: {counts}")

    # Teste de obtenção
    news = ops.get_all_news()
    print(f"Notícias encontradas: {len(news)}")
