import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Configuração
ARQUIVO_DADOS = "data/dataset_aguas_claras_completo.csv"
ARQUIVO_MODELO = "data/modelo_imoveis.pkl"

print("🤖 Iniciando Treinamento da IA...")

# 1. Carregar Dados
df = pd.read_csv(ARQUIVO_DADOS)

# Selecionar o que a IA vai usar para aprender (Features)
# X = As características do imóvel
# y = O que queremos prever (Preço de Venda)
features = ['Area_Util', 'Quartos', 'Vagas', 'Distancia_Metro_km', 'Valor_Condominio']
X = df[features]
y = df['Preco_Venda']

# 2. Separar Dados de Prova vs Treino
# 80% para a IA estudar, 20% para a gente aplicar a "prova final" nela
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Treinar o Modelo (Random Forest)
modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 4. Avaliar a Performance
previsoes = modelo.predict(X_test)
erro_medio = mean_absolute_error(y_test, previsoes)
score = r2_score(y_test, previsoes)

print("-" * 40)
print(f"✅ Modelo Treinado com Sucesso!")
print(f"🎯 Precisão (R²): {score:.2f} (Quanto mais perto de 1.0, melhor)")
print(f"💰 Erro Médio Absoluto: R$ {erro_medio:,.2f}")
print("-" * 40)

# 5. Salvar o "Cérebro" da IA para usar depois
joblib.dump(modelo, ARQUIVO_MODELO)
print(f"💾 Modelo salvo em: {ARQUIVO_MODELO}")

# --- SIMULAÇÃO ---
print("\n🔮 TESTE RÁPIDO: Prevendo um Imóvel")
print("   Apartamento: 70m², 2 Quartos, 1 Vaga, Condomínio R$ 600, Metrô a 300m (0.3km)")

novo_imovel = pd.DataFrame({
    'Area_Util': [70],
    'Quartos': [2],
    'Vagas': [1],
    'Distancia_Metro_km': [0.3],
    'Valor_Condominio': [600]
})

preco_previsto = modelo.predict(novo_imovel)[0]
print(f"   🏷️  A IA diz que vale: R$ {preco_previsto:,.2f}")