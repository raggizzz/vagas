#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final para upload dos dados com estrutura correta
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
    """Upload dos dados de skills"""
    print("📊 Fazendo upload dos dados de skills...")
    
    try:
        # Ler CSV
        df = pd.read_csv('skills_agg.csv')
        print(f"📁 Lendo {len(df)} registros de skills_agg.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('skills_statistics').delete().neq('id', 0).execute()
        
        # Preparar dados - apenas com skill_name primeiro
        records = []
        for _, row in df.iterrows():
            # Converter percentual de string para float
            percentual_str = str(row['percentual']).replace('%', '')
            percentual_float = float(percentual_str)
            
            record = {
                'skill_name': row['skill'],  # Apenas skill_name é obrigatório
                'sector_name': row['setor'],
                'skill_count': int(row['contagem']),
                'total_jobs': int(row['total_setor']),
                'percentage': percentual_float
            }
            records.append(record)
        
        # Upload em lotes pequenos
        batch_size = 10
        success_count = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                result = supabase.table('skills_statistics').insert(batch).execute()
                success_count += len(batch)
                print(f"   ✅ Lote {i//batch_size + 1}: {len(batch)} registros inseridos")
            except Exception as e:
                print(f"   ❌ Erro no lote {i//batch_size + 1}: {e}")
                # Tentar inserir um por um
                for record in batch:
                    try:
                        supabase.table('skills_statistics').insert(record).execute()
                        success_count += 1
                        print(f"      ✅ Registro individual inserido: {record['skill_name']}")
                    except Exception as e2:
                        print(f"      ❌ Erro individual {record['skill_name']}: {e2}")
        
        print(f"✅ Upload de skills concluído: {success_count}/{len(records)} registros")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro geral ao fazer upload de skills: {e}")
        return False

def upload_sectors_data():
    """Upload dos dados de setores"""
    print("\n🏭 Fazendo upload dos dados de setores...")
    
    try:
        # Ler CSV
        df = pd.read_csv('sector_map.csv')
        print(f"📁 Lendo {len(df)} registros de sector_map.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('sector_mapping').delete().neq('id', 0).execute()
        
        # Preparar dados - sector_original e sector_normalized são obrigatórios
        records = []
        for _, row in df.iterrows():
            record = {
                'sector_original': row['raw_sector'],
                'sector_normalized': row['normalized_sector']
                # Não incluir alias pois a coluna não existe
            }
            records.append(record)
        
        # Upload em lotes pequenos
        batch_size = 10
        success_count = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                result = supabase.table('sector_mapping').insert(batch).execute()
                success_count += len(batch)
                print(f"   ✅ Lote {i//batch_size + 1}: {len(batch)} registros inseridos")
            except Exception as e:
                print(f"   ❌ Erro no lote {i//batch_size + 1}: {e}")
                # Tentar inserir um por um
                for record in batch:
                    try:
                        supabase.table('sector_mapping').insert(record).execute()
                        success_count += 1
                        print(f"      ✅ Registro individual inserido: {record['sector_original']}")
                    except Exception as e2:
                        print(f"      ❌ Erro individual {record['sector_original']}: {e2}")
        
        print(f"✅ Upload de setores concluído: {success_count}/{len(records)} registros")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro geral ao fazer upload de setores: {e}")
        return False

def verify_data():
    """Verificar dados inseridos"""
    print("\n🔍 Verificando dados inseridos...")
    
    try:
        # Verificar skills_statistics
        skills_result = supabase.table('skills_statistics').select('*').limit(5).execute()
        print(f"📊 Skills Statistics: {len(skills_result.data)} registros (mostrando 5)")
        for record in skills_result.data:
            print(f"   - {record.get('skill_name', 'N/A')} ({record.get('sector_name', 'N/A')}) - {record.get('percentage', 0)}%")
        
        # Verificar sector_mapping
        sectors_result = supabase.table('sector_mapping').select('*').limit(5).execute()
        print(f"\n🏭 Sector Mapping: {len(sectors_result.data)} registros (mostrando 5)")
        for record in sectors_result.data:
            print(f"   - {record.get('sector_original', 'N/A')} -> {record.get('sector_normalized', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")

def main():
    """Função principal"""
    print("🚀 Upload final de dados para o Supabase")
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
    
    # Fazer upload dos dados
    skills_success = upload_skills_data()
    sectors_success = upload_sectors_data()
    
    # Verificar dados inseridos
    if skills_success or sectors_success:
        verify_data()
    
    # Resumo
    print("\n📋 Resumo do upload:")
    print(f"   Skills: {'✅' if skills_success else '❌'}")
    print(f"   Setores: {'✅' if sectors_success else '❌'}")
    
    if skills_success and sectors_success:
        print("\n🎉 Upload concluído com sucesso!")
        print("\n📝 Dados organizados:")
        print("   • skills_agg.csv -> skills_statistics (percentual de cada skill no mercado)")
        print("   • sector_map.csv -> sector_mapping (profissionais mais requisitados)")
    else:
        print("\n⚠️ Upload parcialmente concluído. Verifique os logs acima.")

if __name__ == "__main__":
    main()