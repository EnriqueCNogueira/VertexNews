# GERENCIADOR UNIFICADO DE BANCO DE DADOS
"""
Módulo responsável por todas as operações de banco de dados do pipeline de notícias.
Unifica operações auxiliares e principais em uma única interface simplificada.
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
from .config import get_db_config
from .validator import get_validator
from pipeline.scraper_utils import detect_source_from_url


class DatabaseManager:
    """Classe unificada para todas as operações de banco de dados"""

    def __init__(self):
        """Inicializa o gerenciador de banco de dados"""
        self.config = get_db_config()
        self.validator = get_validator()
        self.aux_db_path = self.config.get_aux_db_path()
        self.main_db_path = self.config.get_main_db_path()

    def initialize_databases(self) -> bool:
        """
        Inicializa ambos os bancos de dados com suas tabelas e índices

        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        try:
            # Criar diretórios se necessário (usar diretório atual se não especificado)
            aux_dir = os.path.dirname(self.aux_db_path) or '.'
            main_dir = os.path.dirname(self.main_db_path) or '.'

            os.makedirs(aux_dir, exist_ok=True)
            os.makedirs(main_dir, exist_ok=True)

            # Inicializar banco auxiliar
            if not self._init_aux_database():
                return False

            # Inicializar banco principal
            if not self._init_main_database():
                return False

            print("[OK] Ambos os bancos de dados inicializados com sucesso")
            return True

        except Exception as e:
            print(f"[ERRO] Erro ao inicializar bancos: {e}")
            return False

    def _init_aux_database(self) -> bool:
        """Inicializa o banco de dados auxiliar"""
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
                        fonte TEXT NOT NULL DEFAULT 'Desconhecida',
                        resumo TEXT,
                        cluster INTEGER,
                        data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_processamento TIMESTAMP,
                        status TEXT DEFAULT 'coletada'
                    )
                """)

                # Criar índices para performance
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_aux_link ON noticias_aux(link)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_aux_cluster ON noticias_aux(cluster)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_aux_fonte ON noticias_aux(fonte)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_aux_data ON noticias_aux(data_coleta)")

                conn.commit()
                return True

        except Exception as e:
            print(f"[ERRO] Erro ao inicializar banco auxiliar: {e}")
            return False

    def _init_main_database(self) -> bool:
        """Inicializa o banco de dados principal"""
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
                        resumo TEXT NOT NULL,
                        cluster INTEGER NOT NULL,
                        fonte TEXT NOT NULL,
                        score REAL,
                        status TEXT DEFAULT 'arquivada',
                        data_selecao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Criar índices para performance
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_link ON noticias(link)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_data_selecao ON noticias(data_selecao)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_cluster ON noticias(cluster)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_fonte ON noticias(fonte)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_noticias_score ON noticias(score)")

                conn.commit()
                return True

        except Exception as e:
            print(f"[ERRO] Erro ao inicializar banco principal: {e}")
            return False

    def detect_fonte_from_url(self, url: str) -> str:
        """
        Detecta a fonte baseada na URL da notícia
        Usa função utilitária compartilhada

        Args:
            url: URL da notícia

        Returns:
            Nome da fonte detectada
        """
        return detect_source_from_url(url)

    # OPERAÇÕES NO BANCO AUXILIAR

    def insert_news_basic(self, titulo: str, link: str, imagem: Optional[str] = None, fonte: str = None) -> bool:
        """
        Insere notícia básica (após scraping) no banco auxiliar

        Args:
            titulo: Título da notícia
            link: Link da notícia (deve ser único)
            imagem: URL da imagem (opcional)
            fonte: Fonte da notícia (se None, detecta automaticamente)

        Returns:
            True se inserido com sucesso, False caso contrário
        """
        if fonte is None:
            fonte = self.detect_fonte_from_url(link)

        # Validar dados básicos
        news_data = {
            'titulo': titulo,
            'link': link,
            'imagem': imagem,
            'fonte': fonte
        }

        # Sanitizar e validar
        news_data = self.validator.sanitize_data(news_data)
        is_valid, errors = self.validator.validate_basic_news(news_data)

        if not is_valid:
            print(f"[ERRO] Dados inválidos: {', '.join(errors)}")
            return False

        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO noticias_aux (titulo, link, imagem, fonte)
                    VALUES (?, ?, ?, ?)
                """, (news_data['titulo'], news_data['link'], news_data['imagem'], news_data['fonte']))

                conn.commit()
                return True

        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"[ERRO] Erro ao inserir notícia básica: {e}")
            return False

    def update_news_with_resumo(self, link: str, resumo: str) -> bool:
        """
        Atualiza notícia no banco auxiliar com resumo gerado

        Args:
            link: Link da notícia
            resumo: Resumo gerado pela IA

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        # Validar resumo
        is_valid, error = self.validator.validate_resumo(resumo)
        if not is_valid:
            print(f"[ERRO] Resumo inválido: {error}")
            return False

        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias_aux 
                    SET resumo = ?, data_processamento = CURRENT_TIMESTAMP, status = 'processada'
                    WHERE link = ?
                """, (resumo, link))

                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    return False

        except Exception as e:
            print(f"[ERRO] Erro ao atualizar resumo: {e}")
            return False

    def update_news_with_cluster(self, link: str, cluster: int) -> bool:
        """
        Atualiza notícia no banco auxiliar com cluster atribuído

        Args:
            link: Link da notícia
            cluster: Número do cluster

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias_aux 
                    SET cluster = ?, status = 'clusterizada'
                    WHERE link = ?
                """, (cluster, link))

                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    return False

        except Exception as e:
            print(f"[ERRO] Erro ao atualizar cluster: {e}")
            return False

    def get_news_for_summarization(self) -> List[Dict]:
        """
        Obtém notícias que precisam de sumarização

        Returns:
            Lista de notícias sem resumo
        """
        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, fonte
                    FROM noticias_aux
                    WHERE resumo IS NULL AND status = 'coletada'
                    ORDER BY data_coleta ASC
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"[ERRO] Erro ao obter notícias para sumarização: {e}")
            return []

    def get_news_for_clustering(self) -> List[Dict]:
        """
        Obtém notícias que precisam de clustering

        Returns:
            Lista de notícias com resumo mas sem cluster
        """
        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, resumo, fonte
                    FROM noticias_aux
                    WHERE resumo IS NOT NULL AND cluster IS NULL AND status = 'processada'
                    ORDER BY data_processamento ASC
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"[ERRO] Erro ao obter notícias para clustering: {e}")
            return []

    def get_news_for_selection(self) -> List[Dict]:
        """
        Obtém notícias prontas para seleção (com resumo e cluster)

        Returns:
            Lista de notícias prontas para seleção
        """
        try:
            with sqlite3.connect(self.aux_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, fonte
                    FROM noticias_aux
                    WHERE resumo IS NOT NULL AND cluster IS NOT NULL AND status = 'clusterizada'
                    ORDER BY data_processamento DESC
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"[ERRO] Erro ao obter notícias para seleção: {e}")
            return []

    def clear_auxiliary_database(self) -> bool:
        """
        Limpa todos os dados do banco auxiliar

        Returns:
            True se limpo com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.aux_db_path):
                print(
                    f"[AVISO] Banco auxiliar não encontrado: {self.aux_db_path}")
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
                    f"[OK] Banco auxiliar limpo: {count_before} registros removidos")
                return True

        except Exception as e:
            print(f"[ERRO] Erro ao limpar banco auxiliar: {e}")
            return False

    # OPERAÇÕES NO BANCO PRINCIPAL

    def check_link_exists_main(self, link: str) -> bool:
        """
        Verifica se um link já existe no banco principal

        Args:
            link: Link da notícia

        Returns:
            True se existe, False caso contrário
        """
        try:
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT COUNT(*) FROM noticias WHERE link = ?", (link,))
                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            print(f"[ERRO] Erro ao verificar existência do link: {e}")
            return False

    def insert_selected_news(self, titulo: str, link: str, imagem: Optional[str], resumo: str,
                             cluster: int, fonte: str, score: Optional[float] = None,
                             status: str = "arquivada") -> bool:
        """
        Insere uma nova notícia selecionada no banco principal

        Args:
            titulo: Título da notícia
            link: Link da notícia
            imagem: URL da imagem (opcional)
            resumo: Resumo da notícia
            cluster: Número do cluster
            fonte: Fonte da notícia
            score: Score de relevância (opcional)
            status: Status da notícia (postada/arquivada)

        Returns:
            True se inserido com sucesso, False caso contrário
        """
        # Validar dados completos
        news_data = {
            'titulo': titulo,
            'link': link,
            'imagem': imagem,
            'resumo': resumo,
            'cluster': cluster,
            'fonte': fonte,
            'score': score,
            'status': status
        }

        # Sanitizar e validar
        news_data = self.validator.sanitize_data(news_data)
        is_valid, errors = self.validator.validate_complete_news(news_data)

        if not is_valid:
            print(f"[ERRO] Dados inválidos para inserção: {', '.join(errors)}")
            return False

        try:
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO noticias (titulo, link, imagem, resumo, cluster, fonte, score, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (news_data['titulo'], news_data['link'], news_data['imagem'],
                      news_data['resumo'], news_data['cluster'], news_data['fonte'],
                      news_data['score'], news_data['status']))

                conn.commit()
                print(
                    f"[OK] Nova notícia selecionada inserida: {news_data['titulo'][:50]}...")
                return True

        except sqlite3.IntegrityError:
            print(
                f"[AVISO] Link já existe no banco principal: {news_data['link']}")
            return False
        except Exception as e:
            print(f"[ERRO] Erro ao inserir notícia selecionada: {e}")
            return False

    def update_selection_timestamp_and_status(self, link: str) -> bool:
        """
        Atualiza o timestamp de seleção e garante que o status seja "postada"

        Args:
            link: Link da notícia

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias 
                    SET data_selecao = CURRENT_TIMESTAMP, status = 'postada'
                    WHERE link = ?
                """, (link,))

                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    return False

        except Exception as e:
            print(f"[ERRO] Erro ao atualizar timestamp e status: {e}")
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
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE noticias 
                    SET data_selecao = CURRENT_TIMESTAMP 
                    WHERE link = ?
                """, (link,))

                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"[OK] Timestamp atualizado para: {link}")
                    return True
                else:
                    print(
                        f"[AVISO] Nenhuma notícia encontrada com link: {link}")
                    return False

        except Exception as e:
            print(f"[ERRO] Erro ao atualizar timestamp: {e}")
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

        for news in selected_news:
            link = news['link']

            if self.check_link_exists_main(link):
                # Notícia já existe - atualizar timestamp e manter status postada
                if self.update_selection_timestamp_and_status(link):
                    stats['atualizadas'] += 1
                else:
                    stats['falhas'] += 1
            else:
                # Nova notícia - inserir como postada
                if self.insert_selected_news(
                    news['titulo'],
                    news['link'],
                    news.get('imagem'),
                    news['resumo'],
                    news['cluster'],
                    news['fonte'],
                    news.get('score'),
                    'postada'  # Sempre inserir como postada
                ):
                    stats['novas'] += 1
                else:
                    stats['falhas'] += 1

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
            with sqlite3.connect(self.main_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, titulo, link, imagem, resumo, cluster, fonte, data_selecao, score, status
                    FROM noticias
                    ORDER BY data_selecao DESC
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"[ERRO] Erro ao obter notícias recentes: {e}")
            return []

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
                    'fonte': item['fonte'],
                    'data_selecao': item['data_selecao'],
                    'score': item.get('score'),
                    'status': item.get('status')
                }
                api_data.append(api_item)

            return api_data

        except Exception as e:
            print(f"[ERRO] Erro ao obter dados da API: {e}")
            return []

    def get_statistics(self) -> Dict[str, int]:
        """
        Obtém estatísticas do banco principal

        Returns:
            Dicionário com estatísticas
        """
        try:
            with sqlite3.connect(self.main_db_path) as conn:
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
            print(f"[ERRO] Erro ao obter estatísticas: {e}")
            return {}

    def archive_posted_news(self, keep_selected_links: List[str] = None) -> int:
        """
        Arquivar notícias postadas, mas manter como postadas as que foram re-selecionadas

        Args:
            keep_selected_links: Lista de links que devem manter status "postada"

        Returns:
            Número de notícias arquivadas
        """
        try:
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()

                if keep_selected_links:
                    # Criar placeholders para a query IN
                    placeholders = ','.join(['?' for _ in keep_selected_links])

                    cursor.execute(f"""
                        UPDATE noticias 
                        SET status = "arquivada" 
                        WHERE status = "postada" 
                        AND link NOT IN ({placeholders})
                    """, keep_selected_links)
                else:
                    # Se não há links para manter, arquivar todas as postadas
                    cursor.execute("""
                        UPDATE noticias 
                        SET status = "arquivada" 
                        WHERE status = "postada"
                    """)

                archived_count = cursor.rowcount
                conn.commit()

                if archived_count > 0:
                    print(f"[INFO] {archived_count} notícias arquivadas")

                return archived_count

        except Exception as e:
            print(f"[ERRO] Erro ao arquivar notícias: {e}")
            return 0


# Instância global do gerenciador
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """
    Função de conveniência para obter a instância do gerenciador

    Returns:
        Instância de DatabaseManager
    """
    return db_manager


if __name__ == "__main__":
    # Teste do gerenciador
    manager = get_db_manager()

    # Teste de inicialização
    success = manager.initialize_databases()
    print(f"Inicialização: {'Sucesso' if success else 'Falha'}")

    # Teste de estatísticas
    stats = manager.get_statistics()
    print(f"Estatísticas: {stats}")

    # Teste de dados da API
    api_data = manager.get_api_data(5)
    print(f"Dados da API: {len(api_data)} notícias")
