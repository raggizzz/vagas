#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Configuração do Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas no .env")
    exit(1)

# Construir URL de conexão PostgreSQL
parsed_url = urlparse(url)
host = parsed_url.netloc
project_id = host.split('.')[0]

# Para Supabase, a senha é a service key
db_url = f"postgresql://postgres:{key}@db.{project_id}.supabase.co:5432/postgres"

try:
    print(f"🔗 Conectando ao banco PostgreSQL...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    print("✅ Conectado ao banco de dados")
    
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
    """
    
    # Executar criação da tabela
    print("🔧 Criando tabela jobs...")
    cursor.execute(create_jobs_sql)
    
    # Criar índices
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_jobs_external_id ON jobs(external_id);",
        "CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);",
        "CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON jobs(company_name);",
        "CREATE INDEX IF NOT EXISTS idx_jobs_sector ON jobs(sector);",
        "CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);"
    ]
    
    print("🔧 Criando índices...")
    for idx_sql in indices:
        cursor.execute(idx_sql)
    
    # Confirmar mudanças
    conn.commit()
    
    print("✅ Tabela jobs criada com sucesso!")
    
    # Verificar se a tabela foi criada
    cursor.execute("SELECT COUNT(*) FROM jobs;")
    count = cursor.fetchone()[0]
    print(f"📊 Tabela jobs tem {count} registros")
    
except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    if 'conn' in locals():
        conn.close()
        print("🔌 Conexão fechada")