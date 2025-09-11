import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Conectar ao Supabase
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Buscar registros com 'medic' nas habilidades
result_habilidades = supabase.table('jobs').select('*').ilike('habilidades', '%medic%').execute()
print(f'Registros com "medic" em habilidades: {len(result_habilidades.data)}')

for job in result_habilidades.data[:5]:
    print(f'ID: {job["id"]}')
    print(f'Título: {job["titulo"]}')
    print(f'Habilidades: {job["habilidades"]}')
    print(f'Requisitos: {job["requisitos"]}')
    print('---')

# Buscar registros com 'medic' nos requisitos
result_requisitos = supabase.table('jobs').select('*').ilike('requisitos', '%medic%').execute()
print(f'\nRegistros com "medic" em requisitos: {len(result_requisitos.data)}')

for job in result_requisitos.data[:5]:
    print(f'ID: {job["id"]}')
    print(f'Título: {job["titulo"]}')
    print(f'Habilidades: {job["habilidades"]}')
    print(f'Requisitos: {job["requisitos"]}')
    print('---')

# Buscar registros com 'conhecimentos' nas habilidades
result_conhecimentos = supabase.table('jobs').select('*').ilike('habilidades', '%conhecimentos%').execute()
print(f'\nRegistros com "conhecimentos" em habilidades: {len(result_conhecimentos.data)}')

for job in result_conhecimentos.data[:3]:
    print(f'ID: {job["id"]}')
    print(f'Título: {job["titulo"]}')
    print(f'Habilidades: {job["habilidades"]}')
    print('---')