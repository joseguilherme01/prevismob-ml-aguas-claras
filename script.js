/**
 * PrevIsmob - Script Frontend para Previsão de Preços de Imóveis v2.0
 * ================================================================
 * Integração com dataset CSV via endpoint GET /condominio
 * Enriquecimento automático de dados georreferenciados
 */

// =====================================================================
// CONFIGURAÇÃO - ENDPOINTS DA API
// =====================================================================

const API_BASE = "http://localhost:8000";
const API_CONDOMINIO = `${API_BASE}/condominio`; // GET lista de prédios
const API_PREVER = `${API_BASE}/prever`; // POST para previsão

// Seletores de elementos do DOM
const seletores = {
  formulario: "formularioImovel",
  nomePredioDrop: "nome_predio",
  areaUtil: "area_util",
  valorCondominio: "valor_condominio",
  quartos: "quartos",
  vagas: "vagas",
  btnCalcular: "btnCalcular",
  btnLimpar: "btnLimpar",
  resultado: "resultado",
  valorTotalMin: "valorTotalMin",
  valorTotalSug: "valorTotalSug",
  valorTotalMax: "valorTotalMax",
  locDistancia: "loc_distancia",
  locMercados: "loc_mercados",
  locEscolas: "loc_escolas",
  locParques: "loc_parques",
  mensagemErro: "mensagemErro",
  textoErro: "textoErro",
};

// =====================================================================
// FUNÇÕES UTILITÁRIAS
// =====================================================================

/**
 * Formata um número para moeda brasileira (R$)
 * @param {number} valor
 * @returns {string} Ex: "R$ 1.234,56"
 */
function formatarReal(valor) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(valor);
}

/**
 * Exibe mensagem de erro com animação
 * @param {string} mensagem
 */
function exibirErro(mensagem) {
  const elementoErro = document.getElementById(seletores.mensagemErro);
  const textoErro = document.getElementById(seletores.textoErro);

  textoErro.textContent = mensagem;
  elementoErro.classList.add("visivel");

  setTimeout(() => {
    elementoErro.classList.remove("visivel");
  }, 5000);

  console.error(`❌ ${mensagem}`);
}

/**
 * Oculta mensagem de erro
 */
function ocultarErro() {
  const elementoErro = document.getElementById(seletores.mensagemErro);
  elementoErro.classList.remove("visivel");
}

/**
 * Valida os 5 campos obrigatórios do formulário
 * @returns {boolean}
 */
function validarCampos() {
  const nomePredioDrop = document.getElementById(
    seletores.nomePredioDrop,
  ).value;
  const areaUtil = document.getElementById(seletores.areaUtil).value;
  const valorCondominio = document.getElementById(
    seletores.valorCondominio,
  ).value;
  const quartos = document.getElementById(seletores.quartos).value;
  const vagas = document.getElementById(seletores.vagas).value;

  // Validação 1: Prédio selecionado
  if (!nomePredioDrop) {
    exibirErro("Por favor, selecione um condomínio da lista");
    return false;
  }

  // Validação 2: Área
  if (!areaUtil || areaUtil <= 0) {
    exibirErro("Por favor, informe a área útil do imóvel (m²)");
    return false;
  }

  // Validação 3: Valor do condomínio
  if (!valorCondominio || valorCondominio <= 0) {
    exibirErro("Por favor, informe o valor do condomínio mensal");
    return false;
  }

  // Validação 4: Quartos
  if (!quartos || quartos < 0) {
    exibirErro("Por favor, informe a quantidade de quartos");
    return false;
  }

  // Validação 5: Vagas
  if (!vagas || vagas < 0) {
    exibirErro("Por favor, informe a quantidade de vagas");
    return false;
  }

  return true;
}

/**
 * Coleta os 5 dados do formulário
 * @returns {object} Dados formatados para API
 */
