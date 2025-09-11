import json
import re
from typing import Dict, Any, Optional

def extract_unique_company(job_data: Dict[str, Any]) -> str:
    """Extrai empresa de forma mais inteligente, evitando nomes genéricos"""
    # Primeiro, tentar extrair da unidade na descrição
    desc_completa = job_data.get('descricao_completa', {}).get('texto_completo', '')
    
    # Procurar por "Unidade:" na descrição
    unidade_match = re.search(r'Unidade:\s*([^-]+?)\s*-', desc_completa)
    if unidade_match:
        unidade = unidade_match.group(1).strip()
        if len(unidade) > 10 and not any(word in unidade.lower() for word in ['empresa', 'confidencial', 'reconhecida']):
            return unidade
    
    # Tentar extrair de segmentos específicos
    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
    for segmento in segmentos:
        if 'empresa:' in segmento.lower() or 'organização:' in segmento.lower():
            # Extrair nome após "Empresa:" ou "Organização:"
            empresa_match = re.search(r'(?:empresa|organização):\s*([^\n]+)', segmento, re.IGNORECASE)
            if empresa_match:
                empresa = empresa_match.group(1).strip()
                if len(empresa) > 5 and not any(word in empresa.lower() for word in ['confidencial', 'reconhecida']):
                    return empresa
    
    # Fallback para empresa_principal, mas limpar nomes genéricos
    empresa_original = job_data.get('informacoes_basicas', {}).get('empresa_principal', '')
    if empresa_original and not any(word in empresa_original.lower() for word in ['empresa reconhecida', 'empresa confidencial', 'empresa de']):
        return empresa_original
    
    return "Empresa não especificada"

def extract_unique_description(job_data: Dict[str, Any]) -> str:
    """Extrai descrição única para cada vaga, evitando textos padronizados"""
    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
    
    # Procurar por segmentos específicos da vaga
    descricao_parts = []
    
    for segmento in segmentos:
        segmento_lower = segmento.lower()
        
        # Pular segmentos genéricos/padronizados
        if any(skip_word in segmento_lower for skip_word in [
            'assessorar a coordenação',
            'sumário:',
            'unidade: hospital central',
            'jornada de trabalho: 150'
        ]):
            continue
            
        # Incluir segmentos específicos
        if any(include_word in segmento_lower for include_word in [
            'responsabilidades:',
            'atividades:',
            'requisitos:',
            'qualificações:',
            'experiência:',
            'formação:',
            'competências:',
            'habilidades:'
        ]):
            descricao_parts.append(segmento.strip())
    
    if descricao_parts:
        return ' '.join(descricao_parts)[:500]  # Limitar tamanho
    
    # Fallback: usar texto completo mas filtrar partes genéricas
    texto_completo = job_data.get('descricao_completa', {}).get('texto_completo', '')
    
    # Remover partes padronizadas
    texto_limpo = re.sub(r'Unidade: Hospital Central.*?Jornada de Trabalho: \d+/hrs mês\s*', '', texto_completo)
    texto_limpo = re.sub(r'Sumário: Assessorar a coordenação.*?(?=\n|$)', '', texto_limpo)
    
    return texto_limpo.strip()[:500] if texto_limpo.strip() else "Descrição não especificada"

def extract_proper_sector(job_data: Dict[str, Any]) -> str:
    """Extrai setor de forma mais precisa"""
    # Primeiro tentar do campo setor
    setor = job_data.get('informacoes_basicas', {}).get('setor', '')
    
    # Se o setor for muito genérico, tentar extrair da descrição
    if setor in ['ServicoSocial', 'Telecomunicacoes'] and len(setor) < 15:
        # Procurar por indicações de setor na descrição
        desc_completa = job_data.get('descricao_completa', {}).get('texto_completo', '')
        titulo = job_data.get('informacoes_basicas', {}).get('fonte', '')
        
        # Mapear títulos para setores mais específicos
        titulo_lower = titulo.lower()
        if any(word in titulo_lower for word in ['enfermeiro', 'médico', 'saúde', 'hospital']):
            return 'Saúde'
        elif any(word in titulo_lower for word in ['assistente social', 'coordenador social']):
            return 'Serviço Social'
        elif any(word in titulo_lower for word in ['vendas', 'comercial', 'vendedor']):
            return 'Comercial e Vendas'
        elif any(word in titulo_lower for word in ['administrativo', 'admin', 'secretário']):
            return 'Administração'
        elif any(word in titulo_lower for word in ['técnico', 'engenheiro', 'tecnologia']):
            return 'Técnica/Engenharia'
    
    return setor if setor else "Setor não especificado"

def process_job_with_unique_data(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Processa uma vaga extraindo dados únicos"""
    return {
        'id': job_data.get('id'),
        'titulo': job_data.get('informacoes_basicas', {}).get('fonte', 'Título não especificado'),
        'empresa': extract_unique_company(job_data),
        'setor': extract_proper_sector(job_data),
        'descricao': extract_unique_description(job_data),
        'localizacao': {
            'cidade': job_data.get('localizacao', {}).get('cidade_extraida', ''),
            'estado': job_data.get('localizacao', {}).get('estado_extraido', '')
        },
        'remuneracao': job_data.get('remuneracao', {}),
        'jornada': job_data.get('jornada_trabalho', {})
    }

def main():
    input_file = "vagas_todos_setores_estruturadas_completo.jsonl"
    output_file = "vagas_dados_unicos.jsonl"
    
    print("Processando vagas com extração de dados únicos...")
    
    processed_count = 0
    unique_companies = set()
    unique_descriptions = set()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                try:
                    job_data = json.loads(line.strip())
                    processed_job = process_job_with_unique_data(job_data)
                    
                    # Rastrear dados únicos
                    unique_companies.add(processed_job['empresa'])
                    unique_descriptions.add(processed_job['descricao'][:100])  # Primeiros 100 chars
                    
                    # Escrever no arquivo de saída
                    outfile.write(json.dumps(processed_job, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                    # Mostrar progresso
                    if processed_count % 100 == 0:
                        print(f"Processadas {processed_count} vagas...")
                    
                    # Mostrar exemplos das primeiras 5 vagas
                    if processed_count <= 5:
                        print(f"\n=== VAGA {processed_count} PROCESSADA ===")
                        print(f"Título: {processed_job['titulo']}")
                        print(f"Empresa: {processed_job['empresa']}")
                        print(f"Setor: {processed_job['setor']}")
                        print(f"Descrição: {processed_job['descricao'][:150]}...")
                        print(f"Localização: {processed_job['localizacao']['cidade']}, {processed_job['localizacao']['estado']}")
                        
                except json.JSONDecodeError as e:
                    print(f"Erro na linha {line_num}: {e}")
                    continue
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de vagas processadas: {processed_count}")
        print(f"Empresas únicas encontradas: {len(unique_companies)}")
        print(f"Descrições únicas encontradas: {len(unique_descriptions)}")
        print(f"Arquivo salvo como: {output_file}")
        
        # Mostrar algumas empresas únicas
        print(f"\nExemplos de empresas únicas:")
        for i, empresa in enumerate(sorted(unique_companies)[:10]):
            print(f"  {i+1}. {empresa}")
            
    except FileNotFoundError:
        print(f"Arquivo {input_file} não encontrado!")
    except Exception as e:
        print(f"Erro durante processamento: {e}")

if __name__ == "__main__":
    main()