#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a estrutura da tabela vagas no Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_client() -> Client:
    """Conecta ao Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
    
    return create_client(url, key)

def check_table_structure(supabase: Client):
    """Verifica a estrutura da tabela vagas"""
    print("🔍 Verificando estrutura da tabela vagas...")
    
    try:
        # Tentar fazer uma consulta simples para ver os campos
        result = supabase.table('vagas').select('*').limit(1).execute()
        
        if result.data:
            print("✅ Tabela vagas encontrada!")
            print("📋 Campos disponíveis:")
            for field in result.data[0].keys():
                print(f"  - {field}")
        else:
            print("⚠️ Tabela vagas está vazia, mas existe")
            
    except Exception as e:
        print(f"❌ Erro ao acessar tabela vagas: {e}")
        
        # Tentar listar todas as tabelas
        try:
            print("\n🔍 Tentando listar tabelas disponíveis...")
            # Usar uma consulta SQL direta se possível
            result = supabase.rpc('exec_sql', {'query': "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"}).execute()
            print(f"Tabelas encontradas: {result.data}")
        except Exception as e2:
            print(f"❌ Erro ao listar tabelas: {e2}")

def main():
    """Função principal"""
    print("🚀 Verificando estrutura da tabela vagas...")
    print("=" * 50)
    
    try:
        supabase = get_supabase_client()
        print("✅ Conectado ao Supabase com sucesso")
        check_table_structure(supabase)
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()