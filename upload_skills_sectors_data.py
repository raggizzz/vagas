#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fazer upload dos dados de skills_agg.csv e sector_map.csv para o Supabase
Cria as tabelas necessárias e insere os dados
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import json
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

def create_tables():
    """Criar as tabelas necessárias no Supabase"""
    print("🔧 Verificando/criando tabelas no Supabase...")
    
    # Tentar verificar se as tabelas já existem
    try:
        # Tentar acessar as tabelas para ver se existem
        skills_test = supabase.table('skills_statistics').select('id').limit(1).execute()
        sector_test = supabase.table('sector_mapping').select('id').limit(1).execute()
        print("✅ Tabelas já existem!")
        return True
    except Exception as e:
        print(f"ℹ️  Tabelas não existem ainda: {str(e)}")
        print("ℹ️  Você precisa executar o schema SQL manualmente no Supabase")
        print("ℹ️  Execute o arquivo skills_sector_schema.sql no SQL Editor do Supabase")
        
        # Perguntar se quer continuar
        response = input("\n❓ As tabelas foram criadas manualmente? Deseja continuar? (s/n): ")
        if response.lower() == 's':
            return True
        else:
            return False



def upload_skills_data():
    """Fazer upload dos dados de skills_agg.csv"""
    print("\n📊 Fazendo upload dos dados de skills...")
    
    try:
        # Ler o arquivo CSV
        df_skills = pd.read_csv('skills_agg.csv')
        print(f"📁 Lendo {len(df_skills)} registros de skills_agg.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('skills_statistics').delete().neq('id', 0).execute()
        
        # Preparar dados para inserção
        skills_data = []
        for _, row in df_skills.iterrows():
            # Converter percentual de string para float
            percentual_str = row['percentual'].replace('%', '')
            percentual_float = float(percentual_str)
            
            skills_data.append({
                'setor': row['setor'],
                'skill': row['skill'],
                'contagem': int(row['contagem']),
                'total_setor': int(row['total_setor']),
                'percentual': percentual_float
            })
        
        # Inserir dados em lotes
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(skills_data), batch_size):
            batch = skills_data[i:i + batch_size]
            result = supabase.table('skills_statistics').insert(batch).execute()
            total_inserted += len(batch)
            print(f"✅ Inseridos {total_inserted}/{len(skills_data)} registros de skills")
        
        print(f"🎉 Upload de skills concluído! Total: {total_inserted} registros")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer upload de skills: {str(e)}")
        return False

def upload_sectors_data():
    """Fazer upload dos dados de sector_map.csv"""
    print("\n🏭 Fazendo upload dos dados de setores...")
    
    try:
        # Ler o arquivo CSV
        df_sectors = pd.read_csv('sector_map.csv')
        print(f"📁 Lendo {len(df_sectors)} registros de sector_map.csv")
        
        # Limpar dados existentes
        print("🧹 Limpando dados existentes...")
        supabase.table('sector_mapping').delete().neq('id', 0).execute()
        
        # Preparar dados para inserção
        sectors_data = []
        for _, row in df_sectors.iterrows():
            sectors_data.append({
                'raw_sector': row['raw_sector'],
                'normalized_sector': row['normalized_sector'],
                'alias': row['alias'] if pd.notna(row['alias']) else None
            })
        
        # Inserir dados em lotes
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(sectors_data), batch_size):
            batch = sectors_data[i:i + batch_size]
            result = supabase.table('sector_mapping').insert(batch).execute()
            total_inserted += len(batch)
            print(f"✅ Inseridos {total_inserted}/{len(sectors_data)} registros de setores")
        
        print(f"🎉 Upload de setores concluído! Total: {total_inserted} registros")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer upload de setores: {str(e)}")
        return False

def verify_data():
    """Verificar se os dados foram inseridos corretamente"""
    print("\n🔍 Verificando dados inseridos...")
    
    try:
        # Verificar skills
        skills_count = supabase.table('skills_statistics').select('id', count='exact').execute()
        print(f"📊 Skills inseridas: {skills_count.count} registros")
        
        # Verificar setores
        sectors_count = supabase.table('sector_mapping').select('id', count='exact').execute()
        print(f"🏭 Setores inseridos: {sectors_count.count} registros")
        
        # Mostrar alguns exemplos
        print("\n📋 Exemplos de dados inseridos:")
        
        # Top 5 skills por percentual
        top_skills = supabase.table('skills_statistics').select('*').order('percentual', desc=True).limit(5).execute()
        print("\n🏆 Top 5 Skills por percentual:")
        for skill in top_skills.data:
            print(f"   • {skill['skill']} ({skill['setor']}): {skill['percentual']}%")
        
        # Alguns mapeamentos de setores
        sector_samples = supabase.table('sector_mapping').select('*').limit(5).execute()
        print("\n🗺️  Exemplos de mapeamento de setores:")
        for sector in sector_samples.data:
            print(f"   • {sector['raw_sector']} → {sector['normalized_sector']} ({sector['alias']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando upload de dados para o Supabase")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Verificar conexão
    try:
        # Tentar uma operação simples para verificar conexão
        print("✅ Conexão com Supabase estabelecida!")
    except Exception as e:
        print(f"❌ Erro de conexão com Supabase: {str(e)}")
        return
    
    # Verificar se os arquivos CSV existem
    if not os.path.exists('skills_agg.csv'):
        print("❌ Arquivo skills_agg.csv não encontrado!")
        return
    
    if not os.path.exists('sector_map.csv'):
        print("❌ Arquivo sector_map.csv não encontrado!")
        return
    
    print("✅ Arquivos CSV encontrados!")
    
    # Executar upload
    success = True
    
    # 1. Criar tabelas
    if not create_tables():
        print("⚠️  Aviso: Não foi possível criar tabelas automaticamente")
        print("ℹ️  Execute o arquivo skills_sector_schema.sql manualmente no Supabase")
        
        # Tentar continuar mesmo assim
        response = input("\n❓ Deseja continuar com o upload mesmo assim? (s/n): ")
        if response.lower() != 's':
            return
    
    # 2. Upload de skills
    if not upload_skills_data():
        success = False
    
    # 3. Upload de setores
    if not upload_sectors_data():
        success = False
    
    # 4. Verificar dados
    if success:
        verify_data()
        print("\n🎉 Upload concluído com sucesso!")
        print("\n💡 Agora você pode testar os novos endpoints:")
        print("   • GET /skills/statistics")
        print("   • GET /skills/top")
        print("   • GET /skills/search?q=python")
        print("   • GET /sectors/analysis")
        print("   • GET /sectors/mapping")
        print("   • GET /sectors/coverage")
    else:
        print("\n❌ Upload concluído com erros. Verifique os logs acima.")

if __name__ == "__main__":
    main()