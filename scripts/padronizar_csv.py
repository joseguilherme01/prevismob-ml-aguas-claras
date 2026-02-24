import pandas as pd
import os

# Lista dos arquivos que queremos consertar
arquivos = [
    "data/dataset_aguas_claras_ml.csv",       # O arquivo original
    "data/dataset_aguas_claras_features.csv"  # O arquivo que acabamos de gerar
]

print("🔄 Iniciando padronização para Vírgulas (Global Standard)...\n")

for arquivo in arquivos:
    if os.path.exists(arquivo):
        try:
            # 1. Lê usando o padrão brasileiro (ponto e vírgula)
            df = pd.read_csv(arquivo, sep=';', encoding='utf-8-sig')
            
            # 2. Salva usando o padrão global (vírgula)
            # index=False: não cria aquela coluna de números 0,1,2 extra
            df.to_csv(arquivo, sep=',', index=False, encoding='utf-8-sig')
            
            print(f"✅ {arquivo}: Convertido com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao ler {arquivo}: {e}")
    else:
        print(f"⚠️ Arquivo não encontrado: {arquivo}")

print("\n🚀 Tudo pronto! Agora seus arquivos são Universais.")