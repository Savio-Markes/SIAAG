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
            "Todos os registros vinculados a este produto também serão " +
            "removidos, incluindo lotes, movimentações, registros de " +
            "atividades e recursos de aulas.\n\n" +
            "O registro da exclusão permanecerá no histórico de auditoria.\n\n" +
            "Deseja realmente continuar?"
        );

        if (!primeiraConfirmacao) return;

        const segundaConfirmacao = window.confirm(
            "ÚLTIMA CONFIRMAÇÃO!\n\n" +
            "Esta operação não poderá ser desfeita.\n\n" +
            "Confirma a exclusão definitiva do produto?"
        );

        if (!segundaConfirmacao) return;

        botaoExcluir.disabled = true;
        botaoExcluir.textContent = "Excluindo...";

        mostrarFeedback(
            "Removendo o produto e seus registros relacionados...",
            "info"
        );

        try {
            const resposta = await fetch(excluirUrl, {
                method: "POST",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
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
        400: "Não foi possível realizar a exclusão. Verifique os dados do produto.",
        401: "Sua sessão expirou. Faça login novamente.",
        403: "Você não tem permissão para excluir este produto.",
        404: "Produto não encontrado.",
        500: "Erro interno do servidor."
    };

    return mensagens[status] || "Ocorreu um erro inesperado.";
}