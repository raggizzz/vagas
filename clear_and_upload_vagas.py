#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar a tabela vagas e fazer upload das vagas normalizadas
"""

import json
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

def clear_vagas_table(supabase: Client):
    """Limpa completamente a tabela vagas"""
    print("🗑️ Limpando tabela vagas...")
    try:
        # Deletar todos os registros
        result = supabase.table('vagas').delete().neq('id', 0).execute()
        print(f"✅ Tabela vagas limpa com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar tabela: {e}")
        return False

def load_normalized_jobs(file_path: str):
    """Carrega as vagas normalizadas do arquivo JSONL"""
    jobs = []
    print(f"📂 Carregando vagas de {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        job = json.loads(line)
                        jobs.append(job)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Erro na linha {line_num}: {e}")
                        continue
        
        print(f"✅ {len(jobs)} vagas carregadas com sucesso")
        return jobs
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return []

def map_job_to_vagas_format(job):
    """Mapeia uma vaga normalizada para o formato da tabela vagas"""
    return {
        'external_id': job.get('external_id', ''),
        'titulo': job.get('title', '')[:500] if job.get('title') else '',
        'empresa': job.get('company_name', '')[:200] if job.get('company_name') else '',
        'setor': job.get('sector', '')[:100] if job.get('sector') else '',
        'localizacao': job.get('location', '')[:200] if job.get('location') else '',
        'descricao': job.get('description', '')[:2000] if job.get('description') else '',
        'modalidade_trabalho': job.get('work_type', '')[:50] if job.get('work_type') else ''
    }

def upload_jobs_in_batches(supabase: Client, jobs, batch_size=100):
    """Faz upload das vagas em lotes"""
    total_jobs = len(jobs)
    successful_uploads = 0
    failed_uploads = 0
    
    print(f"📤 Iniciando upload de {total_jobs} vagas em lotes de {batch_size}...")
    
    for i in range(0, total_jobs, batch_size):
        batch = jobs[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_jobs + batch_size - 1) // batch_size
        
        print(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} vagas)...")
        
        # Mapear vagas para formato da tabela
        mapped_batch = [map_job_to_vagas_format(job) for job in batch]
        
        try:
            result = supabase.table('vagas').insert(mapped_batch).execute()
            successful_uploads += len(batch)
            print(f"✅ Lote {batch_num} enviado com sucesso ({len(batch)} vagas)")
        except Exception as e:
            failed_uploads += len(batch)
            print(f"❌ Erro no lote {batch_num}: {e}")
            
            # Tentar enviar individualmente em caso de erro
            print(f"🔄 Tentando envio individual para lote {batch_num}...")
            for job in mapped_batch:
                try:
                    supabase.table('vagas').insert([job]).execute()
                    successful_uploads += 1
                    failed_uploads -= 1
                except Exception as individual_error:
                    print(f"❌ Erro individual para vaga {job.get('external_id', 'N/A')}: {individual_error}")
    
    return successful_uploads, failed_uploads

def verify_upload(supabase: Client):
    """Verifica o resultado do upload"""
    try:
        result = supabase.table('vagas').select('id', count='exact').execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        print(f"📊 Total de vagas na tabela após upload: {count}")
        return count
    except Exception as e:
        print(f"❌ Erro ao verificar upload: {e}")
        return 0

def main():
    """Função principal"""
    print("🚀 Iniciando processo de limpeza e upload de vagas...")
    print("=" * 60)
    
    # Conectar ao Supabase
    try:
        supabase = get_supabase_client()
        print("✅ Conectado ao Supabase com sucesso")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return
    
    # Limpar tabela vagas
    if not clear_vagas_table(supabase):
        print("❌ Falha ao limpar tabela. Abortando...")
        return
    
    # Carregar vagas normalizadas
    jobs_file = 'vagas_normalizadas_individuais.jsonl'
    jobs = load_normalized_jobs(jobs_file)
    
    if not jobs:
        print("❌ Nenhuma vaga carregada. Abortando...")
        return
    
    # Fazer upload das vagas
    successful, failed = upload_jobs_in_batches(supabase, jobs)
    
    # Verificar resultado
    final_count = verify_upload(supabase)
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"📂 Vagas carregadas do arquivo: {len(jobs)}")
    print(f"✅ Vagas enviadas com sucesso: {successful}")
    print(f"❌ Vagas com falha: {failed}")
    print(f"📊 Total na tabela: {final_count}")
    print("=" * 60)
    
    if successful > 0:
        print("🎉 Upload concluído com sucesso!")
    else:
        print("😞 Nenhuma vaga foi enviada com sucesso.")

if __name__ == "__main__":
    main()