#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fazer upload dos dados limpos para o Supabase
"""

import json
import os
from supabase import create_client, Client
from typing import List, Dict, Any
import time

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def load_data(filename: str) -> List[Dict[Any, Any]]:
    """Carrega dados do arquivo JSONL"""
    print(f"Carregando dados de: {filename}")
    
    vagas = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    vaga = json.loads(line)
                    vagas.append(vaga)
                except json.JSONDecodeError as e:
                    print(f"Erro ao processar linha {line_num}: {e}")
    
    print(f"Total de vagas carregadas: {len(vagas)}")
    return vagas

def transform_data_for_supabase(vagas: List[Dict]) -> List[Dict]:
    """Transforma dados para formato adequado ao Supabase"""
    print("Transformando dados para formato Supabase...")
    
    transformed_vagas = []
    
    for vaga in vagas:
        # Extrai informações principais
        info_basicas = vaga.get('informacoes_basicas', {})
        localizacao = vaga.get('localizacao', {})
        descricao = vaga.get('descricao_completa', {})
        
        # Monta registro para Supabase
        supabase_record = {
            'id': vaga.get('id'),
            'setor': info_basicas.get('setor', ''),
            'empresa_principal': info_basicas.get('empresa_principal', ''),
            'titulo_vaga': info_basicas.get('titulo_vaga', ''),
            'modalidade': info_basicas.get('modalidade', ''),
            'nivel_experiencia': info_basicas.get('nivel_experiencia', ''),
            'tipo_contrato': info_basicas.get('tipo_contrato', ''),
            'salario_informado': info_basicas.get('salario_informado', ''),
            'beneficios': info_basicas.get('beneficios', []),
            
            # Localização
            'estado': localizacao.get('estado', ''),
            'cidade_extraida': localizacao.get('cidade_extraida', ''),
            'regiao': localizacao.get('regiao', ''),
            'localizacao_completa': localizacao.get('localizacao_completa', ''),
            
            # Descrição
            'texto_completo': descricao.get('texto_completo', ''),
            'responsabilidades': descricao.get('responsabilidades', []),
            'habilidades_requeridas': descricao.get('habilidades_requeridas', []),
            'empresas_mencionadas': descricao.get('empresas_mencionadas', []),
            
            # Metadados
            'data_upload': time.strftime('%Y-%m-%d %H:%M:%S'),
            'versao_dados': '1.0_sem_duplicatas'
        }
        
        transformed_vagas.append(supabase_record)
    
    print(f"Dados transformados: {len(transformed_vagas)} registros")
    return transformed_vagas

def upload_to_supabase(data: List[Dict], table_name: str = 'vagas') -> bool:
    """Faz upload dos dados para o Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_ANON_KEY não configuradas")
        print("\nPara configurar:")
        print("1. No PowerShell:")
        print("   $env:SUPABASE_URL = 'sua_url_aqui'")
        print("   $env:SUPABASE_ANON_KEY = 'sua_chave_aqui'")
        print("\n2. Ou crie um arquivo .env com:")
        print("   SUPABASE_URL=sua_url_aqui")
        print("   SUPABASE_ANON_KEY=sua_chave_aqui")
        return False
    
    try:
        # Conecta ao Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Conectado ao Supabase: {SUPABASE_URL}")
        
        # Verifica se a tabela existe
        print(f"Verificando tabela '{table_name}'...")
        
        # Upload em lotes para evitar timeout
        batch_size = 100
        total_batches = (len(data) + batch_size - 1) // batch_size
        
        print(f"Iniciando upload em {total_batches} lotes de {batch_size} registros...")
        
        uploaded_count = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"Enviando lote {batch_num}/{total_batches} ({len(batch)} registros)...")
            
            try:
                # Insere dados (upsert para evitar duplicatas)
                result = supabase.table(table_name).upsert(batch).execute()
                
                if result.data:
                    uploaded_count += len(batch)
                    print(f"✅ Lote {batch_num} enviado com sucesso")
                else:
                    print(f"⚠️  Lote {batch_num} retornou resultado vazio")
                
                # Pausa entre lotes para evitar rate limiting
                if batch_num < total_batches:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Erro no lote {batch_num}: {e}")
                continue
        
        print(f"\n✅ Upload concluído!")
        print(f"Total de registros enviados: {uploaded_count}/{len(data)}")
        
        # Verifica dados na tabela
        count_result = supabase.table(table_name).select('id', count='exact').execute()
        total_in_table = count_result.count if hasattr(count_result, 'count') else 'N/A'
        print(f"Total de registros na tabela: {total_in_table}")
        
        return uploaded_count == len(data)
        
    except Exception as e:
        print(f"❌ Erro ao conectar/enviar para Supabase: {e}")
        return False

