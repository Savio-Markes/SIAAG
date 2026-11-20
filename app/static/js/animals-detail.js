
document.addEventListener("DOMContentLoaded", () => {
    inicializarDetalhesAnimal();
});

function inicializarDetalhesAnimal() {
    const botaoInativar = document.getElementById("btnInativarAnimal");
    const botaoExcluir = document.getElementById("btnExcluirAnimal");
    const feedback = document.getElementById("animalDetailFeedback");

    const correspondencia = window.location.pathname.match(
        /^\/animais\/(\d+)\/painel\/?$/
    );

    if (!correspondencia) {
        if (botaoInativar) botaoInativar.disabled = true;
        if (botaoExcluir) botaoExcluir.disabled = true;

        mostrarFeedback(
            "Não foi possível identificar o animal.",
            "error"
        );

        return;
    }

    const animalId = correspondencia[1];

    // INATIVAÇÃO
    if (botaoInativar) {
        botaoInativar.addEventListener("click", async () => {
            const confirmou = window.confirm(
                "Deseja realmente inativar este animal?\n\n" +
                "O cadastro e todo o histórico serão preservados."
            );

            if (!confirmou) return;

            botaoInativar.disabled = true;
            botaoInativar.textContent = "Inativando...";

            mostrarFeedback(
                "Processando a solicitação...",
                "info"
            );

            try {
                const resultado = await enviarAcao("inativar");

                mostrarFeedback(
                    resultado.mensagem || "Animal inativado com sucesso!",
                    "success"
                );

                botaoInativar.textContent = "Animal inativado";

                window.setTimeout(() => {
                    window.location.href = "/animais/painel";
                }, 1200);

            } catch (erro) {
                mostrarFeedback(erro.message, "error");

                botaoInativar.disabled = false;
                botaoInativar.textContent = "Inativar animal";
            }
        });
    }

    // EXCLUSÃO DEFINITIVA
    if (botaoExcluir) {
        botaoExcluir.addEventListener("click", async () => {
            const primeiraConfirmacao = window.confirm(
                "ATENÇÃO: a exclusão é definitiva.\n\n" +
                "O cadastro só poderá ser removido se não possuir " +
                "nenhum registro histórico vinculado.\n\n" +
                "Deseja continuar?"
            );

            if (!primeiraConfirmacao) return;

            const segundaConfirmacao = window.confirm(
                "Confirme novamente a exclusão definitiva deste animal."
            );

            if (!segundaConfirmacao) return;

            botaoExcluir.disabled = true;
            botaoExcluir.textContent = "Verificando histórico...";

            mostrarFeedback(
                "Verificando os vínculos e processando a exclusão...",
                "info"
            );

            try {
                const resultado = await enviarAcao("excluir");

                mostrarFeedback(
                    resultado.mensagem || "Animal excluído com sucesso!",
                    "success"
                );

                botaoExcluir.textContent = "Animal excluído";

                window.setTimeout(() => {
                    window.location.href = "/animais/painel";
                }, 1200);

            } catch (erro) {
                mostrarFeedback(erro.message, "error");

                botaoExcluir.disabled = false;
                botaoExcluir.textContent = "Excluir animal";
            }
        });
    }

    // REQUISIÇÃO AO BACKEND
    async function enviarAcao(acao) {
        const resposta = await fetch(
            `/animais/${encodeURIComponent(animalId)}/${acao}`,
            {
                method: "POST",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            }
        );

        const resultado = await resposta.json().catch(() => ({}));

        if (!resposta.ok || resultado.sucesso !== true) {
            throw new Error(
                resultado.mensagem ||
                interpretarErro(resposta.status, acao)
            );
        }

        return resultado;
    }

    // FEEDBACK VISUAL
    function mostrarFeedback(mensagem, tipo) {
        if (!feedback) {
            window.alert(mensagem);
            return;
        }

        feedback.textContent = mensagem;
        feedback.className = `animal-detail-feedback ${tipo}`;
        feedback.hidden = false;
    }
}

// TRATAMENTO DE ERROS HTTP
function interpretarErro(status, acao) {
    if (acao === "excluir" && status === 409) {
        return (
            "Exclusão bloqueada: o animal possui histórico vinculado. " +
            "O cadastro foi preservado."
        );
    }

    const mensagens = {
        400: "Não foi possível realizar a operação.",
        401: "Sua sessão expirou. Faça login novamente.",
        403: "Você não tem permissão para realizar esta operação.",
        404: "Animal não encontrado.",
        500: "Erro interno do servidor."
    };

    return mensagens[status] ||
        "Ocorreu um erro inesperado.";
}
