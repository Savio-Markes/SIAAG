
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const API_URL = "/animais/";

    const formulario = document.getElementById("animalForm");
    const botaoSalvar = document.getElementById("btnSalvarAnimal");
    const feedback = document.getElementById("animalFormFeedback");

    if (!formulario || !botaoSalvar || !feedback) {
        console.error("Elementos do formulário de animais não encontrados.");
        return;
    }

    let enviando = false;

    function mostrarFeedback(mensagem, tipo = "info") {
        feedback.textContent = mensagem;
        feedback.className = `animal-form-feedback ${tipo}`;
        feedback.hidden = false;

        feedback.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }

    function ocultarFeedback() {
        feedback.hidden = true;
        feedback.textContent = "";
        feedback.className = "animal-form-feedback";
    }

    function obterDadosFormulario() {
        const campos = [
            "identificacao",
            "nome",
            "especie",
            "raca",
            "sexo",
            "nascimento",
            "origem",
            "data_entrada",
            "localizacao",
            "situacao",
            "observacoes"
        ];

        const dados = {};

        campos.forEach(nome => {
            const campo = formulario.elements.namedItem(nome);
            dados[nome] = campo ? campo.value.trim() : "";
        });

        return dados;
    }

    function validarFormulario() {
        const obrigatorios = [
            ["identificacao", "Informe a identificação do animal."],
            ["especie", "Informe a espécie do animal."],
            ["situacao", "Informe a situação do animal."]
        ];

        for (const [nome, mensagem] of obrigatorios) {
            const campo = formulario.elements.namedItem(nome);

            if (!campo.value.trim()) {
                campo.setCustomValidity(mensagem);
                campo.reportValidity();
                campo.focus();
                campo.setCustomValidity("");
                return false;
            }
        }

        if (!formulario.checkValidity()) {
            formulario.reportValidity();
            return false;
        }

        return true;
    }

    async function cadastrarAnimal(dados) {
        const resposta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify(dados)
        });

        let resultado;

        try {
            resultado = await resposta.json();
        } catch {
            throw new Error("O servidor retornou uma resposta inválida.");
        }

        if (resposta.status === 401) {
            throw new Error("Sua sessão expirou. Entre novamente no sistema.");
        }

        if (resposta.status === 403) {
            throw new Error("Você não tem permissão para cadastrar animais.");
        }

        if (!resposta.ok || resultado.sucesso !== true) {
            throw new Error(
                resultado.mensagem ||
                resultado.erro ||
                "Não foi possível cadastrar o animal."
            );
        }

        return resultado;
    }

    function definirEstadoEnvio(ativo) {
        enviando = ativo;
        botaoSalvar.disabled = ativo;
        botaoSalvar.textContent = ativo
            ? "Cadastrando..."
            : "✓ Cadastrar animal";
    }

    formulario.addEventListener("submit", async evento => {
        evento.preventDefault();

        if (enviando) return;

        ocultarFeedback();

        if (!validarFormulario()) return;

        const dados = obterDadosFormulario();

        try {
            definirEstadoEnvio(true);

            const resultado = await cadastrarAnimal(dados);

            mostrarFeedback(
                resultado.mensagem || "Animal cadastrado com sucesso!",
                "success"
            );

            formulario.reset();

            const destino = resultado.animal_id
                ? `/animais/${encodeURIComponent(resultado.animal_id)}/painel`
                : "/animais/painel";

            window.setTimeout(() => {
                window.location.href = destino;
            }, 1200);

        } catch (erro) {
            console.error("Erro ao cadastrar animal:", erro);

            mostrarFeedback(
                erro.message || "Ocorreu um erro ao cadastrar o animal.",
                "error"
            );

        } finally {
            definirEstadoEnvio(false);
        }
    });

    formulario.addEventListener("input", evento => {
        if (evento.target.matches("input, textarea, select")) {
            evento.target.setCustomValidity("");
        }
    });

    console.log("Formulário de cadastro de animais inicializado.");
});
