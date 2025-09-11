#!/usr/bin/env python3
"""
Conversor de JSON para JSONL

Converte o arquivo vagas_todos_setores_estruturadas_completo.json para formato JSONL
(uma vaga por linha) para processamento pelo tag_skills_v4.py
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_json_to_jsonl(input_file: str, output_file: str):
    """Converte JSON array para JSONL"""
    logger.info(f"Convertendo {input_file} para {output_file}")
    
    try:
        # Carregar JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Carregadas {len(data)} vagas")
        
        # Escrever JSONL
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, vaga in enumerate(data):
                if i % 1000 == 0:
                    logger.info(f"Processando vaga {i}...")
                
                f.write(json.dumps(vaga, ensure_ascii=False) + '\n')
        
        logger.info(f"Conversão concluída! Arquivo salvo: {output_file}")
    
    except Exception as e:
        logger.error(f"Erro na conversão: {e}")
        raise

if __name__ == '__main__':
    convert_json_to_jsonl(
        'vagas_todos_setores_estruturadas_completo.json',
        'vagas_todos_setores_estruturadas_completo.jsonl'
    )