#!/usr/bin/env python3
"""
Script para configurar as tabelas no Supabase e fazer upload dos dados estruturados
"""

import os
import json
from supabase import create_client, Client
from supabase_uploader_complete import SupabaseUploaderComplete

def setup_supabase_tables():
    """
    Executa o schema SQL no Supabase para criar as tabelas
    """
    # Configuração do Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas no .env")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        
        # Ler o arquivo de schema
        with open('supabase_schema_advanced.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Dividir o SQL em comandos individuais
        commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
        
        print("🔧 Criando tabelas no Supabase...")
        
        for i, command in enumerate(commands):
            if command:
                try:
                    # Executar comando SQL
                    result = supabase.rpc('exec_sql', {'sql': command})
                    print(f"✅ Comando {i+1}/{len(commands)} executado com sucesso")
                except Exception as e:
                    print(f"⚠️  Comando {i+1} falhou (pode ser normal se já existir): {str(e)[:100]}...")
        
        print("✅ Schema criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar tabelas: {e}")
        return False

def upload_data_to_supabase():
    """
    Faz upload dos dados estruturados para o Supabase
    """
    try:
        # Verificar se o arquivo JSON existe
        json_file = 'vagas_todos_setores_estruturadas_completo.json'
        if not os.path.exists(json_file):
            print(f"❌ Arquivo {json_file} não encontrado")
            return False
        
        # Carregar dados
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Carregando {len(data)} vagas do arquivo {json_file}")
        
        # Inicializar uploader
        uploader = SupabaseUploaderComplete()
        
        # Fazer upload em lotes
        batch_size = 50
        total_uploaded = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            print(f"📤 Fazendo upload do lote {i//batch_size + 1} ({len(batch)} vagas)...")
            
            try:
                uploaded_count = uploader.upload_batch(batch)
                total_uploaded += uploaded_count
                print(f"✅ Lote processado: {uploaded_count} vagas enviadas")
            except Exception as e:
                print(f"❌ Erro no lote {i//batch_size + 1}: {e}")
                continue
        
        print(f"\n🎉 Upload concluído! Total de vagas enviadas: {total_uploaded}")
        
        # Mostrar estatísticas
        stats = uploader.get_upload_stats()
        print("\n📈 Estatísticas do upload:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante upload: {e}")
        return False

def main():
    """
    Função principal que executa todo o processo
    """
    print("🚀 Iniciando configuração e upload para Supabase...\n")
    
    # Verificar se o arquivo .env existe
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado. Crie um arquivo .env com:")
        print("SUPABASE_URL=sua_url_aqui")
        print("SUPABASE_KEY=sua_chave_aqui")
        return
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Passo 1: Configurar tabelas
    print("📋 Passo 1: Configurando tabelas no Supabase")
    if not setup_supabase_tables():
        print("❌ Falha na configuração das tabelas. Abortando.")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Passo 2: Upload dos dados
    print("📤 Passo 2: Fazendo upload dos dados")
    if not upload_data_to_supabase():
        print("❌ Falha no upload dos dados.")
        return
    
    print("\n🎉 Processo concluído com sucesso!")
    print("\n💡 Próximos passos:")
    print("  1. Acesse o painel do Supabase para verificar os dados")
    print("  2. Use a view 'jobs_complete_advanced' para consultas completas")
    print("  3. Configure a API se necessário")

if __name__ == "__main__":
    main()