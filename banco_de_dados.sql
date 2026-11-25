CREATE DATABASE IF NOT EXISTS floripa_urbana
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE floripa_urbana;
 
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  senha VARCHAR(255) NOT NULL,
  is_admin TINYINT(1) NOT NULL DEFAULT 0,
  banido TINYINT(1) NOT NULL DEFAULT 0,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
CREATE TABLE IF NOT EXISTS pontos_turisticos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  descricao TEXT NOT NULL,
  latitude DECIMAL(10, 7) NOT NULL,
  longitude DECIMAL(10, 7) NOT NULL,
  imagem VARCHAR(255),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS avaliacoes_locais (
  id INT AUTO_INCREMENT PRIMARY KEY,
  local_id INT NOT NULL,
  usuario_id INT NOT NULL,
  nome VARCHAR(120) NOT NULL,
  nota TINYINT NOT NULL,
  comentario TEXT NOT NULL,
  criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_avaliacoes_local (local_id),
  CONSTRAINT fk_avaliacoes_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios(id) ON DELETE CASCADE
);

