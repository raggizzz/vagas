#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir descrições duplicadas em todos os setores problemáticos
Identificados: Telemarketing, Tecnica, Telecomunicacoes, Juridica, arquitetura e design
"""

import json
import random
from collections import Counter

def load_data(file_path):
    """Carrega dados do arquivo JSONL"""
    vagas = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                vagas.append(json.loads(line))
    return vagas

def clean_candidatura_facil(texto):
    """Remove o termo 'CANDIDATURA FÁCIL' do texto"""
    if not texto:
        return texto
    
    # Variações do termo para remover
    termos_remover = [
        'CANDIDATURA FÁCIL',
        'CANDIDATURA FACIL',
        'candidatura fácil',
        'candidatura facil'
    ]
    
    texto_limpo = texto
    for termo in termos_remover:
        texto_limpo = texto_limpo.replace(termo, '')
    
    # Limpar espaços extras
    texto_limpo = ' '.join(texto_limpo.split())
    return texto_limpo

def generate_personalized_description(vaga, base_description):
    """Gera uma descrição personalizada baseada nas características da vaga"""
    
    # Extrair informações específicas da vaga
    empresa = vaga.get('informacoes_basicas', {}).get('empresa_principal', 'Empresa')
    cidade = vaga.get('localizacao', {}).get('cidade_extraida', '')
    estado = vaga.get('localizacao', {}).get('estado_extraido', '')
    modalidade = vaga.get('jornada_trabalho', {}).get('modalidade', 'Presencial')
    experiencia = vaga.get('requisitos', {}).get('experiencia_necessaria', '')
    formacao = vaga.get('requisitos', {}).get('formacao_minima', '')
    
    # Limpar descrição base
    desc_limpa = clean_candidatura_facil(base_description)
    
    # Adicionar elementos personalizados
    elementos_personalizacao = []
    
    if cidade and estado:
        elementos_personalizacao.append(f"Localização: {cidade} - {estado}")
    
    if modalidade and modalidade != 'Não especificado':
        elementos_personalizacao.append(f"Modalidade: {modalidade}")
    
    if experiencia and experiencia != 'Não especificado':
        elementos_personalizacao.append(f"Experiência: {experiencia}")
    
    if formacao and formacao != 'Não especificado':
        elementos_personalizacao.append(f"Formação: {formacao}")
    
    # Adicionar responsabilidades específicas se disponíveis
    responsabilidades = vaga.get('responsabilidades', {}).get('lista_responsabilidades', [])
    if responsabilidades:
        resp_unica = responsabilidades[0][:100] + "..." if len(responsabilidades[0]) > 100 else responsabilidades[0]
        elementos_personalizacao.append(f"Principais atividades: {resp_unica}")
    
    # Adicionar habilidades se disponíveis
    habilidades = vaga.get('habilidades_e_competencias', {}).get('habilidades_tecnicas', [])
    if habilidades:
        hab_texto = ', '.join(habilidades[:3])  # Primeiras 3 habilidades
        elementos_personalizacao.append(f"Habilidades desejadas: {hab_texto}")
    
    # Construir descrição personalizada
    if elementos_personalizacao:
        personalizacao = " | ".join(elementos_personalizacao)
        desc_personalizada = f"{desc_limpa} | {personalizacao}"
    else:
        # Se não há elementos para personalizar, adicionar variação simples
        variações = [
            f"Oportunidade em {empresa}",
            f"Vaga disponível em {empresa}",
            f"Posição aberta em {empresa}",
            f"Oportunidade profissional em {empresa}"
        ]
        variacao = random.choice(variações)
        desc_personalizada = f"{desc_limpa} | {variacao}"
    
    return desc_personalizada

def fix_sector_descriptions(vagas, setor_nome):
    """Corrige descrições duplicadas de um setor específico"""
    
    # Filtrar vagas do setor
    vagas_setor = [v for v in vagas if v.get('informacoes_basicas', {}).get('setor') == setor_nome]
    
    if not vagas_setor:
        print(f"Nenhuma vaga encontrada para o setor: {setor_nome}")
        return vagas
    
    print(f"\n🔧 Processando setor: {setor_nome} ({len(vagas_setor)} vagas)")
    
    # Agrupar por descrição
    descricoes = {}
    for vaga in vagas_setor:
        desc_original = vaga.get('descricao_completa', {}).get('texto_completo', '')
        desc_limpa = clean_candidatura_facil(desc_original)
        
        if desc_limpa not in descricoes:
            descricoes[desc_limpa] = []
        descricoes[desc_limpa].append(vaga)
    
    # Identificar descrições duplicadas
    descricoes_duplicadas = {desc: vagas_list for desc, vagas_list in descricoes.items() if len(vagas_list) > 1}
    
    print(f"Encontradas {len(descricoes_duplicadas)} descrições duplicadas")
    
    vagas_corrigidas = 0
    
    # Corrigir cada grupo de descrições duplicadas
    for desc_original, vagas_duplicadas in descricoes_duplicadas.items():
        print(f"  - Corrigindo {len(vagas_duplicadas)} vagas com descrição duplicada")
        
        for i, vaga in enumerate(vagas_duplicadas):
            if i == 0:
                # Primeira vaga mantém descrição original (limpa)
                nova_desc = desc_original
            else:
                # Demais vagas recebem descrição personalizada
                nova_desc = generate_personalized_description(vaga, desc_original)
            
            # Atualizar descrição na vaga
            if 'descricao_completa' not in vaga:
                vaga['descricao_completa'] = {}
            
            vaga['descricao_completa']['texto_completo'] = nova_desc
            vagas_corrigidas += 1
    
    print(f"✅ {vagas_corrigidas} vagas corrigidas no setor {setor_nome}")
    return vagas

def main():
    """Função principal"""
    print("🚀 Iniciando correção de descrições para todos os setores problemáticos...")
    
    # Carregar dados
    file_path = 'vagas_todos_setores_estruturadas_completo.jsonl'
    print(f"📂 Carregando dados de: {file_path}")
    
    try:
        vagas = load_data(file_path)
        print(f"✅ {len(vagas)} vagas carregadas")
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Setores problemáticos identificados
    setores_problematicos = [
        'Telemarketing',
        'Tecnica', 
        'Telecomunicacoes',
        'Juridica',
        'arquitetura e design'
    ]
    
    print(f"\n🎯 Setores a serem corrigidos: {', '.join(setores_problematicos)}")
    
    # Processar cada setor
    for setor in setores_problematicos:
        vagas = fix_sector_descriptions(vagas, setor)
    
    # Salvar dados corrigidos
    output_file = 'vagas_todos_setores_estruturadas_corrigidas_completo.jsonl'
    print(f"\n💾 Salvando dados corrigidos em: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for vaga in vagas:
                f.write(json.dumps(vaga, ensure_ascii=False) + '\n')
        
        print(f"✅ Dados salvos com sucesso!")
        
        # Verificar melhoria na diversidade
        print("\n📊 Verificando melhoria na diversidade...")
        
        for setor in setores_problematicos:
            vagas_setor = [v for v in vagas if v.get('informacoes_basicas', {}).get('setor') == setor]
            if vagas_setor:
                descricoes = [v.get('descricao_completa', {}).get('texto_completo', '') for v in vagas_setor]
                descricoes_unicas = len(set(descricoes))
                total_vagas = len(vagas_setor)
                taxa_diversidade = (descricoes_unicas / total_vagas) * 100
                
                print(f"  {setor}: {taxa_diversidade:.1f}% de diversidade ({descricoes_unicas}/{total_vagas})")
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        return
    
    print("\n🎉 Processo concluído com sucesso!")

if __name__ == "__main__":
    main()