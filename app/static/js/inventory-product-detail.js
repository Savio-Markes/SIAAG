document.addEventListener("DOMContentLoaded", () => {
    inicializarDetalhesProduto();
});

function inicializarDetalhesProduto() {
    const botaoExcluir = document.getElementById("btnExcluirProduto");
    const feedback = document.getElementById("productDetailFeedback");

    if (!botaoExcluir) return;

    const excluirUrl = botaoExcluir.dataset.excluirUrl;
    const redirectUrl = botaoExcluir.dataset.redirectUrl;

    if (!excluirUrl || !redirectUrl) {
        botaoExcluir.disabled = true;

        mostrarFeedback(
            "Não foi possível identificar os dados da exclusão.",
            "error"
        );

        return;
    }

    botaoExcluir.addEventListener("click", async () => {
        const primeiraConfirmacao = window.confirm(
            "ATENÇÃO: a exclusão é DEFINITIVA.\n\n" +
            "O cadastro do produto e seus lotes serão excluídos.\n\n" +
            "Os históricos de movimentações, atividades e aulas práticas " +
            "serão preservados, mas deixarão de estar vinculados ao produto.\n\n" +
            "Deseja continuar?"
        );

        if (!primeiraConfirmacao) return;

        const justificativa = window.prompt(
            "Informe a justificativa da exclusão (obrigatória, até 500 caracteres):"
        );

        if (justificativa === null) return;

        const justificativaLimpa = justificativa.trim();

        if (!justificativaLimpa) {
            mostrarFeedback(
                "A justificativa da exclusão é obrigatória.",
                "error"
            );
            return;
        }

        if (justificativaLimpa.length > 500) {
            mostrarFeedback(
                "A justificativa deve ter no máximo 500 caracteres.",
                "error"
            );
            return;
        }

        const segundaConfirmacao = window.confirm(
            "ÚLTIMA CONFIRMAÇÃO!\n\n" +
            "A exclusão não poderá ser desfeita.\n" +
            "A justificativa será registrada no histórico.\n\n" +
            "Confirma a exclusão definitiva do produto?"
        );

        if (!segundaConfirmacao) return;

        botaoExcluir.disabled = true;
        botaoExcluir.textContent = "Excluindo...";

        mostrarFeedback(
            "Registrando a exclusão e preservando os históricos...",
            "info"
        );

        try {
            const resposta = await fetch(excluirUrl, {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    justificativa: justificativaLimpa
                })
            });

            const resultado = await resposta.json().catch(() => ({}));

            if (!resposta.ok || resultado.sucesso !== true) {
                throw new Error(
                    resultado.mensagem ||
                    interpretarErro(resposta.status)
                );
            }

            mostrarFeedback(
                resultado.mensagem || "Produto excluído com sucesso!",
                "success"
            );

            botaoExcluir.textContent = "Produto excluído";

            window.setTimeout(() => {
                window.location.href =
                    resultado.redirecionamento || redirectUrl;
            }, 1000);

        } catch (erro) {
            mostrarFeedback(erro.message, "error");

            botaoExcluir.disabled = false;
            botaoExcluir.textContent = "Excluir produto";
        }
    });

    function mostrarFeedback(mensagem, tipo) {
        if (!feedback) {
            window.alert(mensagem);
            return;
        }

        feedback.textContent = mensagem;
        feedback.className = `product-detail-feedback ${tipo}`;
        feedback.hidden = false;
    }
}

function interpretarErro(status) {
    const mensagens = {
        400: "Não foi possível realizar a exclusão. Verifique os dados informados.",
        401: "Sua sessão expirou. Faça login novamente.",
        403: "Você não tem permissão para excluir este produto.",
        404: "Produto não encontrado.",
        500: "Erro interno do servidor."
    };

    return mensagens[status] || "Ocorreu um erro inesperado.";
}