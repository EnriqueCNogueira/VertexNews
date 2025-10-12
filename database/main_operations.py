# OPERAÇÕES NO BANCO DE DADOS PRINCIPAL
"""
Módulo responsável pelas operações no banco de dados principal (noticias.db)
usado para armazenar notícias selecionadas para exibição na API
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime


class MainOperations:
    """Classe para operações no banco de dados principal"""

    def __init__(self, db_path: str = "noticias.db"):
        """
        Inicializa as operações principais

        Args:
            db_path: Caminho para o banco de dados principal
        """
        self.db_path = db_path

    def check_link_exists(self, link: str) -> bool:
        """
        Verifica se um link já existe no banco principal

        Args:
            link: Link da notícia

        Returns:
            True se existe, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT COUNT(*) FROM noticias WHERE link = ?
                """, (link,))

                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            print(f"Erro ao verificar existência do link: {e}")
            return False

    def insert_new_news(self, titulo: str, link: str, imagem: Optional[str],
                        resumo: str, cluster: int) -> bool:
        """
        Insere uma nova notícia no banco principal

        Args:
            titulo: Título da notícia
            link: Link da notícia
            imagem: URL da imagem (opcional)
            resumo: Resumo da notícia
            cluster: Número do cluster

        Returns:
            True se inserido com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO noticias (titulo, link, imagem, resumo, cluster, data_selecao)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (titulo, link, imagem, resumo, cluster))

                conn.commit()
                print(f"✅ Nova notícia inserida: {titulo[:50]}...")
                return True

        except sqlite3.IntegrityError:
            print(f"⚠️ Link já existe no banco principal: {link}")
            return False
        except Exception as e:
            print(f"❌ Erro ao inserir nova notícia: {e}")
            return False

    def update_selection_timestamp(self, link: str) -> bool:
        """
        Atualiza o timestamp de seleção para uma notícia existente

        Args:
            link: Link da notícia

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias 
                    SET data_selecao = CURRENT_TIMESTAMP 
                    WHERE link = ?
                """, (link,))

                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✅ Timestamp atualizado para: {link}")
                    return True
                else:
                    print(f"⚠️ Nenhuma notícia encontrada com link: {link}")
                    return False

        except Exception as e:
            print(f"❌ Erro ao atualizar timestamp: {e}")
            return False

    def transfer_selected_news(self, selected_news: List[Dict]) -> Dict[str, int]:
        """
        Transfere notícias selecionadas do banco auxiliar para o principal

        Args:
            selected_news: Lista de dicionários com notícias selecionadas

        Returns:
            Dicionário com estatísticas da transferência
        """
        stats = {
            'novas': 0,
            'atualizadas': 0,
            'falhas': 0
        }

        print(
            f"\n🔄 Transferindo {len(selected_news)} notícias selecionadas...")

        for news in selected_news:
            link = news['link']

            if self.check_link_exists(link):
                # Notícia já existe - apenas atualizar timestamp
                if self.update_selection_timestamp(link):
                    stats['atualizadas'] += 1
                else:
                    stats['falhas'] += 1
            else:
                # Nova notícia - inserir
                if self.insert_new_news(
                    news['titulo'],
                    news['link'],
                    news.get('imagem'),
                    news['resumo'],
                    news['cluster']
                ):
                    stats['novas'] += 1
                else:
                    stats['falhas'] += 1

        print(f"\n📊 Estatísticas da transferência:")
        print(f"   - Novas notícias: {stats['novas']}")
        print(f"   - Timestamps atualizados: {stats['atualizadas']}")
        print(f"   - Falhas: {stats['falhas']}")

        return stats

    def get_latest_news(self, limit: int = 15) -> List[Dict]:
        """
        Obtém as notícias mais recentes ordenadas por data_selecao

        Args:
            limit: Número máximo de notícias a retornar

        Returns:
            Lista de dicionários com as notícias mais recentes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, data_selecao
                    FROM noticias
                    ORDER BY data_selecao DESC
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ Erro ao obter notícias recentes: {e}")
            return []

    def get_news_by_cluster(self, cluster: int, limit: int = 50) -> List[Dict]:
        """
        Obtém notícias de um cluster específico

        Args:
            cluster: Número do cluster
            limit: Número máximo de notícias a retornar

        Returns:
            Lista de dicionários com notícias do cluster
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, data_selecao
                    FROM noticias
                    WHERE cluster = ?
                    ORDER BY data_selecao DESC
                    LIMIT ?
                """, (cluster, limit))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ Erro ao obter notícias do cluster {cluster}: {e}")
            return []

    def get_news_by_date_range(self, start_date: str, end_date: str,
                               limit: int = 100) -> List[Dict]:
        """
        Obtém notícias em um intervalo de datas

        Args:
            start_date: Data de início (formato YYYY-MM-DD)
            end_date: Data de fim (formato YYYY-MM-DD)
            limit: Número máximo de notícias a retornar

        Returns:
            Lista de dicionários com notícias do período
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, data_selecao
                    FROM noticias
                    WHERE DATE(data_selecao) BETWEEN ? AND ?
                    ORDER BY data_selecao DESC
                    LIMIT ?
                """, (start_date, end_date, limit))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ Erro ao obter notícias por período: {e}")
            return []

    def search_news(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Busca notícias por termo no título ou resumo

        Args:
            search_term: Termo de busca
            limit: Número máximo de notícias a retornar

        Returns:
            Lista de dicionários com notícias encontradas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                search_pattern = f"%{search_term}%"
                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, data_selecao
                    FROM noticias
                    WHERE titulo LIKE ? OR resumo LIKE ?
                    ORDER BY data_selecao DESC
                    LIMIT ?
                """, (search_pattern, search_pattern, limit))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ Erro ao buscar notícias: {e}")
            return []

    def get_statistics(self) -> Dict[str, int]:
        """
        Obtém estatísticas do banco principal

        Returns:
            Dicionário com estatísticas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total de notícias
                cursor.execute("SELECT COUNT(*) FROM noticias")
                total = cursor.fetchone()[0]

                # Notícias por cluster
                cursor.execute("""
                    SELECT cluster, COUNT(*) 
                    FROM noticias 
                    WHERE cluster IS NOT NULL
                    GROUP BY cluster
                    ORDER BY cluster
                """)
                clusters = dict(cursor.fetchall())

                # Notícias dos últimos 7 dias
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE data_selecao >= datetime('now', '-7 days')
                """)
                ultimos_7_dias = cursor.fetchone()[0]

                # Notícias dos últimos 30 dias
                cursor.execute("""
                    SELECT COUNT(*) FROM noticias 
                    WHERE data_selecao >= datetime('now', '-30 days')
                """)
                ultimos_30_dias = cursor.fetchone()[0]

                return {
                    'total': total,
                    'ultimos_7_dias': ultimos_7_dias,
                    'ultimos_30_dias': ultimos_30_dias,
                    'por_cluster': clusters
                }

        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}

    def get_api_data(self, limit: int = 15) -> List[Dict]:
        """
        Obtém dados formatados para a API

        Args:
            limit: Número máximo de notícias a retornar

        Returns:
            Lista de dicionários formatados para a API
        """
        try:
            news = self.get_latest_news(limit)

            # Formatar dados para a API
            api_data = []
            for item in news:
                api_item = {
                    'id': item['id'],
                    'titulo': item['titulo'],
                    'link': item['link'],
                    'imagem': item['imagem'],
                    'resumo': item['resumo'],
                    'cluster': item['cluster'],
                    'data_selecao': item['data_selecao']
                }
                api_data.append(api_item)

            return api_data

        except Exception as e:
            print(f"❌ Erro ao obter dados da API: {e}")
            return []


# Instância global para operações principais
main_ops = MainOperations()


def get_main_operations() -> MainOperations:
    """
    Função de conveniência para obter a instância das operações principais

    Returns:
        Instância de MainOperations
    """
    return main_ops


if __name__ == "__main__":
    # Teste das operações principais
    ops = get_main_operations()

    # Teste de verificação de link
    exists = ops.check_link_exists("https://teste.com")
    print(f"Link existe: {exists}")

    # Teste de estatísticas
    stats = ops.get_statistics()
    print(f"Estatísticas: {stats}")

    # Teste de dados da API
    api_data = ops.get_api_data(5)
    print(f"Dados da API: {len(api_data)} notícias")
