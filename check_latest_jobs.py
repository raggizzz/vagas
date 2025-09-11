import sqlite3

def check_latest_jobs():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.execute('SELECT titulo, setor FROM jobs ORDER BY id DESC LIMIT 10')
    
    print('Últimas 10 vagas inseridas:')
    for i, row in enumerate(cursor, 1):
        titulo = row[0][:50] + '...' if len(row[0]) > 50 else row[0]
        setor = row[1] if row[1] else 'NULL'
        print(f'{i}. Título: {titulo}, Setor: {setor}')
    
    conn.close()

if __name__ == '__main__':
    check_latest_jobs()