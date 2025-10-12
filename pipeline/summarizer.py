# ETAPA 4: SUMARIZAÇÃO COM TRANSFORMERS
"""
Módulo responsável pela sumarização dos textos usando modelos de IA
Refatorado para usar cache em memória e banco auxiliar
"""

import torch
from transformers import pipeline
import time
from config.config import MODEL_CONFIG
from errors.error_handler import error_handler
from database.aux_operations import get_aux_operations
from database.text_cache import get_text_cache


def inicializar_summarizer():
    """
    Inicializa o modelo de sumarização

    Returns:
        Pipeline de sumarização configurado
    """
    device = 0 if torch.cuda.is_available() else -1
    print("="*60)
    print("INICIANDO SUMARIZAÇÃO COM INTELIGÊNCIA ARTIFICIAL")
    print(f"Dispositivo detectado: {'GPU' if device == 0 else 'CPU'}")
    print(
        f"Otimização: Textos serão truncados em {MODEL_CONFIG['max_length']} caracteres.")
    print("="*60)

    try:
        print("\nCarregando modelo de IA... (Aguarde)")
        summarizer = pipeline(
            "summarization", model=MODEL_CONFIG['model_name'], device=device)
        print("Modelo carregado com sucesso!")
        return summarizer
    except Exception as e:
        error_handler.handle_error(
            e, "Inicialização do modelo de IA", continue_execution=False)
        raise


def sumarizar_textos():
    """
    Sumariza todos os textos coletados do cache em memória
    e salva os resumos no banco auxiliar

    Returns:
        Número de textos sumarizados com sucesso
    """
    # Obter instâncias dos gerenciadores
    aux_ops = get_aux_operations()
    text_cache = get_text_cache()

    # Obter textos do cache
    textos_cache = text_cache.get_texts_for_summarization()

    if not textos_cache:
        print("ERRO: Nenhum texto encontrado no cache para sumarização.")
        return 0

    try:
        summarizer = inicializar_summarizer()
        total_textos = len(textos_cache)
        textos_sumarizados = 0

        print(f"\nIniciando sumarização de {total_textos} textos...")
        start_time = time.time()

        for i, (link, texto) in enumerate(textos_cache):
            try:
                # Truncar texto se necessário
                texto_limitado = texto[:MODEL_CONFIG['max_length']]

                resumo_gerado = summarizer(
                    texto_limitado,
                    max_new_tokens=MODEL_CONFIG['max_new_tokens'],
                    min_new_tokens=MODEL_CONFIG['min_new_tokens'],
                    num_beams=MODEL_CONFIG['num_beams'],
                    early_stopping=MODEL_CONFIG['early_stopping']
                )[0]['summary_text']

                # Salvar resumo no banco auxiliar
                success = aux_ops.update_resumo(link, resumo_gerado)
                if success:
                    textos_sumarizados += 1

                # Remover texto do cache após sumarização
                text_cache.remove_text(link)

                # Mostrar progresso a cada 5 textos
                if (i + 1) % 5 == 0 or (i + 1) == total_textos:
                    tempo_passado = time.time() - start_time
                    print(
                        f"Progresso: {i + 1}/{total_textos} textos sumarizados. (Tempo: {tempo_passado:.2f}s)")

            except Exception as e:
                error_handler.handle_error(
                    e, f"Sumarização de notícia {link}")

                # Marcar como falha no banco auxiliar
                aux_ops.update_resumo(link, f"Falha na sumarização: {e}")
                continue

        print(
            f"\n✅ Sumarização concluída: {textos_sumarizados}/{total_textos} textos processados com sucesso!")

        # Mostrar estatísticas do cache após sumarização
        cache_stats = text_cache.get_cache_stats()
        print(
            f"📊 Cache após sumarização: {cache_stats['total_texts']} textos restantes")

        return textos_sumarizados

    except Exception as e:
        print(f"\nOcorreu um erro crítico durante o processo: {e}")
        return 0
