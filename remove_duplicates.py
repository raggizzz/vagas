#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para remover duplicatas das vagas
Critérios de duplicação:
- Empresa principal + setor + cidade + descrição similar
- Título similar + empresa + localização
"""

import json
import hashlib
from collections import defaultdict
from difflib import SequenceMatcher

def similarity(a, b):
    """Calcula similaridade entre duas strings"""
    return SequenceMatcher(None, a, b).ratio()

def normalize_text(text):
    """Normaliza texto para comparação"""
    if not text:
        return ""
    return text.lower().strip().replace("  ", " ")

def create_job_signature(vaga):
    """Cria assinatura única para a vaga"""
    empresa = normalize_text(vaga.get('informacoes_basicas', {}).get('empresa_principal', ''))
    setor = normalize_text(vaga.get('informacoes_basicas', {}).get('setor', ''))
    cidade = normalize_text(vaga.get('localizacao', {}).get('cidade_extraida', ''))
    titulo = normalize_text(vaga.get('informacoes_basicas', {}).get('fonte', ''))
    
    # Cria hash da descrição para comparação rápida
    descricao = normalize_text(vaga.get('descricao_completa', {}).get('texto_completo', ''))
    descricao_hash = hashlib.md5(descricao.encode()).hexdigest()[:8] if descricao else ""
    
    return f"{empresa}|{setor}|{cidade}|{titulo}|{descricao_hash}"

def is_duplicate(vaga1, vaga2, threshold=0.85):
    """Verifica se duas vagas são duplicatas"""
    # Critério 1: Empresa + setor + cidade iguais
    empresa1 = normalize_text(vaga1.get('informacoes_basicas', {}).get('empresa_principal', ''))
    empresa2 = normalize_text(vaga2.get('informacoes_basicas', {}).get('empresa_principal', ''))
    
    setor1 = normalize_text(vaga1.get('informacoes_basicas', {}).get('setor', ''))
    setor2 = normalize_text(vaga2.get('informacoes_basicas', {}).get('setor', ''))
    
    cidade1 = normalize_text(vaga1.get('localizacao', {}).get('cidade_extraida', ''))
    cidade2 = normalize_text(vaga2.get('localizacao', {}).get('cidade_extraida', ''))
    
    if empresa1 == empresa2 and setor1 == setor2 and cidade1 == cidade2:
        # Se empresa, setor e cidade são iguais, verifica similaridade da descrição
        desc1 = normalize_text(vaga1.get('descricao_completa', {}).get('texto_completo', ''))
        desc2 = normalize_text(vaga2.get('descricao_completa', {}).get('texto_completo', ''))
        
        if desc1 and desc2 and similarity(desc1, desc2) > threshold:
            return True
            
        # Ou se títulos são muito similares
        titulo1 = normalize_text(vaga1.get('informacoes_basicas', {}).get('fonte', ''))
        titulo2 = normalize_text(vaga2.get('informacoes_basicas', {}).get('fonte', ''))
        
        if titulo1 and titulo2 and similarity(titulo1, titulo2) > threshold:
            return True
    
    return False

def remove_duplicates(vagas):
    """Remove duplicatas da lista de vagas"""
    print(f"Processando {len(vagas)} vagas...")
    
    # Agrupa vagas por assinatura para comparação rápida
    signature_groups = defaultdict(list)
    for vaga in vagas:
        signature = create_job_signature(vaga)
        signature_groups[signature].append(vaga)
    
    unique_vagas = []
    duplicates_found = 0
    
    # Processa cada grupo de assinaturas
    for signature, group_vagas in signature_groups.items():
        if len(group_vagas) == 1:
            unique_vagas.extend(group_vagas)
        else:
            # Dentro do grupo, remove duplicatas mais refinadas
            group_unique = []
            for vaga in group_vagas:
                is_dup = False
                for unique_vaga in group_unique:
                    if is_duplicate(vaga, unique_vaga):
                        is_dup = True
                        duplicates_found += 1
                        print(f"Duplicata encontrada: ID {vaga.get('id')} similar a ID {unique_vaga.get('id')}")
                        break
                
                if not is_dup:
                    group_unique.append(vaga)
            
            unique_vagas.extend(group_unique)
    
    print(f"Duplicatas removidas: {duplicates_found}")
    print(f"Vagas únicas restantes: {len(unique_vagas)}")
    
    return unique_vagas

def main():
    input_file = 'vagas_todos_setores_estruturadas_corrigidas_completo.jsonl'
    output_file = 'vagas_todos_setores_sem_duplicatas.jsonl'
    
    print("Carregando dados...")
    vagas = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                vagas.append(json.loads(line))
    
    print(f"Total de vagas carregadas: {len(vagas)}")
    
    # Remove duplicatas
    unique_vagas = remove_duplicates(vagas)
    
    # Reordena IDs
    for i, vaga in enumerate(unique_vagas, 1):
        vaga['id'] = i
    
    # Salva resultado
    print(f"Salvando {len(unique_vagas)} vagas únicas em {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for vaga in unique_vagas:
            f.write(json.dumps(vaga, ensure_ascii=False) + '\n')
    
    # Relatório final
    duplicates_removed = len(vagas) - len(unique_vagas)
    reduction_percentage = (duplicates_removed / len(vagas)) * 100
    
    print("\n=== RELATÓRIO DE REMOÇÃO DE DUPLICATAS ===")
    print(f"Vagas originais: {len(vagas)}")
    print(f"Vagas únicas: {len(unique_vagas)}")
    print(f"Duplicatas removidas: {duplicates_removed}")
    print(f"Redução: {reduction_percentage:.1f}%")
    print(f"Arquivo salvo: {output_file}")

if __name__ == "__main__":
    main()