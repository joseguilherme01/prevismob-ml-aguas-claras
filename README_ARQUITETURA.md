# 🏠 PrevIsmob - Arquitetura Client-Server

> Sistema de Previsão de Preços de Imóveis em Águas Claras  
> Migrado de Streamlit para Arquitetura Client-Server padrão

---

## 📋 Visão Geral

O projeto agora utiliza uma arquitetura **Client-Server** com separação clara entre:

- **Backend**: API FastAPI (Python) - roda na porta `8000`
- **Frontend**: HTML5 + JavaScript - qualquer servidor web (ou arquivo local)
- **Modelo ML**: Scikit-Learn (joblib) - `modelo_imoveis.pkl`

---

## 🗂️ Estrutura de Arquivos

```
Prevismob/
├── api.py                          # Backend FastAPI
├── index.html                      # Frontend UI (HTML5 + CSS)
├── script.js                       # Frontend Lógica (JavaScript)
├── modelo_imoveis.pkl             # Modelo treinado (Scikit-Learn)
├── requirements.txt                # Dependências Python
└── README_ARQUITETURA.md           # Este arquivo
```

---

## 🚀 Como Executar

### 1️⃣ Instalar Dependências

```bash
# No diretório do projeto
pip install -r requirements.txt
```

**Se `requirements.txt` não existir, instale manualmente:**

```bash
pip install fastapi uvicorn joblib pandas scikit-learn
```

### 2️⃣ Iniciar o Backend (API FastAPI)

```bash
# Terminal 1 - Abra PowerShell ou CMD e navegue até a pasta do projeto
cd c:\Users\Meu Computador\OneDrive\Área de Trabalho\Prevismob

# Execute o servidor
python api.py
```

**Você verá algo assim:**

```
============================================================
🚀 Iniciando PrevIsmob API
============================================================
📍 URL: http://localhost:8000
📚 Documentação: http://localhost:8000/docs
============================================================
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3️⃣ Abrir o Frontend (HTML)

**Opção A: Abrir arquivo local diretamente**

```bash
# Terminal 2 - Simplesmente abra o arquivo no navegador
start index.html
```

**Opção B: Subir um servidor web local (recomendado)**

```bash
# Terminal 2 - Com Python
python -m http.server 8001

# Ou com Node.js (se tiver instalado)
npx http-server -p 8001

# Depois abra: http://localhost:8001
```

---

## 🔌 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR (Frontend)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  index.html (UI com formulário)                  │   │
│  │  + script.js (lógica + validação)                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↕ (JSON POST)
        http://localhost:8000/prever
                            ↕ (JSON Response)
┌─────────────────────────────────────────────────────────┐
│                  SERVIDOR (Backend)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  api.py (FastAPI)                                │   │
│  │  ├─ Valida dados com Pydantic                    │   │
│  │  ├─ Converte para DataFrame                      │   │
│  │  ├─ Passa no modelo ML (sklearn)                 │   │
│  │  └─ Retorna preço por m²                         │   │
│  │                                                  │   │
│  │  modelo_imoveis.pkl (Scikit-Learn)               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Variáveis do Modelo ML

O modelo espera **exatamente estas 7 colunas numéricas:**

| Campo                | Tipo  | Descrição                | Exemplo |
| -------------------- | ----- | ------------------------ | ------- |
| `Quartos`            | float | Número de quartos        | 3       |
| `Vagas`              | float | Vagas de garagem         | 2       |
| `Condominio_m2`      | float | Valor condomínio por m²  | 400.0   |
| `Distancia_Metro_km` | float | Distância até metrô (km) | 0.8     |
| `Mercados_500m`      | float | Mercados dentro de 500m  | 2       |
| `Escolas_1000m`      | float | Escolas dentro de 1000m  | 3       |
| `Parques_800m`       | float | Parques dentro de 800m   | 1       |

## 🔑 Cálculos Importantes

### 1. Cálculo de `Condominio_m2` (Frontend - script.js)

```javascript
// O usuário fornece:
// - area = 120 m²
// - valorCondominio = 48000 R$

// O código calcula:
const condominioM2 = valorCondominio / area;
// 48000 / 120 = 400.0
```

### 2. Cálculo do Preço Total (Frontend - script.js)

```javascript
// API retorna: preco_m2_sugerido = 8500.0 R$/m²
// Usuário forneceu: area = 120 m²

