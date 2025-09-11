#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair vagas de todos os setores do Catho
Extrai 2 páginas de cada setor e salva em CSV
"""

import csv
import time
import random
from bs4 import BeautifulSoup
from scraper import CathoProvider, CATHO_SECTORS

def extract_all_sectors_to_csv(output_file="catho_all_sectors_2pages.csv", pages_per_sector=2):
    """
    Extrai vagas de todos os setores do Catho e salva em CSV
    
    Args:
        output_file: Nome do arquivo CSV de saída
        pages_per_sector: Número de páginas a extrair por setor
    """
    print(f"Iniciando extração de {pages_per_sector} páginas de cada setor...")
    print(f"Total de setores: {len(CATHO_SECTORS)}")
    
    all_jobs = []
    
    # Criar uma única instância do CathoProvider
    catho = CathoProvider()
    
    # Configurar driver e fazer login uma vez
    if not catho.setup_driver_and_login():
        print("❌ Falha ao configurar driver")
        return
    
    try:
        # Iterar por todos os setores
        for sector_name, sector_info in CATHO_SECTORS.items():
            print(f"\n=== Processando setor: {sector_name} ===")
            
            try:
                # Configurar URL do setor
                search_url = sector_info['url'] if isinstance(sector_info, dict) else sector_info
                
                # Processar páginas do setor
                sector_jobs = []
                
                for page in range(1, pages_per_sector + 1):
                    # Construir URL da página
                    if '?' in search_url:
                        url = f"{search_url}&p={page}"
                    else:
                        url = f"{search_url}?p={page}"
                    
                    print(f"[Catho] Página {page}: {url}")
                    
                    # Navegar para a página
                    catho.driver.get(url)
                    time.sleep(random.uniform(1, 2))
                    
                    # Obter HTML da página
                    soup = BeautifulSoup(catho.driver.page_source, 'html.parser')
                    
                    # Verificar se é página 404
                    if "404" in catho.driver.title or "não encontrada" in catho.driver.page_source.lower():
                        print(f"[Catho] Página {page}: 404 - fim do setor")
                        break
                    
                    # Extrair vagas da página
                    jobs_from_page = catho.extract_jobs_from_listing(soup, extract_full_details=False, no_details=False)
                    
                    if jobs_from_page:
                        # Definir o setor correto para cada vaga
                        for job in jobs_from_page:
                            if hasattr(job, 'setor'):
                                job.setor = sector_name
                            elif isinstance(job, dict):
                                job['setor'] = sector_name
                        
                        sector_jobs.extend(jobs_from_page)
                        print(f"[Catho] Página {page}: {len(jobs_from_page)} vagas extraídas")
                    else:
                        print(f"[Catho] Página {page}: Nenhuma vaga encontrada")
                
                print(f"[Catho] Setor {sector_name} concluído. Total: {len(sector_jobs)} vagas")
                all_jobs.extend(sector_jobs)
                
                # Pausa entre setores
                time.sleep(2)
                
            except Exception as e:
                print(f"Erro ao processar setor {sector_name}: {e}")
                continue
    
    finally:
        # Fechar driver
        print("[Catho] Fechando driver...")
        if catho.driver:
            try:
                catho.driver.quit()
                print("[Catho] Driver fechado")
            except Exception as e:
                print(f"[Catho] Erro ao fechar driver: {e}")
    
    # Salvar resultados em CSV
    if all_jobs:
        print(f"\n💾 Salvando {len(all_jobs)} vagas em {output_file}...")
        
        # Preparar dados para CSV
        csv_data = []
        for job in all_jobs:
            if hasattr(job, '__dict__'):
                # Se é um objeto Job
                job_dict = {
                    'titulo': getattr(job, 'titulo', ''),
                    'empresa': getattr(job, 'empresa', ''),
                    'local': getattr(job, 'local', ''),
                    'salario': getattr(job, 'salario', ''),
                    'descricao': getattr(job, 'descricao', ''),
                    'link': getattr(job, 'link', ''),
                    'setor': getattr(job, 'setor', ''),
                    'data_publicacao': getattr(job, 'data_publicacao', ''),
                    'tipo_contrato': getattr(job, 'tipo_contrato', ''),
                    'nivel': getattr(job, 'nivel', '')
                }
            else:
                # Se é um dicionário
                job_dict = job
            
            csv_data.append(job_dict)
        
        # Escrever CSV
        if csv_data:
            fieldnames = ['titulo', 'empresa', 'local', 'salario', 'descricao', 'link', 'setor', 'data_publicacao', 'tipo_contrato', 'nivel']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"✅ Arquivo {output_file} criado com sucesso!")
        else:
            print("❌ Nenhum dado para salvar")
    else:
        print("❌ Nenhuma vaga foi extraída")
    
    
    print(f"\nExtração concluída! Total de vagas coletadas: {len(all_jobs)}")
    
    # Estatísticas por setor
    if all_jobs:
        sector_stats = {}
        for job in all_jobs:
            if hasattr(job, 'setor'):
                sector = job.setor or 'Não especificado'
            elif isinstance(job, dict):
                sector = job.get('setor', 'Não especificado')
            else:
                sector = 'Não especificado'
            sector_stats[sector] = sector_stats.get(sector, 0) + 1

        print("\n=== Estatísticas por setor ===")
        for sector, count in sorted(sector_stats.items()):
            print(f"{sector}: {count} vagas")

if __name__ == "__main__":
    # Executar extração
    extract_all_sectors_to_csv()
    print("\n🎉 Extração concluída!")