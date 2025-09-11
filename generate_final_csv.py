#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar CSV final estruturado a partir do JSON processado
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime

def load_json_data(file_path):
    """Carrega dados do arquivo JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_list_field(field_value):
    """Normaliza campos de lista para string separada por vírgula"""
    if isinstance(field_value, list):
        return '; '.join(str(item) for item in field_value if item)
    return field_value if field_value else ''

def process_vagas_data(data):
    """Processa dados das vagas para formato CSV"""
    processed_data = []
    
    for vaga in data:
        # Processa cada vaga
        processed_vaga = {
            'id': f"vaga_{len(processed_data) + 1:06d}",
            'title': vaga.get('title', ''),
            'seniority': vaga.get('seniority', ''),
            'area': vaga.get('area', ''),
            'company_name': vaga.get('company_name', ''),
            'industry': vaga.get('industry', ''),
            'employment_type': vaga.get('employment_type', ''),
            'work_schedule': vaga.get('work_schedule', ''),
            'modality': vaga.get('modality', ''),
            'location_city': vaga.get('location_city', ''),
            'location_state': vaga.get('location_state', ''),
            'location_region': vaga.get('location_region', ''),
            'salary_min': vaga.get('salary_min'),
            'salary_max': vaga.get('salary_max'),
            'salary_currency': vaga.get('salary_currency', 'BRL'),
            'salary_period': vaga.get('salary_period', 'month'),
            'benefits': normalize_list_field(vaga.get('benefits', [])),
            'rewards': normalize_list_field(vaga.get('rewards', [])),
            'requirements_must': normalize_list_field(vaga.get('requirements_must', [])),
            'requirements_nice': normalize_list_field(vaga.get('requirements_nice', [])),
            'education_level': vaga.get('education_level', ''),
            'responsibilities': normalize_list_field(vaga.get('responsibilities', [])),
            'pcd': vaga.get('pcd', False),
            'tags': normalize_list_field(vaga.get('tags', [])),
            'source_name': vaga.get('source_name', ''),
            'source_url': vaga.get('source_url', ''),
            'raw_excerpt': vaga.get('raw_excerpt', ''),
            'confidence': vaga.get('confidence', 0.0),
            'parsed_at': vaga.get('parsed_at', datetime.now().strftime('%Y-%m-%d'))
        }
        
        processed_data.append(processed_vaga)
    
    return processed_data

def generate_csv(input_file, output_file):
    """Gera CSV final a partir do JSON estruturado"""
    print(f"Carregando dados de {input_file}...")
    data = load_json_data(input_file)
    
    print(f"Processando {len(data)} vagas...")
    processed_data = process_vagas_data(data)
    
    # Cria DataFrame
    df = pd.DataFrame(processed_data)
    
    # Ordena por título e área
    df = df.sort_values(['area', 'title', 'seniority'])
    
    # Salva CSV
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\nCSV gerado com sucesso: {output_file}")
    print(f"Total de vagas: {len(df)}")
    
    # Estatísticas básicas
    print("\n=== ESTATÍSTICAS ===")
    print(f"Áreas mais comuns:")
    print(df['area'].value_counts().head(10))
    
    print(f"\nNíveis de senioridade:")
    print(df['seniority'].value_counts())
    
    print(f"\nModalidades de trabalho:")
    print(df['modality'].value_counts())
    
    print(f"\nCidades:")
    print(df['location_city'].value_counts().head(10))
    
    # Salários
    salary_data = df[df['salary_min'].notna()]
    if len(salary_data) > 0:
        print(f"\nEstatísticas salariais ({len(salary_data)} vagas com salário):")
        print(f"Salário mínimo médio: R$ {salary_data['salary_min'].mean():.2f}")
        print(f"Salário máximo médio: R$ {salary_data['salary_max'].mean():.2f}")
        print(f"Mediana salário mínimo: R$ {salary_data['salary_min'].median():.2f}")
    
    return df

if __name__ == "__main__":
    input_file = "vagas_industrial_estruturado_avancado.json"
    output_file = "vagas_industrial_final_estruturado.csv"
    
    try:
        df = generate_csv(input_file, output_file)
        print(f"\nProcessamento concluído com sucesso!")
        print(f"Arquivo gerado: {output_file}")
        
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()