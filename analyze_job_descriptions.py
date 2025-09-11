import json
import re
from collections import defaultdict, Counter

def analyze_job_descriptions():
    """
    Analisa todas as descrições de vagas de 1 a 271 do arquivo vagas_todos_setores_sem_duplicatas.jsonl
    """
    
    # Contadores e estruturas para análise
    analysis_results = {
        'total_vagas_analisadas': 0,
        'problemas_identificados': {
            'descricoes_concatenadas': 0,
            'informacoes_misturadas': 0,
            'dados_corrompidos': 0,
            'empresas_incorretas': 0,
            'localizacoes_incorretas': 0,
            'responsabilidades_duplicadas': 0,
            'habilidades_genericas': 0
        },
        'setores_analisados': defaultdict(int),
        'empresas_problematicas': defaultdict(int),
        'exemplos_problemas': [],
        'estatisticas_por_setor': defaultdict(lambda: {
            'total_vagas': 0,
            'problemas_encontrados': 0,
            'empresas_unicas': set(),
            'responsabilidades_unicas': set(),
            'habilidades_unicas': set()
        })
    }
    
    try:
        with open('vagas_todos_setores_sem_duplicatas.jsonl', 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if line_num > 271:  # Analisar apenas até a vaga 271
                    break
                    
                try:
                    vaga = json.loads(line.strip())
                    vaga_id = vaga.get('id', line_num)
                    
                    analysis_results['total_vagas_analisadas'] += 1
                    
                    # Análise por setor
                    setor = vaga.get('informacoes_basicas', {}).get('setor', 'Desconhecido')
                    analysis_results['setores_analisados'][setor] += 1
                    analysis_results['estatisticas_por_setor'][setor]['total_vagas'] += 1
                    
                    problemas_vaga = []
                    
                    # 1. Verificar descrições concatenadas/misturadas
                    descricao_completa = vaga.get('descricao_completa', {}).get('texto_completo', '')
                    if '|' in descricao_completa and len(descricao_completa.split('|')) > 5:
                        analysis_results['problemas_identificados']['descricoes_concatenadas'] += 1
                        problemas_vaga.append('Descrição concatenada com múltiplas vagas')
                    
                    # 2. Verificar informações básicas corrompidas
                    info_basicas = vaga.get('informacoes_basicas', {})
                    empresa_principal = info_basicas.get('empresa_principal', '')
                    titulo = info_basicas.get('titulo', '')
                    
                    # Empresa no título ou título na empresa
                    if 'http' in empresa_principal or len(empresa_principal) > 100:
                        analysis_results['problemas_identificados']['empresas_incorretas'] += 1
                        analysis_results['empresas_problematicas'][empresa_principal] += 1
                        problemas_vaga.append('Empresa principal corrompida')
                    
                    if 'http' in titulo or 'catho.com.br' in titulo:
                        analysis_results['problemas_identificados']['dados_corrompidos'] += 1
                        problemas_vaga.append('Título contém URL')
                    
                    # 3. Verificar localização corrompida
                    localizacao = vaga.get('localizacao', {})
                    cidade = localizacao.get('cidade_extraida', '') or ''
                    estado = localizacao.get('estado_extraido', '') or ''
                    
                    if len(cidade) > 50 or any(palavra in cidade.lower() for palavra in ['acompanhar', 'realizar', 'desenvolver']):
                        analysis_results['problemas_identificados']['localizacoes_incorretas'] += 1
                        problemas_vaga.append('Cidade corrompida com texto de responsabilidade')
                    
                    if len(estado) > 5 or any(char.isdigit() for char in estado):
                        analysis_results['problemas_identificados']['localizacoes_incorretas'] += 1
                        problemas_vaga.append('Estado corrompido')
                    
                    # 4. Verificar responsabilidades duplicadas/genéricas
                    responsabilidades = vaga.get('responsabilidades', {}).get('lista_responsabilidades', [])
                    if responsabilidades:
                        # Verificar se há responsabilidades muito longas (concatenadas)
                        for resp in responsabilidades:
                            if len(resp) > 500:
                                analysis_results['problemas_identificados']['responsabilidades_duplicadas'] += 1
                                problemas_vaga.append('Responsabilidade muito longa/concatenada')
                                break
                        
                        # Adicionar responsabilidades únicas por setor
                        for resp in responsabilidades:
                            if len(resp) < 500:  # Apenas responsabilidades normais
                                analysis_results['estatisticas_por_setor'][setor]['responsabilidades_unicas'].add(resp)
                    
                    # 5. Verificar habilidades genéricas
                    habilidades = vaga.get('habilidades_e_competencias', {}).get('habilidades_tecnicas', [])
                    habilidades_genericas = ['Excel', 'Word', 'PowerPoint', 'Comunicação', 'Trabalho em equipe']
                    if all(hab in habilidades_genericas for hab in habilidades[:3]):
                        analysis_results['problemas_identificados']['habilidades_genericas'] += 1
                        problemas_vaga.append('Habilidades muito genéricas')
                    
                    # Adicionar habilidades únicas por setor
                    for hab in habilidades:
                        analysis_results['estatisticas_por_setor'][setor]['habilidades_unicas'].add(hab)
                    
                    # Adicionar empresa única por setor
                    if empresa_principal and len(empresa_principal) < 100:
                        analysis_results['estatisticas_por_setor'][setor]['empresas_unicas'].add(empresa_principal)
                    
                    # Contar problemas por setor
                    if problemas_vaga:
                        analysis_results['estatisticas_por_setor'][setor]['problemas_encontrados'] += 1
                    
                    # Salvar exemplos de problemas
                    if problemas_vaga and len(analysis_results['exemplos_problemas']) < 20:
                        analysis_results['exemplos_problemas'].append({
                            'vaga_id': vaga_id,
                            'setor': setor,
                            'problemas': problemas_vaga,
                            'empresa': empresa_principal[:50] + '...' if len(empresa_principal) > 50 else empresa_principal,
                            'titulo': titulo[:50] + '...' if len(titulo) > 50 else titulo
                        })
                    
                except json.JSONDecodeError as e:
                    print(f"Erro ao processar linha {line_num}: {e}")
                    continue
    
    except FileNotFoundError:
        print("Arquivo vagas_todos_setores_sem_duplicatas.jsonl não encontrado!")
        return
    
    # Converter sets para listas para serialização JSON
    for setor_stats in analysis_results['estatisticas_por_setor'].values():
        setor_stats['empresas_unicas'] = list(setor_stats['empresas_unicas'])
        setor_stats['responsabilidades_unicas'] = list(setor_stats['responsabilidades_unicas'])
        setor_stats['habilidades_unicas'] = list(setor_stats['habilidades_unicas'])
        setor_stats['total_empresas_unicas'] = len(setor_stats['empresas_unicas'])
        setor_stats['total_responsabilidades_unicas'] = len(setor_stats['responsabilidades_unicas'])
        setor_stats['total_habilidades_unicas'] = len(setor_stats['habilidades_unicas'])
    
    # Salvar relatório detalhado
    with open('relatorio_analise_descricoes.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    # Imprimir resumo
    print("\n=== ANÁLISE DAS DESCRIÇÕES DE VAGAS (1-271) ===")
    print(f"Total de vagas analisadas: {analysis_results['total_vagas_analisadas']}")
    print("\n=== PROBLEMAS IDENTIFICADOS ===")
    for problema, count in analysis_results['problemas_identificados'].items():
        print(f"{problema.replace('_', ' ').title()}: {count}")
    
    print("\n=== ESTATÍSTICAS POR SETOR ===")
    for setor, stats in analysis_results['estatisticas_por_setor'].items():
        print(f"\n{setor}:")
        print(f"  - Total de vagas: {stats['total_vagas']}")
        print(f"  - Vagas com problemas: {stats['problemas_encontrados']}")
        print(f"  - Empresas únicas: {stats['total_empresas_unicas']}")
        print(f"  - Responsabilidades únicas: {stats['total_responsabilidades_unicas']}")
        print(f"  - Habilidades únicas: {stats['total_habilidades_unicas']}")
    
    print("\n=== EXEMPLOS DE PROBLEMAS ===")
    for i, exemplo in enumerate(analysis_results['exemplos_problemas'][:10], 1):
        print(f"\n{i}. Vaga ID {exemplo['vaga_id']} ({exemplo['setor']})")
        print(f"   Empresa: {exemplo['empresa']}")
        print(f"   Título: {exemplo['titulo']}")
        print(f"   Problemas: {', '.join(exemplo['problemas'])}")
    
    print(f"\nRelatório completo salvo em: relatorio_analise_descricoes.json")

if __name__ == "__main__":
    analyze_job_descriptions()