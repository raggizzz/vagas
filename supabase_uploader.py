import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd

# Carrega variáveis de ambiente
load_dotenv()

class SupabaseUploader:
    def __init__(self):
        """Inicializa o cliente Supabase"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print(f"✅ Conectado ao Supabase: {self.supabase_url}")
    
    def get_or_create_company(self, company_name: str) -> Optional[int]:
        """Busca ou cria uma empresa e retorna seu ID"""
        if not company_name or pd.isna(company_name) or str(company_name).strip() == '':
            return None
        
        company_name = str(company_name).strip()
        
        # Busca empresa existente
        result = self.supabase.table('companies').select('id').eq('name', company_name).execute()
        
        if result.data:
            return result.data[0]['id']
        
        # Cria nova empresa
        try:
            result = self.supabase.table('companies').insert({'name': company_name}).execute()
            return result.data[0]['id']
        except Exception as e:
            print(f"⚠️ Erro ao criar empresa '{company_name}': {e}")
            return None
    
    def upload_job(self, job_data: Dict) -> Optional[int]:
        """Faz upload de uma vaga e retorna o ID inserido"""
        try:
            # Prepara dados da vaga principal
            company_id = self.get_or_create_company(job_data.get('company', ''))
            
            # Função auxiliar para limpar strings
            def clean_string(value, default=''):
                if value is None or pd.isna(value):
                    return default
                return str(value).strip() if str(value).strip() else default
            
            job_record = {
                'external_id': clean_string(job_data.get('id')),
                'title': clean_string(job_data.get('title')),
                'company_id': company_id,
                'company_name': clean_string(job_data.get('company')),
                'location': clean_string(job_data.get('location')),
                'work_type': clean_string(job_data.get('work_type')),
                'contract_type': clean_string(job_data.get('contract_type')),
                'work_model': clean_string(job_data.get('work_model')),
                'description': clean_string(job_data.get('description')),
                'description_raw': clean_string(job_data.get('description_raw')),
                'link': clean_string(job_data.get('link')),
                'published_date': job_data.get('published_date'),
                'extraction_timestamp': job_data.get('extraction_timestamp'),
                'data_quality_score': job_data.get('data_quality_score', 0),
                'sector': clean_string(job_data.get('sector'))
            }
            
            # Remove campos None/vazios
            job_record = {k: v for k, v in job_record.items() if v is not None and v != ''}
            
            # Insere vaga principal
            result = self.supabase.table('jobs').insert(job_record).execute()
            job_id = result.data[0]['id']
            
            # Upload de dados relacionados
            self._upload_salary_data(job_id, job_data.get('salary', {}))
            self._upload_responsibilities(job_id, job_data.get('responsibilities', []))
            self._upload_benefits(job_id, job_data.get('benefits', []))
            self._upload_education(job_id, job_data.get('education', []))
            self._upload_skills(job_id, job_data.get('skills', []))
            self._upload_experience(job_id, job_data.get('experience'))
            
            return job_id
            
        except Exception as e:
            print(f"❌ Erro ao fazer upload da vaga '{job_data.get('title', 'N/A')}': {e}")
            return None
    
    def _upload_salary_data(self, job_id: int, salary_data: Dict):
        """Upload de dados salariais"""
        if not salary_data:
            return
        
        try:
            salary_record = {
                'job_id': job_id,
                'min_salary': salary_data.get('min_salary'),
                'max_salary': salary_data.get('max_salary'),
                'salary_type': salary_data.get('salary_type'),
                'commission': str(salary_data.get('commission')) if salary_data.get('commission') else None,
                'currency': salary_data.get('currency', 'BRL'),
                'period': salary_data.get('period', 'mensal')
            }
            
            # Remove campos None
            salary_record = {k: v for k, v in salary_record.items() if v is not None}
            
            if len(salary_record) > 1:  # Mais que apenas job_id
                self.supabase.table('job_salaries').insert(salary_record).execute()
                
        except Exception as e:
            print(f"⚠️ Erro ao inserir dados salariais para job_id {job_id}: {e}")
    
    def _upload_responsibilities(self, job_id: int, responsibilities: List[str]):
        """Upload de responsabilidades"""
        if not responsibilities:
            return
        
        try:
            records = [{
                'job_id': job_id,
                'responsibility': str(resp).strip()
            } for resp in responsibilities if resp and not pd.isna(resp) and str(resp).strip()]
            
            if records:
                self.supabase.table('job_responsibilities').insert(records).execute()
                
        except Exception as e:
            print(f"⚠️ Erro ao inserir responsabilidades para job_id {job_id}: {e}")
    
    def _upload_benefits(self, job_id: int, benefits: List[str]):
        """Upload de benefícios"""
        if not benefits:
            return
        
        try:
            records = [{
                'job_id': job_id,
                'benefit': str(benefit).strip()
            } for benefit in benefits if benefit and not pd.isna(benefit) and str(benefit).strip()]
            
            if records:
                self.supabase.table('job_benefits').insert(records).execute()
                
        except Exception as e:
            print(f"⚠️ Erro ao inserir benefícios para job_id {job_id}: {e}")
    
    def _upload_education(self, job_id: int, education: List[str]):
        """Upload de requisitos educacionais"""
        if not education:
            return
        
        try:
            records = [{
                'job_id': job_id,
                'education_level': str(edu).strip()
            } for edu in education if edu and not pd.isna(edu) and str(edu).strip()]
            
            if records:
                self.supabase.table('job_education').insert(records).execute()
                
        except Exception as e:
            print(f"⚠️ Erro ao inserir educação para job_id {job_id}: {e}")
    
    def _upload_skills(self, job_id: int, skills: List[str]):
        """Upload de habilidades"""
        if not skills:
            return
        
        try:
            records = [{
                'job_id': job_id,
                'skill': str(skill).strip()
            } for skill in skills if skill and not pd.isna(skill) and str(skill).strip()]
            
            if records:
                self.supabase.table('job_skills').insert(records).execute()
                
        except Exception as e:
            print(f"⚠️ Erro ao inserir habilidades para job_id {job_id}: {e}")
    
    def _upload_experience(self, job_id: int, experience: str):
        """Upload de requisitos de experiência"""
        if not experience or not experience.strip():
            return
        
        try:
            record = {
                'job_id': job_id,
                'experience_description': experience.strip()
            }
            
            self.supabase.table('job_experience').insert(record).execute()
            
        except Exception as e:
            print(f"⚠️ Erro ao inserir experiência para job_id {job_id}: {e}")
    
    def upload_json_file(self, json_file_path: str, batch_size: int = 100):
        """Faz upload de um arquivo JSON completo"""
        print(f"🚀 Iniciando upload do arquivo: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            jobs = data.get('jobs', [])
            total_jobs = len(jobs)
            
            print(f"📊 Total de vagas a processar: {total_jobs}")
            
            uploaded_count = 0
            failed_count = 0
            
            for i, job in enumerate(jobs):
                if i % batch_size == 0:
                    print(f"⚡ Processando lote {i//batch_size + 1} (vagas {i+1}-{min(i+batch_size, total_jobs)})...")
                
                job_id = self.upload_job(job)
                
                if job_id:
                    uploaded_count += 1
                else:
                    failed_count += 1
                
                # Progress update a cada 500 vagas
                if (i + 1) % 500 == 0:
                    print(f"📈 Progresso: {i+1}/{total_jobs} ({(i+1)/total_jobs*100:.1f}%) - Sucesso: {uploaded_count}, Falhas: {failed_count}")
            
            print(f"\n✅ Upload concluído!")
            print(f"📊 Estatísticas finais:")
            print(f"   ✅ Vagas enviadas com sucesso: {uploaded_count}")
            print(f"   ❌ Falhas: {failed_count}")
            print(f"   📈 Taxa de sucesso: {uploaded_count/total_jobs*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo JSON: {e}")
    
    def get_database_stats(self):
        """Retorna estatísticas do banco de dados"""
        try:
            # Conta registros em cada tabela
            jobs_count = self.supabase.table('jobs').select('id', count='exact').execute().count
            companies_count = self.supabase.table('companies').select('id', count='exact').execute().count
            salaries_count = self.supabase.table('job_salaries').select('id', count='exact').execute().count
            benefits_count = self.supabase.table('job_benefits').select('id', count='exact').execute().count
            
            print(f"\n📊 Estatísticas do Banco de Dados:")
            print(f"   👔 Vagas: {jobs_count}")
            print(f"   🏢 Empresas: {companies_count}")
            print(f"   💰 Registros salariais: {salaries_count}")
            print(f"   🎁 Benefícios: {benefits_count}")
            
            return {
                'jobs': jobs_count,
                'companies': companies_count,
                'salaries': salaries_count,
                'benefits': benefits_count
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return None

def main():
    """Função principal para teste"""
    try:
        uploader = SupabaseUploader()
        
        # Verifica se o arquivo JSON existe
        json_file = 'catho_worker3_master_extraction.json'
        if not os.path.exists(json_file):
            print(f"❌ Arquivo {json_file} não encontrado!")
            return
        
        # Faz upload dos dados
        uploader.upload_json_file(json_file)
        
        # Mostra estatísticas finais
        uploader.get_database_stats()
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        print("\n💡 Certifique-se de que:")
        print("   1. O arquivo .env existe com as credenciais do Supabase")
        print("   2. O schema SQL foi executado no Supabase")
        print("   3. As credenciais estão corretas")

if __name__ == "__main__":
    main()