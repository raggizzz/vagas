import json
import pandas as pd
from supabase import create_client, Client
import os
from datetime import datetime
import re
from typing import List, Dict, Any
import glob

# Configurações do Supabase
SUPABASE_URL = "https://your-project.supabase.co"  # Substitua pela sua URL
SUPABASE_KEY = "your-anon-key"  # Substitua pela sua chave

# Inicializar cliente Supabase
def init_supabase() -> Client:
    """Inicializa conexão com Supabase"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return None

def extract_salary_info(description: str, title: str) -> Dict[str, Any]:
    """Extrai informações de salário do texto"""
    text = f"{title} {description}".lower()
    
    # Padrões para detectar salários
    salary_patterns = [
        r'r\$\s*([\d.,]+)\s*(?:a|até|-)\s*r\$\s*([\d.,]+)',  # R$ 1.000 a R$ 2.000
        r'salário\s*:?\s*r\$\s*([\d.,]+)',  # Salário: R$ 1.000
        r'([\d.,]+)\s*(?:a|até|-)\s*([\d.,]+)\s*reais',  # 1.000 a 2.000 reais
        r'entre\s*r\$\s*([\d.,]+)\s*e\s*r\$\s*([\d.,]+)',  # Entre R$ 1.000 e R$ 2.000
    ]
    
    salary_min = None
    salary_max = None
    salary_text = ""
    
    for pattern in salary_patterns:
        matches = re.findall(pattern, text)
        if matches:
            match = matches[0]
            if isinstance(match, tuple) and len(match) == 2:
                try:
                    min_val = float(match[0].replace('.', '').replace(',', '.'))
                    max_val = float(match[1].replace('.', '').replace(',', '.'))
                    salary_min = min(min_val, max_val)
                    salary_max = max(min_val, max_val)
                    salary_text = f"R$ {salary_min:,.2f} - R$ {salary_max:,.2f}"
                    break
                except:
                    continue
            elif isinstance(match, str):
                try:
                    val = float(match.replace('.', '').replace(',', '.'))
                    salary_min = val
                    salary_max = val
                    salary_text = f"R$ {val:,.2f}"
                    break
                except:
                    continue
    
    return {
        'salary_min': salary_min,
        'salary_max': salary_max,
        'salary_text': salary_text,
        'has_salary': salary_min is not None
    }

def calculate_data_quality_score(job: Dict[str, Any]) -> float:
    """Calcula score de qualidade dos dados da vaga"""
    score = 0.0
    
    # Título (obrigatório)
    if job.get('title') and len(job['title'].strip()) > 5:
        score += 0.3
    
    # Empresa
    if job.get('company') and len(job['company'].strip()) > 2:
        score += 0.2
    
    # Localização
    if job.get('location') and len(job['location'].strip()) > 2:
        score += 0.15
    
    # Descrição
    if job.get('description') and len(job['description'].strip()) > 20:
        score += 0.2
    
    # Link
    if job.get('link') and job['link'].startswith('http'):
        score += 0.1
    
    # Classificação de setor com confiança
    if job.get('sector_confidence', 0) > 0:
        score += 0.05
    
    return min(score, 1.0)

def prepare_job_for_database(job: Dict[str, Any]) -> Dict[str, Any]:
    """Prepara dados da vaga para inserção no banco"""
    # Extrai informações de salário
    salary_info = extract_salary_info(
        job.get('description', ''), 
        job.get('title', '')
    )
    
    # Calcula score de qualidade
    quality_score = calculate_data_quality_score(job)
    
    # Prepara dados
    db_job = {
        'title': job.get('title', '').strip()[:500],  # Limita tamanho
        'company': job.get('company', '').strip()[:200] or None,
        'location': job.get('location', '').strip()[:200] or None,
        'description': job.get('description', '').strip() or None,
        'link': job.get('link', '').strip() or None,
        
        # Informações de salário
        'salary_min': salary_info['salary_min'],
        'salary_max': salary_info['salary_max'],
        'salary_text': salary_info['salary_text'] or None,
        
        # Informações de setor
        'source_sector': job.get('source_sector', '').strip() or None,
        'source_sector_name': job.get('source_sector_name', '').strip() or None,
        'classified_sector': job.get('classified_sector', 'outros'),
        'classified_sector_name': job.get('classified_sector_name', 'Outros'),
        'sector_confidence': job.get('sector_confidence', 0),
        
        # Metadados
        'extraction_date': job.get('extraction_date'),
        'extraction_method': job.get('extraction_method', 'catho_sectors'),
        'page_number': job.get('page'),
        'source_url': job.get('link'),
        
        # Qualidade
        'data_quality_score': quality_score,
        'has_salary': salary_info['has_salary'],
        'has_description': bool(job.get('description', '').strip()),
        'has_location': bool(job.get('location', '').strip())
    }
    
    return db_job

def upload_jobs_to_supabase(jobs_file: str, batch_size: int = 100) -> bool:
    """Faz upload das vagas para o Supabase"""
    print(f"🚀 Iniciando upload para Supabase...")
    print(f"📁 Arquivo: {jobs_file}")
    
    # Inicializa Supabase
    supabase = init_supabase()
    if not supabase:
        return False
    
    try:
        # Carrega dados do arquivo JSON
        with open(jobs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        print(f"📊 Total de vagas a processar: {len(jobs)}")
        
        if not jobs:
            print("❌ Nenhuma vaga encontrada no arquivo")
            return False
        
        # Processa vagas em lotes
        total_uploaded = 0
        total_errors = 0
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(jobs) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processando lote {batch_num}/{total_batches} ({len(batch)} vagas)")
            
            # Prepara dados do lote
            prepared_jobs = []
            for job in batch:
                try:
                    prepared_job = prepare_job_for_database(job)
                    prepared_jobs.append(prepared_job)
                except Exception as e:
                    print(f"   ⚠️ Erro ao preparar vaga: {e}")
                    total_errors += 1
                    continue
            
            if not prepared_jobs:
                print(f"   ❌ Nenhuma vaga válida no lote {batch_num}")
                continue
            
            # Faz upload do lote
            try:
                result = supabase.table('vagas').insert(prepared_jobs).execute()
                
                if result.data:
                    uploaded_count = len(result.data)
                    total_uploaded += uploaded_count
                    print(f"   ✅ {uploaded_count} vagas inseridas com sucesso")
                else:
                    print(f"   ❌ Erro no upload do lote {batch_num}")
                    total_errors += len(prepared_jobs)
                    
            except Exception as e:
                print(f"   ❌ Erro no upload do lote {batch_num}: {e}")
                total_errors += len(prepared_jobs)
                continue
        
        # Relatório final
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE UPLOAD")
        print("="*60)
        print(f"✅ Vagas inseridas com sucesso: {total_uploaded}")
        print(f"❌ Erros: {total_errors}")
        print(f"📈 Taxa de sucesso: {(total_uploaded/(total_uploaded+total_errors)*100):.1f}%")
        
        # Estatísticas por setor
        print("\n📊 Estatísticas por setor:")
        try:
            stats_result = supabase.table('vagas_por_setor').select('*').execute()
            if stats_result.data:
                for stat in stats_result.data:
                    print(f"   📋 {stat['sector_name']}: {stat['total_vagas']} vagas")
        except Exception as e:
            print(f"   ⚠️ Erro ao buscar estatísticas: {e}")
        
        return total_uploaded > 0
        
    except Exception as e:
        print(f"❌ Erro geral no upload: {e}")
        return False

def test_supabase_connection() -> bool:
    """Testa conexão com Supabase"""
    print("🔍 Testando conexão com Supabase...")
    
    supabase = init_supabase()
    if not supabase:
        return False
    
    try:
        # Testa consulta simples
        result = supabase.table('setores').select('sector_key, sector_name').limit(1).execute()
        
        if result.data:
            print("✅ Conexão com Supabase estabelecida com sucesso!")
            print(f"📊 Exemplo de setor: {result.data[0]}")
            return True
        else:
            print("❌ Conexão estabelecida, mas não foi possível acessar dados")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def get_latest_extraction_file() -> str:
    """Encontra o arquivo de extração mais recente"""
    # Busca arquivos de extração
    pattern = "catho_all_sectors_*.json"
    files = glob.glob(pattern)
    
    if not files:
        print("❌ Nenhum arquivo de extração encontrado")
        return None
    
    # Retorna o mais recente
    latest_file = max(files, key=os.path.getctime)
    print(f"📁 Arquivo mais recente encontrado: {latest_file}")
    return latest_file

def create_sample_env_file():
    """Cria arquivo .env de exemplo"""
    env_content = """# Configurações do Supabase
