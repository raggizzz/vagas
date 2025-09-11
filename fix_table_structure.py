#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir a estrutura das tabelas no Supabase
Adiciona as colunas necessárias se não existirem
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas no .env")
    exit(1)

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_table_structure():
    """Verificar estrutura atual das tabelas"""
    print("🔍 Verificando estrutura das tabelas...")
    
    try:
        # Tentar consultar skills_statistics
        print("\n📊 Verificando skills_statistics:")
        result = supabase.table('skills_statistics').select('*').limit(1).execute()
        print(f"   ✅ Tabela existe com {len(result.data)} registros")
        if result.data:
            print(f"   📋 Colunas encontradas: {list(result.data[0].keys())}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    try:
        # Tentar consultar sector_mapping
        print("\n🏭 Verificando sector_mapping:")
        result = supabase.table('sector_mapping').select('*').limit(1).execute()
        print(f"   ✅ Tabela existe com {len(result.data)} registros")
        if result.data:
            print(f"   📋 Colunas encontradas: {list(result.data[0].keys())}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def show_sql_fix():
    """Mostrar SQL para corrigir as tabelas"""
    print("\n🔧 SQL PARA CORRIGIR AS TABELAS:")
    print("\n" + "="*60)
    
    sql_commands = """
-- Primeiro, vamos dropar e recriar as tabelas com a estrutura correta

-- Dropar tabelas existentes (cuidado: isso apaga todos os dados!)
DROP TABLE IF EXISTS skills_statistics CASCADE;
DROP TABLE IF EXISTS sector_mapping CASCADE;

-- Recriar tabela skills_statistics com estrutura correta
CREATE TABLE skills_statistics (
    id SERIAL PRIMARY KEY,
    setor VARCHAR(100) NOT NULL,
    skill VARCHAR(200) NOT NULL,
    contagem INTEGER NOT NULL,
    total_setor INTEGER NOT NULL,
    percentual DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Recriar tabela sector_mapping com estrutura correta
CREATE TABLE sector_mapping (
    id SERIAL PRIMARY KEY,
    raw_sector VARCHAR(200) NOT NULL,
    normalized_sector VARCHAR(100) NOT NULL,
    alias VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Criar índices para melhor performance
CREATE INDEX idx_skills_statistics_setor ON skills_statistics(setor);
CREATE INDEX idx_skills_statistics_skill ON skills_statistics(skill);
CREATE INDEX idx_skills_statistics_percentual ON skills_statistics(percentual DESC);

CREATE INDEX idx_sector_mapping_raw ON sector_mapping(raw_sector);
CREATE INDEX idx_sector_mapping_normalized ON sector_mapping(normalized_sector);
CREATE INDEX idx_sector_mapping_alias ON sector_mapping(alias);

-- Habilitar RLS (Row Level Security) se necessário
ALTER TABLE skills_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE sector_mapping ENABLE ROW LEVEL SECURITY;

-- Criar políticas para permitir acesso público (ajuste conforme necessário)
CREATE POLICY "Allow public read access" ON skills_statistics FOR SELECT USING (true);
CREATE POLICY "Allow public insert access" ON skills_statistics FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access" ON skills_statistics FOR UPDATE USING (true);
CREATE POLICY "Allow public delete access" ON skills_statistics FOR DELETE USING (true);

CREATE POLICY "Allow public read access" ON sector_mapping FOR SELECT USING (true);
CREATE POLICY "Allow public insert access" ON sector_mapping FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access" ON sector_mapping FOR UPDATE USING (true);
CREATE POLICY "Allow public delete access" ON sector_mapping FOR DELETE USING (true);
"""
    
    print(sql_commands)
    print("="*60)
    
    print("\n📋 INSTRUÇÕES:")
    print("\n1. Acesse o Supabase Dashboard:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}/sql")
    print("\n2. Cole e execute o SQL acima")
    print("\n3. Após executar, rode novamente:")
    print("   python upload_skills_sectors_data.py")

def main():
    """Função principal"""
    print("🔧 Diagnóstico da estrutura das tabelas")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    check_table_structure()
    show_sql_fix()

if __name__ == "__main__":
    main()