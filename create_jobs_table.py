#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# SQL para criar a tabela jobs
create_jobs_sql = """
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    external_id TEXT UNIQUE,
    title VARCHAR(500) NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    location VARCHAR(255),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    description TEXT,
    work_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para otimização
CREATE INDEX IF NOT EXISTS idx_jobs_external_id ON jobs(external_id);
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON jobs(company_name);
CREATE INDEX IF NOT EXISTS idx_jobs_sector ON jobs(sector);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
"""

print('Criando tabela jobs no Supabase...')

try:
    # Executar o SQL usando rpc
    result = supabase.rpc('exec_sql', {'sql': create_jobs_sql}).execute()
    print('✅ Tabela jobs criada com sucesso!')
except Exception as e:
    print(f'❌ Erro ao criar tabela: {e}')
    print('\n💡 Tente executar manualmente no SQL Editor do Supabase:')
    print(create_jobs_sql)