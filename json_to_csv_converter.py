#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor de JSON Estruturado para CSV Normalizado
Converte o JSON gerado pelo pipeline avançado em CSV com colunas bem definidas
"""

import pandas as pd
import json
import logging
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONToCSVConverter:
    def __init__(self):
        pass
    
    def convert_json_to_csv(self, json_file: str, csv_file: str) -> None:
        """Converter JSON estruturado para CSV normalizado"""
        logger.info(f"Iniciando conversão de {json_file} para {csv_file}")
        
        # Carregar dados JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        logger.info(f"Carregados {len(jobs_data)} registros do JSON")
        
        # Converter para DataFrame
        normalized_data = []
        
        for job in jobs_data:
            normalized_row = self._normalize_job_to_row(job)
            normalized_data.append(normalized_row)
        
        # Criar DataFrame
        df = pd.DataFrame(normalized_data)
        
        # Reordenar colunas para melhor visualização
        column_order = [
            'id', 'title', 'seniority', 'area', 'company_name', 'industry',
            'employment_type', 'work_schedule', 'modality',
            'location_city', 'location_state', 'location_region',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'benefits_count', 'benefits_list', 'rewards_count', 'rewards_list',
            'requirements_must_count', 'requirements_must_list',
            'requirements_nice_count', 'requirements_nice_list',
            'education_level', 'responsibilities_count', 'responsibilities_list',
            'pcd', 'tags_count', 'tags_list',
            'source_name', 'source_url', 'raw_excerpt',
            'confidence', 'parsed_at'
        ]
        
        # Reordenar colunas (manter apenas as que existem)
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Salvar CSV
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        logger.info(f"CSV salvo com {len(df)} linhas e {len(df.columns)} colunas")
        
        # Gerar estatísticas
        self._generate_csv_stats(df)
    
    def _normalize_job_to_row(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar um job JSON para uma linha de CSV"""
        row = {
            'id': hash(job.get('source_url', '') + job.get('title', '')) % 1000000,
            'title': job.get('title', ''),
            'seniority': job.get('seniority', ''),
            'area': job.get('area', ''),
            'company_name': job.get('company_name', ''),
            'industry': job.get('industry', ''),
            'employment_type': job.get('employment_type', ''),
            'work_schedule': job.get('work_schedule', ''),
            'modality': job.get('modality', ''),
            'location_city': job.get('location_city', ''),
            'location_state': job.get('location_state', ''),
            'location_region': job.get('location_region', ''),
            'salary_min': job.get('salary_min'),
            'salary_max': job.get('salary_max'),
            'salary_currency': job.get('salary_currency', ''),
            'salary_period': job.get('salary_period', ''),
            'education_level': job.get('education_level', ''),
            'pcd': job.get('pcd', False),
            'source_name': job.get('source_name', ''),
            'source_url': job.get('source_url', ''),
            'raw_excerpt': job.get('raw_excerpt', ''),
            'confidence': job.get('confidence', 0.0),
            'parsed_at': job.get('parsed_at', '')
        }
        
        # Processar listas
        benefits = job.get('benefits', [])
        row['benefits_count'] = len(benefits)
        row['benefits_list'] = ' | '.join(benefits) if benefits else ''
        
        rewards = job.get('rewards', [])
        row['rewards_count'] = len(rewards)
        row['rewards_list'] = ' | '.join(rewards) if rewards else ''
        
        requirements_must = job.get('requirements_must', [])
        row['requirements_must_count'] = len(requirements_must)
        row['requirements_must_list'] = ' | '.join(requirements_must) if requirements_must else ''
        
        requirements_nice = job.get('requirements_nice', [])
        row['requirements_nice_count'] = len(requirements_nice)
        row['requirements_nice_list'] = ' | '.join(requirements_nice) if requirements_nice else ''
        
        responsibilities = job.get('responsibilities', [])
        row['responsibilities_count'] = len(responsibilities)
        row['responsibilities_list'] = ' | '.join(responsibilities) if responsibilities else ''
        
        tags = job.get('tags', [])
        row['tags_count'] = len(tags)
        row['tags_list'] = ' | '.join(tags) if tags else ''
        
        return row
    
    def _generate_csv_stats(self, df: pd.DataFrame) -> None:
        """Gerar estatísticas do CSV"""
        total_rows = len(df)
        
        logger.info(f"\n=== ESTATÍSTICAS DO CSV GERADO ===")
        logger.info(f"Total de registros: {total_rows}")
        logger.info(f"Total de colunas: {len(df.columns)}")
        
        # Estatísticas de preenchimento
        if 'salary_min' in df.columns:
            with_salary = df['salary_min'].notna().sum()
            logger.info(f"Registros com salário: {with_salary} ({with_salary/total_rows*100:.1f}%)")
        
        if 'benefits_count' in df.columns:
            with_benefits = (df['benefits_count'] > 0).sum()
            logger.info(f"Registros com benefícios: {with_benefits} ({with_benefits/total_rows*100:.1f}%)")
        
        if 'requirements_must_count' in df.columns:
            with_requirements = (df['requirements_must_count'] > 0).sum()
            logger.info(f"Registros com requisitos: {with_requirements} ({with_requirements/total_rows*100:.1f}%)")
        
        # Top valores
        if 'area' in df.columns:
            top_areas = df['area'].value_counts().head(5)
            logger.info(f"\nTop 5 áreas:")
            for area, count in top_areas.items():
                logger.info(f"  {area}: {count}")
        
        if 'seniority' in df.columns:
            top_seniority = df['seniority'].value_counts().head(5)
            logger.info(f"\nTop 5 senioridades:")
            for seniority, count in top_seniority.items():
                logger.info(f"  {seniority}: {count}")
        
        if 'location_city' in df.columns:
            top_cities = df['location_city'].value_counts().head(5)
            logger.info(f"\nTop 5 cidades:")
            for city, count in top_cities.items():
                logger.info(f"  {city}: {count}")
        
        # Estatísticas de qualidade
        if 'confidence' in df.columns:
            avg_confidence = df['confidence'].mean()
            logger.info(f"\nConfiança média: {avg_confidence:.3f}")
            
            confidence_ranges = {
                'Alta (>= 0.8)': (df['confidence'] >= 0.8).sum(),
                'Média (0.6-0.8)': ((df['confidence'] >= 0.6) & (df['confidence'] < 0.8)).sum(),
                'Baixa (< 0.6)': (df['confidence'] < 0.6).sum()
            }
            
            logger.info(f"\nDistribuição de confiança:")
            for range_name, count in confidence_ranges.items():
                logger.info(f"  {range_name}: {count} ({count/total_rows*100:.1f}%)")

    def create_sample_view(self, csv_file: str, sample_file: str, num_samples: int = 5) -> None:
        """Criar arquivo de amostra para visualização"""
        logger.info(f"Criando amostra de {num_samples} registros")
        
        df = pd.read_csv(csv_file)
        
        # Selecionar amostra diversificada
        sample_df = df.head(num_samples)
        
        # Salvar amostra
        sample_df.to_csv(sample_file, index=False, encoding='utf-8')
        
        logger.info(f"Amostra salva em {sample_file}")
        
        # Mostrar preview
        logger.info(f"\n=== PREVIEW DA AMOSTRA ===")
        for idx, row in sample_df.iterrows():
            logger.info(f"\nRegistro {idx + 1}:")
            logger.info(f"  Título: {row.get('title', 'N/A')}")
            logger.info(f"  Área: {row.get('area', 'N/A')}")
            logger.info(f"  Senioridade: {row.get('seniority', 'N/A')}")
            logger.info(f"  Localização: {row.get('location_city', 'N/A')}/{row.get('location_state', 'N/A')}")
            logger.info(f"  Salário: {row.get('salary_min', 'N/A')} - {row.get('salary_max', 'N/A')}")
            logger.info(f"  Benefícios: {row.get('benefits_count', 0)}")
            logger.info(f"  Confiança: {row.get('confidence', 0):.2f}")

if __name__ == "__main__":
    converter = JSONToCSVConverter()
    
    # Arquivos
    json_input = "vagas_industrial_estruturado_avancado.json"
    csv_output = "vagas_industrial_estruturado_avancado.csv"
    sample_output = "vagas_industrial_amostra.csv"
    
    # Converter JSON para CSV
    converter.convert_json_to_csv(json_input, csv_output)
    
    # Criar amostra
    converter.create_sample_view(csv_output, sample_output, num_samples=5)
    
    logger.info("\nConversão concluída com sucesso!")
    logger.info(f"Arquivos gerados:")
    logger.info(f"  - CSV completo: {csv_output}")
    logger.info(f"  - Amostra: {sample_output}")