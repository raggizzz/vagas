#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar as colunas das tabelas existentes
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

def check_skills_statistics():
    """Verificar estrutura da tabela skills_statistics"""
    print("🔍 Verificando tabela skills_statistics...")
    
    try:
        # Tentar fazer select de todas as colunas
        result = supabase.table('skills_statistics').select('*').limit(1).execute()
        
        if result.data:
            print(f"   ✅ Tabela existe com {len(result.data)} registros")
            print(f"   📋 Colunas disponíveis: {list(result.data[0].keys())}")
        else:
            print("   ✅ Tabela existe mas está vazia")
            # Tentar inserir um registro de teste para descobrir a estrutura
            test_data = {'id': 1}
            try:
                supabase.table('skills_statistics').insert(test_data).execute()
            except Exception as e:
                print(f"   📋 Estrutura esperada baseada no erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def check_sector_mapping():
    """Verificar estrutura da tabela sector_mapping"""
    print("\n🔍 Verificando tabela sector_mapping...")
    
    try:
        # Tentar fazer select de todas as colunas
        result = supabase.table('sector_mapping').select('*').limit(1).execute()
        
        if result.data:
            print(f"   ✅ Tabela existe com {len(result.data)} registros")
            print(f"   📋 Colunas disponíveis: {list(result.data[0].keys())}")
        else:
            print("   ✅ Tabela existe mas está vazia")
            # Tentar inserir um registro de teste para descobrir a estrutura
            test_data = {'id': 1}
            try:
                supabase.table('sector_mapping').insert(test_data).execute()
            except Exception as e:
                print(f"   📋 Estrutura esperada baseada no erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_insert_skills():
    """Testar inserção na tabela skills_statistics"""
    print("\n🧪 Testando inserção em skills_statistics...")
    
    # Dados de teste baseados no CSV
    test_data = {
        'setor': 'Administração',
        'skill': 'Excel',
        'contagem': 10,
        'total_setor': 100,
        'percentual': 10.0
    }
    
    try:
        result = supabase.table('skills_statistics').insert(test_data).execute()
        print("   ✅ Inserção bem-sucedida!")
        
        # Limpar dados de teste
        supabase.table('skills_statistics').delete().eq('setor', 'Administração').eq('skill', 'Excel').execute()
        print("   🧹 Dados de teste removidos")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na inserção: {e}")
        return False

def test_insert_sectors():
    """Testar inserção na tabela sector_mapping"""
    print("\n🧪 Testando inserção em sector_mapping...")
    
    # Dados de teste baseados no CSV
    test_data = {
        'raw_sector': 'Comercial e vendas',
        'normalized_sector': 'Comercial/Vendas',
        'alias': 'vendas,comercial,sales'
    }
    
    try:
        result = supabase.table('sector_mapping').insert(test_data).execute()
        print("   ✅ Inserção bem-sucedida!")
        
        # Limpar dados de teste
        supabase.table('sector_mapping').delete().eq('raw_sector', 'Comercial e vendas').execute()
        print("   🧹 Dados de teste removidos")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na inserção: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 Verificando estrutura das tabelas existentes")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    
    skills_ok = check_skills_statistics()
    sector_ok = check_sector_mapping()
    
    if skills_ok:
        test_insert_skills()
    
    if sector_ok:
        test_insert_sectors()
    
    print("\n📋 Resumo:")
    print(f"   Skills Statistics: {'✅' if skills_ok else '❌'}")
    print(f"   Sector Mapping: {'✅' if sector_ok else '❌'}")

if __name__ == "__main__":
    main()