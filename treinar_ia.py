import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

print("🔄 Carregando dados...")
# 1. Carregar os dados
df = pd.read_csv('data/dataset_aguas_claras_completo.csv')

# 2. Configuração das colunas (Baseado no seu print)
# X = As informações que a IA vai usar para pensar
# y = A resposta que ela precisa descobrir (Preço do m2)
colunas_usadas = [
    'Quartos', 
    'Vagas', 
    'Condominio_m2', 
    'Distancia_Metro_km', 
    'Mercados_500m', 
    'Escolas_1000m', 
    'Parques_800m'
]
alvo = 'Preco_m2'

# Limpeza de segurança (remove linhas vazias se existirem)
df_limpo = df[colunas_usadas + [alvo]].dropna()

X = df_limpo[colunas_usadas]
y = df_limpo[alvo]

# 3. Separar dados para Treino (80%) e Teste (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Criar e Treinar o Modelo
print("🧠 Treinando a Inteligência Artificial (Random Forest)...")
# n_estimators=100 significa que ele cria 100 "árvores de decisão" para votar no preço
modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 5. Avaliar a precisão
previsoes = modelo.predict(X_test)
score = r2_score(y_test, previsoes)
erro_medio = mean_absolute_error(y_test, previsoes)

print("-" * 40)
print(f"✅ Treinamento Concluído com Sucesso!")
print("-" * 40)
print(f"📊 Acurácia do Modelo (R²): {score:.2f}")
print(f"   (0.00 = Ruim | 1.00 = Perfeito)")
print(f"💰 Erro médio por m²: R$ {erro_medio:.2f}")
print("-" * 40)

# 6. Salvar o modelo
joblib.dump(modelo, 'modelo_imoveis.pkl')
print("💾 Cérebro da IA salvo: 'modelo_imoveis.pkl'")