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

def list_existing_tables(supabase: Client):
    """
    Lista as tabelas existentes no Supabase
    """
    existing_tables = []
    
    # Tentar algumas tabelas conhecidas
    test_tables = ['companies', 'job_tags', 'skills_statistics', 'sector_mapping', 'jobs', 'vagas']
    
    for table in test_tables:
        try:
            response = supabase.table(table).select('*').limit(1).execute()
            existing_tables.append(table)
            print(f"✅ Tabela '{table}' existe")
        except Exception as e:
            print(f"❌ Tabela '{table}' não existe: {e}")
    
    return existing_tables

def create_vagas_table_sql(supabase: Client):
    """
    Cria a tabela vagas usando SQL direto
    """
    create_sql = """
    -- Criar tabela vagas
    CREATE TABLE IF NOT EXISTS public.vagas (
        id BIGSERIAL PRIMARY KEY,
        external_id VARCHAR(50) UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        empresa TEXT NOT NULL,
        setor TEXT,
        localizacao TEXT,
        salario_min DECIMAL(10,2),
        salario_max DECIMAL(10,2),
        descricao TEXT,
        modalidade_trabalho TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Criar índices
    CREATE INDEX IF NOT EXISTS idx_vagas_external_id ON public.vagas(external_id);
    CREATE INDEX IF NOT EXISTS idx_vagas_empresa ON public.vagas(empresa);
    CREATE INDEX IF NOT EXISTS idx_vagas_setor ON public.vagas(setor);
    CREATE INDEX IF NOT EXISTS idx_vagas_localizacao ON public.vagas(localizacao);
    
    -- Habilitar RLS (Row Level Security)
    ALTER TABLE public.vagas ENABLE ROW LEVEL SECURITY;
    
    -- Criar política para permitir leitura pública
    CREATE POLICY IF NOT EXISTS "Permitir leitura pública de vagas" ON public.vagas
        FOR SELECT USING (true);
    
    -- Criar política para permitir inserção autenticada
    CREATE POLICY IF NOT EXISTS "Permitir inserção autenticada de vagas" ON public.vagas
        FOR INSERT WITH CHECK (true);
    """
    
    try:
        # Tentar executar via RPC
        result = supabase.rpc('exec_sql', {'sql': create_sql}).execute()
        print("✅ Tabela 'vagas' criada com sucesso via RPC")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela via RPC: {e}")
        print("\n📋 SQL para criar a tabela manualmente:")
        print(create_sql)
        return False

def insert_vagas_directly(supabase: Client, jobs: List[Dict]) -> int:
    """
    Insere vagas diretamente usando SQL
    """
    total_inserted = 0
    batch_size = 50
    
    print(f"📤 Inserindo {len(jobs)} vagas em lotes de {batch_size}...")
    
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        
        # Construir SQL de inserção
        values = []
        for job in batch:
            # Escapar aspas simples
            titulo = job['title'].replace("'", "''")
            empresa = job['company_name'].replace("'", "''")
            setor = job['sector'].replace("'", "''") if job['sector'] else 'NULL'
            localizacao = job['location'].replace("'", "''") if job['location'] else 'NULL'
            descricao = job['description'].replace("'", "''") if job['description'] else 'NULL'
            modalidade = job['work_type'].replace("'", "''") if job['work_type'] else 'NULL'
            
            value = f"('{job['external_id']}', '{titulo}', '{empresa}', '{setor}', '{localizacao}', {job['salary_min'] or 'NULL'}, {job['salary_max'] or 'NULL'}, '{descricao}', '{modalidade}')"
            values.append(value)
        
        insert_sql = f"""
        INSERT INTO public.vagas (external_id, titulo, empresa, setor, localizacao, salario_min, salario_max, descricao, modalidade_trabalho)
        VALUES {', '.join(values)}
        ON CONFLICT (external_id) DO NOTHING;
        """
        
        try:
            result = supabase.rpc('exec_sql', {'sql': insert_sql}).execute()
            total_inserted += len(batch)
            print(f"✅ Lote {i//batch_size + 1}: {len(batch)} vagas inseridas (Total: {total_inserted})")
        except Exception as e:
            print(f"❌ Erro no lote {i//batch_size + 1}: {e}")
            continue
    
    return total_inserted

def upload_vagas_normal(supabase: Client, jobs: List[Dict]) -> int:
    """
    Faz upload das vagas usando o método normal do Supabase
    """
    total_uploaded = 0
    batch_size = 50
    
    print(f"📤 Fazendo upload de {len(jobs)} vagas em lotes de {batch_size}...")
    
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        
        try:
            batch_data = []
            for job in batch:
                vaga_data = {
                    'external_id': job['external_id'],
                    'titulo': job['title'][:500],  # Limitar tamanho
                    'empresa': job['company_name'][:500],
                    'setor': job['sector'],
                    'localizacao': job['location'],
                    'salario_min': job['salary_min'],
                    'salario_max': job['salary_max'],
                    'descricao': job['description'],
                    'modalidade_trabalho': job['work_type']
                }
                batch_data.append(vaga_data)
            
            response = supabase.table('vagas').insert(batch_data).execute()
            
            if response.data:
                uploaded_count = len(response.data)
                total_uploaded += uploaded_count
                print(f"✅ Lote {i//batch_size + 1}: {uploaded_count} vagas enviadas (Total: {total_uploaded})")
            
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

def verify_vagas_count(supabase: Client):
    """
    Verifica quantas vagas foram inseridas
    """
    try:
        response = supabase.table('vagas').select('id', count='exact').execute()
        return response.count
    except Exception as e:
        print(f"❌ Erro ao verificar contagem: {e}")
        return 0

def main():
    print("🚀 Iniciando criação da tabela 'vagas' e upload das vagas normalizadas...")
    
    # Conectar ao Supabase
    try:
        supabase = get_supabase_client()
        print("✅ Conectado ao Supabase")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return
    
    # Listar tabelas existentes
    print("\n🔍 Verificando tabelas existentes...")
    existing_tables = list_existing_tables(supabase)
    
    # Criar tabela vagas se não existir
    if 'vagas' not in existing_tables:
        print("\n🏗️ Criando tabela 'vagas'...")
        if not create_vagas_table_sql(supabase):
            print("❌ Não foi possível criar a tabela automaticamente")
            print("Por favor, execute o SQL manualmente no Supabase Dashboard")
            return
    else:
        print("✅ Tabela 'vagas' já existe")
    
    # Carregar vagas normalizadas
    jobs = load_normalized_jobs('vagas_normalizadas_individuais.jsonl')
    if not jobs:
        print("❌ Nenhuma vaga para upload")
        return
    
    # Fazer upload das vagas
    print("\n📤 Fazendo upload das vagas...")
    uploaded_count = upload_vagas_normal(supabase, jobs)
    
    # Se o método normal falhar, tentar SQL direto
    if uploaded_count == 0:
        print("\n🔄 Tentando inserção via SQL direto...")
        uploaded_count = insert_vagas_directly(supabase, jobs)
    
    # Verificar resultado final
    final_count = verify_vagas_count(supabase)
    
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Vagas carregadas do arquivo: {len(jobs)}")
    print(f"Vagas enviadas: {uploaded_count}")
    print(f"Total de vagas na tabela: {final_count}")
    
    if final_count > 0:
        print("\n🎉 Upload concluído com sucesso!")
    else:
        print("\n❌ Nenhuma vaga foi inserida")

if __name__ == "__main__":
    main()