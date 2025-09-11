import os
from supabase import create_client, Client
from collections import Counter
from typing import Dict, List
from dotenv import load_dotenv

def connect_to_supabase() -> Client:
    """Conecta ao Supabase"""
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
    
    return create_client(url, key)

def analyze_data_diversity():
    """Analisa a diversidade de empresas, setores e descrições"""
    print("=== ANÁLISE DE DIVERSIDADE DOS DADOS ===")
    
    try:
        supabase = connect_to_supabase()
        print("Conectado ao Supabase")
        
        # Buscar todas as vagas
        response = supabase.table('vagas').select('*').execute()
        vagas = response.data
        
        print(f"Total de vagas analisadas: {len(vagas)}")
        
        # Analisar empresas
        empresas = [vaga['empresa'] for vaga in vagas if vaga['empresa']]
        empresa_counts = Counter(empresas)
        
        print(f"\n=== ANÁLISE DE EMPRESAS ===")
        print(f"Total de empresas únicas: {len(empresa_counts)}")
        print(f"Empresas mais frequentes (top 10):")
        for empresa, count in empresa_counts.most_common(10):
            print(f"  {empresa}: {count} vagas")
        
        # Verificar se há empresas genéricas demais
        empresas_genericas = 0
        for empresa in empresas:
            if any(word in empresa.lower() for word in ['empresa reconhecida', 'empresa confidencial', 'empresa de', 'não especificada']):
                empresas_genericas += 1
        
        print(f"Empresas com nomes genéricos: {empresas_genericas} ({empresas_genericas/len(empresas)*100:.1f}%)")
        
        # Analisar setores
        setores = [vaga['setor'] for vaga in vagas if vaga['setor']]
        setor_counts = Counter(setores)
        
        print(f"\n=== ANÁLISE DE SETORES ===")
        print(f"Total de setores únicos: {len(setor_counts)}")
        print(f"Distribuição por setor:")
        for setor, count in setor_counts.most_common():
            print(f"  {setor}: {count} vagas")
        
        # Analisar descrições
        descricoes = [vaga['descricao'][:100] for vaga in vagas if vaga['descricao']]  # Primeiros 100 chars
        descricao_counts = Counter(descricoes)
        
        print(f"\n=== ANÁLISE DE DESCRIÇÕES ===")
        print(f"Total de descrições analisadas: {len(descricoes)}")
        print(f"Descrições únicas (primeiros 100 chars): {len(descricao_counts)}")
        print(f"Taxa de diversidade: {len(descricao_counts)/len(descricoes)*100:.1f}%")
        
        # Mostrar descrições mais repetidas
        print(f"\nDescrições mais repetidas:")
        for desc, count in descricao_counts.most_common(5):
            if count > 1:
                print(f"  Repetida {count} vezes: {desc}...")
        
        # Analisar por setor específico
        print(f"\n=== ANÁLISE DETALHADA POR SETOR ===")
        
        setores_principais = ['ServicoSocial', 'Serviço Social', 'Administracao', 'Saude', 'Telecomunicacoes']
        
        for setor_nome in setores_principais:
            vagas_setor = [v for v in vagas if v['setor'] == setor_nome]
            if len(vagas_setor) >= 5:
                empresas_setor = [v['empresa'] for v in vagas_setor]
                empresas_unicas_setor = set(empresas_setor)
                
                descricoes_setor = [v['descricao'][:100] for v in vagas_setor if v['descricao']]
                descricoes_unicas_setor = set(descricoes_setor)
                
                print(f"\n--- {setor_nome} ({len(vagas_setor)} vagas) ---")
                print(f"  Empresas únicas: {len(empresas_unicas_setor)}")
                print(f"  Descrições únicas: {len(descricoes_unicas_setor)}")
                print(f"  Taxa diversidade empresas: {len(empresas_unicas_setor)/len(vagas_setor)*100:.1f}%")
                print(f"  Taxa diversidade descrições: {len(descricoes_unicas_setor)/len(vagas_setor)*100:.1f}%")
                
                if len(empresas_unicas_setor) <= 3:
                    print(f"  Empresas: {list(empresas_unicas_setor)}")
        
        # Mostrar exemplos de vagas diversificadas
        print(f"\n=== EXEMPLOS DE VAGAS DIVERSIFICADAS ===")
        
        # Pegar vagas de diferentes empresas
        empresas_exemplo = list(empresa_counts.keys())[:10]
        for i, empresa in enumerate(empresas_exemplo[:5]):
            vaga_exemplo = next((v for v in vagas if v['empresa'] == empresa), None)
            if vaga_exemplo:
                print(f"\nExemplo {i+1}:")
                print(f"  Título: {vaga_exemplo['titulo']}")
                print(f"  Empresa: {vaga_exemplo['empresa']}")
                print(f"  Setor: {vaga_exemplo['setor']}")
                print(f"  Localização: {vaga_exemplo['localizacao']}")
                print(f"  Descrição: {vaga_exemplo['descricao'][:150]}...")
        
        print(f"\n=== CONCLUSÃO ===")
        if len(empresa_counts) > 50 and len(descricao_counts)/len(descricoes) > 0.3:
            print("✅ SUCESSO: Dados apresentam boa diversidade!")
            print(f"   - {len(empresa_counts)} empresas únicas")
            print(f"   - {len(descricao_counts)/len(descricoes)*100:.1f}% de diversidade nas descrições")
        else:
            print("⚠️  ATENÇÃO: Ainda há problemas de diversidade nos dados")
            print(f"   - Empresas únicas: {len(empresa_counts)}")
            print(f"   - Diversidade descrições: {len(descricao_counts)/len(descricoes)*100:.1f}%")
        
    except Exception as e:
        print(f"Erro durante análise: {e}")

def main():
    analyze_data_diversity()

if __name__ == "__main__":
    main()