# Substitua pelos valores do seu projeto
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Exemplo:
# SUPABASE_URL=https://abcdefghijklmnop.supabase.co
# SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("📝 Arquivo .env.example criado!")
    print("   1. Renomeie para .env")
    print("   2. Configure suas credenciais do Supabase")

if __name__ == "__main__":
    print("🔧 CATHO SECTORS UPLOADER")
    print("="*50)
    
    # Verifica se as credenciais estão configuradas
    if SUPABASE_URL == "https://your-project.supabase.co":
        print("⚠️ IMPORTANTE: Configure suas credenciais do Supabase!")
        print("\n📋 Passos para configurar:")
        print("   1. Abra o arquivo catho_sectors_uploader.py")
        print("   2. Substitua SUPABASE_URL pela URL do seu projeto")
        print("   3. Substitua SUPABASE_KEY pela sua chave anônima")
        print("\n🔗 Encontre suas credenciais em: https://app.supabase.com/project/[seu-projeto]/settings/api")
        
        create_sample_env_file()
        exit(1)
    
    # Testa conexão
    if not test_supabase_connection():
        print("❌ Falha na conexão. Verifique suas credenciais.")
        exit(1)
    
    # Encontra arquivo mais recente
    latest_file = get_latest_extraction_file()
    if not latest_file:
        print("❌ Execute primeiro o catho_sectors_extractor.py")
        exit(1)
    
    # Confirma upload
    print(f"\n📋 Pronto para fazer upload de: {latest_file}")
    confirm = input("🤔 Deseja continuar? (s/N): ").lower().strip()
    
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Upload cancelado pelo usuário")
        exit(0)
    
    # Faz upload
    success = upload_jobs_to_supabase(latest_file)
    
    if success:
        print("\n🎉 Upload concluído com sucesso!")
        print("\n📊 Próximos passos:")
        print("   1. Acesse seu painel do Supabase")
        print("   2. Verifique as tabelas 'vagas' e 'setores'")
        print("   3. Use as views 'vagas_por_setor' e 'vagas_recentes'")
    else:
        print("\n❌ Upload falhou. Verifique os logs acima.")