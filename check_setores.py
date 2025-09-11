import pandas as pd

df = pd.read_csv('vagas_todos_setores_1_pagina.csv')
print(f'Total de registros: {len(df)}')
print(f'Colunas: {list(df.columns)}')

# Verifica a última coluna (setor)
if len(df.columns) > 12:
    setores = df.iloc[:, 12].value_counts()
    print(f'\nValores únicos na coluna do setor (índice 12):')
    print(setores)
    
    print(f'\nPrimeiros 10 valores da coluna setor:')
    for i in range(min(10, len(df))):
        valor = df.iloc[i, 12]
        print(f'Linha {i}: "{valor}" (tipo: {type(valor)})')
else:
    print('CSV não tem coluna de índice 12')