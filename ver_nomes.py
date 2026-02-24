import pandas as pd

# Carrega o dataset
df = pd.read_csv('data/dataset_aguas_claras_completo.csv')

print("📋 LISTA COMPLETA DE COLUNAS:")
print(df.columns.tolist())

print("\n🔍 VENDO AS 3 PRIMEIRAS LINHAS (Para identificar onde está o nome):")
# Mostra colunas que são texto (object)
print(df.select_dtypes(include=['object']).head(3))