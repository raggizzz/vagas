import json
import os
from collections import defaultdict, Counter
from dotenv import load_dotenv

def load_jobs_data():
    """Carrega os dados das vagas do arquivo JSONL"""
    jobs = []
    with open('vagas_todos_setores_estruturadas_completo.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                jobs.append(json.loads(line))
    return jobs

def analyze_description_diversity_by_sector(jobs):
    """Analisa a diversidade das descrições por setor"""
    sector_data = defaultdict(list)
    
    # Agrupa vagas por setor
    for job in jobs:
        sector = job.get('informacoes_basicas', {}).get('setor', 'Não informado')
        description = job.get('descricao_completa', {}).get('texto_completo', '')
        
        sector_data[sector].append({
            'id': job.get('id'),
            'titulo': job.get('informacoes_basicas', {}).get('fonte', ''),
            'empresa': job.get('informacoes_basicas', {}).get('empresa_principal', ''),
            'description': description
        })
    
    print(f"\n=== ANÁLISE DE DIVERSIDADE DE DESCRIÇÕES POR SETOR ===")
    print(f"Total de vagas analisadas: {len(jobs)}")
    print(f"Total de setores: {len(sector_data)}")
    print("\n" + "="*80)
    
    problematic_sectors = []
    
    for sector, jobs_in_sector in sorted(sector_data.items()):
        total_jobs = len(jobs_in_sector)
        
        # Conta descrições únicas
        descriptions = [job['description'] for job in jobs_in_sector]
        unique_descriptions = set(descriptions)
        unique_count = len(unique_descriptions)
        
        # Calcula taxa de diversidade
        diversity_rate = (unique_count / total_jobs) * 100 if total_jobs > 0 else 0
        
        print(f"\nSETOR: {sector}")
        print(f"  Total de vagas: {total_jobs}")
        print(f"  Descrições únicas: {unique_count}")
        print(f"  Taxa de diversidade: {diversity_rate:.1f}%")
        
        # Identifica descrições repetidas
        description_counts = Counter(descriptions)
        repeated_descriptions = {desc: count for desc, count in description_counts.items() if count > 1}
        
        if repeated_descriptions:
            print(f"  ⚠️  DESCRIÇÕES REPETIDAS:")
            for desc, count in sorted(repeated_descriptions.items(), key=lambda x: x[1], reverse=True):
                # Mostra apenas os primeiros 100 caracteres da descrição
                short_desc = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"    - {count}x: {short_desc}")
                
                # Mostra quais vagas têm essa descrição repetida
                repeated_jobs = [job for job in jobs_in_sector if job['description'] == desc]
                print(f"      Vagas com essa descrição:")
                for job in repeated_jobs[:5]:  # Mostra apenas as primeiras 5
                    print(f"        ID {job['id']}: {job['titulo']} - {job['empresa']}")
                if len(repeated_jobs) > 5:
                    print(f"        ... e mais {len(repeated_jobs) - 5} vagas")
                print()
        
        # Marca setores problemáticos (baixa diversidade)
        if diversity_rate < 50 and total_jobs > 2:
            problematic_sectors.append({
                'sector': sector,
                'total_jobs': total_jobs,
                'unique_descriptions': unique_count,
                'diversity_rate': diversity_rate,
                'repeated_count': len(repeated_descriptions)
            })
    
    # Resumo dos setores problemáticos
    if problematic_sectors:
        print("\n" + "="*80)
        print("🚨 SETORES COM BAIXA DIVERSIDADE (< 50%):")
        print("="*80)
        
        for sector_info in sorted(problematic_sectors, key=lambda x: x['diversity_rate']):
            print(f"\n{sector_info['sector']}:")
            print(f"  - {sector_info['total_jobs']} vagas, {sector_info['unique_descriptions']} descrições únicas")
            print(f"  - Taxa de diversidade: {sector_info['diversity_rate']:.1f}%")
            print(f"  - {sector_info['repeated_count']} descrições repetidas")
    
    # Estatísticas gerais
    total_descriptions = sum(len([job['description'] for job in jobs_list]) for jobs_list in sector_data.values())
    all_descriptions = [job['description'] for jobs_list in sector_data.values() for job in jobs_list]
    total_unique = len(set(all_descriptions))
    overall_diversity = (total_unique / total_descriptions) * 100 if total_descriptions > 0 else 0
    
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS GERAIS:")
    print("="*80)
    print(f"Total de descrições: {total_descriptions}")
    print(f"Descrições únicas globais: {total_unique}")
    print(f"Taxa de diversidade geral: {overall_diversity:.1f}%")
    print(f"Setores problemáticos: {len(problematic_sectors)} de {len(sector_data)}")

def main():
    load_dotenv()
    
    print("Carregando dados das vagas...")
    jobs = load_jobs_data()
    
    print("Analisando diversidade de descrições por setor...")
    analyze_description_diversity_by_sector(jobs)

if __name__ == "__main__":
    main()