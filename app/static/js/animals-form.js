
/* =========================================
   SIAAG - MÓDULO DE ANIMAIS
   Cadastro e integração com a API
========================================= */

document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/animais/";
    const PAINEL_URL = "/animais/painel";

    const form = document.getElementById("animalDataForm");
    const feedback = document.getElementById("animalFormFeedback");
    const botaoSalvar = document.getElementById("btnSalvarAnimal");

    if (!form || !feedback || !botaoSalvar) {
        return;
    }

    function mostrarFeedback(mensagem, tipo = "info") {
        feedback.textContent = mensagem;
        feedback.className = `animal-form-feedback ${tipo}`;
        feedback.hidden = false;
    }

    function limparFeedback() {
        feedback.textContent = "";
        feedback.className = "animal-form-feedback";
        feedback.hidden = true;
    }

    function obterDataAtual() {
        const agora = new Date();
        const ano = agora.getFullYear();
        const mes = String(agora.getMonth() + 1).padStart(2, "0");
        const dia = String(agora.getDate()).padStart(2, "0");

        return `${ano}-${mes}-${dia}`;
    }

    function validarNascimento() {
        const campoNascimento = document.getElementById("nascimento");
        const nascimento = campoNascimento.value;

        campoNascimento.setCustomValidity("");

        if (!nascimento) {
            return true;
        }

        if (nascimento > obterDataAtual()) {
            campoNascimento.setCustomValidity(
                "A data de nascimento não pode ser futura."
            );

            campoNascimento.reportValidity();
            return false;
        }

        return true;
    }

    function obterDadosFormulario() {
        const dados = new FormData(form);

        return {
            identificacao: dados.get("identificacao").trim(),
            nome: dados.get("nome").trim(),
            especie: dados.get("especie").trim(),
            raca: dados.get("raca").trim(),
            sexo: dados.get("sexo").trim(),
            nascimento: dados.get("nascimento"),
            origem: dados.get("origem").trim(),
            data_entrada: dados.get("data_entrada"),
            localizacao: dados.get("localizacao").trim(),
            situacao: dados.get("situacao").trim(),
            observacoes: dados.get("observacoes").trim()
        };
    }

    async function enviarCadastro(dados) {
        const resposta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify(dados)
        });

        let resultado = {};

        try {
            resultado = await resposta.json();
        } catch {
            throw new Error(
                "O servidor retornou uma resposta inválida."
            );
        }

        if (!resposta.ok || !resultado.sucesso) {
            if (resposta.status === 401 || resposta.status === 403) {
                throw new Error(
                    "Você não possui permissão para cadastrar animais."
                );
            }

            if (resposta.status === 409) {
                throw new Error(
                    "Essa identificação já está cadastrada."
                );
            }

            throw new Error(
                resultado.mensagem ||
                resultado.erro ||
                "Não foi possível cadastrar o animal."
            );
        }

        return resultado;
    }

    form.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        limparFeedback();

        if (!form.reportValidity()) {
            return;
        }

        if (!validarNascimento()) {
            return;
        }

        const dados = obterDadosFormulario();

        if (!dados.identificacao || !dados.especie || !dados.situacao) {
            mostrarFeedback(
                "Preencha todos os campos obrigatórios.",
                "error"
            );
            return;
        }

        botaoSalvar.disabled = true;
        botaoSalvar.textContent = "Salvando...";

        try {
            await enviarCadastro(dados);

            mostrarFeedback(
                "Animal cadastrado com sucesso! Redirecionando...",
                "success"
            );

            form.reset();

            setTimeout(() => {
                window.location.href = PAINEL_URL;
            }, 1200);

        } catch (erro) {
            mostrarFeedback(
                erro.message || "Erro ao comunicar com o servidor.",
                "error"
            );

            console.error("Erro no cadastro de animal:", erro);

        } finally {
            botaoSalvar.disabled = false;
            botaoSalvar.textContent = "Cadastrar animal";
        }
    });

    const campoNascimento = document.getElementById("nascimento");

    campoNascimento.max = obterDataAtual();

    campoNascimento.addEventListener("change", validarNascimento);
});
