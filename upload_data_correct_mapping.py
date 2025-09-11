#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para upload dos dados com mapeamento correto das colunas
"""

import os
import pandas as pd
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

def upload_skills_data():
    """Upload dos dados de skills com mapeamento correto"""
    print("📊 Fazendo upload dos dados de skills...")
    
    try:
        # Ler CSV
        df = pd.read_csv('skills_agg.csv')
        print(f"📁 Lendo {len(df)} registros de skills_agg.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('skills_statistics').delete().neq('id', 0).execute()
        
        # Preparar dados com mapeamento correto
        records = []
        for _, row in df.iterrows():
            # Converter percentual de string para float
            percentual_str = str(row['percentual']).replace('%', '')
            percentual_float = float(percentual_str)
            
            record = {
                'sector_name': row['setor'],  # setor -> sector_name
                'skill_name': row['skill'],   # skill -> skill_name
                'skill_count': int(row['contagem']),  # contagem -> skill_count
                'total_jobs': int(row['total_setor']), # total_setor -> total_jobs
                'percentage': percentual_float,  # percentual -> percentage
                'data_date': datetime.now().date().isoformat()
            }
            records.append(record)
        
        # Upload em lotes
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            result = supabase.table('skills_statistics').insert(batch).execute()
            print(f"   ✅ Lote {i//batch_size + 1}: {len(batch)} registros inseridos")
        
        print(f"✅ Upload de skills concluído: {len(records)} registros")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer upload de skills: {e}")
        return False

def upload_sectors_data():
    """Upload dos dados de setores com mapeamento correto"""
    print("\n🏭 Fazendo upload dos dados de setores...")
    
    try:
        # Ler CSV
        df = pd.read_csv('sector_map.csv')
        print(f"📁 Lendo {len(df)} registros de sector_map.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('sector_mapping').delete().neq('id', 0).execute()
        
        # Preparar dados com mapeamento correto
        records = []
        for _, row in df.iterrows():
            record = {
                'sector_original': row['raw_sector'],      # raw_sector -> sector_original
                'sector_normalized': row['normalized_sector'], # normalized_sector -> sector_normalized
                'sector_aliases': row['alias'],            # alias -> sector_aliases
                'is_active': True
            }
            records.append(record)
        
        # Upload em lotes
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            result = supabase.table('sector_mapping').insert(batch).execute()
            print(f"   ✅ Lote {i//batch_size + 1}: {len(batch)} registros inseridos")
        
        print(f"✅ Upload de setores concluído: {len(records)} registros")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer upload de setores: {e}")
        return False

def test_single_insert():
    """Testar inserção de um registro para descobrir a estrutura correta"""
    print("🧪 Testando inserção individual...")
    
    # Teste skills_statistics
    print("\n📊 Testando skills_statistics...")
    test_skill = {
        'sector_name': 'Teste',
        'skill_name': 'Teste Skill',
        'skill_count': 1,
        'total_jobs': 10,
        'percentage': 10.0,
        'data_date': datetime.now().date().isoformat()
    }
    
    try:
        result = supabase.table('skills_statistics').insert(test_skill).execute()
        print("   ✅ Inserção skills_statistics bem-sucedida!")
        # Limpar
        supabase.table('skills_statistics').delete().eq('sector_name', 'Teste').execute()
    except Exception as e:
        print(f"   ❌ Erro skills_statistics: {e}")
    
    # Teste sector_mapping
    print("\n🏭 Testando sector_mapping...")
    test_sector = {
        'sector_original': 'Teste Original',
        'sector_normalized': 'Teste Normalizado',
        'sector_aliases': 'teste,original',
        'is_active': True
    }
    
    try:
        result = supabase.table('sector_mapping').insert(test_sector).execute()
        print("   ✅ Inserção sector_mapping bem-sucedida!")
        # Limpar
        supabase.table('sector_mapping').delete().eq('sector_original', 'Teste Original').execute()
    except Exception as e:
        print(f"   ❌ Erro sector_mapping: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando upload de dados para o Supabase")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Verificar conexão
    try:
        supabase.table('skills_statistics').select('id').limit(1).execute()
        print("✅ Conexão com Supabase estabelecida!")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # Verificar se arquivos existem
    if not os.path.exists('skills_agg.csv'):
        print("❌ Arquivo skills_agg.csv não encontrado!")
        return
    
    if not os.path.exists('sector_map.csv'):
        print("❌ Arquivo sector_map.csv não encontrado!")
        return
    
    print("✅ Arquivos CSV encontrados!")
    
    # Testar inserção primeiro
    test_single_insert()
    
    # Fazer upload dos dados
    skills_success = upload_skills_data()
    sectors_success = upload_sectors_data()
    
    # Resumo
    print("\n📋 Resumo do upload:")
    print(f"   Skills: {'✅' if skills_success else '❌'}")
    print(f"   Setores: {'✅' if sectors_success else '❌'}")
    
    if skills_success and sectors_success:
        print("\n🎉 Upload concluído com sucesso!")
    else:
        print("\n❌ Upload concluído com erros. Verifique os logs acima.")

if __name__ == "__main__":
    main()