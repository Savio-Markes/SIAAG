
/* =========================================
   SIAAG - GERENCIAMENTO DE USUÁRIOS
   ========================================= */

document.addEventListener("DOMContentLoaded", () => {
    const campoPesquisa = document.getElementById("campoPesquisa");
    const tabelaBody = document.getElementById("usersTableBody");

    const tabelaContainer = document.getElementById("usersTableContainer");
    const estadoVazio = document.getElementById("usersEmpty");
    const pesquisaVazia = document.getElementById("usersSearchEmpty");

    const carregamento = document.getElementById("usersLoading");
    const erro = document.getElementById("usersError");

    const botaoTentarNovamente =
        document.getElementById("btnTentarNovamente");

    let usuarios = [];

    function exibirEstado(estado) {
        carregamento.hidden = estado !== "loading";
        erro.hidden = estado !== "error";
        estadoVazio.hidden = estado !== "empty";
        pesquisaVazia.hidden = estado !== "search-empty";
        tabelaContainer.hidden = estado !== "table";
    }

    function usuarioEstaAtivo(valor) {
        return valor === true ||
            valor === 1 ||
            valor === "1" ||
            valor === "true";
    }

    function criarCelula(conteudo, classe = "") {
        const celula = document.createElement("td");

        if (classe) {
            celula.className = classe;
        }

        celula.textContent = conteudo ?? "—";

        return celula;
    }

    function criarSituacao(ativo) {
        const badge = document.createElement("span");

        badge.className = ativo
            ? "user-status user-status--active"
            : "user-status user-status--blocked";

        badge.textContent = ativo ? "Ativo" : "Inativo";

        return badge;
    }

    function renderizarUsuarios(lista) {
        tabelaBody.replaceChildren();

        lista.forEach((usuario) => {
            const linha = document.createElement("tr");

            linha.appendChild(
                criarCelula(usuario.nome, "user-name")
            );

            linha.appendChild(
                criarCelula(usuario.login, "user-login")
            );

            linha.appendChild(
                criarCelula(usuario.funcao_referencia)
            );

            const celulaSituacao = document.createElement("td");
            const ativo = usuarioEstaAtivo(usuario.ativo);

            celulaSituacao.appendChild(criarSituacao(ativo));
            linha.appendChild(celulaSituacao);

            const celulaAcoes = document.createElement("td");
            const grupoAcoes = document.createElement("div");

            grupoAcoes.className = "users-actions";

            const botaoEditar = document.createElement("button");
            botaoEditar.type = "button";
            botaoEditar.className = "users-action";
            botaoEditar.textContent = "Editar";
            botaoEditar.disabled = true;
            botaoEditar.title =
                "Aguardando implementação da rota de edição";

            const botaoPermissoes = document.createElement("button");
            botaoPermissoes.type = "button";
            botaoPermissoes.className = "users-action";
            botaoPermissoes.textContent = "Permissões";
            botaoPermissoes.disabled = true;
            botaoPermissoes.title =
                "Aguardando rota para exibir a página de permissões";

            grupoAcoes.append(botaoEditar, botaoPermissoes);
            celulaAcoes.appendChild(grupoAcoes);
            linha.appendChild(celulaAcoes);

            tabelaBody.appendChild(linha);
        });

        exibirEstado("table");
    }

    function pesquisarUsuarios() {
        const termo = campoPesquisa.value
            .trim()
            .toLocaleLowerCase("pt-BR");

        const filtrados = usuarios.filter((usuario) => {
            const nome = String(usuario.nome || "")
                .toLocaleLowerCase("pt-BR");

            const login = String(usuario.login || "")
                .toLocaleLowerCase("pt-BR");

            return nome.includes(termo) || login.includes(termo);
        });

        if (filtrados.length === 0) {
            tabelaBody.replaceChildren();

            exibirEstado(
                usuarios.length === 0 ? "empty" : "search-empty"
            );

            return;
        }

        renderizarUsuarios(filtrados);
    }

    async function atualizarLista() {
        exibirEstado("loading");
        tabelaBody.replaceChildren();

        try {
            const resposta = await fetch("/usuarios/", {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

            if (!resposta.ok) {
                throw new Error(
                    `Erro ao carregar usuários: ${resposta.status}`
                );
            }

            const dados = await resposta.json();

            if (!Array.isArray(dados.usuarios)) {
                throw new Error(
                    "Formato de resposta inválido."
                );
            }

            usuarios = dados.usuarios;

            if (usuarios.length === 0) {
                exibirEstado("empty");
                return;
            }

            pesquisarUsuarios();

        } catch (erroApi) {
            console.error(
                "Erro na listagem de usuários:",
                erroApi
            );

            usuarios = [];
            exibirEstado("error");
        }
    }

    campoPesquisa.addEventListener(
        "input",
        pesquisarUsuarios
    );

    botaoTentarNovamente.addEventListener(
        "click",
        atualizarLista
    );

    atualizarLista();
});
