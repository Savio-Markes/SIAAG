
/* =========================================
   SIAAG - GERENCIAMENTO DE USUÁRIOS
   ========================================= */

document.addEventListener("DOMContentLoaded", () => {
    // Elementos da página
    const campoPesquisa = document.getElementById("campoPesquisa");
    const tabelaBody = document.getElementById("usersTableBody");

    const tabelaContainer = document.getElementById("usersTableContainer");
    const estadoVazio = document.getElementById("usersEmpty");
    const pesquisaVazia = document.getElementById("usersSearchEmpty");

    const carregamento = document.getElementById("usersLoading");
    const erro = document.getElementById("usersError");

    const botaoNovoUsuario = document.getElementById("btnNovoUsuario");
    const botaoTentarNovamente = document.getElementById("btnTentarNovamente");

    // Estado inicial
    let usuarios = [];

    /**
     * Controla a exibição dos estados da página.
     */
    function exibirEstado(estado) {
        carregamento.hidden = estado !== "loading";
        erro.hidden = estado !== "error";
        estadoVazio.hidden = estado !== "empty";
        pesquisaVazia.hidden = estado !== "search-empty";
        tabelaContainer.hidden = estado !== "table";
    }

    /**
     * Pesquisa usuários pelo nome ou login.
     */
    function pesquisarUsuarios() {
        const termo = campoPesquisa.value
            .trim()
            .toLocaleLowerCase("pt-BR");

        const usuariosFiltrados = usuarios.filter((usuario) => {
            const nome = String(usuario.nome || "").toLocaleLowerCase("pt-BR");
            const login = String(usuario.login || "").toLocaleLowerCase("pt-BR");

            return nome.includes(termo) || login.includes(termo);
        });

        if (usuariosFiltrados.length === 0) {
            if (usuarios.length === 0) {
                exibirEstado("empty");
            } else {
                exibirEstado("search-empty");
            }

            return;
        }

        renderizarUsuarios(usuariosFiltrados);
    }

    /**
     * Cria um elemento de situação do usuário.
     */
    function criarSituacao(situacao) {
        const ativo = situacao === "ativo";

        const badge = document.createElement("span");

        badge.className = ativo
            ? "user-status user-status--active"
            : "user-status user-status--blocked";

        badge.textContent = ativo ? "Ativo" : "Bloqueado";

        return badge;
    }

    /**
     * Cria uma célula da tabela com texto seguro.
     */
    function criarCelula(conteudo, classe = "") {
        const celula = document.createElement("td");

        if (classe) {
            celula.className = classe;
        }

        celula.textContent = conteudo || "—";

        return celula;
    }

    /**
     * Renderiza os usuários recebidos.
     *
     * A estrutura esperada aqui é provisória:
     * {
     *   nome: "Nome",
     *   login: "login",
     *   funcao: "Função",
     *   situacao: "ativo" ou "bloqueado"
     * }
     *
     * A integração definitiva dependerá do contrato
     * de resposta confirmado pelo backend.
     */
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
                criarCelula(usuario.funcao)
            );

            const celulaSituacao = document.createElement("td");

            const situacao = String(usuario.situacao || "").toLowerCase();

            celulaSituacao.appendChild(
                criarSituacao(situacao)
            );

            linha.appendChild(celulaSituacao);

            const celulaAcoes = document.createElement("td");
            const grupoAcoes = document.createElement("div");

            grupoAcoes.className = "users-actions";

            const botaoEditar = document.createElement("button");
            botaoEditar.type = "button";
            botaoEditar.className = "users-action";
            botaoEditar.textContent = "Editar";
            botaoEditar.disabled = true;
            botaoEditar.title = "Aguardando rota de edição";

            const botaoPermissoes = document.createElement("button");
            botaoPermissoes.type = "button";
            botaoPermissoes.className = "users-action";
            botaoPermissoes.textContent = "Permissões";
            botaoPermissoes.disabled = true;
            botaoPermissoes.title = "Aguardando integração de permissões";

            grupoAcoes.appendChild(botaoEditar);
            grupoAcoes.appendChild(botaoPermissoes);

            celulaAcoes.appendChild(grupoAcoes);
            linha.appendChild(celulaAcoes);

            tabelaBody.appendChild(linha);
        });

        exibirEstado("table");
    }

    /**
     * Atualiza os dados da listagem.
     *
     * Não realiza requisição ao backend ainda.
     * A rota GET /usuarios e seu formato de resposta
     * precisam ser confirmados antes da integração.
     */
    function atualizarLista() {
        exibirEstado("loading");

        // Enquanto não existe contrato confirmado,
        // não enviamos requisições para rotas inexistentes.
        usuarios = [];

        tabelaBody.replaceChildren();

        exibirEstado("empty");
    }

    // Eventos
    campoPesquisa.addEventListener("input", pesquisarUsuarios);

    botaoTentarNovamente.addEventListener("click", atualizarLista);

    // O cadastro ainda depende da rota do backend.
    botaoNovoUsuario.addEventListener("click", () => {
        return;
    });

    // Inicialização
    atualizarLista();
});