function coletarDados() {
  const nomePredioDrop = document.getElementById(
    seletores.nomePredioDrop,
  ).value;
  const areaUtil = parseFloat(
    document.getElementById(seletores.areaUtil).value,
  );
  const valorCondominio = parseFloat(
    document.getElementById(seletores.valorCondominio).value,
  );
  const quartos = parseInt(document.getElementById(seletores.quartos).value);
  const vagas = parseInt(document.getElementById(seletores.vagas).value);

  // Montar objeto JSON com os 5 campos que a API espera
  const dados = {
    Nome_Predio: nomePredioDrop,
    Area_Util: areaUtil,
    Valor_Condominio: valorCondominio,
    Quartos: quartos,
    Vagas: vagas,
  };

  return { dados, areaUtil };
}

/**
 * Exibe resultado da previsão na tela
 * @param {number} precoM2 - Preço por m²
 * @param {number} areaUtil - Área em m²
 */
function exibirResultado(precoMin, precoSug, precoMax, areaUtil, localData) {
  // Calcular valores totais
  const totalMin = precoMin * areaUtil;
  const totalSug = precoSug * areaUtil;
  const totalMax = precoMax * areaUtil;

  // Atualizar badges de localização
  document.getElementById(seletores.locDistancia).textContent = Number(
    localData.Distancia_Metro_km,
  ).toFixed(2);
  document.getElementById(seletores.locMercados).textContent =
    localData.Mercados_500m;
  document.getElementById(seletores.locEscolas).textContent =
    localData.Escolas_1000m;
  document.getElementById(seletores.locParques).textContent =
    localData.Parques_800m;

  // Atualizar cards com valores formatados
  document.getElementById(seletores.valorTotalMin).textContent =
    formatarReal(totalMin);
  document.getElementById(seletores.valorTotalSug).textContent =
    formatarReal(totalSug);
  document.getElementById(seletores.valorTotalMax).textContent =
    formatarReal(totalMax);

  // Carregar mapa se coordenadas estiverem disponíveis
  try {
    const mapa = document.getElementById("mapa_iframe");
    const lat = Number(localData.Latitude);
    const lon = Number(localData.Longitude);
    if (!isNaN(lat) && !isNaN(lon)) {
      mapa.src = `https://maps.google.com/maps?q=${lat},${lon}&z=16&output=embed`;
    } else {
      mapa.src = "";
    }
  } catch (err) {
    console.warn("Não foi possível carregar o mapa:", err);
  }

  // Exibir seção de resultados
  document.getElementById(seletores.resultado).classList.add("visivel");
  document
    .getElementById(seletores.resultado)
    .scrollIntoView({ behavior: "smooth", block: "start" });

  console.log("✓ Resultado exibido:", { totalMin, totalSug, totalMax });
}

// =====================================================================
// CARREGAMENTO INICIAL: POPULATE DROPDOWN DE CONDOMÍNIOS
// =====================================================================

/**
 * Busca lista de condomínios e popula o dropdown
 * Executada no DOMContentLoaded
 */
async function carregarCondominio() {
  try {
    console.log("📥 Carregando lista de condomínios...");

    const resposta = await fetch(API_CONDOMINIO);

    if (!resposta.ok) {
      throw new Error(`Erro HTTP: ${resposta.status}`);
    }

    const condominios = await resposta.json(); // Array de strings (nomes)
    console.log(`✓ ${condominios.length} condomínios carregados`);

    // Preencher datalist (autocomplete)
    const datalist = document.getElementById("lista_condominios");
    datalist.innerHTML = ""; // limpar opções anteriores

    condominios.forEach((nome) => {
      const opcao = document.createElement("option");
      opcao.value = nome;
      datalist.appendChild(opcao);
    });

    console.log("✓ Datalist preenchido com sucesso");
  } catch (erro) {
    console.error("✗ Erro ao carregar condomínios:", erro);
    exibirErro(
      "Erro ao carregar lista de condomínios. Verifique se o servidor está rodando.",
    );
  }
}

// =====================================================================
// FUNÇÃO PRINCIPAL: CALCULAR VALOR
// =====================================================================

