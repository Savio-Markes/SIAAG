document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const API_URL = "/animais/";
    const LIMITE = 50;

    const elementos = {
        filtroIdentificacao: document.getElementById("filtroIdentificacao"),
        filtroEspecie: document.getElementById("filtroEspecie"),
        filtroSituacao: document.getElementById("filtroSituacao"),
        filtroAtivo: document.getElementById("filtroAtivo"),
        feedback: document.getElementById("animalsFeedback"),
        contador: document.getElementById("totalAnimais"),
        tabela: document.getElementById("animalsTableBody"),
        informacaoPaginacao: document.getElementById("paginationInfo"),
        paginaAtual: document.getElementById("paginaAtual"),
        anterior: document.getElementById("btnPaginaAnterior"),
        proxima: document.getElementById("btnProximaPagina"),
        limpar: document.getElementById("btnLimparFiltros"),
        novoAnimal: document.getElementById("btnNovoAnimal"),
        kpiTotal: document.getElementById("kpiTotalAnimais"),
        kpiAtivos: document.getElementById("kpiAnimaisAtivos"),
        kpiInativos: document.getElementById("kpiAnimaisInativos"),
        graficoEspecies: document.getElementById("graficoEspecies"),
        graficoSituacoes: document.getElementById("graficoSituacoes")
    };

    let pagina = 1;
    let totalRegistros = 0;
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

        celula.colSpan = 7;
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

    function obterIconeEspecie(especie) {
        const nome = String(especie || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();

        if (/bovino|boi|vaca/.test(nome)) return "🐄";
        if (/ovino|ovelha|carneiro/.test(nome)) return "🐑";
        if (/caprino|cabra|bode/.test(nome)) return "🐐";
        if (/suino|porco|leitao/.test(nome)) return "🐖";
        if (/equino|cavalo|egua/.test(nome)) return "🐎";
        if (/asinino|jumento|burro|mula/.test(nome)) return "🫏";
        if (/ave|galinha|frango|galo|pato/.test(nome)) return "🐔";

        return "🐾";
    }

    function criarIdentificacao(animal) {
        const celula = document.createElement("td");

        const container = document.createElement("div");
        container.className = "animal-identification";

        const icone = document.createElement("span");
        icone.className = "animal-species-icon";
        icone.setAttribute("aria-hidden", "true");
        icone.textContent = obterIconeEspecie(animal.especie);

        const textos = document.createElement("div");
        textos.className = "animal-identification-text";

        const identificacao = document.createElement("strong");
        identificacao.textContent =
            animal.identificacao || "Sem identificação";

        const nome = document.createElement("span");
        nome.textContent = animal.nome || "Nome não informado";

        textos.append(identificacao, nome);
        container.append(icone, textos);
        celula.appendChild(container);

        return celula;
    }

    function criarStatus(animal) {
        const celula = document.createElement("td");
        const badge = document.createElement("span");
        const ativo = Number(animal.ativo) === 1;

        badge.className = ativo
            ? "animal-status-badge"
            : "animal-status-badge inactive";

        badge.textContent = ativo ? "Ativo" : "Inativo";
        celula.appendChild(badge);

        return celula;
    }

    function renderizarGrafico(container, dados, classe = "") {
        container.replaceChildren();

        if (!Array.isArray(dados) || dados.length === 0) {
            const vazio = document.createElement("div");
            vazio.className = "animals-chart-empty";
            vazio.textContent = "Não há registros para este gráfico.";
            container.appendChild(vazio);
            return;
        }

        const maior = Math.max(
            ...dados.map(item => Number(item.total) || 0),
            1
        );

        dados.forEach(item => {
            const total = Number(item.total) || 0;

            const linha = document.createElement("div");
            linha.className = "animals-chart-row";

            const nome = document.createElement("span");
            nome.className = "animals-chart-label";
            nome.textContent = item.especie || item.situacao || "Não informado";

            const trilho = document.createElement("div");
            trilho.className = "animals-chart-track";

            const barra = document.createElement("div");
            barra.className = `animals-chart-fill ${classe}`;
            barra.style.width = `${(total / maior) * 100}%`;

            trilho.appendChild(barra);

            const valor = document.createElement("span");
            valor.className = "animals-chart-value";
            valor.textContent = String(total);

            linha.append(nome, trilho, valor);
            container.appendChild(linha);
        });
    }

    function atualizarIndicadores(indicadores) {
        if (!indicadores) return;

        elementos.kpiTotal.textContent = indicadores.total ?? 0;
        elementos.kpiAtivos.textContent = indicadores.ativos ?? 0;
        elementos.kpiInativos.textContent = indicadores.inativos ?? 0;

        renderizarGrafico(
            elementos.graficoEspecies,
            indicadores.especies
        );

        renderizarGrafico(
            elementos.graficoSituacoes,
            indicadores.situacoes,
            "active"
        );
    }

    async function alterarStatus(animal, acao, botao) {
        const reativando = acao === "reativar";

        const mensagem = reativando
            ? `Deseja reativar o animal ${animal.identificacao}?`
            : `Deseja inativar o animal ${animal.identificacao}?`;

        if (!window.confirm(mensagem)) return;

        botao.disabled = true;

        try {
            const resposta = await fetch(
                `${API_URL}${encodeURIComponent(animal.id)}/${acao}`,
                {
                    method: "POST",
                    headers: { "Accept": "application/json" },
                    credentials: "same-origin"
                }
            );

            const resultado = await resposta.json();

            if (!resposta.ok || resultado.sucesso !== true) {
                throw new Error(
                    resultado.mensagem || "Não foi possível alterar o status."
                );
            }

            await carregarAnimais();
            mostrarFeedback(resultado.mensagem, "success");

        } catch (erro) {
            mostrarFeedback(
                erro.message || "Erro ao alterar o status do animal.",
                "error"
            );
            botao.disabled = false;
        }
    }

    function criarAcao(animal) {
        const celula = document.createElement("td");

        const link = document.createElement("a");
        link.href = `/animais/${encodeURIComponent(animal.id)}/painel`;
        link.className = "btn-action";
        link.textContent = "Abrir ficha";

        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "btn-action btn-status";

        const ativo = Number(animal.ativo) === 1;
        const acao = ativo ? "inativar" : "reativar";

        botao.textContent = ativo ? "Inativar" : "Reativar";
        botao.setAttribute(
            "aria-label",
            `${acao} animal ${animal.identificacao || animal.id}`
        );

        botao.addEventListener("click", () => {
            alterarStatus(animal, acao, botao);
        });

        celula.append(link, botao);
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

            linha.appendChild(criarIdentificacao(animal));
            linha.appendChild(criarCelula(animal.especie));
            linha.appendChild(criarCelula(animal.raca));
            linha.appendChild(
                criarCelula(formatarSituacao(animal.situacao))
            );
            linha.appendChild(criarCelula(animal.localizacao));
            linha.appendChild(criarStatus(animal));
            linha.appendChild(criarAcao(animal));

            fragmento.appendChild(linha);
        });

        elementos.tabela.appendChild(fragmento);
    }

    function atualizarPaginacao(quantidade) {
        const totalPaginas = Math.max(
            1,
            Math.ceil(totalRegistros / LIMITE)
        );

        elementos.paginaAtual.textContent = String(pagina);

        elementos.informacaoPaginacao.textContent =
            `${totalRegistros} registro(s) encontrado(s)`;

        elementos.contador.textContent =
            `${totalRegistros} registro(s)`;

        elementos.anterior.disabled = pagina <= 1;
        elementos.proxima.disabled = pagina >= totalPaginas;

        if (quantidade === 0) {
            elementos.informacaoPaginacao.textContent =
                "Nenhum registro encontrado";
        }
    }

    function obterFiltros() {
        return {
            identificacao: elementos.filtroIdentificacao.value.trim(),
            especie: elementos.filtroEspecie.value.trim(),
            situacao: elementos.filtroSituacao.value.trim(),
            ativo: elementos.filtroAtivo.value
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

        if (filtros.ativo !== "") {
            parametros.set("ativo", filtros.ativo);
        }

        parametros.set("limite", String(LIMITE));
        parametros.set(
            "deslocamento",
            String((pagina - 1) * LIMITE)
        );

        try {
            const resposta = await fetch(
                `${API_URL}?${parametros.toString()}`,
                {
                    method: "GET",
                    headers: { "Accept": "application/json" },
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
                throw new Error("Sua sessão expirou. Entre novamente.");
            }

            if (resposta.status === 403) {
                throw new Error(
                    "Você não tem permissão para visualizar os animais."
                );
            }

            if (!resposta.ok || resultado.sucesso !== true) {
                throw new Error(
                    resultado.mensagem || "Não foi possível carregar os animais."
                );
            }

            if (!Array.isArray(resultado.dados)) {
                throw new Error("O formato dos dados recebidos é inválido.");
            }

            totalRegistros = Number(resultado.total) || 0;

            renderizarAnimais(resultado.dados);
            atualizarPaginacao(resultado.dados.length);
            atualizarIndicadores(resultado.indicadores);

        } catch (erro) {
            console.error("Erro ao carregar animais:", erro);

            criarLinhaVazia("Não foi possível carregar os registros.");
            elementos.contador.textContent = "Indisponível";
            elementos.informacaoPaginacao.textContent = "Falha ao carregar";
            elementos.paginaAtual.textContent = String(pagina);

            elementos.anterior.disabled = true;
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
        elementos.filtroAtivo.value = "";

        pagina = 1;
        carregarAnimais();
    }

    elementos.novoAnimal.addEventListener("click", () => {
        window.location.href = "/animais/novo";
    });

    elementos.filtroIdentificacao.addEventListener("input", () => {
        clearTimeout(temporizadorBusca);
        temporizadorBusca = setTimeout(aplicarFiltros, 350);
    });

    elementos.filtroEspecie.addEventListener("input", () => {
        clearTimeout(temporizadorBusca);
        temporizadorBusca = setTimeout(aplicarFiltros, 350);
    });

    elementos.filtroSituacao.addEventListener("input", () => {
        clearTimeout(temporizadorBusca);
        temporizadorBusca = setTimeout(aplicarFiltros, 350);
    });

    elementos.filtroAtivo.addEventListener("change", aplicarFiltros);
    elementos.limpar.addEventListener("click", limparFiltros);

    elementos.anterior.addEventListener("click", () => {
        if (pagina > 1 && !carregando) {
            pagina--;
            carregarAnimais();
        }
    });

    elementos.proxima.addEventListener("click", () => {
        const totalPaginas = Math.ceil(totalRegistros / LIMITE);

        if (!carregando && pagina < totalPaginas) {
            pagina++;
            carregarAnimais();
        }
    });

    carregarAnimais();
});