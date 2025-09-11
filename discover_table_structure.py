#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir a estrutura real das tabelas
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

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

def discover_skills_structure():
    """Descobrir estrutura da tabela skills_statistics"""
    print("🔍 Descobrindo estrutura de skills_statistics...")
    
    # Tentar diferentes combinações de colunas baseadas nos erros anteriores
    possible_columns = [
        # Baseado no erro anterior
        ['skill_name'],
        ['skill_name', 'sector_name'],
        ['skill_name', 'sector_name', 'skill_count'],
        ['skill_name', 'sector_name', 'skill_count', 'total_jobs'],
        ['skill_name', 'sector_name', 'skill_count', 'total_jobs', 'percentage'],
        # Outras possibilidades
        ['id', 'skill_name', 'sector_name', 'skill_count', 'total_jobs', 'percentage'],
        ['id', 'skill_name', 'sector_name', 'skill_count', 'total_jobs', 'percentage', 'created_at'],
        ['id', 'skill_name', 'sector_name', 'skill_count', 'total_jobs', 'percentage', 'created_at', 'updated_at'],
    ]
    
    for cols in possible_columns:
        try:
            result = supabase.table('skills_statistics').select(','.join(cols)).limit(1).execute()
            print(f"   ✅ Colunas funcionais: {cols}")
            return cols
        except Exception as e:
            print(f"   ❌ Tentativa {cols}: {str(e)[:100]}...")
    
    return None

def discover_sector_structure():
    """Descobrir estrutura da tabela sector_mapping"""
    print("\n🔍 Descobrindo estrutura de sector_mapping...")
    
    # Tentar diferentes combinações de colunas baseadas nos erros anteriores
    possible_columns = [
        # Baseado no erro anterior
        ['sector_original'],
        ['sector_original', 'sector_normalized'],
        ['sector_original', 'sector_normalized', 'sector_aliases'],
        # Outras possibilidades
        ['id', 'sector_original', 'sector_normalized', 'sector_aliases'],
        ['id', 'sector_original', 'sector_normalized', 'sector_aliases', 'created_at'],
        ['id', 'sector_original', 'sector_normalized', 'sector_aliases', 'created_at', 'updated_at'],
    ]
    
    for cols in possible_columns:
        try:
            result = supabase.table('sector_mapping').select(','.join(cols)).limit(1).execute()
            print(f"   ✅ Colunas funcionais: {cols}")
            return cols
        except Exception as e:
            print(f"   ❌ Tentativa {cols}: {str(e)[:100]}...")
    
    return None

def test_minimal_insert():
    """Testar inserção com colunas mínimas"""
    print("\n🧪 Testando inserção mínima...")
    
    # Teste skills_statistics com apenas colunas obrigatórias
    print("📊 Testando skills_statistics...")
    test_skill = {
        'skill_name': 'Teste Skill'
    }
    
    try:
        result = supabase.table('skills_statistics').insert(test_skill).execute()
        print("   ✅ Inserção mínima skills_statistics bem-sucedida!")
        # Limpar
        supabase.table('skills_statistics').delete().eq('skill_name', 'Teste Skill').execute()
    except Exception as e:
        print(f"   ❌ Erro skills_statistics: {e}")
        
        # Tentar com mais campos
        test_skill_full = {
            'skill_name': 'Teste Skill',
            'sector_name': 'Teste Setor',
            'skill_count': 1,
            'total_jobs': 10,
            'percentage': 10.0
        }
        
        try:
            result = supabase.table('skills_statistics').insert(test_skill_full).execute()
            print("   ✅ Inserção completa skills_statistics bem-sucedida!")
            # Limpar
            supabase.table('skills_statistics').delete().eq('skill_name', 'Teste Skill').execute()
        except Exception as e2:
            print(f"   ❌ Erro inserção completa: {e2}")
    
    # Teste sector_mapping com apenas colunas obrigatórias
    print("\n🏭 Testando sector_mapping...")
    test_sector = {
        'sector_original': 'Teste Original'
    }
    
    try:
        result = supabase.table('sector_mapping').insert(test_sector).execute()
        print("   ✅ Inserção mínima sector_mapping bem-sucedida!")
        # Limpar
        supabase.table('sector_mapping').delete().eq('sector_original', 'Teste Original').execute()
    except Exception as e:
        print(f"   ❌ Erro sector_mapping: {e}")
        
        # Tentar com mais campos
        test_sector_full = {
            'sector_original': 'Teste Original',
            'sector_normalized': 'Teste Normalizado',
            'sector_aliases': 'teste,original'
        }
        
        try:
            result = supabase.table('sector_mapping').insert(test_sector_full).execute()
            print("   ✅ Inserção completa sector_mapping bem-sucedida!")
            # Limpar
            supabase.table('sector_mapping').delete().eq('sector_original', 'Teste Original').execute()
        except Exception as e2:
            print(f"   ❌ Erro inserção completa: {e2}")

def main():
    """Função principal"""
    print("🔍 Descobrindo estrutura real das tabelas")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    
    skills_cols = discover_skills_structure()
    sector_cols = discover_sector_structure()
    
    test_minimal_insert()
    
    print("\n📋 Resumo das descobertas:")
    if skills_cols:
        print(f"   Skills Statistics: {skills_cols}")
    else:
        print("   Skills Statistics: Estrutura não descoberta")
    
    if sector_cols:
        print(f"   Sector Mapping: {sector_cols}")
    else:
        print("   Sector Mapping: Estrutura não descoberta")

if __name__ == "__main__":
    main()