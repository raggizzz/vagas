import pandas as pd
import json

print("Iniciando teste do master extractor...")

# Carrega o CSV
print("Carregando CSV...")
df = pd.read_csv('catho_batch_009_vagas_36001-40500.csv')
print(f"CSV carregado: {len(df)} linhas")

# Testa uma linha
print("Testando primeira linha...")
first_row = df.iloc[0]
print(f"Título: {first_row['Título']}")
print(f"Descrição (primeiros 100 chars): {first_row['Descrição'][:100]}")

print("Teste concluído!")