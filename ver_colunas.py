import pandas as pd

try:
    # Tenta ler o arquivo
    df = pd.read_csv('data/dataset_aguas_claras_completo.csv')
    
    print("\n📋 LISTA DE COLUNAS ENCONTRADAS:")
    print("-" * 30)
    for col in df.columns:
        print(f" -> {col}")
    print("-" * 30)
    
    # Mostra a primeira linha para vermos se os dados estão certos
    print("\n🔍 EXEMPLO DA PRIMEIRA LINHA:")
    print(df.iloc[0])

except Exception as e:
    print(f"❌ Erro ao ler arquivo: {e}")