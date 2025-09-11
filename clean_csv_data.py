#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar dados problemáticos dos arquivos CSV do Catho
Remove linhas com dados corrompidos da interface do site
"""

import pandas as pd
import re
import os
from pathlib import Path

def clean_csv_file(input_file, output_file=None):
    """
    Limpa um arquivo CSV removendo linhas com dados problemáticos
    
    Args:
        input_file (str): Caminho para o arquivo CSV de entrada
        output_file (str): Caminho para o arquivo CSV limpo (opcional)
    """
    if output_file is None:
        # Se não especificado, sobrescreve o arquivo original
        output_file = input_file
    
    print(f"Limpando arquivo: {input_file}")
    
    try:
        # Lê o arquivo CSV
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"Total de linhas antes da limpeza: {len(df)}")
        print(f"Colunas encontradas: {list(df.columns)}")
        
        # Identifica os nomes das colunas (podem variar entre arquivos)
        titulo_col = None
        link_col = None
        descricao_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'titulo' in col_lower or 'título' in col_lower:
                titulo_col = col
            elif 'link' in col_lower:
                link_col = col
            elif 'descricao' in col_lower or 'descrição' in col_lower:
                descricao_col = col
        
        print(f"Coluna título: {titulo_col}")
        print(f"Coluna link: {link_col}")
        print(f"Coluna descrição: {descricao_col}")
        
        # Padrões problemáticos para remover
        problematic_patterns = [
            r'O que v"',  # Texto truncado
            r'Menu\s+Ajuda\s+Perfil',  # Menu do site
            r'717\.300 resultados',  # Contador de resultados
            r'\d+\.\d+ resultados',  # Qualquer contador de resultados
            r'Vagas de emprego em todo Brasil',  # Título genérico
            r'Ordenar por:',  # Opções de ordenação
            r'Limpar filtros',  # Botões da interface
            r'Para salvar a busca',  # Instruções do site
            r'mais relevantes',  # Opções de ordenação
            r'^\s*Menu\s*$',  # Linha só com "Menu"
            r'Buscar\s+Salário\s+Distância',  # Filtros do site
        ]
        
        # Combina todos os padrões em uma única regex
        combined_pattern = '|'.join(problematic_patterns)
        
        # Remove linhas onde qualquer coluna contém os padrões problemáticos
        mask = df.astype(str).apply(lambda x: x.str.contains(combined_pattern, case=False, na=False, regex=True)).any(axis=1)
        
        # Filtra as linhas problemáticas
        df_clean = df[~mask]
        
        # Remove linhas onde o título é "Vagas de emprego em todo Brasil" (se a coluna existir)
        if titulo_col and titulo_col in df_clean.columns:
            df_clean = df_clean[df_clean[titulo_col] != 'Vagas de emprego em todo Brasil']
        
        # Remove linhas onde a descrição contém apenas elementos da interface (se a coluna existir)
        if descricao_col and descricao_col in df_clean.columns:
            interface_desc_patterns = [
                r'^Menu\s',
                r'Ajuda\s+Perfil\s+Buscar',
                r'\d+ resultados\s*Ordenar por',
                r'^\s*$'  # Linhas vazias
            ]
            
            interface_pattern = '|'.join(interface_desc_patterns)
            desc_mask = df_clean[descricao_col].astype(str).str.contains(interface_pattern, case=False, na=False, regex=True)
            df_clean = df_clean[~desc_mask]
        
        # Remove duplicatas baseadas no link da vaga (se a coluna existir)
        if link_col and link_col in df_clean.columns:
            df_clean = df_clean.drop_duplicates(subset=[link_col], keep='first')
        
        # Remove linhas onde campos essenciais estão vazios
        essential_cols = []
        if titulo_col:
            essential_cols.append(titulo_col)
        if link_col:
            essential_cols.append(link_col)
        
        if essential_cols:
            df_clean = df_clean.dropna(subset=essential_cols)
        
        print(f"Total de linhas após a limpeza: {len(df_clean)}")
        print(f"Linhas removidas: {len(df) - len(df_clean)}")
        
        # Salva o arquivo limpo
        df_clean.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Arquivo limpo salvo em: {output_file}")
        
        return df_clean
        
    except Exception as e:
        print(f"Erro ao processar arquivo {input_file}: {str(e)}")
        return None

def main():
    """
    Função principal para limpar os arquivos CSV
    """
    # Diretório de trabalho
    base_dir = Path(r"c:\Users\nuxay\Documents\BancoDeDados")
    
    # Arquivos para limpar
    files_to_clean = [
        "vagas_informatica_teste.csv",
        "vagas_informatica_teste_Informatica.csv"
    ]
    
    for filename in files_to_clean:
        file_path = base_dir / filename
        if file_path.exists():
            # Cria um backup antes de limpar
            backup_path = base_dir / f"{filename}.backup"
            if not backup_path.exists():
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"Backup criado: {backup_path}")
            
            # Limpa o arquivo
            clean_csv_file(str(file_path))
            print("-" * 50)
        else:
            print(f"Arquivo não encontrado: {file_path}")

if __name__ == "__main__":
    main()