CREATE DATABASE IF NOT EXISTS siaag;
USE siaag;

-- 1. USUARIOS
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    funcao_referencia VARCHAR(100),
    ativo TINYINT DEFAULT 1,
    criado_em DATETIME,
    atualizado_em DATETIME,
    ultimo_login_em DATETIME
);

-- 2. PERMISSOES
CREATE TABLE permissoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    modulo VARCHAR(80),
    acao VARCHAR(80),
    descricao TEXT
);

-- 3. USUARIO_PERMISSOES
CREATE TABLE usuario_permissoes (
    usuario_id INT NOT NULL,
    permissao_id INT NOT NULL,
    concedido_por INT,
    concedido_em DATETIME,
    PRIMARY KEY (usuario_id, permissao_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (permissao_id) REFERENCES permissoes(id),
    FOREIGN KEY (concedido_por) REFERENCES usuarios(id)
);

-- 4. LOGS_AUDITORIA
CREATE TABLE logs_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    data_hora DATETIME,
    modulo VARCHAR(80),
    acao VARCHAR(100),
    entidade VARCHAR(100),
    registro_id INT,
    resultado VARCHAR(30),
    detalhes_resumidos TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 5. ANIMAIS
CREATE TABLE animais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identificacao VARCHAR(100) NOT NULL,
    nome VARCHAR(100),
    especie VARCHAR(100),
    raca VARCHAR(100),
    sexo VARCHAR(20),
    nascimento DATE,
    origem VARCHAR(150),
    data_entrada DATE,
    localizacao VARCHAR(150),
    situacao VARCHAR(50),
    observacoes TEXT,
    ativo TINYINT DEFAULT 1,
    criado_por INT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
);

-- 6. PESAGENS_ANIMAL
CREATE TABLE pesagens_animal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT NOT NULL,
    data_pesagem DATE,
    peso_kg DECIMAL(10,2),
    observacao TEXT,
    registrado_por INT,
    criado_em DATETIME,
    FOREIGN KEY (animal_id) REFERENCES animais(id),
    FOREIGN KEY (registrado_por) REFERENCES usuarios(id)
);

-- 7. ATENDIMENTOS_VETERINARIOS
CREATE TABLE atendimentos_veterinarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT NOT NULL,
    data_hora DATETIME,
    responsavel_id INT,
    motivo TEXT,
    avaliacao TEXT,
    procedimento TEXT,
    tratamento_informado TEXT,
    recomendacao TEXT,
    data_retorno DATE,
    observacoes TEXT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (animal_id) REFERENCES animais(id),
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
);

-- 8. OCORRENCIAS_ANIMAIS
CREATE TABLE ocorrencias_animais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT NOT NULL,
    data_hora DATETIME,
    tipo VARCHAR(100),
    descricao TEXT,
    responsavel_id INT,
    proximo_acompanhamento DATE,
    situacao VARCHAR(50),
    observacoes TEXT,
    criado_em DATETIME,
    FOREIGN KEY (animal_id) REFERENCES animais(id),
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
);

-- 9. CATEGORIAS_PRODUTO
CREATE TABLE categorias_produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ativa TINYINT DEFAULT 1
);

-- 10. PRODUTOS
CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria_id INT,
    descricao TEXT,
    unidade VARCHAR(30),
    estoque_minimo DECIMAL(12,3),
    controla_lote_validade TINYINT DEFAULT 0,
    ativo TINYINT DEFAULT 1,
    criado_por INT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (categoria_id) REFERENCES categorias_produto(id),
    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
);

-- 11. LOTES_PRODUTO
CREATE TABLE lotes_produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    codigo_lote VARCHAR(100),
    validade DATE,
    quantidade_inicial DECIMAL(12,3),
    saldo_atual DECIMAL(12,3),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- 12. MOVIMENTACOES_ESTOQUE
CREATE TABLE movimentacoes_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    lote_id INT,
    tipo VARCHAR(20),
    quantidade DECIMAL(12,3),
    data_hora DATETIME,
    responsavel_id INT,
    motivo TEXT,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (lote_id) REFERENCES lotes_produto(id),
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
);

