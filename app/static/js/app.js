
// SIAAG - Validação dos formulários
// Etapa de testes: sem comunicação com o banco de dados.

document.addEventListener("DOMContentLoaded", () => {
    inicializarLogin();
    inicializarCadastroAnimal();
    inicializarCadastroPatrimonio();
    inicializarCancelamentos();

    console.log("SIAAG: JavaScript carregado com sucesso.");
});


// FUNÇÕES AUXILIARES

function mostrarFeedback(elemento, mensagem, tipo) {
    if (!elemento) {
        console.error("Elemento de feedback não encontrado.");
        return;
    }

    elemento.textContent = mensagem;
    elemento.hidden = false;
    elemento.setAttribute("role", tipo === "erro" ? "alert" : "status");

    elemento.classList.remove("is-error", "is-success");
    elemento.classList.add(
        tipo === "erro" ? "is-error" : "is-success"
    );
}

function limparFeedback(elemento) {
    if (!elemento) return;

    elemento.textContent = "";
    elemento.classList.remove("is-error", "is-success");
}

function prepararFormulario(formulario) {
    formulario.querySelectorAll(
        'input[type="text"], textarea'
    ).forEach(campo => {
        campo.value = campo.value.trim();
    });

    return Object.fromEntries(new FormData(formulario));
}

function validarFormulario(formulario, feedback) {
    if (!formulario.checkValidity()) {
        formulario.reportValidity();

        mostrarFeedback(
            feedback,
            "Verifique os campos obrigatórios e os valores informados.",
            "erro"
        );

        return false;
    }

    return true;
}

function converterData(valor) {
    if (!valor) return null;

    const [ano, mes, dia] = valor.split("-").map(Number);

    return new Date(ano, mes - 1, dia);
}

function obterHoje() {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    return hoje;
}


// 1. LOGIN

function inicializarLogin() {
    const formulario = document.getElementById("login-form");

    if (!formulario) return;

    formulario.addEventListener("submit", evento => {
        evento.preventDefault();

        const mensagens = document.querySelector(".login-messages");
        limparFeedback(mensagens);

        const dados = prepararFormulario(formulario);

        if (!validarFormulario(formulario, mensagens)) return;

        if (!dados.login || !dados.senha) {
            mostrarFeedback(
                mensagens,
                "Informe sua matrícula e senha.",
                "erro"
            );
            return;
        }

        console.log("Dados do login recebidos:", {
            matricula: dados.login,
            senha: "[OCULTA NOS TESTES]"
        });

        mostrarFeedback(
            mensagens,
            "Dados recebidos! A autenticação ainda não está integrada.",
            "sucesso"
        );

        formulario.reset();
    });
}


// 2. CADASTRO DE ANIMAIS

function inicializarCadastroAnimal() {
    const formulario = document.getElementById("animal-form");
    const feedback = document.getElementById("animal-form-feedback");

    if (!formulario) return;

    formulario.addEventListener("submit", evento => {
        evento.preventDefault();
        limparFeedback(feedback);

        const dados = prepararFormulario(formulario);

        if (!validarFormulario(formulario, feedback)) return;

        if (!dados.identificacao || !dados.especie) {
            mostrarFeedback(
                feedback,
                "Identificação e espécie são obrigatórias.",
                "erro"
            );
            return;
        }

        const nascimento = converterData(dados.data_nascimento);
        const entrada = converterData(dados.data_entrada);
        const hoje = obterHoje();

        if (nascimento && nascimento > hoje) {
            mostrarFeedback(
                feedback,
                "A data de nascimento não pode ser futura.",
                "erro"
            );
            return;
        }

        if (entrada && entrada > hoje) {
            mostrarFeedback(
                feedback,
                "A data de entrada não pode ser futura.",
                "erro"
            );
            return;
        }

        if (nascimento && entrada && nascimento > entrada) {
            mostrarFeedback(
                feedback,
                "A data de nascimento não pode ser posterior à entrada.",
                "erro"
            );
            return;
        }

        console.log("Dados do animal recebidos:", dados);

        mostrarFeedback(
            feedback,
            "Cadastro validado! Dados recebidos, sem gravação no banco.",
            "sucesso"
        );

        formulario.reset();
    });
}


// 3. CADASTRO DE PATRIMÔNIO

function inicializarCadastroPatrimonio() {
    const formulario = document.getElementById("patrimonio-form");
    const feedback = document.getElementById("patrimonio-form-feedback");

    if (!formulario) return;

    formulario.addEventListener("submit", evento => {
        evento.preventDefault();
        limparFeedback(feedback);

        const dados = prepararFormulario(formulario);

        if (!validarFormulario(formulario, feedback)) return;

        if (!dados.nome) {
            mostrarFeedback(
                feedback,
                "O nome do patrimônio é obrigatório.",
                "erro"
            );
            return;
        }

        const aquisicao = converterData(dados.data_aquisicao);

        if (aquisicao && aquisicao > obterHoje()) {
            mostrarFeedback(
                feedback,
                "A data de aquisição não pode ser futura.",
                "erro"
            );
            return;
        }

        console.log("Dados do patrimônio recebidos:", dados);

        mostrarFeedback(
            feedback,
            "Cadastro validado! Dados recebidos, sem gravação no banco.",
            "sucesso"
        );

        formulario.reset();
    });
}


// 4. CANCELAMENTO DOS FORMULÁRIOS

function inicializarCancelamentos() {
    const botoes = document.querySelectorAll(
        '[data-action="cancel"]'
    );

    botoes.forEach(botao => {
        botao.addEventListener("click", () => {
            const formulario = botao.closest("form");

            if (!formulario) return;

            formulario.reset();

            const feedback = formulario
                .closest(".content-panel")
                ?.querySelector(".form-feedback");

            limparFeedback(feedback);
        });
    });
}
