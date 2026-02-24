import pandas as pd
import os

print("--- 🕵️‍♂️ DIAGNÓSTICO DE PARQUES ---")

# 1. Verificar o arquivo de ENTRADA (O que veio do Google Maps)
file_in = "data/dataset_aguas_claras_features.csv"

if os.path.exists(file_in):
    df_in = pd.read_csv(file_in)
    print(f"\n1️⃣ Arquivo ORIGINAL ({file_in}):")
    
    # Procura qualquer coluna que tenha "parq" no nome
    cols_parque = [c for c in df_in.columns if 'parq' in c.lower()]
    
    if cols_parque:
        print(f"   ✅ ACHEI! Nome da coluna: {cols_parque}")
        print(f"   📊 Primeiros 5 valores: {df_in[cols_parque[0]].head(5).tolist()}")
    else:
        print("   ❌ NÃO TEM coluna de parques aqui. O problema começou na coleta!")
        print(f"   As colunas que existem são: {list(df_in.columns)}")
else:
    print("❌ Arquivo de entrada nem existe.")

# 2. Verificar o arquivo FINAL (O que o site usa)
file_out = "data/dataset_aguas_claras_completo.csv"

if os.path.exists(file_out):
    df_out = pd.read_csv(file_out)
    print(f"\n2️⃣ Arquivo FINAL ({file_out}):")
    
    cols_parque_out = [c for c in df_out.columns if 'parq' in c.lower()]
    
    if cols_parque_out:
         print(f"   ✅ O site deveria ver: {cols_parque_out}")
    else:
         print("   ❌ O arquivo final NÃO recebeu a coluna de parques.")
else:
    print("❌ Arquivo final não existe.")