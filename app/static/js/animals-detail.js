
document.addEventListener("DOMContentLoaded", () => {
    inicializarDetalhesAnimal();
});

function inicializarDetalhesAnimal() {
    const botaoInativar = document.getElementById("btnInativarAnimal");
    const feedback = document.getElementById("animalDetailFeedback");

    if (!botaoInativar) return;

    // Identifica o animal pelo endereço da página.
    const correspondencia = window.location.pathname.match(
        /^\/animais\/(\d+)\/painel\/?$/
    );

    if (!correspondencia) {
        botaoInativar.disabled = true;

        mostrarFeedback(
            "Não foi possível identificar o animal.",
            "error"
        );

        return;
    }

    const animalId = correspondencia[1];

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
            const resposta = await fetch(
                `/animais/${encodeURIComponent(animalId)}/inativar`,
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
                    resultado.erro ||
                    interpretarErro(resposta.status)
                );
            }

            mostrarFeedback(
                resultado.mensagem || "Animal inativado com sucesso!",
                "success"
            );

            botaoInativar.textContent = "Animal inativado";

            // Retorna à listagem após a confirmação do servidor.
            window.setTimeout(() => {
                window.location.href = "/animais/painel";
            }, 1200);

        } catch (erro) {
            mostrarFeedback(
                erro.message || "Não foi possível inativar o animal.",
                "error"
            );

            botaoInativar.disabled = false;
            botaoInativar.textContent = "Inativar animal";
        }
    });

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

function interpretarErro(status) {
    const mensagens = {
        400: "Não foi possível realizar a inativação.",
        401: "Sua sessão expirou. Faça login novamente.",
        403: "Você não tem permissão para inativar animais.",
        404: "Animal não encontrado.",
        409: "Este animal já está inativado.",
        500: "Erro interno do servidor."
    };

    return mensagens[status] ||
        "Ocorreu um erro inesperado ao inativar o animal.";
}
