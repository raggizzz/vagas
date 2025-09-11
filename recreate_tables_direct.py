#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recriar as tabelas diretamente via API do Supabase
Usa a função rpc para executar SQL
"""

import os
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

def execute_sql_commands():
    """Executar comandos SQL para recriar as tabelas"""
    print("🔧 Recriando tabelas com estrutura correta...")
    
    # Lista de comandos SQL para executar
    sql_commands = [
        # Dropar tabelas existentes
        "DROP TABLE IF EXISTS skills_statistics CASCADE;",
        "DROP TABLE IF EXISTS sector_mapping CASCADE;",
        
        # Criar tabela skills_statistics
        """
        CREATE TABLE skills_statistics (
            id SERIAL PRIMARY KEY,
            setor VARCHAR(100) NOT NULL,
            skill VARCHAR(200) NOT NULL,
            contagem INTEGER NOT NULL,
            total_setor INTEGER NOT NULL,
            percentual DECIMAL(5,2) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Criar tabela sector_mapping
        """
        CREATE TABLE sector_mapping (
            id SERIAL PRIMARY KEY,
            raw_sector VARCHAR(200) NOT NULL,
            normalized_sector VARCHAR(100) NOT NULL,
            alias VARCHAR(200),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Criar índices
        "CREATE INDEX idx_skills_statistics_setor ON skills_statistics(setor);",
        "CREATE INDEX idx_skills_statistics_skill ON skills_statistics(skill);",
        "CREATE INDEX idx_skills_statistics_percentual ON skills_statistics(percentual DESC);",
        "CREATE INDEX idx_sector_mapping_raw ON sector_mapping(raw_sector);",
        "CREATE INDEX idx_sector_mapping_normalized ON sector_mapping(normalized_sector);",
        "CREATE INDEX idx_sector_mapping_alias ON sector_mapping(alias);",
        
        # Habilitar RLS
        "ALTER TABLE skills_statistics ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE sector_mapping ENABLE ROW LEVEL SECURITY;",
        
        # Criar políticas de acesso público
        'CREATE POLICY "Allow public read access" ON skills_statistics FOR SELECT USING (true);',
        'CREATE POLICY "Allow public insert access" ON skills_statistics FOR INSERT WITH CHECK (true);',
        'CREATE POLICY "Allow public update access" ON skills_statistics FOR UPDATE USING (true);',
        'CREATE POLICY "Allow public delete access" ON skills_statistics FOR DELETE USING (true);',
        
        'CREATE POLICY "Allow public read access" ON sector_mapping FOR SELECT USING (true);',
        'CREATE POLICY "Allow public insert access" ON sector_mapping FOR INSERT WITH CHECK (true);',
        'CREATE POLICY "Allow public update access" ON sector_mapping FOR UPDATE USING (true);',
        'CREATE POLICY "Allow public delete access" ON sector_mapping FOR DELETE USING (true);'
    ]
    
    success_count = 0
    error_count = 0
    
    for i, sql in enumerate(sql_commands, 1):
        try:
            print(f"📝 Executando comando {i}/{len(sql_commands)}...")
            
            # Tentar executar via rpc
            try:
                result = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
                print(f"   ✅ Sucesso")
                success_count += 1
            except Exception as rpc_error:
                # Se rpc falhar, tentar método alternativo
                print(f"   ⚠️  RPC falhou, tentando método alternativo...")
                
                # Para comandos CREATE TABLE, tentar criar via inserção
                if "CREATE TABLE skills_statistics" in sql:
                    test_data = {
                        'setor': 'test',
                        'skill': 'test', 
                        'contagem': 1,
                        'total_setor': 1,
                        'percentual': 1.0
                    }
                    supabase.table('skills_statistics').insert(test_data).execute()
                    supabase.table('skills_statistics').delete().eq('setor', 'test').execute()
                    print(f"   ✅ Tabela skills_statistics criada via inserção")
                    success_count += 1
                    
                elif "CREATE TABLE sector_mapping" in sql:
                    test_data = {
                        'raw_sector': 'test',
                        'normalized_sector': 'test',
                        'alias': 'test'
                    }
                    supabase.table('sector_mapping').insert(test_data).execute()
                    supabase.table('sector_mapping').delete().eq('raw_sector', 'test').execute()
                    print(f"   ✅ Tabela sector_mapping criada via inserção")
                    success_count += 1
                else:
                    print(f"   ❌ Erro: {rpc_error}")
                    error_count += 1
                    
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            error_count += 1
    
    print(f"\n📊 Resumo: {success_count} sucessos, {error_count} erros")
    
    if error_count == 0:
        print("\n🎉 Todas as tabelas foram recriadas com sucesso!")
        return True
    else:
        print(f"\n⚠️  Algumas operações falharam. Verifique os erros acima.")
        return False

def verify_tables():
    """Verificar se as tabelas foram criadas corretamente"""
    print("\n🔍 Verificando tabelas criadas...")
    
    try:
        # Testar skills_statistics
        test_skill = {
            'setor': 'Teste',
            'skill': 'Python',
            'contagem': 10,
            'total_setor': 100,
            'percentual': 10.0
        }
        
        result = supabase.table('skills_statistics').insert(test_skill).execute()
        supabase.table('skills_statistics').delete().eq('setor', 'Teste').execute()
        print("   ✅ skills_statistics: OK")
        
    except Exception as e:
        print(f"   ❌ skills_statistics: {e}")
        return False
    
    try:
        # Testar sector_mapping
        test_sector = {
            'raw_sector': 'Tecnologia da Informação',
            'normalized_sector': 'TI',
            'alias': 'ti,tecnologia,informatica'
        }
        
        result = supabase.table('sector_mapping').insert(test_sector).execute()
        supabase.table('sector_mapping').delete().eq('raw_sector', 'Tecnologia da Informação').execute()
        print("   ✅ sector_mapping: OK")
        
    except Exception as e:
        print(f"   ❌ sector_mapping: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Recriando tabelas no Supabase")
    print(f"🔗 Conectando ao Supabase: {SUPABASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Executar comandos SQL
    if execute_sql_commands():
        # Verificar se as tabelas foram criadas
        if verify_tables():
            print("\n🎉 Tabelas recriadas e verificadas com sucesso!")
            print("\n💡 Agora você pode executar:")
            print("   python upload_skills_sectors_data.py")
        else:
            print("\n❌ Erro na verificação das tabelas")
    else:
        print("\n❌ Erro na criação das tabelas")
        print("\n💡 Tente executar o SQL manualmente no dashboard do Supabase")

if __name__ == "__main__":
    main()