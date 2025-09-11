import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.execute('SELECT titulo, setor FROM jobs WHERE setor IS NOT NULL LIMIT 5')
print('Vagas com setor:')
for row in cursor:
    print(f'Título: {row[0]}, Setor: {row[1]}')

# Verificar total de vagas com setor
cursor = conn.execute('SELECT COUNT(*) FROM jobs WHERE setor IS NOT NULL')
total_com_setor = cursor.fetchone()[0]
print(f'\nTotal de vagas com setor: {total_com_setor}')

# Verificar total de vagas
cursor = conn.execute('SELECT COUNT(*) FROM jobs')
total_vagas = cursor.fetchone()[0]
print(f'Total de vagas: {total_vagas}')

conn.close()