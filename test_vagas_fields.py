#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar quais campos a tabela vagas aceita
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_client() -> Client:
    """Conecta ao Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
    
    return create_client(url, key)

def test_basic_fields(supabase: Client):
    """Testa campos básicos da tabela vagas"""
    print("🧪 Testando campos básicos...")
    
    # Teste 1: Campos mínimos
    test_data_1 = {
        'external_id': 'test_001',
        'titulo': 'Vaga de Teste',
        'empresa': 'Empresa Teste'
    }
    
    try:
        result = supabase.table('vagas').insert([test_data_1]).execute()
        print("✅ Teste 1 (campos básicos) - SUCESSO")
        print(f"   Dados inseridos: {result.data}")
        
        # Limpar o teste
        supabase.table('vagas').delete().eq('external_id', 'test_001').execute()
        return True
        
    except Exception as e:
        print(f"❌ Teste 1 (campos básicos) - FALHOU: {e}")
        return False

def test_extended_fields(supabase: Client):
    """Testa campos estendidos da tabela vagas"""
    print("🧪 Testando campos estendidos...")
    
    # Teste 2: Mais campos
    test_data_2 = {
        'external_id': 'test_002',
        'titulo': 'Vaga de Teste 2',
        'empresa': 'Empresa Teste 2',
        'setor': 'Tecnologia',
        'localizacao': 'São Paulo, SP',
        'descricao': 'Descrição da vaga de teste',
        'modalidade_trabalho': 'Remoto',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        result = supabase.table('vagas').insert([test_data_2]).execute()
        print("✅ Teste 2 (campos estendidos) - SUCESSO")
        print(f"   Dados inseridos: {result.data}")
        
        # Limpar o teste
        supabase.table('vagas').delete().eq('external_id', 'test_002').execute()
        return True
        
    except Exception as e:
        print(f"❌ Teste 2 (campos estendidos) - FALHOU: {e}")
        return False

def test_with_original_id(supabase: Client):
    """Testa se o campo original_id existe"""
    print("🧪 Testando campo original_id...")
    
    # Teste 3: Com original_id
    test_data_3 = {
        'external_id': 'test_003',
        'titulo': 'Vaga de Teste 3',
        'empresa': 'Empresa Teste 3',
        'original_id': 123
    }
    
    try:
        result = supabase.table('vagas').insert([test_data_3]).execute()
        print("✅ Teste 3 (com original_id) - SUCESSO")
        print(f"   Dados inseridos: {result.data}")
        
        # Limpar o teste
        supabase.table('vagas').delete().eq('external_id', 'test_003').execute()
        return True
        
    except Exception as e:
        print(f"❌ Teste 3 (com original_id) - FALHOU: {e}")
        return False

def test_without_original_id(supabase: Client):
    """Testa sem o campo original_id"""
    print("🧪 Testando sem campo original_id...")
    
    # Teste 4: Sem original_id
    test_data_4 = {
        'external_id': 'test_004',
        'titulo': 'Vaga de Teste 4',
        'empresa': 'Empresa Teste 4',
        'setor': 'Tecnologia',
        'localizacao': 'São Paulo, SP',
        'descricao': 'Descrição da vaga de teste',
        'modalidade_trabalho': 'Remoto',
        'source_line': 1,
        'created_at': datetime.now().isoformat()
    }
    
    try:
        result = supabase.table('vagas').insert([test_data_4]).execute()
        print("✅ Teste 4 (sem original_id) - SUCESSO")
        print(f"   Dados inseridos: {result.data}")
        
        # Mostrar campos disponíveis
        if result.data:
            print("📋 Campos disponíveis na tabela:")
            for field in result.data[0].keys():
                print(f"  - {field}")
        
        # Limpar o teste
        supabase.table('vagas').delete().eq('external_id', 'test_004').execute()
        return True
        
    except Exception as e:
        print(f"❌ Teste 4 (sem original_id) - FALHOU: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Testando estrutura da tabela vagas...")
    print("=" * 50)
    
    try:
        supabase = get_supabase_client()
        print("✅ Conectado ao Supabase com sucesso")
        
        # Executar testes
        test_basic_fields(supabase)
        test_extended_fields(supabase)
        test_with_original_id(supabase)
        test_without_original_id(supabase)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()