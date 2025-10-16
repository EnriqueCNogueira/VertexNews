#!/usr/bin/env python3
"""
Script unificado para gerenciar a API REST do Vertex News.
Substitui run_server.py, test_api.py, setup_check.py e example_client.py
"""

import sys
import os
import argparse
import subprocess
import importlib
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class APIManager:
    """Gerenciador unificado da API Vertex News"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Inicializa o gerenciador"""
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()

    # ==================== FUNCIONALIDADES DE SERVIDOR ====================

    def run_server(self, host: str = None, port: int = None, debug: bool = False, reload: bool = False):
        """Executa o servidor da API"""
        try:
            from api.config import get_api_config
            config = get_api_config()

            # Aplicar parâmetros
            if host:
                config.HOST = host
            if port:
                config.PORT = port
            if debug:
                config.DEBUG = True

            print("=" * 60)
            print("VERTEX NEWS API SERVER")
            print("=" * 60)
            print(f"Host: {config.HOST}")
            print(f"Port: {config.PORT}")
            print(f"Debug: {config.DEBUG}")
            print(f"Reload: {reload}")
            print("=" * 60)
            print("Iniciando servidor...")
            print("Documentação disponível em: http://localhost:8000/docs")
            print("Health check: http://localhost:8000/api/v1/health")
            print("=" * 60)

            import uvicorn
            uvicorn.run(
                "api.app:app",
                host=config.HOST,
                port=config.PORT,
                reload=reload or config.DEBUG,
                log_level="info" if not config.DEBUG else "debug"
            )

        except KeyboardInterrupt:
            print("\n[INFO] Servidor interrompido pelo usuário.")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERRO] Falha ao iniciar servidor: {e}")
            sys.exit(1)

    # ==================== FUNCIONALIDADES DE TESTE ====================

    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, **kwargs) -> Dict[str, Any]:
        """Testa um endpoint específico"""
        url = f"{self.api_url}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)

            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": response.status_code == expected_status,
                "response_time": response.elapsed.total_seconds(),
                "content_type": response.headers.get("content-type", ""),
                "content_length": len(response.content)
            }

            try:
                result["json_data"] = response.json()
            except:
                result["text_data"] = response.text[:200]

            return result

        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e)
            }

    def run_tests(self) -> bool:
        """Executa todos os testes da API"""
        print("=" * 60)
        print("TESTANDO VERTEX NEWS API")
        print("=" * 60)

        tests = [
            ("GET", "/", 200),
            ("GET", "/health", 200),
            ("GET", "/news", 200),
            ("GET", "/news?limit=5", 200),
            # Deve falhar (limite máximo é 50)
            ("GET", "/news?limit=100", 422),
            ("GET", "/news/1", 200),  # Assumindo que existe uma notícia com ID 1
            ("GET", "/news/99999", 404),  # Deve falhar (notícia não existe)
            ("GET", "/cache/stats", 200),
            ("POST", "/cache/clear", 200),
        ]

        results = []
        all_passed = True

        for method, endpoint, expected_status in tests:
            print(f"\nTestando {method} {endpoint}...")

            result = self.test_endpoint(method, endpoint, expected_status)
            results.append(result)

            if result["success"]:
                print(
                    f"OK PASSOU - Status: {result['status_code']} - Tempo: {result['response_time']:.3f}s")
            else:
                print(
                    f"ERRO FALHOU - Status: {result.get('status_code', 'N/A')} - Esperado: {expected_status}")
                if "error" in result:
                    print(f"   Erro: {result['error']}")
                all_passed = False

        # Testar estrutura dos dados
        data_structure_ok = self.test_news_data_structure()

        # Imprimir resumo
        self.print_test_summary(results)

        return all_passed and data_structure_ok

    def test_news_data_structure(self) -> bool:
        """Testa se a estrutura dos dados de notícias está correta"""
        print("\n" + "=" * 60)
        print("TESTANDO ESTRUTURA DOS DADOS DE NOTÍCIAS")
        print("=" * 60)

        result = self.test_endpoint("GET", "/news?limit=1")

        if not result["success"]:
            print("ERRO Falha ao obter dados de notícias")
            return False

        try:
            json_data = result["json_data"]

            # Verificar estrutura da resposta
            required_fields = ["success", "data",
                               "total", "cached", "timestamp"]
            for field in required_fields:
                if field not in json_data:
                    print(
                        f"ERRO Campo obrigatório '{field}' não encontrado na resposta")
                    return False

            print("OK Estrutura da resposta está correta")

            # Verificar estrutura dos dados de notícias
            if json_data["data"]:
                news_item = json_data["data"][0]
                required_news_fields = [
                    "id", "titulo", "link", "imagem", "resumo",
                    "fonte", "score", "cluster", "data_selecao", "status"
                ]

                for field in required_news_fields:
                    if field not in news_item:
                        print(
                            f"ERRO Campo obrigatório '{field}' não encontrado na notícia")
                        return False

                print("OK Estrutura dos dados de notícias está correta")

                if news_item["status"] != "postada":
                    print(
                        f"AVISO  AVISO: Notícia com status '{news_item['status']}' (esperado: 'postada')")

                print(f"OK Notícia encontrada: {news_item['titulo'][:50]}...")
            else:
                print("AVISO  AVISO: Nenhuma notícia encontrada no banco de dados")

            return True

        except Exception as e:
            print(f"ERRO Erro ao verificar estrutura dos dados: {e}")
            return False

    def print_test_summary(self, results: List[Dict[str, Any]]):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("RESUMO DOS TESTES")
        print("=" * 60)

        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total de testes: {total_tests}")
        print(f"Testes passaram: {passed_tests}")
        print(f"Testes falharam: {failed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\nTestes que falharam:")
            for result in results:
                if not result["success"]:
                    print(f"  - {result['method']} {result['endpoint']}")

        print("=" * 60)

    # ==================== FUNCIONALIDADES DE VERIFICAÇÃO ====================

    def check_python_version(self) -> bool:
        """Verifica se a versão do Python é compatível"""
        print("Verificando versão do Python...")

        if sys.version_info < (3, 8):
            print("ERRO: Python 3.8+ é necessário")
            return False

        print(f"OK Python {sys.version.split()[0]} detectado")
        return True

    def check_dependencies(self) -> bool:
        """Verifica se as dependências estão instaladas"""
        print("\nPACOTES Verificando dependências...")

        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "requests"
        ]

        missing_packages = []

        for package in required_packages:
            try:
                importlib.import_module(package)
                print(f"OK {package}")
            except ImportError:
                print(f"ERRO {package} não encontrado")
                missing_packages.append(package)

        if missing_packages:
            print(f"\nINFO Para instalar as dependências faltantes:")
            print(f"pip install {' '.join(missing_packages)}")
            return False

        return True

    def check_database(self) -> bool:
        """Verifica se o banco de dados existe"""
        print("\nBANCO Verificando banco de dados...")

        db_files = ["noticias.db", "noticias_aux.db"]
        missing_dbs = []

        for db_file in db_files:
            if os.path.exists(db_file):
                print(f"OK {db_file}")
            else:
                print(f"ERRO {db_file} não encontrado")
                missing_dbs.append(db_file)

        if missing_dbs:
            print(f"\nINFO Para criar os bancos de dados:")
            print("python main.py")
            return False

        return True

    def check_api_files(self) -> bool:
        """Verifica se os arquivos da API existem"""
        print("\nARQUIVOS Verificando arquivos da API...")

        api_dir = Path("api")
        required_files = [
            "app.py",
            "config.py",
            "cache.py",
            "models.py",
            "routes.py",
            "services.py",
            "manage.py"
        ]

        missing_files = []

        for file_name in required_files:
            file_path = api_dir / file_name
            if file_path.exists():
                print(f"OK {file_name}")
            else:
                print(f"ERRO {file_name} não encontrado")
                missing_files.append(file_name)

        if missing_files:
            print(
                f"\nERRO Arquivos da API faltando: {', '.join(missing_files)}")
            return False

        return True

    def test_api_import(self) -> bool:
        """Testa se a API pode ser importada"""
        print("\nCONFIG Testando importação da API...")

        try:
            from api.config import get_api_config
            from api.cache import get_api_cache
            from api.models import NewsItem
            from api.services import get_news_service
            from api.routes import router

            print("OK Todos os módulos da API importados com sucesso")
            return True

        except Exception as e:
            print(f"ERRO Erro ao importar módulos da API: {e}")
            return False

    def run_quick_test(self) -> bool:
        """Executa um teste rápido da API"""
        print("\nTESTE Executando teste rápido...")

        try:
            from api.config import get_api_config
            config = get_api_config()
            print(f"OK Configuração carregada: {config.HOST}:{config.PORT}")

            from api.cache import get_api_cache
            cache = get_api_cache()
            cache.set("test", "value")
            assert cache.get("test") == "value"
            print("OK Cache funcionando")

            from api.services import get_news_service
            service = get_news_service()
            print("OK Serviço inicializado")

            return True

        except Exception as e:
            print(f"ERRO Erro no teste rápido: {e}")
            return False

    def setup_check(self) -> bool:
        """Executa verificação completa do setup"""
        print("=" * 60)
        print("INICIALIZAÇÃO DA API VERTEX NEWS")
        print("=" * 60)

        checks = [
            ("Versão do Python", self.check_python_version),
            ("Dependências", self.check_dependencies),
            ("Arquivos da API", self.check_api_files),
            ("Banco de dados", self.check_database),
            ("Importação da API", self.test_api_import),
            ("Teste rápido", self.run_quick_test)
        ]

        all_passed = True

        for check_name, check_func in checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                print(f"ERRO Erro em {check_name}: {e}")
                all_passed = False

        print("\n" + "=" * 60)

        if all_passed:
            print("SUCESSO TODAS AS VERIFICAÇÕES PASSARAM!")
            print("\nPara iniciar a API:")
            print("python api/manage.py run")
            print("\nPara testar a API:")
            print("python api/manage.py test")
            print("\nDocumentação:")
            print("http://localhost:8000/docs")
        else:
            print("ERRO ALGUMAS VERIFICAÇÕES FALHARAM!")
            print("Corrija os problemas acima antes de executar a API.")

        print("=" * 60)
        return all_passed

    # ==================== FUNCIONALIDADES DE EXEMPLO ====================

    def get_news(self, limit: int = 15) -> Dict[str, Any]:
        """Obtém notícias postadas"""
        url = f"{self.api_url}/news"
        params = {"limit": limit}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_news_by_id(self, news_id: int) -> Dict[str, Any]:
        """Obtém uma notícia específica por ID"""
        url = f"{self.api_url}/news/{news_id}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_health(self) -> Dict[str, Any]:
        """Verifica o status da API"""
        url = f"{self.api_url}/health"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def clear_cache(self) -> Dict[str, Any]:
        """Limpa o cache da API"""
        url = f"{self.api_url}/cache/clear"

        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        url = f"{self.api_url}/cache/stats"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def print_news(self, news_item: Dict[str, Any]):
        """Imprime uma notícia formatada"""
        print(f"NOTICIA {news_item['titulo']}")
        print(f"LINK {news_item['link']}")
        print(f"FONTE: {news_item['fonte']}")
        print(f"SCORE: {news_item.get('score', 'N/A')}")
        print(f"CLUSTER: {news_item['cluster']}")
        print(f"DATA: {news_item['data_selecao']}")
        print(f"RESUMO: {news_item['resumo'][:100]}...")
        if news_item.get('imagem'):
            print(f"IMAGEM: {news_item['imagem']}")
        print("-" * 60)

    def run_example(self):
        """Executa exemplo de uso da API"""
        print("=" * 60)
        print("EXEMPLO DE USO DA API VERTEX NEWS")
        print("=" * 60)

        try:
            # 1. Verificar saúde da API
            print("\n1. Verificando saúde da API...")
            health = self.get_health()
            print(f"Status: {health['status']}")
            print(f"Versão: {health['version']}")
            print(f"Banco conectado: {health['database_connected']}")

            # 2. Obter notícias
            print("\n2. Obtendo notícias postadas...")
            news_response = self.get_news(limit=5)

            print(f"Total de notícias: {news_response['total']}")
            print(f"Dados do cache: {news_response['cached']}")
            print(f"Timestamp: {news_response['timestamp']}")

            # 3. Exibir notícias
            print("\n3. Exibindo notícias:")
            for news in news_response['data']:
                self.print_news(news)

            # 4. Obter notícia específica (se houver)
            if news_response['data']:
                first_news_id = news_response['data'][0]['id']
                print(
                    f"\n4. Obtendo notícia específica (ID: {first_news_id})...")

                specific_news = self.get_news_by_id(first_news_id)
                print(
                    f"Notícia encontrada: {specific_news['data'][0]['titulo']}")

            # 5. Estatísticas do cache
            print("\n5. Estatísticas do cache:")
            cache_stats = self.get_cache_stats()
            print(f"Itens no cache: {cache_stats['data']['active_items']}")
            print(f"Itens expirados: {cache_stats['data']['expired_items']}")
            print(f"Tamanho máximo: {cache_stats['data']['max_size']}")

            # 6. Limpar cache
            print("\n6. Limpando cache...")
            clear_result = self.clear_cache()
            print(f"Cache limpo: {clear_result['success']}")

            print("\nOK Exemplo concluído com sucesso!")

        except requests.exceptions.ConnectionError:
            print("\nERRO Erro: Não foi possível conectar à API.")
            print("Certifique-se de que a API está rodando em http://localhost:8000")
            print("Execute: python api/manage.py run")

        except requests.exceptions.HTTPError as e:
            print(f"\nERRO Erro HTTP: {e}")

        except Exception as e:
            print(f"\nERRO Erro inesperado: {e}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Gerenciador da API Vertex News")
    subparsers = parser.add_subparsers(
        dest="command", help="Comandos disponíveis")

    # Comando run (servidor)
    run_parser = subparsers.add_parser("run", help="Executar servidor da API")
    run_parser.add_argument("--host", help="Host para executar a API")
    run_parser.add_argument(
        "--port", type=int, help="Porta para executar a API")
    run_parser.add_argument("--debug", action="store_true",
                            help="Executar em modo debug")
    run_parser.add_argument("--reload", action="store_true",
                            help="Recarregar automaticamente")

    # Comando test
    test_parser = subparsers.add_parser("test", help="Testar API")
    test_parser.add_argument(
        "--url", default="http://localhost:8000", help="URL base da API")
    test_parser.add_argument(
        "--wait", type=int, default=0, help="Aguardar N segundos antes de iniciar")

    # Comando setup
    subparsers.add_parser("setup", help="Verificar configuração da API")

    # Comando example
    example_parser = subparsers.add_parser(
        "example", help="Executar exemplo de uso")
    example_parser.add_argument(
        "--url", default="http://localhost:8000", help="URL base da API")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = APIManager()

    if args.command == "run":
        manager.run_server(
            host=args.host,
            port=args.port,
            debug=args.debug,
            reload=args.reload
        )

    elif args.command == "test":
        if args.wait > 0:
            print(
                f"Aguardando {args.wait} segundos antes de iniciar os testes...")
            time.sleep(args.wait)

        manager.base_url = args.url
        manager.api_url = f"{args.url}/api/v1"

        try:
            all_passed = manager.run_tests()
            data_structure_ok = manager.test_news_data_structure()
            manager.print_test_summary([])

            if all_passed and data_structure_ok:
                print("\nSUCESSO TODOS OS TESTES PASSARAM!")
                sys.exit(0)
            else:
                print("\nERRO ALGUNS TESTES FALHARAM!")
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n[INFO] Testes interrompidos pelo usuário.")
            sys.exit(1)
        except Exception as e:
            print(f"\n[ERRO] Erro inesperado durante os testes: {e}")
            sys.exit(1)

    elif args.command == "setup":
        success = manager.setup_check()
        sys.exit(0 if success else 1)

    elif args.command == "example":
        manager.base_url = args.url
        manager.api_url = f"{args.url}/api/v1"
        manager.run_example()


if __name__ == "__main__":
    main()
