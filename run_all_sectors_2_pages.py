#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair 2 páginas de vagas de todos os setores do Catho
"""

import sys
import os
from scraper import CathoProvider, CATHO_SECTORS
import time

def main():
    print("[EXTRAÇÃO] Iniciando extração de 2 páginas de todos os setores...")
    
    # Lista de setores para processar
    sectors_to_process = list(CATHO_SECTORS.keys())
    print(f"[EXTRAÇÃO] Setores a processar: {len(sectors_to_process)}")
    for i, sector in enumerate(sectors_to_process, 1):
        print(f"  {i}. {sector}")
    
    # Configurar provider com lista de setores
    provider = CathoProvider(sectors_list=sectors_to_process)
    
    # Arquivo de saída
    output_file = "vagas_todos_setores_2_paginas.csv"
    
    try:
        # Executar extração
        print(f"\n[EXTRAÇÃO] Iniciando extração para arquivo: {output_file}")
        start_time = time.time()
        
        # Usar o método search com 2 páginas
        jobs_extracted = 0
        for job in provider.search(termo=None, paginas=2):
            jobs_extracted += 1
            if jobs_extracted % 50 == 0:
                print(f"[EXTRAÇÃO] Progresso: {jobs_extracted} vagas extraídas...")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n[EXTRAÇÃO] ✅ Extração concluída!")
        print(f"[EXTRAÇÃO] Total de vagas extraídas: {jobs_extracted}")
        print(f"[EXTRAÇÃO] Tempo total: {duration:.2f} segundos")
        print(f"[EXTRAÇÃO] Arquivo gerado: {output_file}")
        
        # Verificar se o arquivo foi criado
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"[EXTRAÇÃO] Tamanho do arquivo: {file_size:,} bytes")
        else:
            print(f"[EXTRAÇÃO] ⚠️ Arquivo {output_file} não foi encontrado")
            
    except KeyboardInterrupt:
        print("\n[EXTRAÇÃO] ⚠️ Extração interrompida pelo usuário")
    except Exception as e:
        print(f"\n[EXTRAÇÃO] ❌ Erro durante a extração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpar recursos
        try:
            if hasattr(provider, 'driver') and provider.driver:
                provider.driver.quit()
                print("[EXTRAÇÃO] Driver fechado")
        except Exception as e:
            print(f"[EXTRAÇÃO] Erro ao fechar driver: {e}")

if __name__ == "__main__":
    main()