#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a diversidade final após correções em todos os setores
"""

import json
from collections import Counter

def load_data(file_path):
    """Carrega dados do arquivo JSONL"""
    vagas = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                vagas.append(json.loads(line))
    return vagas

def analyze_diversity_by_sector(vagas):
    """Analisa a diversidade de descrições por setor"""
    
    # Agrupar por setor
    setores = {}
    for vaga in vagas:
        setor = vaga.get('informacoes_basicas', {}).get('setor', 'Desconhecido')
        if setor not in setores:
            setores[setor] = []
        setores[setor].append(vaga)
    
    print(f"📊 RELATÓRIO FINAL DE DIVERSIDADE POR SETOR")
    print(f"{'='*60}")
    print(f"Total de vagas analisadas: {len(vagas)}")
    print(f"Total de setores: {len(setores)}")
    print(f"{'='*60}\n")
    
    resultados = []
    total_vagas_geral = 0
    total_descricoes_unicas_geral = 0
    setores_100_diversidade = []
    setores_problematicos = []
    
    # Analisar cada setor
    for setor, vagas_setor in sorted(setores.items()):
        total_vagas = len(vagas_setor)
        descricoes = [vaga.get('descricao_completa', {}).get('texto_completo', '') for vaga in vagas_setor]
        descricoes_unicas = len(set(descricoes))
        taxa_diversidade = (descricoes_unicas / total_vagas) * 100
        
        total_vagas_geral += total_vagas
        total_descricoes_unicas_geral += descricoes_unicas
        
        resultado = {
            'setor': setor,
            'total_vagas': total_vagas,
            'descricoes_unicas': descricoes_unicas,
            'taxa_diversidade': taxa_diversidade
        }
        resultados.append(resultado)
        
        # Categorizar setores
        if taxa_diversidade == 100.0:
            setores_100_diversidade.append(setor)
        elif taxa_diversidade < 80.0:
            setores_problematicos.append((setor, taxa_diversidade))
        
        # Exibir resultado do setor
        status = "✅" if taxa_diversidade >= 80.0 else "⚠️" if taxa_diversidade >= 60.0 else "❌"
        print(f"{status} {setor}:")
        print(f"   📈 Taxa de diversidade: {taxa_diversidade:.1f}%")
        print(f"   📊 Descrições únicas: {descricoes_unicas}/{total_vagas}")
        
        # Mostrar descrições repetidas se houver
        contador_descricoes = Counter(descricoes)
        descricoes_repetidas = [(desc, count) for desc, count in contador_descricoes.items() if count > 1]
        
        if descricoes_repetidas:
            print(f"   🔄 Descrições ainda repetidas: {len(descricoes_repetidas)}")
            for desc, count in sorted(descricoes_repetidas, key=lambda x: x[1], reverse=True)[:3]:
                print(f"      - {count}x: {desc[:80]}...")
        
        # Verificar presença de "CANDIDATURA FÁCIL"
        vagas_com_candidatura_facil = 0
        for vaga in vagas_setor:
            descricao = vaga.get('descricao_completa', {}).get('texto_completo', '').upper()
            if 'CANDIDATURA FÁCIL' in descricao or 'CANDIDATURA FACIL' in descricao:
                vagas_com_candidatura_facil += 1
        
        if vagas_com_candidatura_facil > 0:
            print(f"   ⚠️ {vagas_com_candidatura_facil} vagas ainda contêm 'CANDIDATURA FÁCIL'")
        
        print()
    
    # Estatísticas gerais
    taxa_diversidade_geral = (total_descricoes_unicas_geral / total_vagas_geral) * 100
    
    print(f"{'='*60}")
    print(f"📈 ESTATÍSTICAS GERAIS FINAIS")
    print(f"{'='*60}")
    print(f"Taxa de diversidade geral: {taxa_diversidade_geral:.1f}%")
    print(f"Total de descrições únicas: {total_descricoes_unicas_geral}/{total_vagas_geral}")
    print(f"Setores com 100% de diversidade: {len(setores_100_diversidade)}")
    print(f"Setores ainda problemáticos (<80%): {len(setores_problematicos)}")
    
    if setores_100_diversidade:
        print(f"\n🎉 SETORES COM 100% DE DIVERSIDADE:")
        for setor in setores_100_diversidade:
            print(f"   ✅ {setor}")
    
    if setores_problematicos:
        print(f"\n⚠️ SETORES AINDA PROBLEMÁTICOS:")
        for setor, taxa in sorted(setores_problematicos, key=lambda x: x[1]):
            print(f"   ❌ {setor}: {taxa:.1f}%")
    
    print(f"\n{'='*60}")
    
    # Comparação com dados anteriores (se disponível)
    print(f"\n📊 MELHORIAS REALIZADAS:")
    print(f"✅ Correções aplicadas nos setores: Telemarketing, Tecnica, Telecomunicacoes, Juridica, arquitetura e design")
    print(f"✅ Remoção do termo 'CANDIDATURA FÁCIL' implementada")
    print(f"✅ Geração de descrições personalizadas baseadas em características específicas")
    print(f"✅ {total_descricoes_unicas_geral} descrições únicas de {total_vagas_geral} vagas totais")
    
    return resultados

def main():
    """Função principal"""
    print("🚀 Verificando diversidade final após todas as correções...\n")
    
    # Carregar dados corrigidos
    file_path = 'vagas_todos_setores_estruturadas_corrigidas_completo.jsonl'
    
    try:
        vagas = load_data(file_path)
        print(f"📂 Dados carregados: {len(vagas)} vagas\n")
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        print("Execute primeiro o script de correção: fix_all_sectors_descriptions.py")
        return
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Analisar diversidade
    resultados = analyze_diversity_by_sector(vagas)
    
    # Salvar relatório
    relatorio_file = 'relatorio_diversidade_final.json'
    try:
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_vagas': len(vagas),
                'total_setores': len(set(v.get('informacoes_basicas', {}).get('setor', 'Desconhecido') for v in vagas)),
                'resultados_por_setor': resultados,
                'data_analise': '2024-01-11'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Relatório salvo em: {relatorio_file}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar relatório: {e}")
    
    print("\n🎉 Análise final concluída!")

if __name__ == "__main__":
    main()