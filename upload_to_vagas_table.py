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
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no .env")
    
    return create_client(url, key)

def check_vagas_table_structure(supabase: Client):
    """
    Verifica a estrutura da tabela vagas
    """
    try:
        # Tentar buscar uma vaga para ver a estrutura
        response = supabase.table('vagas').select('*').limit(1).execute()
        
        if response.data:
            print("✅ Tabela 'vagas' encontrada")
            print("Estrutura da primeira vaga:")
            for key in response.data[0].keys():
                print(f"  - {key}")
            return True
        else:
            print("ℹ️ Tabela 'vagas' existe mas está vazia")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabela 'vagas': {e}")
        return False

def backup_existing_vagas(supabase: Client) -> List[Dict]:
    """
    Faz backup dos dados existentes na tabela vagas
    """
    try:
        response = supabase.table('vagas').select('*').execute()
        vagas = response.data
        
        if vagas:
            backup_file = f"vagas_backup_{int(time.time())}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(vagas, f, ensure_ascii=False, indent=2)
            print(f"✅ Backup de {len(vagas)} vagas salvo em: {backup_file}")
        else:
            print("ℹ️ Nenhuma vaga existente para backup")
            
        return vagas
        
    except Exception as e:
        print(f"⚠️ Erro ao fazer backup: {e}")
        return []

def clear_vagas_table(supabase: Client):
    """
    Limpa completamente a tabela vagas
    """
    try:
        response = supabase.table('vagas').delete().neq('id', 0).execute()
        print("✅ Tabela vagas limpa com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar tabela: {e}")
        return False

def upload_vagas_batch(supabase: Client, jobs: List[Dict], batch_size: int = 100) -> int:
    """
    Faz upload das vagas em lotes para a tabela 'vagas'
    """
    total_uploaded = 0
    total_jobs = len(jobs)
    
    print(f"📤 Iniciando upload de {total_jobs} vagas em lotes de {batch_size}...")
    
    for i in range(0, total_jobs, batch_size):
        batch = jobs[i:i + batch_size]
        
        try:
            # Preparar dados do lote para a tabela vagas
            batch_data = []
            for job in batch:
                vaga_data = {
                    'external_id': job['external_id'],
                    'titulo': job['title'][:255],  # Mapear title para titulo
                    'empresa': job['company_name'][:255],  # Mapear company_name para empresa
                    'setor': job['sector'],
                    'localizacao': job['location'],  # Mapear location para localizacao
                    'salario_min': job['salary_min'],
                    'salario_max': job['salary_max'],
                    'descricao': job['description'],
                    'modalidade_trabalho': job['work_type']  # Mapear work_type para modalidade_trabalho
                }
                batch_data.append(vaga_data)
            
            # Fazer upload do lote
            response = supabase.table('vagas').insert(batch_data).execute()
            
            if response.data:
                uploaded_count = len(response.data)
                total_uploaded += uploaded_count
                print(f"✅ Lote {i//batch_size + 1}: {uploaded_count} vagas enviadas (Total: {total_uploaded}/{total_jobs})")
            else:
                print(f"⚠️ Lote {i//batch_size + 1}: Nenhuma vaga foi inserida")
                
        except Exception as e:
            print(f"❌ Erro no lote {i//batch_size + 1}: {e}")
            # Tentar inserir individualmente em caso de erro
            for job in batch:
                try:
                    vaga_data = {
                        'external_id': job['external_id'],
                        'titulo': job['title'][:255],
                        'empresa': job['company_name'][:255],
                        'setor': job['sector'],
                        'localizacao': job['location'],
                        'salario_min': job['salary_min'],
                        'salario_max': job['salary_max'],
                        'descricao': job['description'],
                        'modalidade_trabalho': job['work_type']
                    }
                    
                    response = supabase.table('vagas').insert([vaga_data]).execute()
                    if response.data:
                        total_uploaded += 1
                        
                except Exception as individual_error:
                    print(f"❌ Erro individual para vaga {job['external_id']}: {individual_error}")
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
    Verifica o resultado do upload na tabela vagas
    """
    try:
        # Contar total de vagas
        response = supabase.table('vagas').select('id', count='exact').execute()
        total_count = response.count
        
        # Contar por setor
        response = supabase.table('vagas').select('setor').execute()
        sectors = {}
        
        if response.data:
            for vaga in response.data:
                sector = vaga.get('setor', 'Não especificado')
                sectors[sector] = sectors.get(sector, 0) + 1
        
        return {
            'total_vagas': total_count,
            'sectors': sectors
        }
        
    except Exception as e:
        print(f"❌ Erro ao verificar upload: {e}")
        return {'total_vagas': 0, 'sectors': {}}

def main():
    print("🚀 Iniciando upload das vagas normalizadas para a tabela 'vagas' no Supabase...")
    
    # Conectar ao Supabase
    try:
        supabase = get_supabase_client()
        print("✅ Conectado ao Supabase")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return
    
    # Verificar estrutura da tabela vagas
    print("\n🔍 Verificando tabela 'vagas'...")
    if not check_vagas_table_structure(supabase):
        print("❌ Não foi possível acessar a tabela 'vagas'")
        return
    
    # Carregar vagas normalizadas
    jobs = load_normalized_jobs('vagas_normalizadas_individuais.jsonl')
    if not jobs:
        print("❌ Nenhuma vaga para upload")
        return
    
    # Fazer backup das vagas existentes
    print("\n📋 Fazendo backup das vagas existentes...")
    backup_existing_vagas(supabase)
    
    # Limpar tabela
    print("\n🧹 Limpando tabela vagas...")
    if not clear_vagas_table(supabase):
        print("⚠️ Continuando mesmo com erro na limpeza...")
    
    # Fazer upload
    print("\n📤 Fazendo upload das vagas normalizadas...")
    uploaded_count = upload_vagas_batch(supabase, jobs, batch_size=50)
    
    # Verificar resultado
    print("\n🔍 Verificando resultado do upload...")
    verification = verify_upload(supabase)
    
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Vagas carregadas do arquivo: {len(jobs)}")
    print(f"Vagas enviadas com sucesso: {uploaded_count}")
    print(f"Total de vagas na tabela: {verification['total_vagas']}")
    
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