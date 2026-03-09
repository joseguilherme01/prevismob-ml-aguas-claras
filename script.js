/**
 * PrevIsmob - Script Frontend para Previsão de Preços de Imóveis v2.1
 * ================================================================
 * Campo de condomínio usa Google Places Autocomplete (sem dataset local)
 * Enriquecimento automático de dados georreferenciados via backend
 */

// =====================================================================
// CONFIGURAÇÃO - ENDPOINTS DA API
// =====================================================================

const API_BASE = "http://localhost:8000";
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
 * @param {boolean} [isCritico=false] - Erros críticos ficam visíveis por mais tempo
 */
function exibirErro(mensagem, isCritico = false) {
  const elementoErro = document.getElementById(seletores.mensagemErro);
  const textoErro = document.getElementById(seletores.textoErro);

  textoErro.textContent = mensagem;
  elementoErro.classList.add("visivel");

  if (isCritico) {
    elementoErro.classList.add("critico");
  } else {
    elementoErro.classList.remove("critico");
  }

  // Cancela qualquer auto-hide anterior antes de agendar o novo
  if (exibirErro._timeout) {
    clearTimeout(exibirErro._timeout);
  }

  const duracao = isCritico ? 12000 : 5000;
  exibirErro._timeout = setTimeout(() => {
    elementoErro.classList.remove("visivel", "critico");
  }, duracao);

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
  // mostrar nome da estação junto com a distância
  document.getElementById("metro_nome").textContent =
    localData.metro_nome || "--";
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

  // Carregar mapa se coordenadas estiverem disponíveis (OpenStreetMap, sem API key)
  try {
    const mapa = document.getElementById("mapa_iframe");
    const lat = Number(localData.Latitude);
    const lon = Number(localData.Longitude);
    if (!isNaN(lat) && !isNaN(lon) && lat !== 0 && lon !== 0) {
      const delta = 0.008;
      mapa.src = `https://www.openstreetmap.org/export/embed.html?bbox=${lon - delta},${lat - delta},${lon + delta},${lat + delta}&layer=mapnik&marker=${lat},${lon}`;
    } else {
      mapa.src = "";
      console.warn("Coordenadas inválidas ou ausentes — mapa não carregado.");
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
  // Declarar fora do try para que estejam acessíveis no finally
  const btnCalcular = document.getElementById(seletores.btnCalcular);
  const textoBotaoOriginal = btnCalcular
    ? btnCalcular.textContent
    : "Calcular valor de mercado";

  try {
    // ========== VALIDAÇÃO ==========
    if (!validarCampos()) {
      return;
    }

    ocultarErro();

    // ========== DESABILITAR BOTÃO ==========
    if (btnCalcular) {
      btnCalcular.disabled = true;
      btnCalcular.textContent = "Calculando...";
    }

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
      metro_nome: resultado.metro_nome,
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
    let isCritico = false;

    if (erro instanceof TypeError) {
      mensagemErro =
        "❌ Não consigo conectar com o servidor. Verifique se a API está rodando em http://localhost:8000";
      isCritico = true;
    } else if (erro.message.includes("HTTP")) {
      mensagemErro = `❌ Erro do servidor: ${erro.message}`;
    } else if (erro.message.includes("Prédio")) {
      mensagemErro = `❌ ${erro.message}`;
    } else {
      mensagemErro = `❌ ${erro.message}`;
    }

    exibirErro(mensagemErro, isCritico);
  } finally {
    // ========== RESTAURAR BOTÃO ==========
    if (btnCalcular) {
      btnCalcular.disabled = false;
      btnCalcular.textContent = textoBotaoOriginal;
    }
  }
}

// =====================================================================
// EVENT LISTENERS - INICIALIZAR AO CARREGAR PÁGINA
// =====================================================================

document.addEventListener("DOMContentLoaded", async function () {
  console.log("✓ PrevIsmob Frontend v2.0 - Carregado");
  console.log(`📍 API: ${API_BASE}`);

  // landing page: iniciar app quando usuário clicar
  // função reutilizável para iniciar a aplicação a partir da landing
  function iniciarApp() {
    document.getElementById("landing-section").style.display = "none";
    const app = document.getElementById("app-section");
    app.style.display = "block";
    app.classList.add("fade-in");
  }

  // vincular tanto o botão antigo (se existir) quanto o botão dentro do card
  const btnComecar = document.getElementById("btn-comecar");
  if (btnComecar) {
    btnComecar.addEventListener("click", iniciarApp);
  }
  const btnCard = document.querySelector(".card-button");
  if (btnCard) {
    btnCard.addEventListener("click", iniciarApp);
  }
  // botão voltar na app-section
  const btnVoltar = document.getElementById("btn-voltar");
  if (btnVoltar) {
    btnVoltar.addEventListener("click", () => {
      const app = document.getElementById("app-section");
      app.style.display = "none";
      const landing = document.getElementById("landing-section");
      landing.style.display = "block";
      landing.classList.add("fade-in");
    });
  }

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
