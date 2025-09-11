import json
from collections import Counter

def analyze_all_sectors():
    # Carregar dados originais
    with open('vagas_todos_setores_estruturadas_completo.jsonl', 'r', encoding='utf-8') as f:
        vagas = [json.loads(line) for line in f]
    
    print(f"Total de vagas carregadas: {len(vagas)}")
    
    # Agrupar por setor
    setores = {}
    for vaga in vagas:
        setor = vaga.get('informacoes_basicas', {}).get('setor', 'Desconhecido')
        if setor not in setores:
            setores[setor] = []
        setores[setor].append(vaga)
    
    print(f"\nTotal de setores: {len(setores)}")
    
    # Analisar diversidade por setor
    setores_problematicos = []
    
    for setor, vagas_setor in setores.items():
        total_vagas = len(vagas_setor)
        descricoes = [vaga.get('descricao_completa', {}).get('texto_completo', '') for vaga in vagas_setor]
        descricoes_unicas = len(set(descricoes))
        taxa_diversidade = (descricoes_unicas / total_vagas) * 100
        
        # Considerar problemático se diversidade < 80%
        if taxa_diversidade < 80.0:
            setores_problematicos.append({
                'setor': setor,
                'total_vagas': total_vagas,
                'descricoes_unicas': descricoes_unicas,
                'taxa_diversidade': taxa_diversidade
            })
    
    # Ordenar por taxa de diversidade (menor primeiro)
    setores_problematicos.sort(key=lambda x: x['taxa_diversidade'])
    
    print("\n" + "="*60)
    print("SETORES PROBLEMÁTICOS (Diversidade < 80%)")
    print("="*60)
    
    for setor_info in setores_problematicos:
        print(f"\nSETOR: {setor_info['setor']}")
        print(f"Total de vagas: {setor_info['total_vagas']}")
        print(f"Descrições únicas: {setor_info['descricoes_unicas']}")
        print(f"Taxa de diversidade: {setor_info['taxa_diversidade']:.1f}%")
        
        # Mostrar descrições duplicadas
        vagas_setor = setores[setor_info['setor']]
        descricoes = [vaga.get('descricao_completa', {}).get('texto_completo', '') for vaga in vagas_setor]
        contador_descricoes = Counter(descricoes)
        
        print("\nDescrições repetidas:")
        for descricao, count in contador_descricoes.most_common():
            if count > 1:
                print(f"  - {count}x: {descricao[:100]}...")
        
        # Verificar presença de "CANDIDATURA FÁCIL"
        vagas_com_candidatura_facil = 0
        for vaga in vagas_setor:
            descricao = vaga.get('descricao_completa', {}).get('texto_completo', '').upper()
            if 'CANDIDATURA FÁCIL' in descricao or 'CANDIDATURA FACIL' in descricao:
                vagas_com_candidatura_facil += 1
        
        if vagas_com_candidatura_facil > 0:
            print(f"\n⚠️  {vagas_com_candidatura_facil} vagas contêm 'CANDIDATURA FÁCIL'")
    
    print(f"\n\nTotal de setores problemáticos: {len(setores_problematicos)}")
    
    return setores_problematicos

if __name__ == "__main__":
    setores_problematicos = analyze_all_sectors()
    
    # Salvar lista de setores problemáticos
    with open('setores_problematicos.json', 'w', encoding='utf-8') as f:
        json.dump(setores_problematicos, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Lista de setores problemáticos salva em 'setores_problematicos.json'")