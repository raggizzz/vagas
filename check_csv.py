import pandas as pd

df = pd.read_csv('vagas_todos_setores_1_pagina.csv')
print('Colunas:', list(df.columns))
print('\nPrimeira linha:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col} = {df.iloc[0, i]}')