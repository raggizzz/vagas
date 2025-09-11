#!/usr/bin/env python3
"""
Script para upload de dados estruturados avançados para o Supabase
Baseado na estrutura do arquivo vagas_industrial_estruturado_avancado.json
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseUploaderAdvanced:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print(f"✅ Conectado ao Supabase: {self.supabase_url}")
    
    def clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        if not text or text.lower() in ['nan', 'null', 'none']:
            return None
        return str(text).strip()
    
    def clean_numeric(self, value: Any) -> Optional[float]:
        """Limpa e converte valores numéricos"""
        if value is None or str(value).lower() in ['nan', 'null', 'none', '']:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def clean_array(self, arr: List[str]) -> List[str]:
        """Limpa array removendo valores vazios ou nulos"""
        if not arr:
            return []
        return [self.clean_text(item) for item in arr if self.clean_text(item)]
    
    def insert_or_get_company(self, company_name: str, industry: str = None) -> int:
        """Insere ou busca empresa existente"""
        company_name = self.clean_text(company_name)
        if not company_name:
            return None
        
        # Buscar empresa existente
        result = self.supabase.table('companies').select('id').eq('name', company_name).execute()
        
        if result.data:
            return result.data[0]['id']
        
        # Inserir nova empresa
        company_data = {
            'name': company_name,
            'industry': self.clean_text(industry)
        }
        
        result = self.supabase.table('companies').insert(company_data).execute()
        return result.data[0]['id'] if result.data else None
    
    def insert_job(self, job_data: Dict[str, Any]) -> Optional[int]:
        """Insere uma vaga no Supabase"""
        try:
            # Processar dados da empresa
            company_id = self.insert_or_get_company(
                job_data.get('company_name'),
                job_data.get('industry')
            )
            
            # Preparar dados principais da vaga
            job_record = {
                'title': self.clean_text(job_data.get('title')),
                'seniority': self.clean_text(job_data.get('seniority')),
                'area': self.clean_text(job_data.get('area')),
                'company_id': company_id,
                'company_name': self.clean_text(job_data.get('company_name')),
                'industry': self.clean_text(job_data.get('industry')),
                'employment_type': self.clean_text(job_data.get('employment_type')),
                'work_schedule': self.clean_text(job_data.get('work_schedule')),
                'modality': self.clean_text(job_data.get('modality')),
                'location_city': self.clean_text(job_data.get('location_city')),
                'location_state': self.clean_text(job_data.get('location_state')),
                'location_region': self.clean_text(job_data.get('location_region')),
                'salary_min': self.clean_numeric(job_data.get('salary_min')),
                'salary_max': self.clean_numeric(job_data.get('salary_max')),
                'salary_currency': self.clean_text(job_data.get('salary_currency', 'BRL')),
                'salary_period': self.clean_text(job_data.get('salary_period', 'month')),
                'education_level': self.clean_text(job_data.get('education_level')),
                'pcd': bool(job_data.get('pcd', False)),
                'source_name': self.clean_text(job_data.get('source_name')),
                'source_url': self.clean_text(job_data.get('source_url')),
                'raw_excerpt': self.clean_text(job_data.get('raw_excerpt')),
                'confidence': self.clean_numeric(job_data.get('confidence')),
                'parsed_at': job_data.get('parsed_at'),
                'sector': self.clean_text(job_data.get('industry')),  # Usando industry como sector
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # Remover campos None
            job_record = {k: v for k, v in job_record.items() if v is not None}
            
            # Inserir vaga principal
            result = self.supabase.table('jobs').insert(job_record).execute()
            
            if not result.data:
                print(f"❌ Erro ao inserir vaga: {job_data.get('title')}")
                return None
            
            job_id = result.data[0]['id']
            print(f"✅ Vaga inserida: {job_data.get('title')} (ID: {job_id})")
            
            # Inserir dados relacionados
            self.insert_job_benefits(job_id, job_data.get('benefits', []))
            self.insert_job_rewards(job_id, job_data.get('rewards', []))
            self.insert_job_requirements_must(job_id, job_data.get('requirements_must', []))
            self.insert_job_requirements_nice(job_id, job_data.get('requirements_nice', []))
            self.insert_job_responsibilities(job_id, job_data.get('responsibilities', []))
            self.insert_job_tags(job_id, job_data.get('tags', []))
            
            return job_id
            
        except Exception as e:
            print(f"❌ Erro ao processar vaga {job_data.get('title', 'N/A')}: {str(e)}")
            return None
    
    def insert_job_benefits(self, job_id: int, benefits: List[str]):
        """Insere benefícios da vaga"""
        benefits = self.clean_array(benefits)
        if not benefits:
            return
        
        benefit_records = [{'job_id': job_id, 'benefit': benefit} for benefit in benefits]
        self.supabase.table('job_benefits').insert(benefit_records).execute()
    
    def insert_job_rewards(self, job_id: int, rewards: List[str]):
        """Insere recompensas da vaga"""
        rewards = self.clean_array(rewards)
        if not rewards:
            return
        
        reward_records = [{'job_id': job_id, 'reward': reward} for reward in rewards]
        self.supabase.table('job_rewards').insert(reward_records).execute()
    
    def insert_job_requirements_must(self, job_id: int, requirements: List[str]):
        """Insere requisitos obrigatórios da vaga"""
        requirements = self.clean_array(requirements)
        if not requirements:
            return
        
        requirement_records = [{'job_id': job_id, 'requirement': req} for req in requirements]
        self.supabase.table('job_requirements_must').insert(requirement_records).execute()
    
    def insert_job_requirements_nice(self, job_id: int, requirements: List[str]):
        """Insere requisitos desejáveis da vaga"""
        requirements = self.clean_array(requirements)
        if not requirements:
            return
        
        requirement_records = [{'job_id': job_id, 'requirement': req} for req in requirements]
        self.supabase.table('job_requirements_nice').insert(requirement_records).execute()
    
    def insert_job_responsibilities(self, job_id: int, responsibilities: List[str]):
        """Insere responsabilidades da vaga"""
        responsibilities = self.clean_array(responsibilities)
        if not responsibilities:
            return
        
        responsibility_records = [{'job_id': job_id, 'responsibility': resp} for resp in responsibilities]
        self.supabase.table('job_responsibilities').insert(responsibility_records).execute()
    
    def insert_job_tags(self, job_id: int, tags: List[str]):
        """Insere tags da vaga"""
        tags = self.clean_array(tags)
        if not tags:
            return
        
        tag_records = [{'job_id': job_id, 'tag': tag} for tag in tags]
        self.supabase.table('job_tags').insert(tag_records).execute()
    
    def upload_from_json(self, json_file_path: str, batch_size: int = 10):
        """Faz upload de vagas a partir de um arquivo JSON"""
        print(f"📁 Carregando dados de: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            print(f"📊 Total de vagas encontradas: {len(jobs_data)}")
            
            successful_uploads = 0
            failed_uploads = 0
            
            for i, job_data in enumerate(jobs_data, 1):
                print(f"\n[{i}/{len(jobs_data)}] Processando: {job_data.get('title', 'N/A')}")
                
                job_id = self.insert_job(job_data)
                
                if job_id:
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                
                # Pausa a cada batch para evitar rate limiting
                if i % batch_size == 0:
                    print(f"\n⏸️ Processados {i} registros. Pausando...")
                    import time
                    time.sleep(1)
            
            print(f"\n📈 Resumo do upload:")
            print(f"✅ Sucessos: {successful_uploads}")
            print(f"❌ Falhas: {failed_uploads}")
            print(f"📊 Total: {len(jobs_data)}")
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {json_file_path}")
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON: {json_file_path}")
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
    
    def get_stats(self):
        """Obtém estatísticas das vagas no Supabase"""
        try:
            # Total de vagas
            total_jobs = self.supabase.table('jobs').select('id', count='exact').execute()
            print(f"📊 Total de vagas: {total_jobs.count}")
            
            # Vagas por setor
            sectors = self.supabase.table('jobs').select('sector', count='exact').execute()
            print(f"📊 Setores únicos: {len(set([job['sector'] for job in sectors.data if job['sector']]))}")
            
            # Vagas por modalidade
            modalities = self.supabase.table('jobs').select('modality').execute()
            modality_counts = {}
            for job in modalities.data:
                mod = job.get('modality', 'N/A')
                modality_counts[mod] = modality_counts.get(mod, 0) + 1
            
            print(f"📊 Vagas por modalidade:")
            for mod, count in modality_counts.items():
                print(f"   {mod}: {count}")
            
            # Vagas por senioridade
            seniorities = self.supabase.table('jobs').select('seniority').execute()
            seniority_counts = {}
            for job in seniorities.data:
                sen = job.get('seniority', 'N/A')
                seniority_counts[sen] = seniority_counts.get(sen, 0) + 1
            
            print(f"📊 Vagas por senioridade:")
            for sen, count in seniority_counts.items():
                print(f"   {sen}: {count}")
                
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {str(e)}")

def main():
    """Função principal"""
    uploader = SupabaseUploaderAdvanced()
    
    # Arquivo JSON estruturado avançado
    json_file = 'vagas_industrial_estruturado_avancado.json'
    
    if os.path.exists(json_file):
        print(f"🚀 Iniciando upload do arquivo: {json_file}")
        uploader.upload_from_json(json_file, batch_size=5)
        
        print(f"\n📊 Estatísticas após upload:")
        uploader.get_stats()
    else:
        print(f"❌ Arquivo não encontrado: {json_file}")
        print("📁 Arquivos disponíveis:")
        for file in os.listdir('.'):
            if file.endswith('.json'):
                print(f"   - {file}")

if __name__ == "__main__":
    main()