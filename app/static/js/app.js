
/* =====================================================
   SIAAG — VALIDAÇÃO DOS FORMULÁRIOS
   Etapa atual: testes sem gravação no banco de dados.
   ===================================================== */

document.addEventListener("DOMContentLoaded", () => {
    inicializarLogin();
    inicializarCadastroAnimal();
    inicializarCadastroPatrimonio();
    inicializarCancelamentos();

    console.log("SIAAG: JavaScript carregado com sucesso.");
});


/* =====================================================
   1. FEEDBACK VISUAL
   ===================================================== */

function mostrarFeedback(elemento, mensagem, tipo = "sucesso") {
    if (!elemento) {
        console.error("Elemento de feedback não encontrado.");
        return;
    }

    const erro = tipo === "erro";

    const icone = document.createElement("span");
    icone.className = "feedback-icon";
    icone.setAttribute("aria-hidden", "true");
    icone.textContent = erro ? "!" : "✓";

    const conteudo = document.createElement("div");
    conteudo.className = "feedback-content";

    const titulo = document.createElement("strong");
    titulo.className = "feedback-title";
    titulo.textContent = erro
        ? "Atenção: verifique os dados"
        : "Operação concluída";

    const descricao = document.createElement("p");
    descricao.className = "feedback-description";
    descricao.textContent = mensagem;

    conteudo.append(titulo, descricao);

    elemento.replaceChildren(icone, conteudo);
    elemento.hidden = false;

    elemento.classList.remove("is-error", "is-success");
    elemento.classList.add(erro ? "is-error" : "is-success");

    elemento.setAttribute("role", erro ? "alert" : "status");
    elemento.setAttribute("aria-live", erro ? "assertive" : "polite");
    elemento.setAttribute("aria-atomic", "true");

    // Sobe a página até o feedback nos formulários de cadastro.
    if (
        elemento.id === "animal-form-feedback" ||
        elemento.id === "patrimonio-form-feedback"
    ) {
        elemento.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }
}


function limparFeedback(elemento) {
    if (!elemento) return;

    elemento.replaceChildren();
    elemento.classList.remove("is-error", "is-success");
    elemento.hidden = true;
}


/* =====================================================
   2. FUNÇÕES AUXILIARES
   ===================================================== */

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
            "Existem campos obrigatórios ou valores inválidos. Confira as informações e tente novamente.",
            "erro"
        );

        return false;
    }

    return true;
}


function converterData(valor) {
    if (!valor) return null;

    const partes = valor.split("-").map(Number);

    if (partes.length !== 3 || partes.some(Number.isNaN)) {
        return null;
    }

    const [ano, mes, dia] = partes;
    const data = new Date(ano, mes - 1, dia);

    if (
        data.getFullYear() !== ano ||
        data.getMonth() !== mes - 1 ||
        data.getDate() !== dia
    ) {
        return null;
    }

    data.setHours(0, 0, 0, 0);
    return data;
}


function obterHoje() {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    return hoje;
}


/* =====================================================
   3. LOGIN
   ===================================================== */

function inicializarLogin() {
    const formulario = document.getElementById("login-form");
    const mensagens = document.querySelector(".login-messages");

    if (!formulario) return;

    formulario.addEventListener("submit", evento => {
        evento.preventDefault();

        limparFeedback(mensagens);

        const dados = prepararFormulario(formulario);

        if (!validarFormulario(formulario, mensagens)) {
            return;
        }

        if (!dados.login || !dados.senha) {
            mostrarFeedback(
                mensagens,
                "Informe sua matrícula e senha para continuar.",
                "erro"
            );
            return;
        }

        // Não registrar matrícula ou senha no console.
        console.log("SIAAG: dados de autenticação recebidos para teste.");

        mostrarFeedback(
            mensagens,
            "Seus dados foram recebidos corretamente. A autenticação ainda não está integrada ao sistema.",
            "sucesso"
        );

        formulario.reset();
    });
}


/* =====================================================
   4. CADASTRO DE ANIMAIS
   ===================================================== */

