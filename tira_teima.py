import pandas as pd

df = pd.read_csv('data/dataset_aguas_claras_completo.csv')

print("📊 Média de Preço do m² por quantidade de Vagas:")
print(df.groupby('Vagas')['Preco_m2'].mean())