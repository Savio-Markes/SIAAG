USE siaag;

-- 1. Criar a tabela de usuários, se não existir
CREATE TABLE IF NOT EXISTS usuarios (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    login VARCHAR(100) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    funcao_referencia VARCHAR(100),
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    ultimo_login_em DATETIME,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_login (login)
) ENGINE=InnoDB;


-- 2. Criar um usuário de teste
-- Se já existir, reutiliza o ID dele
INSERT INTO usuarios (
    nome,
    login,
    senha_hash,
    funcao_referencia,
    ativo
)
VALUES (
    'Usuario de Teste',
    'teste_bd_animais',
    '!SEM_SENHA_DE_LOGIN!',
    'Administrador de teste',
    1
)
ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id);

SET @usuario_teste = LAST_INSERT_ID();


-- 3. Criar a tabela de animais, se não existir
-- Estrutura sem a coluna identificacao
CREATE TABLE IF NOT EXISTS animais (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100),
    especie VARCHAR(100) NOT NULL,
    raca VARCHAR(100),
    sexo VARCHAR(20),
    nascimento DATE,
    origem VARCHAR(150),
    data_entrada DATE,
    localizacao VARCHAR(150),
    situacao VARCHAR(50),
    observacoes TEXT,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    criado_por INT UNSIGNED,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_animais_especie (especie),

    CONSTRAINT fk_animais_criado_por
        FOREIGN KEY (criado_por)
        REFERENCES usuarios(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- 4. Inserir cinco animais de teste
INSERT INTO animais (
    nome,
    especie,
    raca,
    sexo,
    nascimento,
    origem,
    data_entrada,
    localizacao,
    situacao,
    observacoes,
    criado_por
)
VALUES
(
    'Mimosa',
    'Bovino',
    'Nelore',
    'Fêmea',
    '2022-03-15',
    'Nascimento na fazenda',
    '2022-03-15',
    'Curral 1',
    'Ativo',
    'Animal de teste',
    @usuario_teste
),
(
    'Trovão',
    'Bovino',
    'Girolando',
    'Macho',
    '2021-08-20',
    'Aquisição',
    '2023-01-10',
    'Curral 2',
    'Ativo',
    'Animal de teste',
    @usuario_teste
),
(
    'Estrela',
    'Caprino',
    'Anglo-Nubiana',
    'Fêmea',
    '2023-05-12',
    'Nascimento na fazenda',
    '2023-05-12',
    'Aprisco 1',
    'Ativo',
    'Animal de teste',
    @usuario_teste
),
(
    'Relâmpago',
    'Equino',
    'Mestiço',
    'Macho',
    '2020-11-02',
    'Aquisição',
    '2024-02-05',
    'Baia 1',
    'Ativo',
    'Animal de teste',
    @usuario_teste
),
(
    'Lua',
    'Ovino',
    'Santa Inês',
    'Fêmea',
    '2024-01-18',
    'Nascimento na fazenda',
    '2024-01-18',
    'Aprisco 2',
    'Ativo',
    'Animal de teste',
    @usuario_teste
);


-- 5. Conferir os resultados
SELECT * FROM usuarios;

SELECT * FROM animais;