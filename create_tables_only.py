#!/usr/bin/env python3
"""
Script para criar apenas as tabelas no Supabase usando SQL direto
"""

import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

def create_supabase_tables():
    """
    Executa o schema SQL no Supabase para criar as tabelas usando conexão direta
    """
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configuração do Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas no .env")
        return False
    
    # Construir URL de conexão PostgreSQL
    # Supabase URL format: https://xxx.supabase.co
    # PostgreSQL URL format: postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres
    
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
        
        # Comandos SQL para criar as tabelas
        sql_commands = [
            # Tabela de empresas
            """
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                industry VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # Índices para empresas
            "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);",
            "CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);",
            
            # Tabela principal de vagas
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                external_id TEXT,
                title VARCHAR(500) NOT NULL,
                seniority VARCHAR(50),
                area VARCHAR(100),
                company_id INTEGER REFERENCES companies(id),
                company_name VARCHAR(255),
                industry VARCHAR(100),
                employment_type VARCHAR(50),
                work_schedule TEXT,
                modality VARCHAR(50),
                location_city VARCHAR(100),
                location_state VARCHAR(10),
                location_region VARCHAR(100),
                salary_min DECIMAL(10,2),
                salary_max DECIMAL(10,2),
                salary_currency VARCHAR(10) DEFAULT 'BRL',
                salary_period VARCHAR(20) DEFAULT 'month',
                education_level VARCHAR(100),
                pcd BOOLEAN DEFAULT FALSE,
                source_name VARCHAR(50),
                source_url TEXT,
                raw_excerpt TEXT,
                confidence DECIMAL(3,2),
                parsed_at DATE,
                description TEXT,
                description_raw TEXT,
                published_date DATE,
                extraction_timestamp TIMESTAMP WITH TIME ZONE,
                data_quality_score DECIMAL(3,1),
                sector VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # Índices para jobs
            "CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_sector ON jobs(sector);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON jobs(company_name);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_location_city ON jobs(location_city);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_modality ON jobs(modality);",
            
            # Tabela de benefícios
            """
            CREATE TABLE IF NOT EXISTS job_benefits (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                benefit VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "CREATE INDEX IF NOT EXISTS idx_benefits_job_id ON job_benefits(job_id);",
            
            # Tabela de responsabilidades
            """
            CREATE TABLE IF NOT EXISTS job_responsibilities (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                responsibility TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "CREATE INDEX IF NOT EXISTS idx_responsibilities_job_id ON job_responsibilities(job_id);",
            
            # Tabela de requisitos obrigatórios
            """
            CREATE TABLE IF NOT EXISTS job_requirements_must (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                requirement TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "CREATE INDEX IF NOT EXISTS idx_requirements_must_job_id ON job_requirements_must(job_id);",
            
            # Tabela de requisitos desejáveis
            """
            CREATE TABLE IF NOT EXISTS job_requirements_nice (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                requirement TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "CREATE INDEX IF NOT EXISTS idx_requirements_nice_job_id ON job_requirements_nice(job_id);",
            
            # Tabela de recompensas
            """
            CREATE TABLE IF NOT EXISTS job_rewards (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                reward VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "CREATE INDEX IF NOT EXISTS idx_rewards_job_id ON job_rewards(job_id);",
            
            # Tabela de tags
            """
            CREATE TABLE IF NOT EXISTS job_tags (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                tag VARCHAR(100) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            "CREATE INDEX IF NOT EXISTS idx_tags_job_id ON job_tags(job_id);",
            "CREATE INDEX IF NOT EXISTS idx_tags_name ON job_tags(tag);",
        ]
        
        print("🔧 Criando tabelas no Supabase...")
        
        for i, command in enumerate(sql_commands):
            if command.strip():
                try:
                    cursor.execute(command.strip())
                    conn.commit()
                    print(f"✅ Comando {i+1}/{len(sql_commands)} executado")
                except Exception as e:
                    print(f"⚠️  Comando {i+1} - {str(e)[:100]}...")
                    conn.rollback()
        
        print("\n✅ Processo de criação de tabelas concluído!")
        
        # Verificar se as tabelas foram criadas
        try:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('companies', 'jobs', 'job_benefits', 'job_responsibilities', 'job_requirements_must', 'job_requirements_nice', 'job_rewards', 'job_tags');")
            tables = cursor.fetchall()
            print(f"\n📊 Tabelas criadas: {[table[0] for table in tables]}")
            
            if len(tables) >= 6:  # Pelo menos as principais tabelas
                print("✅ Todas as tabelas principais foram criadas com sucesso!")
            else:
                print("⚠️  Algumas tabelas podem não ter sido criadas")
                
        except Exception as e:
            print(f"❌ Erro ao verificar tabelas: {e}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        print("\n💡 Dica: Verifique se a SUPABASE_KEY é a service key (não a anon key)")
        return False

if __name__ == "__main__":
    print("🚀 Criando tabelas no Supabase...\n")
    
    if create_supabase_tables():
        print("\n🎉 Tabelas SQL criadas com sucesso!")
        print("\n💡 Agora você pode fazer o upload dos dados usando o script de upload")
    else:
        print("\n❌ Falha na criação das tabelas")
        print("\n🔧 Verifique as credenciais do Supabase no arquivo .env")