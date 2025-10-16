# SCRIPT PRINCIPAL DE TESTES
"""
Script principal para executar os testes do pipeline de notícias de marketing.
Permite executar testes individuais ou todos os testes de uma vez.
"""

from scripts.test_scrapers_robust import run_scraper_robust_test
from scripts.test_database_integrity import run_database_integrity_test
import sys
import os
import argparse
from typing import List, Dict, Any
from datetime import datetime

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    """Classe principal para executar os testes"""

    def __init__(self):
        """Inicializa o executor de testes"""
        self.tests = {
            'database': {
                'name': 'Teste de Integridade do Banco de Dados',
                'description': 'Teste rápido para verificar integridade dos bancos antes do pipeline',
                'function': run_database_integrity_test,
                'required_before_pipeline': True,
                'execution_time': 'rápido'
            },
            'scrapers': {
                'name': 'Teste Robusto dos Scrapers',
                'description': 'Teste robusto para detectar mudanças nos sites dos scrapers',
                'function': run_scraper_robust_test,
                'required_before_pipeline': False,
                'execution_time': 'robusto'
            }
        }

        self.results = {}

    def run_test(self, test_name: str) -> bool:
        """
        Executa um teste específico

        Args:
            test_name: Nome do teste a executar

        Returns:
            True se o teste passou, False caso contrário
        """
        if test_name not in self.tests:
            print(f"❌ Teste '{test_name}' não encontrado.")
            print(f"   Testes disponíveis: {', '.join(self.tests.keys())}")
            return False

        test_config = self.tests[test_name]

        print(f"[RUN] Executando: {test_config['name']}")
        print(f"   Descrição: {test_config['description']}")
        print(f"   Tempo estimado: {test_config['execution_time']}")
        print(
            f"   Obrigatório antes do pipeline: {'Sim' if test_config['required_before_pipeline'] else 'Não'}")
        print("-" * 60)

        try:
            start_time = datetime.now()
            success = test_config['function']()
            end_time = datetime.now()

            execution_time = (end_time - start_time).total_seconds()

            # Armazenar resultado
            self.results[test_name] = {
                'success': success,
                'execution_time': execution_time,
                'timestamp': start_time
            }

            print("-" * 60)
            if success:
                print(f"[OK] {test_config['name']} - PASSOU")
            else:
                print(f"[ERRO] {test_config['name']} - FALHOU")

            print(f"   Tempo de execução: {execution_time:.2f}s")

            return success

        except Exception as e:
            print(
                f"❌ Erro inesperado ao executar {test_config['name']}: {str(e)}")
            self.results[test_name] = {
                'success': False,
                'execution_time': 0,
                'timestamp': datetime.now(),
                'error': str(e)
            }
            return False

    def run_all_tests(self) -> bool:
        """
        Executa todos os testes

        Returns:
            True se todos os testes passaram, False caso contrário
        """
        print("\n[TEST] Executando todos os testes do pipeline...")
        print(f"   Total de testes: {len(self.tests)}")
        print("=" * 60)

        all_success = True

        for test_name in self.tests.keys():
            success = self.run_test(test_name)
            if not success:
                all_success = False

            print()  # Linha em branco entre testes

        # Exibir resumo final
        self._display_final_summary()

        return all_success

    def run_pipeline_prerequisites(self) -> bool:
        """
        Executa apenas os testes obrigatórios antes do pipeline

        Returns:
            True se todos os testes obrigatórios passaram, False caso contrário
        """
        print("\n[INFO] Executando testes obrigatórios antes do pipeline...")

        required_tests = [
            test_name for test_name, config in self.tests.items()
            if config['required_before_pipeline']
        ]

        if not required_tests:
            print("⚠️ Nenhum teste obrigatório configurado.")
            return True

        print(f"   Testes obrigatórios: {len(required_tests)}")
        print("=" * 60)

        all_success = True

        for test_name in required_tests:
            success = self.run_test(test_name)
            if not success:
                all_success = False
            print()

        # Exibir resumo
        self._display_final_summary()

        return all_success

    def list_tests(self):
        """Lista todos os testes disponíveis"""
        print("\n[LIST] Testes disponíveis:")
        print("=" * 60)

        for test_name, config in self.tests.items():
            status_icon = "[CRITICAL]" if config['required_before_pipeline'] else "[OPTIONAL]"
            time_icon = "[FAST]" if config['execution_time'] == 'rápido' else "[ROBUST]"

            print(f"{status_icon} {test_name}")
            print(f"   Nome: {config['name']}")
            print(f"   Descrição: {config['description']}")
            print(f"   Tempo: {time_icon} {config['execution_time']}")
            print(
                f"   Obrigatório: {'Sim' if config['required_before_pipeline'] else 'Não'}")
            print()

    def _display_final_summary(self):
        """Exibe resumo final dos testes"""
        if not self.results:
            return

        print("\n[RESULTADO] RESUMO FINAL DOS TESTES")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(
            1 for result in self.results.values() if result['success'])
        failed_tests = total_tests - passed_tests

        print(f"   Total de testes: {total_tests}")
        print(f"   [OK] Passou: {passed_tests}")
        print(f"   [ERRO] Falhou: {failed_tests}")

        if failed_tests > 0:
            print(f"\n[ERRO] Testes que falharam:")
            for test_name, result in self.results.items():
                if not result['success']:
                    print(f"   • {test_name}")
                    if 'error' in result:
                        print(f"     Erro: {result['error']}")

        total_time = sum(result['execution_time']
                         for result in self.results.values())
        print(f"\n[TIME] Tempo total de execução: {total_time:.2f}s")

        if passed_tests == total_tests:
            print(
                f"\n[SUCESSO] Todos os testes passaram! Pipeline pode ser executado.")
        else:
            print(
                f"\n[AVISO] Alguns testes falharam. Corrija os problemas antes de executar o pipeline.")

    def get_test_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual dos testes

        Returns:
            Dicionário com status dos testes
        """
        if not self.results:
            return {'status': 'not_run', 'message': 'Nenhum teste executado ainda'}

        total_tests = len(self.results)
        passed_tests = sum(
            1 for result in self.results.values() if result['success'])

        if passed_tests == total_tests:
            return {
                'status': 'all_passed',
                'message': 'Todos os testes passaram',
                'details': self.results
            }
        else:
            return {
                'status': 'some_failed',
                'message': f'{passed_tests}/{total_tests} testes passaram',
                'details': self.results
            }


def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(
        description='Script de testes para o pipeline de notícias de marketing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/run_tests.py --all                    # Executar todos os testes
  python scripts/run_tests.py --database              # Executar apenas teste de banco
  python scripts/run_tests.py --scrapers              # Executar apenas teste de scrapers
  python scripts/run_tests.py --prerequisites          # Executar testes obrigatórios
  python scripts/run_tests.py --list                   # Listar testes disponíveis
        """
    )

    # Argumentos mutuamente exclusivos
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='Executar todos os testes')
    group.add_argument('--database', action='store_true',
                       help='Executar apenas teste de integridade do banco')
    group.add_argument('--scrapers', action='store_true',
                       help='Executar apenas teste robusto dos scrapers')
    group.add_argument('--prerequisites', action='store_true',
                       help='Executar apenas testes obrigatórios antes do pipeline')
    group.add_argument('--list', action='store_true',
                       help='Listar todos os testes disponíveis')

    # Argumentos opcionais
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Modo verboso (mais detalhes)')

    args = parser.parse_args()

    # Criar executor de testes
    runner = TestRunner()

    try:
        if args.list:
            runner.list_tests()
            return 0

        elif args.all:
            success = runner.run_all_tests()

        elif args.database:
            success = runner.run_test('database')

        elif args.scrapers:
            success = runner.run_test('scrapers')

        elif args.prerequisites:
            success = runner.run_pipeline_prerequisites()

        else:
            print("❌ Argumento não reconhecido.")
            parser.print_help()
            return 1

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n[AVISO] Testes interrompidos pelo usuário.")
        return 1

    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