-- 13. ATIVIDADES
CREATE TABLE atividades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150),
    tipo VARCHAR(80),
    descricao TEXT,
    inicio_em DATETIME,
    responsavel_id INT,
    area_cultura_local VARCHAR(150),
    animal_id INT,
    lote_animal VARCHAR(100),
    local VARCHAR(150),
    situacao VARCHAR(50),
    observacoes TEXT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
    FOREIGN KEY (animal_id) REFERENCES animais(id)
);

-- 14. ATIVIDADE_INSUMOS
CREATE TABLE atividade_insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    atividade_id INT NOT NULL,
    produto_id INT NOT NULL,
    lote_id INT,
    movimentacao_id INT,
    quantidade DECIMAL(12,3),
    unidade VARCHAR(30),
    FOREIGN KEY (atividade_id) REFERENCES atividades(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (lote_id) REFERENCES lotes_produto(id),
    FOREIGN KEY (movimentacao_id) REFERENCES movimentacoes_estoque(id)
);

-- 15. AULAS_PRATICAS
CREATE TABLE aulas_praticas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150),
    professor_id INT,
    disciplina VARCHAR(120),
    turma VARCHAR(80),
    data_aula DATE,
    hora_inicio TIME,
    hora_fim TIME,
    conteudo_objetivo TEXT,
    local VARCHAR(150),
    situacao VARCHAR(50),
    observacoes TEXT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (professor_id) REFERENCES usuarios(id)
);

-- 16. RECURSOS_AULA
CREATE TABLE recursos_aula (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aula_id INT NOT NULL,
    descricao VARCHAR(255),
    produto_id INT,
    quantidade DECIMAL(12,3),
    movimentacao_id INT,
    criado_em DATETIME,
    FOREIGN KEY (aula_id) REFERENCES aulas_praticas(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (movimentacao_id) REFERENCES movimentacoes_estoque(id)
);

-- 17. PARTICIPANTES_AULA
CREATE TABLE participantes_aula (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aula_id INT NOT NULL,
    usuario_id INT,
    nome_externo VARCHAR(150),
    presenca TINYINT DEFAULT 0,
    FOREIGN KEY (aula_id) REFERENCES aulas_praticas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 18. PROJETOS_PESQUISA
CREATE TABLE projetos_pesquisa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200),
    objetivo TEXT,
    responsavel_id INT,
    area_tema VARCHAR(150),
    inicio_em DATE,
    fim_em DATE,
    andamento TEXT,
    situacao VARCHAR(50),
    referencias TEXT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
);

-- 19. PARTICIPANTES_PROJETO
CREATE TABLE participantes_projeto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    usuario_id INT,
    nome_externo VARCHAR(150),
    papel VARCHAR(100),
    FOREIGN KEY (projeto_id) REFERENCES projetos_pesquisa(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 20. PATRIMONIOS
CREATE TABLE patrimonios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_tombamento VARCHAR(100),
    nome VARCHAR(150),
    categoria VARCHAR(100),
    modelo_descricao TEXT,
    localizacao VARCHAR(150),
    data_aquisicao DATE,
    estado_conservacao VARCHAR(50),
    responsavel_id INT,
    situacao VARCHAR(50),
    observacoes TEXT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
);

-- 21. MANUTENCOES_PATRIMONIO
CREATE TABLE manutencoes_patrimonio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patrimonio_id INT NOT NULL,
    data_abertura DATE,
    tipo VARCHAR(80),
    descricao TEXT,
    responsavel_fornecedor VARCHAR(150),
    custo_centavos BIGINT,
    situacao VARCHAR(50),
    data_conclusao DATE,
    proxima_revisao DATE,
    criado_por INT,
    criado_em DATETIME,
    atualizado_em DATETIME,
    FOREIGN KEY (patrimonio_id) REFERENCES patrimonios(id),
    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
);

-- CONFERIR AS TABELAS
ALTER TABLE animais
MODIFY COLUMN raca VARCHAR(100) NOT NULL;