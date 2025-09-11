import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def connect_supabase() -> Client:
    """Conecta ao Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
    
    return create_client(url, key)

def verify_data_quality():
    """Verifica a qualidade dos dados inseridos"""
    supabase = connect_supabase()
    
    print("=== VERIFICAÇÃO DA QUALIDADE DOS DADOS ===")
    
    # 1. Verificar total de vagas
    result = supabase.table('vagas').select('*', count='exact').execute()
    total_vagas = result.count if hasattr(result, 'count') else len(result.data)
    print(f"\n1. Total de vagas: {total_vagas}")
    
    # 2. Verificar vagas com títulos adequados
    vagas_sem_titulo = supabase.table('vagas').select('*').or_('titulo.is.null,titulo.eq.').execute()
    print(f"2. Vagas sem título: {len(vagas_sem_titulo.data)}")
    
    # 3. Verificar vagas com localização
    vagas_sem_localizacao = supabase.table('vagas').select('*').eq('localizacao', 'Localização não especificada').execute()
    print(f"3. Vagas sem localização específica: {len(vagas_sem_localizacao.data)}")
    
    # 4. Verificar duplicatas por external_id
    all_vagas = supabase.table('vagas').select('external_id').execute()
    external_ids = [vaga['external_id'] for vaga in all_vagas.data]
    duplicates = len(external_ids) - len(set(external_ids))
    print(f"4. Duplicatas encontradas: {duplicates}")
    
    # 5. Mostrar algumas vagas de exemplo
    sample_vagas = supabase.table('vagas').select('*').limit(5).execute()
    print("\n5. Exemplos de vagas processadas:")
    print("-" * 80)
    
    for i, vaga in enumerate(sample_vagas.data, 1):
        print(f"\nVaga {i}:")
        print(f"  Título: {vaga['titulo'][:100]}{'...' if len(vaga['titulo']) > 100 else ''}")
        print(f"  Empresa: {vaga['empresa']}")
        print(f"  Localização: {vaga['localizacao']}")
        print(f"  Setor: {vaga['setor']}")
        print(f"  Modalidade: {vaga['modalidade_trabalho']}")
        print(f"  Descrição: {vaga['descricao'][:150]}{'...' if len(vaga['descricao']) > 150 else ''}")
    
    # 6. Verificar distribuição por localização
    print("\n6. Distribuição por localização (top 10):")
    # Buscar todas as vagas com localização
    all_vagas_with_location = supabase.table('vagas').select('localizacao').execute()
    localizacoes = {}
    for vaga in all_vagas_with_location.data:
        loc = vaga.get('localizacao', 'Não especificada')
        localizacoes[loc] = localizacoes.get(loc, 0) + 1
    
    top_localizacoes = sorted(localizacoes.items(), key=lambda x: x[1], reverse=True)[:10]
    for loc, count in top_localizacoes:
        print(f"  {loc}: {count} vagas")
    
    # 7. Verificar distribuição por setor
    print("\n7. Distribuição por setor:")
    setores = {}
    for vaga in sample_vagas.data:
        setor = vaga.get('setor', 'Não especificado')
        setores[setor] = setores.get(setor, 0) + 1
    
    for setor, count in setores.items():
        print(f"  {setor}: {count} vagas (na amostra)")
    
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    verify_data_quality()