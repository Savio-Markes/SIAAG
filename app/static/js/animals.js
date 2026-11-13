
/* =========================================
   SIAAG - MÓDULO DE ANIMAIS
   Listagem e integração com a API
========================================= */

document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/animais/";
    const LIMITE = 50;

    const elementos = {
        identificacao: document.getElementById("filtroIdentificacao"),
        especie: document.getElementById("filtroEspecie"),
        situacao: document.getElementById("filtroSituacao"),
        corpo: document.getElementById("animalsTableBody"),
        feedback: document.getElementById("animalsFeedback"),
        total: document.getElementById("totalAnimais"),
        informacao: document.getElementById("paginationInfo"),
        pagina: document.getElementById("paginaAtual"),
        anterior: document.getElementById("btnPaginaAnterior"),
        proxima: document.getElementById("btnProximaPagina"),
        limpar: document.getElementById("btnLimparFiltros"),
        novo: document.getElementById("btnNovoAnimal")
    };

    let deslocamento = 0;
    let animais = [];
    let carregando = false;

    function mostrarFeedback(mensagem, tipo = "info") {
        elementos.feedback.textContent = mensagem;
        elementos.feedback.className = `animals-feedback ${tipo}`;
        elementos.feedback.hidden = false;
    }

    function limparFeedback() {
        elementos.feedback.textContent = "";
        elementos.feedback.hidden = true;
        elementos.feedback.className = "animals-feedback";
    }

    function mostrarCarregamento() {
        elementos.corpo.innerHTML = `
            <tr>
                <td colspan="6" class="animals-loading">
                    Carregando animais...
                </td>
            </tr>
        `;
    }

    function mostrarEstadoVazio(mensagem) {
        elementos.corpo.innerHTML = "";

        const linha = document.createElement("tr");
        const celula = document.createElement("td");

        celula.colSpan = 6;
        celula.className = "animals-empty";
        celula.textContent = mensagem;

        linha.appendChild(celula);
        elementos.corpo.appendChild(linha);
    }

    function criarCelula(valor) {
        const celula = document.createElement("td");
        celula.textContent = valor ?? "—";
        return celula;
    }

    function criarAcao(animal) {
        const celula = document.createElement("td");
        const link = document.createElement("a");

        link.className = "animal-action";
        link.textContent = "Abrir ficha";
        link.href = `/animais/${encodeURIComponent(animal.id)}/painel`;
        celula.appendChild(link);
        return celula;
    }

    function renderizarAnimais(lista) {
        elementos.corpo.innerHTML = "";

        if (!lista.length) {
            mostrarEstadoVazio("Nenhum animal encontrado.");
            return;
        }

        const fragmento = document.createDocumentFragment();

        lista.forEach(animal => {
            const linha = document.createElement("tr");

            linha.appendChild(criarCelula(animal.identificacao));
            linha.appendChild(criarCelula(animal.especie));
            linha.appendChild(criarCelula(animal.raca));
            linha.appendChild(criarCelula(animal.situacao));
            linha.appendChild(criarCelula(animal.localizacao));
            linha.appendChild(criarAcao(animal));

            fragmento.appendChild(linha);
        });

        elementos.corpo.appendChild(fragmento);
    }

    function atualizarPaginacao(quantidade) {
        elementos.pagina.textContent = String(
            Math.floor(deslocamento / LIMITE) + 1
        );

        elementos.informacao.textContent =
            `${quantidade} registro(s) nesta página.`;

        elementos.anterior.disabled = deslocamento === 0;

        // A API atual não informa total de páginas.
        // Uma página com menos registros que o limite indica o fim.
        elementos.proxima.disabled = quantidade < LIMITE;
    }

    async function carregarAnimais() {
        if (carregando) return;

        carregando = true;
        limparFeedback();
        mostrarCarregamento();

        const parametros = new URLSearchParams({
            identificacao: elementos.identificacao.value.trim(),
            especie: elementos.especie.value,
            situacao: elementos.situacao.value,
            limite: String(LIMITE),
            deslocamento: String(deslocamento)
        });

        try {
            const resposta = await fetch(`${API_URL}?${parametros}`, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

            if (!resposta.ok) {
                if (resposta.status === 401 || resposta.status === 403) {
                    throw new Error(
                        "Você não possui autorização para visualizar os animais."
                    );
                }

                throw new Error("Não foi possível carregar os animais.");
            }

            const resultado = await resposta.json();

            if (!resultado.sucesso || !Array.isArray(resultado.dados)) {
                throw new Error("A resposta recebida pela API é inválida.");
            }

            animais = resultado.dados;

            renderizarAnimais(animais);

            elementos.total.textContent =
                `${animais.length} ${animais.length === 1 ? "animal" : "animais"}`;

            atualizarPaginacao(animais.length);

        } catch (erro) {
            mostrarEstadoVazio("Não foi possível carregar os registros.");

            mostrarFeedback(
                erro.message || "Erro de comunicação com o servidor.",
                "error"
            );

            elementos.total.textContent = "—";
            elementos.informacao.textContent = "Falha ao carregar registros.";
            elementos.anterior.disabled = true;
            elementos.proxima.disabled = true;

            console.error("Erro ao carregar animais:", erro);

        } finally {
            carregando = false;
        }
    }

    function limparFiltros() {
        elementos.identificacao.value = "";
        elementos.especie.value = "";
        elementos.situacao.value = "";

        deslocamento = 0;
        carregarAnimais();
    }

    function configurarEventos() {
        let temporizadorPesquisa;

        elementos.identificacao.addEventListener("input", () => {
            clearTimeout(temporizadorPesquisa);

            temporizadorPesquisa = setTimeout(() => {
                deslocamento = 0;
                carregarAnimais();
            }, 350);
        });

        elementos.especie.addEventListener("change", () => {
            deslocamento = 0;
            carregarAnimais();
        });

        elementos.situacao.addEventListener("change", () => {
            deslocamento = 0;
            carregarAnimais();
        });

        elementos.limpar.addEventListener("click", limparFiltros);

        elementos.anterior.addEventListener("click", () => {
            if (deslocamento >= LIMITE) {
                deslocamento -= LIMITE;
                carregarAnimais();
            }
        });

        elementos.proxima.addEventListener("click", () => {
            if (animais.length === LIMITE) {
                deslocamento += LIMITE;
                carregarAnimais();
            }
        });

        elementos.novo.addEventListener("click", () => {
            window.location.href = "/animais/novo";
        });
    }

    configurarEventos();
    carregarAnimais();
});
