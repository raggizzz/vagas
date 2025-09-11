import json
from collections import defaultdict, Counter
from supabase import create_client, Client
import os
from dotenv import load_dotenv

def connect_to_supabase():
    """Conecta ao Supabase usando as credenciais do arquivo .env"""
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("As variáveis SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
    
    return create_client(url, key)

def analyze_descriptions_by_sector():
    """Analisa as descrições das vagas agrupadas por setor"""
    try:
        supabase = connect_to_supabase()
        
        # Buscar todas as vagas
        response = supabase.table('vagas').select('setor, descricao').execute()
        vagas = response.data
        
        print(f"\n=== ANÁLISE DE DESCRIÇÕES POR SETOR ===")
        print(f"Total de vagas analisadas: {len(vagas)}")
        
        # Agrupar por setor
        setores_descricoes = defaultdict(list)
        for vaga in vagas:
            setor = vaga.get('setor', 'Não informado')
            descricao = vaga.get('descricao', '')
            if descricao:
                setores_descricoes[setor].append(descricao)
        
        print(f"\nSetores encontrados: {len(setores_descricoes)}")
        
        # Analisar cada setor
        for setor, descricoes in setores_descricoes.items():
            print(f"\n{'='*60}")
            print(f"SETOR: {setor}")
            print(f"Total de vagas: {len(descricoes)}")
            
            # Contar descrições únicas
            descricoes_unicas = set(descricoes)
            taxa_diversidade = len(descricoes_unicas) / len(descricoes) * 100
            
            print(f"Descrições únicas: {len(descricoes_unicas)}")
            print(f"Taxa de diversidade: {taxa_diversidade:.1f}%")
            
            # Identificar descrições repetidas
            contador_descricoes = Counter(descricoes)
            descricoes_repetidas = {desc: count for desc, count in contador_descricoes.items() if count > 1}
            
            if descricoes_repetidas:
                print(f"\n⚠️  DESCRIÇÕES REPETIDAS ({len(descricoes_repetidas)} diferentes):")
                for desc, count in sorted(descricoes_repetidas.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  • Repetida {count}x: {desc[:100]}{'...' if len(desc) > 100 else ''}")
            else:
                print("\n✅ Todas as descrições são únicas!")
            
            # Mostrar algumas descrições únicas como exemplo
            if len(descricoes_unicas) > 1:
                print(f"\n📝 EXEMPLOS DE DESCRIÇÕES ÚNICAS:")
                for i, desc in enumerate(list(descricoes_unicas)[:3]):
                    print(f"  {i+1}. {desc[:150]}{'...' if len(desc) > 150 else ''}")
            
            # Alerta se taxa de diversidade for muito baixa
            if taxa_diversidade < 50:
                print(f"\n🚨 ALERTA: Taxa de diversidade baixa ({taxa_diversidade:.1f}%)")
            elif taxa_diversidade < 80:
                print(f"\n⚠️  ATENÇÃO: Taxa de diversidade moderada ({taxa_diversidade:.1f}%)")
            else:
                print(f"\n✅ Taxa de diversidade boa ({taxa_diversidade:.1f}%)")
        
        # Resumo geral
        print(f"\n{'='*60}")
        print(f"RESUMO GERAL")
        print(f"{'='*60}")
        
        setores_problematicos = []
        for setor, descricoes in setores_descricoes.items():
            descricoes_unicas = set(descricoes)
            taxa_diversidade = len(descricoes_unicas) / len(descricoes) * 100
            if taxa_diversidade < 50:
                setores_problematicos.append((setor, taxa_diversidade, len(descricoes)))
        
        if setores_problematicos:
            print(f"\n🚨 SETORES COM BAIXA DIVERSIDADE DE DESCRIÇÕES:")
            for setor, taxa, total in sorted(setores_problematicos, key=lambda x: x[1]):
                print(f"  • {setor}: {taxa:.1f}% diversidade ({total} vagas)")
        else:
            print(f"\n✅ Todos os setores têm boa diversidade de descrições!")
            
    except Exception as e:
        print(f"Erro durante a análise: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Iniciando análise de descrições por setor...")
    success = analyze_descriptions_by_sector()
    if success:
        print("\n✅ Análise concluída com sucesso!")
    else:
        print("\n❌ Erro durante a análise.")