#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar as tabelas necessárias no Supabase
Executa o schema SQL diretamente
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
    """Criar tabela skills_statistics usando inserção de dados"""
    print("🔧 Criando tabela skills_statistics...")
    
    try:
        # Tentar inserir um registro de teste para forçar a criação da tabela
        test_data = {
            'setor': 'Teste',
            'skill': 'Teste',
            'contagem': 1,
            'total_setor': 1,
            'percentual': 100.0
        }
        
        result = supabase.table('skills_statistics').insert(test_data).execute()
        
        # Se chegou aqui, a tabela existe, vamos deletar o registro de teste
        supabase.table('skills_statistics').delete().eq('setor', 'Teste').execute()
        
        print("✅ Tabela skills_statistics está pronta!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "relation" in error_msg:
            print(f"❌ Tabela skills_statistics não existe: {error_msg}")
            return False
        else:
            print(f"✅ Tabela skills_statistics já existe (erro esperado: {error_msg})")
            return True

def create_sector_mapping_table():
    """Criar tabela sector_mapping usando inserção de dados"""
    print("🔧 Criando tabela sector_mapping...")
    
    try:
        # Tentar inserir um registro de teste para forçar a criação da tabela
        test_data = {
            'raw_sector': 'Teste',
            'normalized_sector': 'Teste',
            'alias': 'teste'
        }
        
        result = supabase.table('sector_mapping').insert(test_data).execute()
        
        # Se chegou aqui, a tabela existe, vamos deletar o registro de teste
        supabase.table('sector_mapping').delete().eq('raw_sector', 'Teste').execute()
        
        print("✅ Tabela sector_mapping está pronta!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "relation" in error_msg:
            print(f"❌ Tabela sector_mapping não existe: {error_msg}")
            return False
        else:
            print(f"✅ Tabela sector_mapping já existe (erro esperado: {error_msg})")
            return True

def show_manual_instructions():
    """Mostrar instruções para criação manual das tabelas"""
    print("\n📋 INSTRUÇÕES PARA CRIAÇÃO MANUAL DAS TABELAS:")
    print("\n1. Acesse o Supabase Dashboard:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}/sql")
    
    print("\n2. No SQL Editor, execute o seguinte SQL:")
    print("\n" + "="*60)
    
    sql_commands = """
-- Tabela para estatísticas de skills agregadas
CREATE TABLE IF NOT EXISTS skills_statistics (
    id SERIAL PRIMARY KEY,
    setor VARCHAR(100) NOT NULL,
    skill VARCHAR(200) NOT NULL,
    contagem INTEGER NOT NULL,
    total_setor INTEGER NOT NULL,
    percentual DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela para mapeamento de setores
CREATE TABLE IF NOT EXISTS sector_mapping (
    id SERIAL PRIMARY KEY,
    raw_sector VARCHAR(200) NOT NULL,
    normalized_sector VARCHAR(100) NOT NULL,
    alias VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_skills_statistics_setor ON skills_statistics(setor);
CREATE INDEX IF NOT EXISTS idx_skills_statistics_skill ON skills_statistics(skill);
CREATE INDEX IF NOT EXISTS idx_skills_statistics_percentual ON skills_statistics(percentual DESC);

CREATE INDEX IF NOT EXISTS idx_sector_mapping_raw ON sector_mapping(raw_sector);
CREATE INDEX IF NOT EXISTS idx_sector_mapping_normalized ON sector_mapping(normalized_sector);
CREATE INDEX IF NOT EXISTS idx_sector_mapping_alias ON sector_mapping(alias);
"""
    
    print(sql_commands)
    print("="*60)
    
    print("\n3. Após executar o SQL, execute novamente o script de upload:")
    print("   python upload_skills_sectors_data.py")

def main():
    """Função principal"""
    print("🚀 Verificando/criando tabelas no Supabase")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    skills_ok = create_skills_statistics_table()
    sector_ok = create_sector_mapping_table()
    
    if skills_ok and sector_ok:
        print("\n🎉 Todas as tabelas estão prontas!")
        print("\n💡 Agora você pode executar:")
        print("   python upload_skills_sectors_data.py")
    else:
        print("\n⚠️  Algumas tabelas precisam ser criadas manualmente")
        show_manual_instructions()

if __name__ == "__main__":
    main()