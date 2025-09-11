#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print('Verificando tabelas disponíveis no Supabase:')
tables = ['jobs', 'vagas', 'companies', 'job_tags', 'skills_statistics', 'sector_mapping']

for table in tables:
    try:
        result = supabase.table(table).select('id').limit(1).execute()
        print(f'{table}: ✅ Existe')
    except Exception as e:
        print(f'{table}: ❌ Não existe - {str(e)[:50]}...')