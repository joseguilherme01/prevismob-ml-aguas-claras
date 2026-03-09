# 🏠 PrevIsmob - Arquitetura Client-Server (V2)

> Sistema de Previsão de Preços de Imóveis em Águas Claras  
> Migrado para Arquitetura Client-Server com Geocoding em Tempo Real via Google Maps

---

## 📋 Visão Geral

O projeto agora utiliza uma arquitetura **Client-Server** com separação clara entre:

- **Backend**: API FastAPI (Python) - roda na porta `8000` e usa Google Maps para geocoding em tempo real e cálculo de proximidades.
- **Frontend**: HTML5 + JavaScript - qualquer servidor web (ou arquivo local).
- **Modelo ML**: Scikit-Learn (Random Forest via joblib) - `modelo_imoveis.pkl`.

---

## 🗂️ Estrutura de Arquivos

```text
Prevismob/
├── api.py                          # Backend FastAPI + Integração Google Maps
├── treinar_ia.py                   # Script de treinamento do modelo ML
├── index.html                      # Frontend UI (HTML5 + CSS)
├── script.js                       # Frontend Lógica (JavaScript)
├── modelo_imoveis.pkl              # Modelo treinado (Scikit-Learn)
├── requirements.txt                # Dependências Python
├── .env                            # Variáveis de ambiente (Chaves de API)
└── README_ARQUITETURA.md           # Este arquivo
🚀 Como ExecutarNota: a partir da versão atual a previsão depende de uma chave válida doGoogle Maps. Crie um arquivo .env na raiz com:PlaintextMaps_API_KEY=SEU_TOKEN_AQUI
1️⃣ Instalar DependênciasBash# No diretório do projeto
pip install -r requirements.txt
Se requirements.txt não existir, instale manualmente:Bashpip install fastapi uvicorn joblib pandas scikit-learn googlemaps python-dotenv
2️⃣ Iniciar o Backend (API FastAPI)Bash# Terminal 1 - Abra PowerShell ou CMD e navegue até a pasta do projeto
cd c:\Users\Meu Computador\OneDrive\Área de Trabalho\Prevismob

# Execute o servidor
python api.py
Você verá algo assim:Plaintext============================================================
🚀 Iniciando PrevIsmob API
============================================================
📍 URL: http://localhost:8000
📚 Documentação: http://localhost:8000/docs
============================================================
INFO:     Application startup complete
INFO:     Uvicorn running on [http://0.0.0.0:8000](http://0.0.0.0:8000) (Press CTRL+C to quit)
3️⃣ Abrir o Frontend (HTML)Opção A: Abrir arquivo local diretamenteBash# Terminal 2 - Simplesmente abra o arquivo no navegador
start index.html
Opção B: Subir um servidor web local (recomendado)Bash# Terminal 2 - Com Python
python -m http.server 8001

# Ou com Node.js (se tiver instalado)
npx http-server -p 8001

# Depois abra: http://localhost:8001
🔌 Fluxo de DadosPlaintext┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR (Frontend)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  index.html (UI com formulário)                  │   │
│  │  + script.js (lógica + validação)                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↕ (JSON POST via script.js)
                  http://localhost:8000/prever
                            ↕ (JSON Response)
┌─────────────────────────────────────────────────────────┐
│                    SERVIDOR (Backend)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  api.py (FastAPI)                                │   │
│  │  ├─ Valida dados com Pydantic                    │   │
│  │  ├─ 🌍 Busca Localização/Distâncias no Google Maps│   │
│  │  ├─ Converte para DataFrame                      │   │
│  │  ├─ Passa no modelo ML (sklearn)                 │   │
│  │  └─ Retorna preço por m² e dados de geolocalização│   │
│  │                                                  │   │
│  │  modelo_imoveis.pkl (Scikit-Learn)               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
📊 Variáveis do Modelo MLO modelo espera exatamente estas 7 colunas numéricas (agora montadas automaticamente pelo backend a partir do endereço):CampoTipoOrigemDescriçãoExemploQuartosfloatInputNúmero de quartos3VagasfloatInputVagas de garagem2Condominio_m2floatCalculadoValor condomínio por m²400.0Distancia_Metro_kmfloatMaps APIDistância até metrô (km)0.8Mercados_500mfloatMaps APIMercados dentro de 500m2Escolas_1000mfloatMaps APIEscolas dentro de 1000m3Parques_800mfloatMaps APIParques dentro de 800m1🔑 Cálculos Importantes1. Cálculo de Condominio_m2 (Frontend - script.js)JavaScript// O usuário fornece:
// - area = 120 m²
// - valorCondominio = 48000 R$ (ou 650 R$ na versão mensal)

// O código calcula:
const condominioM2 = valorCondominio / area;
// 48000 / 120 = 400.0
2. Cálculo do Preço Total (Frontend - script.js)JavaScript// API retorna: preco_m2_sugerido = 8500.0 R$/m²
// Usuário forneceu: area = 120 m²

// Cálculo final:
const precoTotal = preco_m2_sugerido * area;
// 8500.0 * 120 = 1.020.000 R$
🔗 API EndpointsPOST /preverPrediz o preço do imóvel baseado nas características do imóvel e na
localização obtida em tempo real via Google Maps.O backend monta automaticamente as métricas de proximidade (metrô,mercados, escolas, parques) após converter o endereço em coordenadas.Não é mais necessário fornecer manualmente Distancia_Metro_km,Mercados_500m, etc. Basta enviar o nome/endereço (campo Nome_Predio) eas dimensões básicas do imóvel.Request de exemplo (usando o modelo de entrada do frontend):JSON{
  "Nome_Predio": "Residencial Portal das Araucarias",
  "Area_Util": 120,
  "Valor_Condominio": 650,
  "Quartos": 3,
  "Vagas": 2
}
O response agora também inclui o nome da estação de metrô mais próximano campo metro_nome, além das demais métricas de localização.Response (Sucesso):JSON{
  "preco_m2_sugerido": 8500.0,
  "Distancia_Metro_km": 0.45,
  "metro_nome": "Estação Águas Claras",
  "status": "sucesso"
}
Response (Erro):JSON{
  "preco_m2_sugerido": 0,
  "status": "erro - modelo não disponível ou limite da API Maps excedido"
}
GET /Retorna informações da API.GET /statusVerifica se o modelo está carregado.GET /docsDocumentação interativa (Swagger UI).🐛 Troubleshooting❌ Erro: "Não consigo conectar no servidor"Solução:Verifique se o backend está rodando:Bash# Terminal 1 deve estar com a API rodando
python api.py
Verifique se a porta 8000 está aberta:Bash# PowerShell
netstat -ano | findstr :8000
# Se houver algo na porta, o servidor está rodando
Tente acessar a API diretamente:http://localhost:8000/
❌ Erro: "Modelo não encontrado"Solução:Certifique-se que modelo_imoveis.pkl está na mesma pasta de api.py.Verifique o nome exato do arquivo (case-sensitive).Verifique a saída do servidor (deve mostrar se carregou ou não).❌ CORS Error no consoleSolução:A API já tem CORS configurado para aceitar "*". Se ainda tiver erro:Abra o navegador em http://localhost:8001 (não arquivo local).Verifique a URL da API em script.js - deve ser http://localhost:8000.❌ Dados não estão sendo enviadosSolução:Abra DevTools (F12) → Console.Verifique se há mensagens de erro.Verifique se todos os campos do formulário estão preenchidos.Tente preencher com valores válidos (números positivos).🧪 Testar a API com cURLComo o Backend agora se comunica com o Maps, envie apenas os dados do prédio:Bash# Windows PowerShell
$dados = @{
    Nome_Predio = "Residencial Portal das Araucarias"
    Area_Util = 68.0
    Quartos = 2
    Vagas = 1
    Valor_Condominio = 650.0
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://localhost:8000/prever" `
  -Method POST `
  -ContentType "application/json" `
  -Body $dados
