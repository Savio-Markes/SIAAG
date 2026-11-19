
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const API_URL = "/animais/";
    const LIMITE = 50;

    const elementos = {
        filtroIdentificacao: document.getElementById("filtroIdentificacao"),
        filtroEspecie: document.getElementById("filtroEspecie"),
        filtroSituacao: document.getElementById("filtroSituacao"),
        feedback: document.getElementById("animalsFeedback"),
        contador: document.getElementById("totalAnimais"),
        tabela: document.getElementById("animalsTableBody"),
        informacaoPaginacao: document.getElementById("paginationInfo"),
        paginaAtual: document.getElementById("paginaAtual"),
        anterior: document.getElementById("btnPaginaAnterior"),
        proxima: document.getElementById("btnProximaPagina"),
        limpar: document.getElementById("btnLimparFiltros"),
        novoAnimal: document.getElementById("btnNovoAnimal")
    };

    let pagina = 1;
    let carregando = false;
    let temporizadorBusca = null;

    function mostrarFeedback(mensagem, tipo = "info") {
        elementos.feedback.textContent = mensagem;
        elementos.feedback.className = `animals-feedback ${tipo}`;
        elementos.feedback.hidden = false;
    }

    function ocultarFeedback() {
        elementos.feedback.hidden = true;
        elementos.feedback.textContent = "";
    }

    function criarCelula(valor) {
        const celula = document.createElement("td");
        celula.textContent = valor || "—";
        return celula;
    }

    function criarLinhaVazia(mensagem) {
        const linha = document.createElement("tr");
        const celula = document.createElement("td");

        celula.colSpan = 6;
        celula.className = "animals-loading";
        celula.textContent = mensagem;

        linha.appendChild(celula);
        elementos.tabela.replaceChildren(linha);
    }

    function formatarSituacao(situacao) {
        if (!situacao) return "—";

        return String(situacao)
            .replace(/_/g, " ")
            .replace(/\b\w/g, letra => letra.toUpperCase());
    }

    function criarAcao(animal) {
        const celula = document.createElement("td");
        const link = document.createElement("a");

        link.href = `/animais/${encodeURIComponent(animal.id)}/painel`;
        link.className = "btn-action";
        link.textContent = "Abrir ficha";
        link.setAttribute(
            "aria-label",
            `Abrir ficha do animal ${animal.identificacao || animal.id}`
        );

        celula.appendChild(link);
        return celula;
    }

    function renderizarAnimais(animais) {
        elementos.tabela.replaceChildren();

        if (!animais.length) {
            criarLinhaVazia("Nenhum animal encontrado.");
            return;
        }

        const fragmento = document.createDocumentFragment();

        animais.forEach(animal => {
            const linha = document.createElement("tr");

            const identificacao = animal.nome
                ? `${animal.identificacao || "—"} — ${animal.nome}`
                : animal.identificacao || "—";

            linha.appendChild(criarCelula(identificacao));
            linha.appendChild(criarCelula(animal.especie));
            linha.appendChild(criarCelula(animal.raca));
            linha.appendChild(criarCelula(formatarSituacao(animal.situacao)));
            linha.appendChild(criarCelula(animal.localizacao));
            linha.appendChild(criarAcao(animal));

            fragmento.appendChild(linha);
        });

        elementos.tabela.appendChild(fragmento);
    }

    function atualizarPaginacao(quantidade) {
        elementos.paginaAtual.textContent = String(pagina);

        elementos.informacaoPaginacao.textContent =
            `${quantidade} animal(is) nesta página`;

        elementos.contador.textContent =
            `${quantidade} nesta página`;

        elementos.anterior.disabled = pagina <= 1;
        elementos.proxima.disabled = quantidade < LIMITE;
    }

    function obterFiltros() {
        return {
            identificacao: elementos.filtroIdentificacao.value.trim(),
            especie: elementos.filtroEspecie.value,
            situacao: elementos.filtroSituacao.value
        };
    }

    async function carregarAnimais() {
        if (carregando) return;

        carregando = true;
        elementos.anterior.disabled = true;
        elementos.proxima.disabled = true;

        ocultarFeedback();
        criarLinhaVazia("Carregando animais...");

        const filtros = obterFiltros();
        const parametros = new URLSearchParams();

        if (filtros.identificacao) {
            parametros.set("identificacao", filtros.identificacao);
        }

        if (filtros.especie) {
            parametros.set("especie", filtros.especie);
        }

        if (filtros.situacao) {
            parametros.set("situacao", filtros.situacao);
        }

        parametros.set("limite", String(LIMITE));
        parametros.set("deslocamento", String((pagina - 1) * LIMITE));

        try {
            const resposta = await fetch(
                `${API_URL}?${parametros.toString()}`,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );

            let resultado = {};

            try {
                resultado = await resposta.json();
            } catch {
                throw new Error("O servidor retornou uma resposta inválida.");
            }

            if (resposta.status === 401) {
                throw new Error("Sua sessão expirou. Entre novamente no sistema.");
            }

            if (resposta.status === 403) {
                throw new Error("Você não tem permissão para visualizar os animais.");
            }

            if (!resposta.ok || resultado.sucesso !== true) {
                throw new Error(
                    resultado.mensagem ||
                    resultado.erro ||
                    "Não foi possível carregar os animais."
                );
            }

            if (!Array.isArray(resultado.dados)) {
                throw new Error("O formato dos dados recebidos é inválido.");
            }

            renderizarAnimais(resultado.dados);
            atualizarPaginacao(resultado.dados.length);

        } catch (erro) {
            console.error("Erro ao carregar animais:", erro);

            criarLinhaVazia("Não foi possível carregar os registros.");
            elementos.contador.textContent = "Indisponível";
            elementos.informacaoPaginacao.textContent = "Falha ao carregar";
            elementos.paginaAtual.textContent = String(pagina);

            elementos.anterior.disabled = pagina <= 1;
            elementos.proxima.disabled = true;

            mostrarFeedback(
                erro.message || "Ocorreu um erro inesperado.",
                "error"
            );

        } finally {
            carregando = false;
        }
    }

    function aplicarFiltros() {
        pagina = 1;
        carregarAnimais();
    }

    function limparFiltros() {
        elementos.filtroIdentificacao.value = "";
        elementos.filtroEspecie.value = "";
        elementos.filtroSituacao.value = "";

        pagina = 1;
        carregarAnimais();
    }

    elementos.novoAnimal.addEventListener("click", () => {
        window.location.href = "/animais/novo";
    });

    elementos.filtroIdentificacao.addEventListener("input", () => {
        clearTimeout(temporizadorBusca);

        temporizadorBusca = setTimeout(() => {
            aplicarFiltros();
        }, 350);
    });

    elementos.filtroEspecie.addEventListener("change", aplicarFiltros);
    elementos.filtroSituacao.addEventListener("change", aplicarFiltros);

    elementos.limpar.addEventListener("click", limparFiltros);

    elementos.anterior.addEventListener("click", () => {
        if (pagina > 1 && !carregando) {
            pagina--;
            carregarAnimais();
        }
    });

    elementos.proxima.addEventListener("click", () => {
        if (!carregando && elementos.proxima.disabled === false) {
            pagina++;
            carregarAnimais();
        }
    });

    carregarAnimais();
});
