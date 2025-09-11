#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a qualidade dos dados após remoção de duplicatas
"""

import json
from collections import Counter, defaultdict

def analyze_data_quality(filename):
    """Analisa a qualidade dos dados"""
    print(f"Analisando arquivo: {filename}")
    
    vagas = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                vagas.append(json.loads(line))
    
    print(f"\n=== ANÁLISE DE QUALIDADE DOS DADOS ===")
    print(f"Total de vagas: {len(vagas)}")
    
    # Análise por setor
    setores = Counter()
    empresas = Counter()
    cidades = Counter()
    modalidades = Counter()
    
    vagas_sem_descricao = 0
    vagas_sem_empresa = 0
    vagas_sem_setor = 0
    vagas_sem_cidade = 0
    
    for vaga in vagas:
        # Setor
        setor = vaga.get('informacoes_basicas', {}).get('setor', '')
        if setor:
            setores[setor] += 1
        else:
            vagas_sem_setor += 1
        
        # Empresa
        empresa = vaga.get('informacoes_basicas', {}).get('empresa_principal', '')
        if empresa:
            empresas[empresa] += 1
        else:
            vagas_sem_empresa += 1
        
        # Cidade
        cidade = vaga.get('localizacao', {}).get('cidade_extraida', '')
        if cidade:
            cidades[cidade] += 1
        else:
            vagas_sem_cidade += 1
        
        # Modalidade
        modalidade = vaga.get('informacoes_basicas', {}).get('modalidade', '')
        modalidades[modalidade] += 1
        
        # Descrição
        descricao = vaga.get('descricao_completa', {}).get('texto_completo', '')
        if not descricao:
            vagas_sem_descricao += 1
    
    print(f"\n=== DISTRIBUIÇÃO POR SETOR ===")
    for setor, count in setores.most_common():
        percentage = (count / len(vagas)) * 100
        print(f"{setor}: {count} vagas ({percentage:.1f}%)")
    
    print(f"\n=== TOP 10 EMPRESAS ===")
    for empresa, count in empresas.most_common(10):
        percentage = (count / len(vagas)) * 100
        print(f"{empresa}: {count} vagas ({percentage:.1f}%)")
    
    print(f"\n=== TOP 10 CIDADES ===")
    for cidade, count in cidades.most_common(10):
        percentage = (count / len(vagas)) * 100
        print(f"{cidade}: {count} vagas ({percentage:.1f}%)")
    
    print(f"\n=== MODALIDADES ===")
    for modalidade, count in modalidades.most_common():
        percentage = (count / len(vagas)) * 100
        print(f"{modalidade}: {count} vagas ({percentage:.1f}%)")
    
    print(f"\n=== QUALIDADE DOS DADOS ===")
    print(f"Vagas sem descrição: {vagas_sem_descricao} ({(vagas_sem_descricao/len(vagas)*100):.1f}%)")
    print(f"Vagas sem empresa: {vagas_sem_empresa} ({(vagas_sem_empresa/len(vagas)*100):.1f}%)")
    print(f"Vagas sem setor: {vagas_sem_setor} ({(vagas_sem_setor/len(vagas)*100):.1f}%)")
    print(f"Vagas sem cidade: {vagas_sem_cidade} ({(vagas_sem_cidade/len(vagas)*100):.1f}%)")
    
    # Verifica IDs únicos
    ids = [vaga.get('id') for vaga in vagas]
    ids_unicos = len(set(ids))
    print(f"\n=== INTEGRIDADE DOS DADOS ===")
    print(f"IDs únicos: {ids_unicos}/{len(vagas)} ({(ids_unicos/len(vagas)*100):.1f}%)")
    
    if ids_unicos != len(vagas):
        print("⚠️  ATENÇÃO: Existem IDs duplicados!")
        id_counts = Counter(ids)
        duplicated_ids = [id_val for id_val, count in id_counts.items() if count > 1]
        print(f"IDs duplicados: {duplicated_ids}")
    else:
        print("✅ Todos os IDs são únicos")
    
    # Verifica sequência de IDs
    ids_sorted = sorted([id_val for id_val in ids if id_val is not None])
    expected_sequence = list(range(1, len(ids_sorted) + 1))
    
    if ids_sorted == expected_sequence:
        print("✅ IDs estão em sequência correta (1 a N)")
    else:
        print("⚠️  IDs não estão em sequência correta")
        missing_ids = set(expected_sequence) - set(ids_sorted)
        if missing_ids:
            print(f"IDs faltando: {sorted(missing_ids)}")
    
    return {
        'total_vagas': len(vagas),
        'setores': dict(setores),
        'empresas': dict(empresas.most_common(10)),
        'cidades': dict(cidades.most_common(10)),
        'qualidade': {
            'sem_descricao': vagas_sem_descricao,
            'sem_empresa': vagas_sem_empresa,
            'sem_setor': vagas_sem_setor,
            'sem_cidade': vagas_sem_cidade
        },
        'ids_unicos': ids_unicos == len(vagas)
    }

def compare_files(original_file, cleaned_file):
    """Compara arquivo original com o limpo"""
    print(f"\n=== COMPARAÇÃO ENTRE ARQUIVOS ===")
    
    # Carrega dados originais
    with open(original_file, 'r', encoding='utf-8') as f:
        original_vagas = [json.loads(line) for line in f if line.strip()]
    
    # Carrega dados limpos
    with open(cleaned_file, 'r', encoding='utf-8') as f:
        cleaned_vagas = [json.loads(line) for line in f if line.strip()]
    
    print(f"Arquivo original: {len(original_vagas)} vagas")
    print(f"Arquivo limpo: {len(cleaned_vagas)} vagas")
    print(f"Redução: {len(original_vagas) - len(cleaned_vagas)} vagas ({((len(original_vagas) - len(cleaned_vagas))/len(original_vagas)*100):.1f}%)")
    
    # Compara distribuição por setor
    original_setores = Counter(vaga.get('informacoes_basicas', {}).get('setor', '') for vaga in original_vagas)
    cleaned_setores = Counter(vaga.get('informacoes_basicas', {}).get('setor', '') for vaga in cleaned_vagas)
    
    print(f"\n=== MUDANÇAS POR SETOR ===")
    for setor in set(list(original_setores.keys()) + list(cleaned_setores.keys())):
        original_count = original_setores.get(setor, 0)
        cleaned_count = cleaned_setores.get(setor, 0)
        diff = original_count - cleaned_count
        if diff > 0:
            print(f"{setor}: {original_count} → {cleaned_count} (-{diff})")
        elif diff < 0:
            print(f"{setor}: {original_count} → {cleaned_count} (+{abs(diff)})")
        else:
            print(f"{setor}: {original_count} → {cleaned_count} (sem mudança)")

def main():
    original_file = 'vagas_todos_setores_estruturadas_corrigidas_completo.jsonl'
    cleaned_file = 'vagas_todos_setores_sem_duplicatas.jsonl'
    
    # Analisa arquivo limpo
    quality_report = analyze_data_quality(cleaned_file)
    
    # Compara com original
    compare_files(original_file, cleaned_file)
    
    # Salva relatório
    report_file = 'relatorio_qualidade_dados_limpos.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Relatório de qualidade salvo em: {report_file}")

if __name__ == "__main__":
    main()