def create_table_schema():
    """Mostra o schema SQL para criar a tabela no Supabase"""
    schema = """
-- Schema SQL para criar a tabela 'vagas' no Supabase

CREATE TABLE IF NOT EXISTS vagas (
    id BIGINT PRIMARY KEY,
    setor TEXT,
    empresa_principal TEXT,
    titulo_vaga TEXT,
    modalidade TEXT,
    nivel_experiencia TEXT,
    tipo_contrato TEXT,
    salario_informado TEXT,
    beneficios JSONB,
    
    -- Localização
    estado TEXT,
    cidade_extraida TEXT,
    regiao TEXT,
    localizacao_completa TEXT,
    
    -- Descrição
    texto_completo TEXT,
    responsabilidades JSONB,
    habilidades_requeridas JSONB,
    empresas_mencionadas JSONB,
    
    -- Metadados
    data_upload TIMESTAMP DEFAULT NOW(),
    versao_dados TEXT,
    
    -- Índices para consultas rápidas
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_vagas_setor ON vagas(setor);
CREATE INDEX IF NOT EXISTS idx_vagas_empresa ON vagas(empresa_principal);
CREATE INDEX IF NOT EXISTS idx_vagas_cidade ON vagas(cidade_extraida);
CREATE INDEX IF NOT EXISTS idx_vagas_estado ON vagas(estado);
CREATE INDEX IF NOT EXISTS idx_vagas_modalidade ON vagas(modalidade);

-- RLS (Row Level Security) - opcional
ALTER TABLE vagas ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública (ajuste conforme necessário)
CREATE POLICY "Permitir leitura pública" ON vagas
    FOR SELECT USING (true);
"""
    
    print("\n=== SCHEMA SQL PARA SUPABASE ===")
    print(schema)
    
    # Salva schema em arquivo
    with open('schema_supabase.sql', 'w', encoding='utf-8') as f:
        f.write(schema)
    
    print("\n✅ Schema salvo em: schema_supabase.sql")

def main():
    filename = 'vagas_todos_setores_sem_duplicatas.jsonl'
    
    print("=== UPLOAD PARA SUPABASE ===")
    print(f"Arquivo de dados: {filename}")
    
    # Verifica se arquivo existe
    if not os.path.exists(filename):
        print(f"❌ Arquivo não encontrado: {filename}")
        return
    
    # Gera schema SQL
    create_table_schema()
    
    # Carrega dados
    vagas = load_data(filename)
    
    if not vagas:
        print("❌ Nenhuma vaga encontrada no arquivo")
        return
    
    # Transforma dados
    transformed_data = transform_data_for_supabase(vagas)
    
    # Salva dados transformados para verificação
    output_file = 'vagas_para_supabase.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data[:5], f, ensure_ascii=False, indent=2)  # Salva apenas 5 exemplos
    
    print(f"\n✅ Exemplo de dados transformados salvo em: {output_file}")
    
    # Faz upload
    success = upload_to_supabase(transformed_data)
    
    if success:
        print("\n🎉 Upload concluído com sucesso!")
    else:
        print("\n❌ Upload falhou. Verifique as configurações e tente novamente.")
        print("\nPara instalar dependências:")
        print("pip install supabase")

if __name__ == "__main__":
    main()