🔐 Notas de Segurança⚠️ Desenvolvimento:CORS aberto para "*" ✅ (OK para dev)Servidor em 0.0.0.0 ✅ (OK para dev)🔒 Produção (TODO):[ ] Restringir CORS para domínios específicos[ ] Adicionar autenticação/API keys[ ] Usar HTTPS[ ] Validar e sanitizar inputs[ ] Rate limiting[ ] Logging e monitoramento📦 DependênciasPlaintextfastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.0
joblib==1.3.2
pandas==2.1.1
scikit-learn==1.3.2
googlemaps>=4.10.0
python-dotenv>=1.0.0
Instalar todas:Bashpip install -r requirements.txt
📝 Arquivos Explicadosapi.py✅ Backend com FastAPI  ✅ Integração com Google Maps API em tempo real✅ Carrega modelo com joblib  ✅ Rota /prever para previsões  ✅ Documentação automática em /docs  ✅ Tratamento de erros robustotreinar_ia.py✅ Separa os dados de treino (80%) e teste (20%)✅ Limpa dados vazios dinamicamente✅ Treina a IA (Random Forest) com 7 variáveis geolocalizadas✅ Salva o modelo_imoveis.pkl na raizindex.html✅ HTML5 semântico  ✅ Design moderno com tema escuro  ✅ CSS inline para facilitar distribuição  ✅ Formulário intuitivo com validação  ✅ Seção de resultados dinâmicascript.js✅ Validação de campos  ✅ Cálculo correto de Condominio_m2  ✅ Requisição à API com tratamento de erros  ✅ Formatação de moeda (Real)  ✅ Mensagens amigáveis ao usuário  ✅ Suporte a scroll suave💡 Melhorias Futuras[ ] Visão Computacional (Nível Advanced): Integrar a API do Google Cloud Vision para analisar fotos do Street View da fachada dos prédios e cruzar com os dados de localização.[ ] Sistema de Cache Local: Salvar requisições feitas ao Google Maps em um SQLite para economizar cota.[ ] Autenticação OAuth2[ ] Base de dados para histórico de previsões[ ] Gráficos de tendência[ ] Exportar resultados em PDF[ ] Deploy em cloud (Heroku, AWS, etc)👨‍💻 DesenvolvedorPrevIsmob v2.0 - Arquitetura Client-Server  Baseado em Machine Learning (Scikit-Learn) e Google Maps.📞 SuporteSe tiver problemas:Verifique o console (F12) no navegadorVerifique o terminal do servidorCertifique-se que modelo está em modelo_imoveis.pklTeste os endpoints em http://localhost:8000/docsÚltima atualização: Março 2026  Status: ✅ Pronto para Produção (com ajustes de segurança)
Olha bem as seções `Troubleshooting`, `Notas de Segurança`, `Dependências` e `Arquivos Explicados`. Todas elas voltaram para a forma exata e super detalhada que você tinha escrito originalmente.

Pode me dizer se agora ficou 100% igual à sua visão?
```
