
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
            "ATENÇÃO: a exclusão é definitiva.\n\n" +
            "O produto somente poderá ser removido se não possuir " +
            "lotes, movimentações ou vínculos com atividades e aulas.\n\n" +
            "Deseja continuar?"
        );

        if (!primeiraConfirmacao) return;

        const segundaConfirmacao = window.confirm(
            "Confirme novamente a exclusão definitiva deste produto."
        );

        if (!segundaConfirmacao) return;

        botaoExcluir.disabled = true;
        botaoExcluir.textContent = "Excluindo...";

        mostrarFeedback(
            "Verificando os vínculos e processando a exclusão...",
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
        400: "Não foi possível realizar a exclusão. Verifique os vínculos do produto.",
        401: "Sua sessão expirou. Faça login novamente.",
        403: "Você não tem permissão para excluir este produto.",
        404: "Produto não encontrado.",
        500: "Erro interno do servidor."
    };

    return mensagens[status] || "Ocorreu um erro inesperado.";
}
