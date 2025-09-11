#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para upload apenas das skills com estrutura mínima
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

def upload_skills_minimal():
    """Upload das skills apenas com skill_name"""
    print("📊 Fazendo upload das skills (estrutura mínima)...")
    
    try:
        # Ler CSV
        df = pd.read_csv('skills_agg.csv')
        print(f"📁 Lendo {len(df)} registros de skills_agg.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('skills_statistics').delete().neq('id', 0).execute()
        
        # Preparar dados - apenas skill_name
        records = []
        for _, row in df.iterrows():
            # Criar um nome de skill mais descritivo incluindo setor e percentual
            percentual_str = str(row['percentual']).replace('%', '')
            skill_description = f"{row['skill']} ({row['setor']}) - {percentual_str}% do mercado"
            
            record = {
                'skill_name': skill_description
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
                        print(f"      ✅ Registro individual inserido")
                    except Exception as e2:
                        print(f"      ❌ Erro individual: {e2}")
        
        print(f"✅ Upload de skills concluído: {success_count}/{len(records)} registros")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro geral ao fazer upload de skills: {e}")
        return False

def verify_all_data():
    """Verificar todos os dados inseridos"""
    print("\n🔍 Verificando todos os dados...")
    
    try:
        # Verificar skills_statistics
        skills_result = supabase.table('skills_statistics').select('*').execute()
        print(f"📊 Skills Statistics: {len(skills_result.data)} registros")
        
        # Mostrar algumas skills
        for i, record in enumerate(skills_result.data[:10]):
            print(f"   {i+1}. {record.get('skill_name', 'N/A')}")
        
        if len(skills_result.data) > 10:
            print(f"   ... e mais {len(skills_result.data) - 10} registros")
        
        # Verificar sector_mapping
        sectors_result = supabase.table('sector_mapping').select('*').execute()
        print(f"\n🏭 Sector Mapping: {len(sectors_result.data)} registros")
        
        # Mostrar alguns setores
        for i, record in enumerate(sectors_result.data[:10]):
            print(f"   {i+1}. {record.get('sector_original', 'N/A')} -> {record.get('sector_normalized', 'N/A')}")
        
        if len(sectors_result.data) > 10:
            print(f"   ... e mais {len(sectors_result.data) - 10} registros")
        
        return len(skills_result.data), len(sectors_result.data)
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        return 0, 0

def main():
    """Função principal"""
    print("🚀 Upload final das skills para o Supabase")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Verificar conexão
    try:
        supabase.table('skills_statistics').select('id').limit(1).execute()
        print("✅ Conexão com Supabase estabelecida!")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # Verificar se arquivo existe
    if not os.path.exists('skills_agg.csv'):
        print("❌ Arquivo skills_agg.csv não encontrado!")
        return
    
    print("✅ Arquivo CSV encontrado!")
    
    # Fazer upload das skills
    skills_success = upload_skills_minimal()
    
    # Verificar todos os dados
    skills_count, sectors_count = verify_all_data()
    
    # Resumo final
    print("\n📋 Resumo final:")
    print(f"   Skills carregadas: {skills_count} registros")
    print(f"   Setores carregados: {sectors_count} registros")
    
    if skills_success and skills_count > 0 and sectors_count > 0:
        print("\n🎉 Todos os dados foram carregados com sucesso!")
        print("\n📝 Organização dos dados:")
        print("   • skills_agg.csv -> skills_statistics")
        print("     (cada skill com setor e percentual no mercado)")
        print("   • sector_map.csv -> sector_mapping")
        print("     (mapeamento de setores originais para normalizados)")
        print("\n✅ API pronta para uso com os dados carregados!")
    else:
        print("\n⚠️ Alguns dados podem não ter sido carregados corretamente.")

if __name__ == "__main__":
    main()