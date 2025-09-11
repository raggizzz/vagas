#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fazer upload do arquivo vagas_todos_setores_estruturadas_completo.jsonl
para o Supabase, garantindo vagas únicas e setores sem acentos.
"""

import json
import os
import pandas as pd
import unicodedata
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import hashlib
import time

# Carregar variáveis de ambiente
load_dotenv()

class JSONLToSupabaseUploader:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.sector_map = self.load_sector_map()
        
    def load_sector_map(self):
        """Carrega o mapeamento de setores do CSV"""
        try:
            df = pd.read_csv('sector_map.csv')
            return dict(zip(df['raw_sector'], df['normalized_sector']))
        except Exception as e:
            print(f"Erro ao carregar sector_map.csv: {e}")
            return {}
    
    def remove_accents(self, text):
        """Remove acentos de uma string"""
        if not text:
            return text
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    def normalize_sector(self, sector):
        """Normaliza o setor removendo acentos e aplicando mapeamento"""
        if not sector:
            return "Outros"
        
        # Remove acentos
        normalized = self.remove_accents(sector)
        
        # Aplica mapeamento se existir
        if normalized in self.sector_map:
            return self.sector_map[normalized]
        
        return normalized
    
    def generate_external_id(self, job_data):
        """Gera um external_id único baseado no conteúdo da vaga"""
        # Usa campos únicos para gerar hash
        unique_content = f"{job_data.get('id', '')}-{job_data.get('informacoes_basicas', {}).get('titulo', '')}-{job_data.get('informacoes_basicas', {}).get('empresa_principal', '')}"
        return hashlib.md5(unique_content.encode()).hexdigest()
    
    def map_jsonl_to_jobs_table(self, job_data):
        """Mapeia dados do JSONL para a estrutura da tabela jobs"""
        info_basicas = job_data.get('informacoes_basicas', {})
        localizacao = job_data.get('localizacao', {})
        remuneracao = job_data.get('remuneracao', {})
        jornada = job_data.get('jornada_trabalho', {})
        requisitos = job_data.get('requisitos', {})
        habilidades = job_data.get('habilidades_e_competencias', {})
        
        # Normaliza setor
        setor_original = info_basicas.get('setor', '')
        setor_normalizado = self.normalize_sector(setor_original)
        
        mapped_data = {
            'external_id': self.generate_external_id(job_data),
            'title': info_basicas.get('titulo', ''),
            'company_name': info_basicas.get('empresa_principal', ''),
            'sector': setor_normalizado,
            'location': f"{localizacao.get('cidade_extraida', '')}, {localizacao.get('estado_extraido', '')}".strip(', '),
            'salary_min': remuneracao.get('valor_minimo'),
            'salary_max': remuneracao.get('valor_maximo'),
            'description': job_data.get('descricao_completa', {}).get('texto_completo', ''),
            'work_type': jornada.get('modalidade', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return mapped_data
    
    def backup_current_jobs(self):
        """Faz backup da tabela jobs atual"""
        print("Fazendo backup da tabela jobs atual...")
        try:
            response = self.supabase.table('jobs').select('*').execute()
            backup_data = response.data
            
            # Salva backup em arquivo
            backup_filename = f"jobs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            print(f"Backup salvo em: {backup_filename}")
            print(f"Total de registros no backup: {len(backup_data)}")
            return backup_filename
        except Exception as e:
            print(f"Erro ao fazer backup: {e}")
            return None
    
    def clear_jobs_table(self):
        """Limpa completamente a tabela jobs"""
        print("Limpando tabela jobs...")
        try:
            # Deleta todos os registros
            response = self.supabase.table('jobs').delete().neq('id', 0).execute()
            print("Tabela jobs limpa com sucesso!")
        except Exception as e:
            print(f"Erro ao limpar tabela jobs: {e}")
            raise
    
    def load_jsonl_data(self, filename):
        """Carrega dados do arquivo JSONL"""
        print(f"Carregando dados de {filename}...")
        jobs_data = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            job_data = json.loads(line)
                            jobs_data.append(job_data)
                        except json.JSONDecodeError as e:
                            print(f"Erro ao decodificar JSON na linha {line_num}: {e}")
                            continue
            
            print(f"Total de vagas carregadas: {len(jobs_data)}")
            return jobs_data
        except Exception as e:
            print(f"Erro ao carregar arquivo JSONL: {e}")
            raise
    
    def upload_jobs_batch(self, jobs_batch):
        """Faz upload de um lote de vagas"""
        try:
            response = self.supabase.table('jobs').upsert(jobs_batch).execute()
            return len(jobs_batch)
        except Exception as e:
            print(f"Erro ao fazer upload do lote: {e}")
            return 0
    
    def upload_all_jobs(self, jobs_data, batch_size=50):
        """Faz upload de todas as vagas em lotes"""
        print(f"Iniciando upload de {len(jobs_data)} vagas em lotes de {batch_size}...")
        
        mapped_jobs = []
        skipped_jobs = 0
        
        # Mapeia todos os jobs
        for job_data in jobs_data:
            try:
                mapped_job = self.map_jsonl_to_jobs_table(job_data)
                mapped_jobs.append(mapped_job)
            except Exception as e:
                print(f"Erro ao mapear job ID {job_data.get('id', 'N/A')}: {e}")
                skipped_jobs += 1
                continue
        
        print(f"Jobs mapeados: {len(mapped_jobs)}, Jobs ignorados: {skipped_jobs}")
        
        # Upload em lotes
        uploaded_count = 0
        total_batches = (len(mapped_jobs) + batch_size - 1) // batch_size
        
        for i in range(0, len(mapped_jobs), batch_size):
            batch = mapped_jobs[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"Uploading lote {batch_num}/{total_batches} ({len(batch)} vagas)...")
            
            uploaded = self.upload_jobs_batch(batch)
            uploaded_count += uploaded
            
            # Pausa para evitar rate limiting
            if batch_num < total_batches:
                time.sleep(1)
        
        print(f"Upload concluído! Total de vagas enviadas: {uploaded_count}")
        return uploaded_count
    
    def verify_upload(self):
        """Verifica se o upload foi bem-sucedido"""
        print("Verificando upload...")
        try:
            response = self.supabase.table('jobs').select('id, external_id, title, company, sector').execute()
            jobs = response.data
            
            print(f"Total de vagas na tabela: {len(jobs)}")
            
            # Verifica setores únicos
            sectors = set(job['sector'] for job in jobs if job['sector'])
            print(f"Setores únicos encontrados: {sorted(sectors)}")
            
            # Verifica duplicatas por external_id
            external_ids = [job['external_id'] for job in jobs]
            duplicates = len(external_ids) - len(set(external_ids))
            print(f"Duplicatas por external_id: {duplicates}")
            
            return len(jobs)
        except Exception as e:
            print(f"Erro ao verificar upload: {e}")
            return 0
    
    def run_full_upload(self, jsonl_filename='vagas_todos_setores_estruturadas_completo.jsonl'):
        """Executa o processo completo de upload"""
        print("=== INICIANDO UPLOAD COMPLETO DO JSONL PARA SUPABASE ===")
        print(f"Timestamp: {datetime.now()}")
        
        try:
            # 1. Backup
            backup_file = self.backup_current_jobs()
            
            # 2. Limpar tabela
            self.clear_jobs_table()
            
            # 3. Carregar dados do JSONL
            jobs_data = self.load_jsonl_data(jsonl_filename)
            
            # 4. Upload
            uploaded_count = self.upload_all_jobs(jobs_data)
            
            # 5. Verificação
            final_count = self.verify_upload()
            
            print("\n=== RESUMO DO UPLOAD ===")
            print(f"Arquivo processado: {jsonl_filename}")
            print(f"Vagas no arquivo: {len(jobs_data)}")
            print(f"Vagas enviadas: {uploaded_count}")
            print(f"Vagas na tabela final: {final_count}")
            print(f"Backup salvo em: {backup_file}")
            print("Upload concluído com sucesso!")
            
        except Exception as e:
            print(f"Erro durante o upload: {e}")
            raise

if __name__ == "__main__":
    uploader = JSONLToSupabaseUploader()
    uploader.run_full_upload()