import json
from collections import Counter
from typing import Dict, List

def analyze_companies_and_descriptions(file_path: str):
    """Analisa padrões de empresas e descrições nos dados originais"""
    companies = []
    descriptions = []
    sectors = []
    
    print("Analisando padrões nos dados originais...")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            if line_num > 50:  # Analisar apenas as primeiras 50 vagas para exemplo
                break
                
            try:
                job_data = json.loads(line.strip())
                
                # Extrair empresa principal
                empresa = job_data.get('informacoes_basicas', {}).get('empresa_principal', '')
                companies.append(empresa)
                
                # Extrair setor
                setor = job_data.get('informacoes_basicas', {}).get('setor', '')
                sectors.append(setor)
                
                # Extrair descrição completa
                desc_completa = job_data.get('descricao_completa', {}).get('texto_completo', '')
                descriptions.append(desc_completa[:200])  # Primeiros 200 caracteres
                
                # Mostrar exemplo detalhado das primeiras 5 vagas
                if line_num <= 5:
                    print(f"\n=== VAGA {line_num} ===")
                    print(f"ID: {job_data.get('id')}")
                    print(f"Empresa: {empresa}")
                    print(f"Setor: {setor}")
                    print(f"Título/Fonte: {job_data.get('informacoes_basicas', {}).get('fonte', '')}")
                    print(f"Descrição (primeiros 150 chars): {desc_completa[:150]}...")
                    
                    # Verificar segmentos separados
                    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
                    print(f"Número de segmentos: {len(segmentos)}")
                    if segmentos:
                        print(f"Primeiro segmento: {segmentos[0][:100]}...")
                        
            except json.JSONDecodeError as e:
                print(f"Erro na linha {line_num}: {e}")
                continue
    
    # Análise estatística
    print("\n=== ANÁLISE ESTATÍSTICA ===")
    
    # Empresas mais comuns
    company_counts = Counter(companies)
    print(f"\nEmpresas mais comuns (top 10):")
    for company, count in company_counts.most_common(10):
        print(f"  {company}: {count} vagas")
    
    # Setores mais comuns
    sector_counts = Counter(sectors)
    print(f"\nSetores mais comuns:")
    for sector, count in sector_counts.most_common():
        print(f"  {sector}: {count} vagas")
    
    # Verificar se descrições são idênticas
    desc_counts = Counter(descriptions)
    print(f"\nDescrições únicas vs repetidas:")
    print(f"  Total de descrições analisadas: {len(descriptions)}")
    print(f"  Descrições únicas: {len(desc_counts)}")
    print(f"  Descrições repetidas: {len(descriptions) - len(desc_counts)}")
    
    if len(desc_counts) < len(descriptions):
        print(f"\nDescrições mais repetidas:")
        for desc, count in desc_counts.most_common(5):
            if count > 1:
                print(f"  Repetida {count} vezes: {desc[:100]}...")

def analyze_different_sectors(file_path: str):
    """Analisa vagas de diferentes setores para comparar padrões"""
    print("\n=== ANÁLISE POR SETORES ===")
    
    sectors_data = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            try:
                job_data = json.loads(line.strip())
                setor = job_data.get('informacoes_basicas', {}).get('setor', '')
                
                if setor not in sectors_data:
                    sectors_data[setor] = {
                        'empresas': [],
                        'titulos': [],
                        'descricoes': [],
                        'count': 0
                    }
                
                sectors_data[setor]['count'] += 1
                sectors_data[setor]['empresas'].append(
                    job_data.get('informacoes_basicas', {}).get('empresa_principal', '')
                )
                sectors_data[setor]['titulos'].append(
                    job_data.get('informacoes_basicas', {}).get('fonte', '')
                )
                sectors_data[setor]['descricoes'].append(
                    job_data.get('descricao_completa', {}).get('texto_completo', '')[:200]
                )
                
            except json.JSONDecodeError:
                continue
    
    # Analisar cada setor
    for setor, data in sectors_data.items():
        if data['count'] >= 5:  # Apenas setores com pelo menos 5 vagas
            print(f"\n--- SETOR: {setor} ({data['count']} vagas) ---")
            
            # Empresas únicas no setor
            unique_companies = set(data['empresas'])
            print(f"Empresas únicas: {len(unique_companies)}")
            if len(unique_companies) <= 3:
                print(f"Empresas: {list(unique_companies)}")
            
            # Títulos únicos no setor
            unique_titles = set(data['titulos'])
            print(f"Títulos únicos: {len(unique_titles)}")
            
            # Descrições únicas no setor
            unique_descriptions = set(data['descricoes'])
            print(f"Descrições únicas: {len(unique_descriptions)}")
            
            # Verificar se há padronização excessiva
            if len(unique_companies) == 1:
                print(f"⚠️  ALERTA: Todas as vagas têm a mesma empresa!")
            if len(unique_descriptions) == 1:
                print(f"⚠️  ALERTA: Todas as vagas têm a mesma descrição!")

def main():
    file_path = "vagas_todos_setores_estruturadas_completo.jsonl"
    
    print("=== ANÁLISE DE PADRÕES NOS DADOS ===\n")
    
    try:
        analyze_companies_and_descriptions(file_path)
        analyze_different_sectors(file_path)
        
        print("\n=== CONCLUSÃO ===")
        print("Análise concluída. Verifique os padrões identificados acima.")
        print("Se houver padronização excessiva, o problema está nos dados originais.")
        
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado!")
    except Exception as e:
        print(f"Erro durante análise: {e}")

if __name__ == "__main__":
    main()