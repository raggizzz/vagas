#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print('Verificando tabelas disponíveis...')
try:
    # Tentar listar tabelas
    response = supabase.table('jobs').select('*').limit(1).execute()
    print('✓ Tabela jobs existe')
    print(f'Colunas da tabela jobs: {list(response.data[0].keys()) if response.data else "Tabela vazia"}')
except Exception as e:
    print(f'✗ Erro ao acessar tabela jobs: {e}')

try:
    response = supabase.table('job_requirements_must').select('*').limit(1).execute()
    print('✓ Tabela job_requirements_must existe')
    print(f'Colunas da tabela job_requirements_must: {list(response.data[0].keys()) if response.data else "Tabela vazia"}')
except Exception as e:
    print(f'✗ Erro ao acessar tabela job_requirements_must: {e}')

try:
    response = supabase.table('companies').select('*').limit(1).execute()
    print('✓ Tabela companies existe')
except Exception as e:
    print(f'✗ Erro ao acessar tabela companies: {e}')