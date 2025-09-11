#!/usr/bin/env python3
"""
Script para upload dos dados processados com skills para o Supabase
Inclui vagas taggeadas, taxonomias e estatísticas
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SkillsSupabaseUploader:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print(f"✅ Conectado ao Supabase: {self.supabase_url}")
    
    def create_skills_tables(self):
        """Cria as tabelas necessárias para skills e taxonomias"""
        print("📋 Criando tabelas para skills e taxonomias...")
        
        # SQL para criar as novas tabelas
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS skills_taxonomy (
                id SERIAL PRIMARY KEY,
                sector VARCHAR(100) NOT NULL,
                skill VARCHAR(255) NOT NULL,
                alias TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(sector, skill)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sector_mapping (
                id SERIAL PRIMARY KEY,
                raw_sector VARCHAR(255) NOT NULL,
                normalized_sector VARCHAR(100) NOT NULL,
                alias TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(raw_sector)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS skills_statistics (
                id SERIAL PRIMARY KEY,
                sector VARCHAR(100) NOT NULL,
                skill VARCHAR(255) NOT NULL,
                count INTEGER NOT NULL,
                total_sector INTEGER NOT NULL,
                percentage DECIMAL(5,2) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(sector, skill)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sector_coverage (
                id SERIAL PRIMARY KEY,
                sector VARCHAR(100) NOT NULL UNIQUE,
                total_jobs INTEGER NOT NULL,
                skills_found INTEGER NOT NULL,
                top_skills TEXT[], -- Array de top 3 skills
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_skills_taxonomy_sector ON skills_taxonomy(sector);
            CREATE INDEX IF NOT EXISTS idx_skills_taxonomy_skill ON skills_taxonomy(skill);
            CREATE INDEX IF NOT EXISTS idx_sector_mapping_raw ON sector_mapping(raw_sector);
            CREATE INDEX IF NOT EXISTS idx_sector_mapping_normalized ON sector_mapping(normalized_sector);
            CREATE INDEX IF NOT EXISTS idx_skills_statistics_sector ON skills_statistics(sector);
            CREATE INDEX IF NOT EXISTS idx_skills_statistics_skill ON skills_statistics(skill);
            CREATE INDEX IF NOT EXISTS idx_sector_coverage_sector ON sector_coverage(sector);
            """
        ]
        
        try:
            for sql in sql_commands:
                if sql.strip():
                    self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            print("✅ Tabelas criadas com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao criar tabelas (podem já existir): {e}")
    
    def upload_skills_taxonomy(self, csv_file: str = 'skills_taxonomy.csv'):
        """Upload da taxonomia de skills"""
        print(f"📤 Fazendo upload da taxonomia de skills de {csv_file}...")
        
        if not os.path.exists(csv_file):
            print(f"❌ Arquivo {csv_file} não encontrado!")
            return
        
        try:
            # Limpar tabela existente
            self.supabase.table('skills_taxonomy').delete().neq('id', 0).execute()
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                
                for row in reader:
                    if row['sector'] and row['skill']:
                        batch.append({
                            'sector': row['sector'].strip(),
                            'skill': row['skill'].strip(),
                            'alias': row.get('alias', '').strip() or None
                        })
                    
                    # Upload em lotes de 100
                    if len(batch) >= 100:
                        self.supabase.table('skills_taxonomy').insert(batch).execute()
                        print(f"  ✅ Uploaded {len(batch)} registros de taxonomia")
                        batch = []
                
                # Upload do último lote
                if batch:
                    self.supabase.table('skills_taxonomy').insert(batch).execute()
                    print(f"  ✅ Uploaded {len(batch)} registros de taxonomia")
            
            print("✅ Taxonomia de skills carregada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar taxonomia: {e}")
    
    def upload_sector_mapping(self, csv_file: str = 'sector_map.csv'):
        """Upload do mapeamento de setores"""
        print(f"📤 Fazendo upload do mapeamento de setores de {csv_file}...")
        
        if not os.path.exists(csv_file):
            print(f"❌ Arquivo {csv_file} não encontrado!")
            return
        
        try:
            # Limpar tabela existente
            self.supabase.table('sector_mapping').delete().neq('id', 0).execute()
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                
                for row in reader:
                    if row['raw_sector'] and row['normalized_sector']:
                        batch.append({
                            'raw_sector': row['raw_sector'].strip(),
                            'normalized_sector': row['normalized_sector'].strip(),
                            'alias': row.get('alias', '').strip() or None
                        })
                    
                    # Upload em lotes de 100
                    if len(batch) >= 100:
                        self.supabase.table('sector_mapping').insert(batch).execute()
                        print(f"  ✅ Uploaded {len(batch)} registros de mapeamento")
                        batch = []
                
                # Upload do último lote
                if batch:
                    self.supabase.table('sector_mapping').insert(batch).execute()
                    print(f"  ✅ Uploaded {len(batch)} registros de mapeamento")
            
            print("✅ Mapeamento de setores carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar mapeamento: {e}")
    
    def upload_skills_statistics(self, csv_file: str = 'skills_agg.csv'):
        """Upload das estatísticas de skills"""
        print(f"📤 Fazendo upload das estatísticas de skills de {csv_file}...")
        
        if not os.path.exists(csv_file):
            print(f"❌ Arquivo {csv_file} não encontrado!")
            return
        
        try:
            # Limpar tabela existente
            self.supabase.table('skills_statistics').delete().neq('id', 0).execute()
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                
                for row in reader:
                    if row['sector'] and row['skill']:
                        batch.append({
                            'sector': row['sector'].strip(),
                            'skill': row['skill'].strip(),
                            'count': int(row['count']) if row['count'] else 0,
                            'total_sector': int(row['total_sector']) if row['total_sector'] else 0,
                            'percentage': float(row['percentage']) if row['percentage'] else 0.0
                        })
                    
                    # Upload em lotes de 100
                    if len(batch) >= 100:
                        self.supabase.table('skills_statistics').insert(batch).execute()
                        print(f"  ✅ Uploaded {len(batch)} registros de estatísticas")
                        batch = []
                
                # Upload do último lote
                if batch:
                    self.supabase.table('skills_statistics').insert(batch).execute()
                    print(f"  ✅ Uploaded {len(batch)} registros de estatísticas")
            
            print("✅ Estatísticas de skills carregadas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar estatísticas: {e}")
    
    def upload_coverage_report(self, csv_file: str = 'coverage_report.csv'):
        """Upload do relatório de cobertura"""
        print(f"📤 Fazendo upload do relatório de cobertura de {csv_file}...")
        
        if not os.path.exists(csv_file):
            print(f"❌ Arquivo {csv_file} não encontrado!")
            return
        
        try:
            # Limpar tabela existente
            self.supabase.table('sector_coverage').delete().neq('id', 0).execute()
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                
                for row in reader:
                    if row['sector']:
                        # Processar top_skills como array
                        top_skills = []
                        if row.get('top_skills'):
                            top_skills = [skill.strip() for skill in row['top_skills'].split(',')]
                        
                        batch.append({
                            'sector': row['sector'].strip(),
                            'total_jobs': int(row['total_jobs']) if row['total_jobs'] else 0,
                            'skills_found': int(row['skills_found']) if row['skills_found'] else 0,
                            'top_skills': top_skills
                        })
                    
                    # Upload em lotes de 50
                    if len(batch) >= 50:
                        self.supabase.table('sector_coverage').insert(batch).execute()
                        print(f"  ✅ Uploaded {len(batch)} registros de cobertura")
                        batch = []
                
                # Upload do último lote
                if batch:
                    self.supabase.table('sector_coverage').insert(batch).execute()
                    print(f"  ✅ Uploaded {len(batch)} registros de cobertura")
            
            print("✅ Relatório de cobertura carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar relatório de cobertura: {e}")
    
    def upload_tagged_jobs(self, jsonl_file: str = 'vagas_tagged.jsonl'):
        """Upload das vagas com skills taggeadas"""
        print(f"📤 Fazendo upload das vagas taggeadas de {jsonl_file}...")
        
        if not os.path.exists(jsonl_file):
            print(f"❌ Arquivo {jsonl_file} não encontrado!")
            return
        
        try:
            jobs_uploaded = 0
            skills_uploaded = 0
            
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        job_data = json.loads(line.strip())
                        
                        # Primeiro, inserir/buscar empresa
                        company_data = {
                            'name': job_data.get('empresa', 'Empresa não informada'),
                            'industry': job_data.get('setor_resolvido', 'Não informado')
                        }
                        
                        company_result = self.supabase.table('companies').upsert(
                            company_data, on_conflict='name'
                        ).execute()
                        company_id = company_result.data[0]['id']
                        
                        # Preparar dados da vaga conforme schema avançado
                        job_record = {
                            'title': (job_data.get('titulo', 'Título não informado') or 'Título não informado')[:500],
                            'company_id': company_id,
                            'seniority': (job_data.get('senioridade', 'Não informado') or 'Não informado')[:50],
                            'area': (job_data.get('area', 'Não informado') or 'Não informado')[:100],
                            'employment_type': (job_data.get('tipo_contrato', 'CLT') or 'CLT')[:50],
                            'work_schedule': job_data.get('jornada_trabalho', 'Não informado') or 'Não informado',
                            'modality': (job_data.get('modalidade', 'Presencial') or 'Presencial')[:50],
                            'location_city': (job_data.get('cidade', 'Não informado') or 'Não informado')[:100],
                            'location_state': (job_data.get('estado', 'Não informado') or 'Não informado')[:10],
                            'source_name': 'catho',
                            'description': job_data.get('descricao_completa', '') or '',
                            'external_id': f"tagged_{line_num}"
                        }
                        
                        # Inserir vaga
                        job_result = self.supabase.table('jobs').insert(job_record).execute()
                        job_id = job_result.data[0]['id']
                        jobs_uploaded += 1
                        
                        # Inserir skills como requisitos obrigatórios
                        skills = job_data.get('skills_mapeadas', [])
                        if skills:
                            skill_records = []
                            for skill in skills:
                                skill_records.append({
                                    'job_id': job_id,
                                    'requirement': skill
                                })
                            
                            if skill_records:
                                self.supabase.table('job_requirements_must').insert(skill_records).execute()
                                skills_uploaded += len(skill_records)
                        
                        if line_num % 100 == 0:
                            print(f"  ✅ Processadas {line_num} vagas, {jobs_uploaded} inseridas, {skills_uploaded} skills")
                    
                    except json.JSONDecodeError as e:
                        print(f"  ⚠️ Erro ao processar linha {line_num}: {e}")
                        continue
                    except Exception as e:
                        print(f"  ⚠️ Erro ao inserir vaga linha {line_num}: {e}")
                        continue
            
            print(f"✅ {jobs_uploaded} vagas e {skills_uploaded} skills carregadas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar vagas taggeadas: {e}")
    
    def run_complete_upload(self):
        """Executa o upload completo de todos os dados"""
        print("🚀 Iniciando upload completo dos dados processados...")
        
        # 1. Criar tabelas
        self.create_skills_tables()
        
        # 2. Upload das taxonomias
        self.upload_skills_taxonomy()
        self.upload_sector_mapping()
        
        # 3. Upload das estatísticas
        self.upload_skills_statistics()
        self.upload_coverage_report()
        
        # 4. Upload das vagas taggeadas
        self.upload_tagged_jobs()
        
        print("\n🎉 Upload completo finalizado!")
        print("\n📊 Resumo dos dados carregados:")
        
        # Mostrar estatísticas
        try:
            # Contar registros em cada tabela
            tables = ['skills_taxonomy', 'sector_mapping', 'skills_statistics', 'sector_coverage', 'jobs']
            for table in tables:
                try:
                    result = self.supabase.table(table).select('id', count='exact').execute()
                    count = result.count if hasattr(result, 'count') else len(result.data)
                    print(f"  📋 {table}: {count} registros")
                except:
                    print(f"  📋 {table}: Erro ao contar registros")
        except Exception as e:
            print(f"  ⚠️ Erro ao obter estatísticas: {e}")

def main():
    """Função principal"""
    try:
        uploader = SkillsSupabaseUploader()
        uploader.run_complete_upload()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())