#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair 2 páginas de cada setor do Catho e salvar em CSV
"""

from scraper import extract_2_pages_per_sector_to_csv

if __name__ == "__main__":
    print("Iniciando extração de 2 páginas por setor...")
    extract_2_pages_per_sector_to_csv("vagas_2_paginas_por_setor.csv")
    print("Extração concluída!")