import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Any
import time

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_client() -> Client:
    """
    Cria e retorna cliente Supabase
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')  # Usar SUPABASE_KEY em vez de SUPABASE_ANON_KEY
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no .env")
    
    return create_client(url, key)

def create_jobs_table(supabase: Client):
    """
    Cria a tabela jobs usando RPC se não existir
    """
    try:
        # Tentar criar a tabela via RPC
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.jobs (
            id BIGSERIAL PRIMARY KEY,
            external_id VARCHAR(50) UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            sector TEXT,
            location TEXT,
            salary_min DECIMAL(10,2),
            salary_max DECIMAL(10,2),
            description TEXT,
            work_type TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Criar índices para otimização
        CREATE INDEX IF NOT EXISTS idx_jobs_external_id ON public.jobs(external_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON public.jobs(company_name);
        CREATE INDEX IF NOT EXISTS idx_jobs_sector ON public.jobs(sector);
        CREATE INDEX IF NOT EXISTS idx_jobs_location ON public.jobs(location);
        """
        
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Tabela jobs criada/verificada com sucesso")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao criar tabela via RPC: {e}")
        print("ℹ️ A tabela pode já existir ou precisar ser criada manualmente")
        return False

def backup_existing_jobs(supabase: Client) -> List[Dict]:
    """
    Faz backup dos dados existentes na tabela jobs
    """
    try:
        response = supabase.table('jobs').select('*').execute()
        jobs = response.data
        
        if jobs:
            backup_file = f"jobs_backup_{int(time.time())}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            print(f"✅ Backup de {len(jobs)} vagas salvo em: {backup_file}")
        else:
            print("ℹ️ Nenhuma vaga existente para backup")
            
        return jobs
        
    except Exception as e:
        print(f"⚠️ Erro ao fazer backup: {e}")
        return []

def clear_jobs_table(supabase: Client):
    """
    Limpa completamente a tabela jobs
    """
    try:
        response = supabase.table('jobs').delete().neq('id', 0).execute()
        print("✅ Tabela jobs limpa com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar tabela: {e}")
        return False

def upload_jobs_batch(supabase: Client, jobs: List[Dict], batch_size: int = 100) -> int:
    """
    Faz upload das vagas em lotes
    """
    total_uploaded = 0
    total_jobs = len(jobs)
    
    print(f"📤 Iniciando upload de {total_jobs} vagas em lotes de {batch_size}...")
    
    for i in range(0, total_jobs, batch_size):
        batch = jobs[i:i + batch_size]
        
        try:
            # Preparar dados do lote
            batch_data = []
            for job in batch:
                job_data = {
                    'external_id': job['external_id'],
                    'title': job['title'][:255],  # Limitar título
                    'company_name': job['company_name'][:255],  # Limitar nome da empresa
                    'sector': job['sector'],
                    'location': job['location'],
                    'salary_min': job['salary_min'],
                    'salary_max': job['salary_max'],
                    'description': job['description'],
                    'work_type': job['work_type']
                }
                batch_data.append(job_data)
            
            # Fazer upload do lote
            response = supabase.table('jobs').insert(batch_data).execute()
            
            if response.data:
                uploaded_count = len(response.data)
                total_uploaded += uploaded_count
                print(f"✅ Lote {i//batch_size + 1}: {uploaded_count} vagas enviadas (Total: {total_uploaded}/{total_jobs})")
            else:
                print(f"⚠️ Lote {i//batch_size + 1}: Nenhuma vaga foi inserida")
                
        except Exception as e:
            print(f"❌ Erro no lote {i//batch_size + 1}: {e}")
            continue
    
    return total_uploaded

def load_normalized_jobs(file_path: str) -> List[Dict]:
    """
    Carrega as vagas normalizadas do arquivo JSONL
    """
    jobs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    job = json.loads(line.strip())
                    jobs.append(job)
                except json.JSONDecodeError as e:
                    print(f"Erro na linha {line_num}: {e}")
                    continue
        
        print(f"📋 Carregadas {len(jobs)} vagas do arquivo {file_path}")
        return jobs
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return []

def verify_upload(supabase: Client) -> Dict[str, Any]:
    """
    Verifica o resultado do upload
    """
    try:
        # Contar total de vagas
        response = supabase.table('jobs').select('id', count='exact').execute()
        total_count = response.count
        
        # Contar por setor
        response = supabase.table('jobs').select('sector', count='exact').execute()
        sectors = {}
        
        if response.data:
            for job in response.data:
                sector = job.get('sector', 'Não especificado')
                sectors[sector] = sectors.get(sector, 0) + 1
        
        return {
            'total_jobs': total_count,
            'sectors': sectors
        }
        
    except Exception as e:
        print(f"❌ Erro ao verificar upload: {e}")
        return {'total_jobs': 0, 'sectors': {}}

def main():
    print("🚀 Iniciando upload das vagas normalizadas para o Supabase...")
    
    # Conectar ao Supabase
    try:
        supabase = get_supabase_client()
        print("✅ Conectado ao Supabase")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return
    
    # Carregar vagas normalizadas
    jobs = load_normalized_jobs('vagas_normalizadas_individuais.jsonl')
    if not jobs:
        print("❌ Nenhuma vaga para upload")
        return
    
    # Fazer backup das vagas existentes
    print("\n📋 Fazendo backup das vagas existentes...")
    backup_existing_jobs(supabase)
    
    # Limpar tabela
    print("\n🧹 Limpando tabela jobs...")
    if not clear_jobs_table(supabase):
        print("⚠️ Continuando mesmo com erro na limpeza...")
    
    # Fazer upload
    print("\n📤 Fazendo upload das vagas normalizadas...")
    uploaded_count = upload_jobs_batch(supabase, jobs, batch_size=50)
    
    # Verificar resultado
    print("\n🔍 Verificando resultado do upload...")
    verification = verify_upload(supabase)
    
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Vagas carregadas do arquivo: {len(jobs)}")
    print(f"Vagas enviadas com sucesso: {uploaded_count}")
    print(f"Total de vagas na tabela: {verification['total_jobs']}")
    
    if verification['sectors']:
        print(f"\nVagas por setor:")
        for sector, count in sorted(verification['sectors'].items()):
            print(f"  {sector}: {count} vagas")
    
    if uploaded_count == len(jobs):
        print("\n🎉 Upload concluído com sucesso!")
    else:
        print(f"\n⚠️ Upload parcial: {uploaded_count}/{len(jobs)} vagas enviadas")

if __name__ == "__main__":
    main()