// Cálculo final:
const precoTotal = preco_m2_sugerido * area;
// 8500.0 * 120 = 1.020.000 R$
```

---

## 🔗 API Endpoints

### `POST /prever`

**Prediz o preço do imóvel baseado nas características.**

**Request:**

```json
{
  "Quartos": 3,
  "Vagas": 2,
  "Condominio_m2": 400.0,
  "Distancia_Metro_km": 0.8,
  "Mercados_500m": 2,
  "Escolas_1000m": 3,
  "Parques_800m": 1
}
```

**Response (Sucesso):**

```json
{
  "preco_m2_sugerido": 8500.0,
  "status": "sucesso"
}
```

**Response (Erro):**

```json
{
  "preco_m2_sugerido": 0,
  "status": "erro - modelo não disponível"
}
```

### `GET /`

Retorna informações da API

### `GET /status`

Verifica se o modelo está carregado

### `GET /docs`

Documentação interativa (Swagger UI)

---

## 🐛 Troubleshooting

### ❌ Erro: "Não consigo conectar no servidor"

**Solução:**

1. Verifique se o backend está rodando:

   ```bash
   # Terminal 1 deve estar com a API rodando
   python api.py
   ```

2. Verifique se a porta 8000 está aberta:

   ```bash
   # PowerShell
   netstat -ano | findstr :8000

   # Se houver algo na porta, o servidor está rodando
   ```

3. Tente acessar a API diretamente:
   ```
   http://localhost:8000/
   ```

### ❌ Erro: "Modelo não encontrado"

**Solução:**

1. Certifique-se que `modelo_imoveis.pkl` está na mesma pasta de `api.py`
2. Verifique o nome exato do arquivo (case-sensitive)
3. Verifique a saída do servidor (deve mostrar se carregou ou não)

### ❌ CORS Error no console

**Solução:**

A API já tem CORS configurado para aceitar `"*"`. Se ainda tiver erro:

1. Abra o navegador em `http://localhost:8001` (não arquivo local)
2. Verifique a URL da API em `script.js` - deve ser `http://localhost:8000`

### ❌ Dados não estão sendo enviados

**Solução:**

1. Abra DevTools (F12) → Console
2. Verifique se há mensagens de erro
3. Verifique se todos os campos do formulário estão preenchidos
4. Tente preencher com valores válidos (números positivos)

---

## 🧪 Testar a API com cURL

```bash
# Windows PowerShell
$dados = @{
    Quartos = 3
    Vagas = 2
    Condominio_m2 = 400.0
    Distancia_Metro_km = 0.8
    Mercados_500m = 2
    Escolas_1000m = 3
    Parques_800m = 1
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://localhost:8000/prever" `
  -Method POST `
  -ContentType "application/json" `
  -Body $dados
```

---

## 🔐 Notas de Segurança

⚠️ **Desenvolvimento:**

- CORS aberto para `"*"` ✅ (OK para dev)
- Servidor em `0.0.0.0` ✅ (OK para dev)

🔒 **Produção (TODO):**

- [ ] Restringir CORS para domínios específicos
- [ ] Adicionar autenticação/API keys
- [ ] Usar HTTPS
- [ ] Validar e sanitizar inputs
- [ ] Rate limiting
- [ ] Logging e monitoramento

---

## 📦 Dependências

```
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.0
joblib==1.3.2
pandas==2.1.1
scikit-learn==1.3.2
```

Instalar todas:

```bash
pip install -r requirements.txt
```

---

## 📝 Arquivos Explicados

### `api.py`

✅ Backend com FastAPI  
✅ Carrega modelo com joblib  
✅ Rota `/prever` para previsões  
✅ Documentação automática em `/docs`  
✅ Tratamento de erros robusto

### `index.html`

✅ HTML5 semântico  
✅ Design moderno com tema escuro  
✅ CSS inline para facilitar distribuição  
✅ Formulário intuitivo com validação  
✅ Seção de resultados dinâmica

### `script.js`

✅ Validação de campos  
✅ Cálculo correto de `Condominio_m2`  
✅ Requisição à API com tratamento de erros  
✅ Formatação de moeda (Real)  
✅ Mensagens amigáveis ao usuário  
✅ Suporte a scroll suave

---

## 💡 Melhorias Futuras

- [ ] Autenticação OAuth2
- [ ] Cache de resultados
- [ ] Base de dados para histórico de previsões
- [ ] Gráficos de tendência
- [ ] Integração com Google Maps API
- [ ] Exportar resultados em PDF
- [ ] Deploy em cloud (Heroku, AWS, etc)

---

## 👨‍💻 Desenvolvedor

PrevIsmob v1.0 - Arquitetura Client-Server  
Baseado em Machine Learning com Scikit-Learn

---

## 📞 Suporte

Se tiver problemas:

1. Verifique o console (F12) no navegador
2. Verifique o terminal do servidor
3. Certifique-se que modelo está em `modelo_imoveis.pkl`
4. Teste os endpoints em `http://localhost:8000/docs`

---

**Última atualização:** Fevereiro 2024  
**Status:** ✅ Pronto para Produção (com ajustes de segurança)
