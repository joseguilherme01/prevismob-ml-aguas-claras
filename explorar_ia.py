import pandas as pd
import joblib
import matplotlib.pyplot as plt

# 1. Carregar Modelo e Dados
modelo = joblib.load('modelo_imoveis.pkl')
features = [
    'Quartos', 
    'Vagas', 
    'Condominio_m2', 
    'Distancia_Metro_km', 
    'Mercados_500m', 
    'Escolas_1000m', 
    'Parques_800m'
]

# 2. Pegar a importância de cada item
importancia = modelo.feature_importances_

# 3. Criar um gráfico bonito
df_importancia = pd.DataFrame({'Característica': features, 'Importância': importancia})
df_importancia = df_importancia.sort_values(by='Importância', ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(df_importancia['Característica'], df_importancia['Importância'], color='#ff4b4b')
plt.xlabel('Peso na Decisão do Preço (0 a 1)')
plt.title('O que a IA mais valoriza em Águas Claras?')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()

# Salvar e mostrar
plt.savefig('grafico_importancia.png')
print("✅ Gráfico gerado: 'grafico_importancia.png'")
print("Abra esse arquivo para ver o cérebro da sua IA!")