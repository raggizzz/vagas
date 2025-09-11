#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from scraper import CathoProvider, CATHO_SECTORS

def debug_setor():
    print("=== DEBUG SETOR ===")
    
    # Testar se o setor está sendo passado corretamente
    sector = "informatica"
    print(f"\n1. Testando setor: {sector}")
    print(f"   Setor existe em CATHO_SECTORS: {sector in CATHO_SECTORS}")
    
    if sector in CATHO_SECTORS:
        print(f"   URL do setor: {CATHO_SECTORS[sector]}")
    
    # Criar instância do CathoProvider
    print(f"\n2. Criando CathoProvider com setor: {sector}")
    cp = CathoProvider(sector=sector)
    print(f"   cp.sector = {cp.sector}")
    print(f"   cp.search_url = {cp.search_url}")
    print(f"   cp.name = {cp.name}")
    
    # Testar classificação manual
    print(f"\n3. Testando classificação de setor:")
    
    # Simular dados de uma vaga de TI
    titulo = "Desenvolvedor Python"
    empresa = "Tech Company"
    descricao_parts = ["Desenvolvedor Python com experiência em Django"]
    
    print(f"   Título: {titulo}")
    print(f"   Empresa: {empresa}")
    print(f"   Descrição: {descricao_parts}")
    
    # Lógica de classificação (copiada do código original)
    setor = None
    if cp.sector:
        setor = cp.sector
        print(f"   Setor definido pela instância: {setor}")
    else:
        texto_completo = f"{titulo} {empresa or ''} {' '.join(descricao_parts)}".lower()
        print(f"   Texto para análise: {texto_completo}")
        
        for sector_key, sector_data in CATHO_SECTORS.items():
            keywords = sector_data.get('keywords', [])
            matches = [keyword for keyword in keywords if keyword.lower() in texto_completo]
            if matches:
                print(f"   Setor {sector_key} - palavras encontradas: {matches}")
                if not setor:  # Pega o primeiro match
                    setor = sector_key
    
    print(f"\n   Setor final atribuído: {setor}")
    
    print("\n=== FIM DEBUG ===")

if __name__ == '__main__':
    debug_setor()