function inicializarCadastroAnimal() {
    const formulario = document.getElementById("animal-form");
    const feedback = document.getElementById("animal-form-feedback");

    if (!formulario) return;

    formulario.addEventListener("submit", evento => {
        evento.preventDefault();

        limparFeedback(feedback);

        const dados = prepararFormulario(formulario);

        if (!validarFormulario(formulario, feedback)) {
            return;
        }

        if (!dados.identificacao || !dados.especie) {
            mostrarFeedback(
                feedback,
                "Preencha a identificação e a espécie do animal. Esses campos são indispensáveis para o cadastro.",
                "erro"
            );
            return;
        }

        const nascimento = converterData(dados.data_nascimento);
        const entrada = converterData(dados.data_entrada);
        const hoje = obterHoje();

        if (dados.data_nascimento && !nascimento) {
            mostrarFeedback(
                feedback,
                "A data de nascimento informada não é válida.",
                "erro"
            );
            return;
        }

        if (dados.data_entrada && !entrada) {
            mostrarFeedback(
                feedback,
                "A data de entrada informada não é válida.",
                "erro"
            );
            return;
        }

        if (nascimento && nascimento > hoje) {
            mostrarFeedback(
                feedback,
                "A data de nascimento não pode ser posterior à data atual.",
                "erro"
            );
            return;
        }

        if (entrada && entrada > hoje) {
            mostrarFeedback(
                feedback,
                "A data de entrada não pode ser posterior à data atual.",
                "erro"
            );
            return;
        }

        if (nascimento && entrada && nascimento > entrada) {
            mostrarFeedback(
                feedback,
                "A data de nascimento não pode ser posterior à data de entrada do animal.",
                "erro"
            );
            return;
        }

        console.log("SIAAG: dados do animal recebidos para teste.");

        formulario.reset();

        mostrarFeedback(
            feedback,
            "Os dados do animal foram recebidos e validados com sucesso. O cadastro ainda não foi gravado no banco de dados.",
            "sucesso"
        );
    });
}


/* =====================================================
   5. CADASTRO DE PATRIMÔNIO
   ===================================================== */

function inicializarCadastroPatrimonio() {
    const formulario = document.getElementById("patrimonio-form");
    const feedback = document.getElementById("patrimonio-form-feedback");

    if (!formulario) return;

    formulario.addEventListener("submit", evento => {
        evento.preventDefault();

        limparFeedback(feedback);

        const dados = prepararFormulario(formulario);

        if (!validarFormulario(formulario, feedback)) {
            return;
        }

        if (!dados.nome) {
            mostrarFeedback(
                feedback,
                "Informe o nome ou a identificação do patrimônio para continuar.",
                "erro"
            );
            return;
        }

        const aquisicao = converterData(dados.data_aquisicao);

        if (dados.data_aquisicao && !aquisicao) {
            mostrarFeedback(
                feedback,
                "A data de aquisição informada não é válida.",
                "erro"
            );
            return;
        }

        if (aquisicao && aquisicao > obterHoje()) {
            mostrarFeedback(
                feedback,
                "A data de aquisição não pode ser posterior à data atual.",
                "erro"
            );
            return;
        }

        console.log("SIAAG: dados do patrimônio recebidos para teste.");

        formulario.reset();

        mostrarFeedback(
            feedback,
            "Os dados do patrimônio foram recebidos e validados com sucesso. O cadastro ainda não foi gravado no banco de dados.",
            "sucesso"
        );
    });
}


/* =====================================================
   6. CANCELAMENTO DOS FORMULÁRIOS
   ===================================================== */

function inicializarCancelamentos() {
    const botoes = document.querySelectorAll(
        '[data-action="cancel"]'
    );

    botoes.forEach(botao => {
        botao.addEventListener("click", () => {
            const formulario = botao.closest("form");

            if (!formulario) return;

            formulario.reset();

            const painel = formulario.closest(".content-panel");
            const feedback = painel?.querySelector(".form-feedback");

            limparFeedback(feedback);
        });
    });
}
