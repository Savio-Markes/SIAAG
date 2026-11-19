
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const formulario = document.getElementById("editAnimalForm");
    const botaoSalvar = document.getElementById("btnSalvarEdicao");
    const feedback = document.getElementById("editAnimalFeedback");
    const campoId = document.getElementById("animalId");

    if (!formulario || !botaoSalvar || !feedback || !campoId) {
        console.error("Elementos da edição de animais não encontrados.");
        return;
    }

    const animalId = campoId.value.trim();
    let enviando = false;

    if (!animalId) {
        mostrarFeedback("Não foi possível identificar o animal.", "error");
        botaoSalvar.disabled = true;
        return;
    }

    const campoNascimento = formulario.elements.namedItem("nascimento");

    if (campoNascimento) {
        campoNascimento.max = hojeLocal();
    }

    function hojeLocal() {
        const agora = new Date();
        const ano = agora.getFullYear();
        const mes = String(agora.getMonth() + 1).padStart(2, "0");
        const dia = String(agora.getDate()).padStart(2, "0");

        return `${ano}-${mes}-${dia}`;
    }

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
    }

    function obterDados() {
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

    function validarDados(dados) {
        if (!dados.identificacao) {
            mostrarFeedback("Informe a identificação do animal.", "error");
            formulario.elements.namedItem("identificacao").focus();
            return false;
        }

        if (!dados.especie) {
            mostrarFeedback("Informe a espécie do animal.", "error");
            formulario.elements.namedItem("especie").focus();
            return false;
        }

        if (!formulario.checkValidity()) {
            formulario.reportValidity();
            return false;
        }

        if (dados.nascimento && dados.nascimento > hojeLocal()) {
            mostrarFeedback(
                "A data de nascimento não pode ser futura.",
                "error"
            );
            campoNascimento.focus();
            return false;
        }

        return true;
    }

    function interpretarErro(status) {
        const mensagens = {
            400: "Os dados enviados são inválidos. Confira os campos.",
            401: "Sua sessão expirou. Entre novamente no sistema.",
            403: "Você não tem permissão para editar animais.",
            404: "Animal não encontrado.",
            409: "Já existe um animal com essa identificação.",
            500: "Erro interno do servidor."
        };

        return mensagens[status] ||
            "Não foi possível atualizar o cadastro.";
    }

    async function atualizarAnimal(dados) {
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

        let resultado = {};

        try {
            resultado = await resposta.json();
        } catch {
            throw new Error("O servidor retornou uma resposta inválida.");
        }

        if (resposta.status === 401 || resposta.status === 403) {
            throw new Error(interpretarErro(resposta.status));
        }

        if (!resposta.ok || resultado.sucesso !== true) {
            throw new Error(
                resultado.mensagem ||
                resultado.erro ||
                interpretarErro(resposta.status)
            );
        }

        return resultado;
    }

    function definirEstadoEnvio(ativo) {
        enviando = ativo;
        botaoSalvar.disabled = ativo;

        botaoSalvar.innerHTML = ativo
            ? "Salvando alterações..."
            : '<span aria-hidden="true">✓</span> Salvar alterações';
    }

    formulario.addEventListener("submit", async evento => {
        evento.preventDefault();

        if (enviando) return;

        ocultarFeedback();

        const dados = obterDados();

        if (!validarDados(dados)) return;

        try {
            definirEstadoEnvio(true);

            mostrarFeedback(
                "Atualizando cadastro do animal...",
                "info"
            );

            const resultado = await atualizarAnimal(dados);

            mostrarFeedback(
                resultado.mensagem || "Animal atualizado com sucesso!",
                "success"
            );

            setTimeout(() => {
                window.location.href =
                    `/animais/${encodeURIComponent(animalId)}/painel`;
            }, 1200);

        } catch (erro) {
            console.error("Erro ao atualizar animal:", erro);

            mostrarFeedback(
                erro.message || "Ocorreu um erro ao atualizar o animal.",
                "error"
            );

        } finally {
            definirEstadoEnvio(false);
        }
    });

    formulario.addEventListener("input", evento => {
        if (evento.target instanceof HTMLInputElement ||
            evento.target instanceof HTMLTextAreaElement) {
            evento.target.setCustomValidity("");
        }
    });

    formulario.addEventListener("change", evento => {
        if (evento.target instanceof HTMLSelectElement) {
            evento.target.setCustomValidity("");
        }
    });
});
