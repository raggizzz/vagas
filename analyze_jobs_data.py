#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar a estrutura dos dados da tabela jobs
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

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

def analyze_jobs_structure():
    """Analisa a estrutura dos dados da tabela jobs"""
    print("🔍 Analisando estrutura da tabela jobs...")
    
    try:
        # Buscar algumas vagas para análise
        result = supabase.table('jobs').select('id, titulo, habilidades, requisitos, setor').limit(10).execute()
        
        if not result.data:
            print("❌ Nenhum dado encontrado na tabela jobs")
            return
        
        print(f"✅ Encontrados {len(result.data)} registros")
        print("\n📋 Amostras de dados:")
        print("=" * 80)
        
        for i, job in enumerate(result.data[:5], 1):
            print(f"\n🔸 Vaga {i}:")
            print(f"   ID: {job['id']}")
            print(f"   Título: {job['titulo'][:60]}..." if len(job['titulo']) > 60 else f"   Título: {job['titulo']}")
            print(f"   Setor: {job['setor']}")
            print(f"   Habilidades: {job['habilidades']}")
            print(f"   Requisitos: {job['requisitos']}")
            print("-" * 60)
        
        # Analisar tipos de dados
        print("\n📊 Análise dos tipos de dados:")
        sample_job = result.data[0]
        
        print(f"   - habilidades: {type(sample_job['habilidades'])} - {sample_job['habilidades'][:100] if sample_job['habilidades'] else 'None'}")
        print(f"   - requisitos: {type(sample_job['requisitos'])} - {sample_job['requisitos'][:100] if sample_job['requisitos'] else 'None'}")
        
        # Contar setores únicos
        sectors_result = supabase.table('jobs').select('setor').execute()
        sectors = [job['setor'] for job in sectors_result.data if job['setor']]
        unique_sectors = list(set(sectors))
        
        print(f"\n🏭 Setores únicos encontrados ({len(unique_sectors)}):")
        for sector in sorted(unique_sectors):
            count = sectors.count(sector)
            print(f"   - {sector}: {count} vagas")
        
        return result.data
        
    except Exception as e:
        print(f"❌ Erro ao analisar dados: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 Análise da estrutura dos dados da tabela jobs")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    
    data = analyze_jobs_structure()
    
    if data:
        print("\n✅ Análise concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Criar função para extrair habilidades dos campos de texto")
        print("   2. Implementar análise de pontos em comum")
        print("   3. Criar endpoint da API")
    else:
        print("\n❌ Falha na análise dos dados")

if __name__ == "__main__":
    main()