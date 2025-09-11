import json
from collections import Counter

def analyze_servico_social_sector():
    """Analisa especificamente o setor ServicoSocial"""
    jobs = []
    
    # Carrega os dados
    with open('vagas_todos_setores_estruturadas_completo.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                job = json.loads(line)
                sector = job.get('informacoes_basicas', {}).get('setor', '')
                if sector == 'ServicoSocial':
                    jobs.append(job)
    
    print(f"=== ANÁLISE DETALHADA DO SETOR 'ServicoSocial' ===")
    print(f"Total de vagas encontradas: {len(jobs)}")
    print("\n" + "="*80)
    
    # Analisa as descrições
    descriptions = []
    for job in jobs:
        desc = job.get('descricao_completa', {}).get('texto_completo', '')
        descriptions.append(desc)
    
    # Conta descrições únicas
    description_counts = Counter(descriptions)
    unique_descriptions = len(set(descriptions))
    
    print(f"\nDESCRIÇÕES:")
    print(f"Total de descrições: {len(descriptions)}")
    print(f"Descrições únicas: {unique_descriptions}")
    print(f"Taxa de diversidade: {(unique_descriptions/len(descriptions)*100):.1f}%")
    
    print(f"\n=== DETALHES DE CADA VAGA ===")
    for i, job in enumerate(jobs, 1):
        print(f"\nVAGA {i} (ID: {job.get('id')})")
        print(f"Título: {job.get('informacoes_basicas', {}).get('fonte', 'N/A')}")
        print(f"Empresa: {job.get('informacoes_basicas', {}).get('empresa_principal', 'N/A')}")
        print(f"Cidade: {job.get('localizacao', {}).get('cidade_extraida', 'N/A')}")
        print(f"Estado: {job.get('localizacao', {}).get('estado_extraido', 'N/A')}")
        
        # Mostra os primeiros 200 caracteres da descrição
        desc = job.get('descricao_completa', {}).get('texto_completo', '')
        short_desc = desc[:200] + "..." if len(desc) > 200 else desc
        print(f"Descrição (primeiros 200 chars): {short_desc}")
        print("-" * 60)
    
    # Mostra as descrições repetidas
    print(f"\n=== ANÁLISE DE DUPLICAÇÃO ===")
    repeated_descriptions = {desc: count for desc, count in description_counts.items() if count > 1}
    
    if repeated_descriptions:
        for desc, count in repeated_descriptions.items():
            print(f"\nDescrição repetida {count} vezes:")
            print(f"Primeiros 300 caracteres: {desc[:300]}...")
            
            # Mostra quais vagas têm essa descrição
            matching_jobs = [job for job in jobs if job.get('descricao_completa', {}).get('texto_completo', '') == desc]
            print(f"\nVagas com essa descrição:")
            for job in matching_jobs:
                print(f"  - ID {job.get('id')}: {job.get('informacoes_basicas', {}).get('fonte', 'N/A')} - {job.get('informacoes_basicas', {}).get('empresa_principal', 'N/A')}")
    else:
        print("Nenhuma descrição repetida encontrada.")
    
    # Analisa outros campos para ver se há padrões
    print(f"\n=== ANÁLISE DE OUTROS CAMPOS ===")
    
    # Empresas
    empresas = [job.get('informacoes_basicas', {}).get('empresa_principal', '') for job in jobs]
    empresa_counts = Counter(empresas)
    print(f"\nEmpresas mais frequentes:")
    for empresa, count in empresa_counts.most_common(5):
        print(f"  - {empresa}: {count} vagas")
    
    # Títulos
    titulos = [job.get('informacoes_basicas', {}).get('fonte', '') for job in jobs]
    titulo_counts = Counter(titulos)
    print(f"\nTítulos mais frequentes:")
    for titulo, count in titulo_counts.most_common(5):
        print(f"  - {titulo}: {count} vagas")
    
    # Responsabilidades
    all_responsabilidades = []
    for job in jobs:
        responsabilidades = job.get('responsabilidades', {}).get('lista_responsabilidades', [])
        all_responsabilidades.extend(responsabilidades)
    
    resp_counts = Counter(all_responsabilidades)
    print(f"\nResponsabilidades mais frequentes:")
    for resp, count in resp_counts.most_common(5):
        short_resp = resp[:100] + "..." if len(resp) > 100 else resp
        print(f"  - {count}x: {short_resp}")

if __name__ == "__main__":
    analyze_servico_social_sector()