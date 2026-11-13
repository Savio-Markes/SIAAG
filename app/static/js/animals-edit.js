document.addEventListener("DOMContentLoaded", () => {
    inicializarEdicaoAnimal();
});

function inicializarEdicaoAnimal() {
    const formulario = document.getElementById("editAnimalForm");

    if (!formulario) return;

    const botaoSalvar = document.getElementById("btnSalvarEdicao");
    const feedback = document.getElementById("editAnimalFeedback");
    const animalId = document.getElementById("animalId")?.value;

    if (!animalId) {
        mostrarFeedback("Não foi possível identificar o animal.", "erro");
        botaoSalvar.disabled = true;
        return;
    }

    const campoNascimento = document.getElementById("nascimento");

    if (campoNascimento) {
        campoNascimento.max = new Date().toISOString().split("T")[0];
    }

    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!formulario.checkValidity()) {
            formulario.reportValidity();
            return;
        }

        const dados = {
            identificacao: obterValor("identificacao"),
            nome: obterValor("nome"),
            especie: obterValor("especie"),
            raca: obterValor("raca"),
            sexo: obterValor("sexo"),
            nascimento: obterValor("nascimento"),
            origem: obterValor("origem"),
            data_entrada: obterValor("data_entrada"),
            localizacao: obterValor("localizacao"),
            situacao: obterValor("situacao"),
            observacoes: obterValor("observacoes")
        };

        if (!dados.identificacao || !dados.especie || !dados.situacao) {
            mostrarFeedback(
                "Preencha os campos obrigatórios: identificação, espécie e situação.",
                "erro"
            );
            return;
        }

        if (dados.nascimento && dados.nascimento > hojeLocal()) {
            mostrarFeedback(
                "A data de nascimento não pode ser futura.",
                "erro"
            );
            return;
        }

        botaoSalvar.disabled = true;
        botaoSalvar.textContent = "Salvando...";

        mostrarFeedback("Atualizando cadastro do animal...", "carregando");

        try {
            const resposta = await fetch(
                `/animais/${encodeURIComponent(animalId)}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    credentials: "same-origin",
                    body: JSON.stringify(dados)
                }
            );

            const resultado = await resposta.json().catch(() => ({}));

            if (!resposta.ok || resultado.sucesso === false) {
                const mensagem =
                    resultado.mensagem ||
                    resultado.erro ||
                    interpretarErro(resposta.status);

                throw new Error(mensagem);
            }

            mostrarFeedback(
                resultado.mensagem || "Animal atualizado com sucesso!",
                "sucesso"
            );

            setTimeout(() => {
                window.location.href = `/animais/${encodeURIComponent(animalId)}/painel`;
            }, 1200);

        } catch (erro) {
            mostrarFeedback(
                erro.message || "Não foi possível atualizar o animal.",
                "erro"
            );

            botaoSalvar.disabled = false;
            botaoSalvar.textContent = "Salvar alterações";
        }
    });

    function obterValor(nome) {
        const campo = formulario.elements.namedItem(nome);
        return campo ? campo.value.trim() : "";
    }

    function mostrarFeedback(mensagem, tipo) {
        feedback.textContent = mensagem;
        feedback.className = `animals-feedback ${tipo}`;
    }
}

function hojeLocal() {
    const agora = new Date();
    const ano = agora.getFullYear();
    const mes = String(agora.getMonth() + 1).padStart(2, "0");
    const dia = String(agora.getDate()).padStart(2, "0");

    return `${ano}-${mes}-${dia}`;
}

function interpretarErro(status) {
    const mensagens = {
        400: "Os dados enviados são inválidos. Confira os campos.",
        401: "Sua sessão expirou. Faça login novamente.",
        403: "Você não tem permissão para editar animais.",
        404: "Animal não encontrado.",
        409: "Já existe um animal com essa identificação.",
        500: "Erro interno do servidor."
    };

    return mensagens[status] || "Ocorreu um erro ao atualizar o cadastro.";
}