/**
 * Fluxo completo de previsão
 * 1. Valida campos
 * 2. Coleta dados
 * 3. Envia para API
 * 4. Exibe resultado
 */
async function calcularValor() {
  try {
    // ========== VALIDAÇÃO ==========
    if (!validarCampos()) {
      return;
    }

    ocultarErro();

    // ========== DESABILITAR BOTÃO ==========
    const btnCalcular = document.getElementById(seletores.btnCalcular);
    const textoBotaoOriginal = btnCalcular.textContent;
    btnCalcular.disabled = true;
    btnCalcular.textContent = "Calculando...";

    // ========== COLETAR DADOS ==========
    console.log("📊 Coletando dados do formulário...");
    const { dados, areaUtil } = coletarDados();
    console.log("📤 Enviando para API:", dados);

    // ========== ENVIAR PARA API ==========
    console.log(`🌐 POST para ${API_PREVER}...`);
    const resposta = await fetch(API_PREVER, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(dados),
    });

    // ========== VERIFICAR RESPOSTA ==========
    if (!resposta.ok) {
      const erroData = await resposta.json();
      throw new Error(erroData.detail || `Erro HTTP: ${resposta.status}`);
    }

    const resultado = await resposta.json();

    // Verificar campos esperados
    if (
      resultado.preco_m2_minimo === undefined ||
      resultado.preco_m2_sugerido === undefined ||
      resultado.preco_m2_maximo === undefined
    ) {
      throw new Error("API retornou dados incompletos");
    }

    // Extrair preços por m² e dados de localização
    const precoMin = Number(resultado.preco_m2_minimo);
    const precoSug = Number(resultado.preco_m2_sugerido);
    const precoMax = Number(resultado.preco_m2_maximo);

    const localData = {
      Distancia_Metro_km: resultado.Distancia_Metro_km,
      Mercados_500m: resultado.Mercados_500m,
      Escolas_1000m: resultado.Escolas_1000m,
      Parques_800m: resultado.Parques_800m,
      Latitude: resultado.Latitude,
      Longitude: resultado.Longitude,
    };

    console.log(`✅ Resposta recebida: R$ ${precoSug}/m² (sugerido)`);

    exibirResultado(precoMin, precoSug, precoMax, areaUtil, localData);
  } catch (erro) {
    // ========== TRATAMENTO DE ERROS ==========

    let mensagemErro = "Erro desconhecido. Tente novamente.";

    if (erro instanceof TypeError) {
      mensagemErro =
        "❌ Não consigo conectar com o servidor. Verifique se a API está rodando em http://localhost:8000";
    } else if (erro.message.includes("HTTP")) {
      mensagemErro = `❌ Erro do servidor: ${erro.message}`;
    } else if (erro.message.includes("Prédio")) {
      mensagemErro = `❌ ${erro.message}`;
    } else {
      mensagemErro = `❌ ${erro.message}`;
    }

    exibirErro(mensagemErro);
  } finally {
    // ========== RESTAURAR BOTÃO ==========
    const btnCalcular = document.getElementById(seletores.btnCalcular);
    btnCalcular.disabled = false;
    btnCalcular.textContent = textoBotaoOriginal;
  }
}

// =====================================================================
// EVENT LISTENERS - INICIALIZAR AO CARREGAR PÁGINA
// =====================================================================

document.addEventListener("DOMContentLoaded", async function () {
  console.log("✓ PrevIsmob Frontend v2.0 - Carregado");
  console.log(`📍 API: ${API_BASE}`);

  // ========== CARREGAR LISTA DE CONDOMÍNIOS ==========
  await carregarCondominio();

  // ========== FORMULÁRIO ==========
  const formulario = document.getElementById(seletores.formulario);
  if (formulario) {
    formulario.addEventListener("submit", function (e) {
      e.preventDefault();
      calcularValor();
    });
  }

  // ========== LIMPAR ERRO AO FOCAR EM INPUT ==========
  document.querySelectorAll("input, select").forEach((elemento) => {
    elemento.addEventListener("focus", ocultarErro);
  });
});
