#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para criar tabelas via inserção de dados de teste
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

def create_skills_statistics_table():
    """Criar/verificar tabela skills_statistics"""
    print("🔧 Verificando tabela skills_statistics...")
    
    try:
        # Tentar inserir dados de teste com a estrutura correta
        test_data = {
            'setor': 'Tecnologia',
            'skill': 'Python',
            'contagem': 150,
            'total_setor': 500,
            'percentual': 30.0
        }
        
        result = supabase.table('skills_statistics').insert(test_data).execute()
        print("   ✅ Tabela skills_statistics criada/verificada com sucesso!")
        
        # Limpar dados de teste
        supabase.table('skills_statistics').delete().eq('setor', 'Tecnologia').eq('skill', 'Python').execute()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def create_sector_mapping_table():
    """Criar/verificar tabela sector_mapping"""
    print("🔧 Verificando tabela sector_mapping...")
    
    try:
        # Tentar inserir dados de teste com a estrutura correta
        test_data = {
            'raw_sector': 'Tecnologia da Informação',
            'normalized_sector': 'Tecnologia',
            'alias': 'ti,tecnologia,informatica,tech'
        }
        
        result = supabase.table('sector_mapping').insert(test_data).execute()
        print("   ✅ Tabela sector_mapping criada/verificada com sucesso!")
        
        # Limpar dados de teste
        supabase.table('sector_mapping').delete().eq('raw_sector', 'Tecnologia da Informação').execute()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def show_manual_sql():
    """Mostrar SQL para execução manual"""
    print("\n📋 EXECUTE O SQL ABAIXO NO SUPABASE DASHBOARD:")
    print(f"\n🔗 Link: {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}/sql")
    print("\n" + "="*60)
    
    sql = """
-- Dropar e recriar tabelas com estrutura correta
DROP TABLE IF EXISTS skills_statistics CASCADE;
DROP TABLE IF EXISTS sector_mapping CASCADE;

-- Criar tabela skills_statistics
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

-- Criar tabela sector_mapping
CREATE TABLE sector_mapping (
    id SERIAL PRIMARY KEY,
    raw_sector VARCHAR(200) NOT NULL,
    normalized_sector VARCHAR(100) NOT NULL,
    alias VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Criar índices
CREATE INDEX idx_skills_statistics_setor ON skills_statistics(setor);
CREATE INDEX idx_skills_statistics_skill ON skills_statistics(skill);
CREATE INDEX idx_skills_statistics_percentual ON skills_statistics(percentual DESC);
CREATE INDEX idx_sector_mapping_raw ON sector_mapping(raw_sector);
CREATE INDEX idx_sector_mapping_normalized ON sector_mapping(normalized_sector);
CREATE INDEX idx_sector_mapping_alias ON sector_mapping(alias);

-- Habilitar RLS e criar políticas
ALTER TABLE skills_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE sector_mapping ENABLE ROW LEVEL SECURITY;

CREATE POLICY \"Allow all access\" ON skills_statistics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY \"Allow all access\" ON sector_mapping FOR ALL USING (true) WITH CHECK (true);
"""
    
    print(sql)
    print("="*60)
    print("\n⚠️  IMPORTANTE: Execute este SQL no dashboard do Supabase antes de continuar!")

def main():
    """Função principal"""
    print("🚀 Criando/verificando tabelas no Supabase")
    print(f"🔗 URL: {SUPABASE_URL}")
    print(f"⏰ {datetime.now().isoformat()}")
    
    skills_ok = create_skills_statistics_table()
    sector_ok = create_sector_mapping_table()
    
    if skills_ok and sector_ok:
        print("\n🎉 Tabelas prontas! Executando upload dos dados...")
        return True
    else:
        print("\n❌ Tabelas precisam ser criadas manualmente")
        show_manual_sql()
        return False

if __name__ == "__main__":
    if main():
        print("\n💡 Executando upload dos dados CSV...")
        os.system("python upload_skills_sectors_data.py")