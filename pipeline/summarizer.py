# ETAPA 4: SUMARIZAÇÃO COM TRANSFORMERS
"""
Módulo responsável pela sumarização dos textos usando modelos de IA
"""

import torch
from transformers import pipeline
import time
from .config import MODEL_CONFIG


def inicializar_summarizer():
    """
    Inicializa o modelo de sumarização

    Returns:
        Pipeline de sumarização configurado
    """
    device = 0 if torch.cuda.is_available() else -1
    print("="*60)
    print("INICIANDO ETAPA 3: SUMARIZAÇÃO EM FILA COM TRANSFORMERS")
    print(f"Dispositivo detectado: {'GPU' if device == 0 else 'CPU'}")
    print(
        f"Otimização: Textos de entrada serão truncados em {MODEL_CONFIG['max_length']} caracteres.")
    print("="*60)

    try:
        print("\nCarregando o modelo de IA... (Aguarde um momento)")
        summarizer = pipeline(
            "summarization", model=MODEL_CONFIG['model_name'], device=device)
        print("Modelo carregado com sucesso!")
        return summarizer
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        raise


def sumarizar_textos(df_noticias, textos_para_sumarizar, indices_validos):
    """
    Sumariza todos os textos coletados

    Args:
        df_noticias: DataFrame com as notícias
        textos_para_sumarizar: Lista de textos para sumarizar
        indices_validos: Lista de índices válidos no DataFrame

    Returns:
        DataFrame atualizado com resumos
    """
    if not textos_para_sumarizar or not indices_validos:
        print("ERRO: Listas de textos ou índices vazias.")
        return df_noticias

    try:
        summarizer = inicializar_summarizer()
        total_textos = len(textos_para_sumarizar)

        print(
            f"\n--- Iniciando a sumarização de {total_textos} textos, um por um. ---")
        start_time = time.time()

        for i, (texto, indice_df) in enumerate(zip(textos_para_sumarizar, indices_validos)):
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

                df_noticias.loc[indice_df, 'resumo'] = resumo_gerado

                # Mostrar progresso a cada 5 textos
                if (i + 1) % 5 == 0 or (i + 1) == total_textos:
                    tempo_passado = time.time() - start_time
                    print(
                        f"Progresso: {i + 1}/{total_textos} sumarizados. (Tempo: {tempo_passado:.2f} segundos)")

            except Exception as e:
                print(
                    f"ERRO ao sumarizar a notícia de índice {indice_df}: {e}")
                df_noticias.loc[indice_df,
                                'resumo'] = f"Falha na sumarização: {e}"
                continue

        print("\n--- Sumarização sequencial concluída com sucesso! ---")
        print("\n--- Tabela Final com Notícias e Resumos (Amostra) ---")
        print(df_noticias[['fonte', 'titulo', 'resumo']].head())

        return df_noticias

    except Exception as e:
        print(f"\nOcorreu um erro crítico durante o processo: {e}")
        return df_noticias
