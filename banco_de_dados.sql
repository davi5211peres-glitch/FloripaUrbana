CREATE DATABASE IF NOT EXISTS floripa_urbana
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE floripa_urbana;
 
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  senha VARCHAR(255) NOT NULL,
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
 
INSERT INTO pontos_turisticos (nome, descricao, latitude, longitude)
SELECT 'Mercado Público de Florianópolis', 'Espaço histórico e cultural no centro da cidade.', -27.5978, -48.5495
WHERE NOT EXISTS (SELECT 1 FROM pontos_turisticos WHERE nome = 'Mercado Público de Florianópolis');
 
INSERT INTO pontos_turisticos (nome, descricao, latitude, longitude)
SELECT 'Ponte Hercílio Luz', 'Um dos principais cartões-postais de Florianópolis.', -27.5927, -48.5661
WHERE NOT EXISTS (SELECT 1 FROM pontos_turisticos WHERE nome = 'Ponte Hercílio Luz');
