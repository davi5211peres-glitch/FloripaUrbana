from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
from config import MYSQL_CONFIG
from mapa import LOCAIS, montar_mapa
 
app = Flask(__name__, template_folder="paginas", static_folder="arquivos", static_url_path="/static")
app.secret_key = "chave-local-floripa-urbana"
 
 
def conectar_banco():
    """Abre a conexão com o MySQL usando as configurações de config.py."""
    return mysql.connector.connect(**MYSQL_CONFIG)
 
 
def consultar(sql, parametros=(), retornar=False):
    """Executa uma consulta e fecha cursor/conexão mesmo em caso de erro."""
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(sql, parametros)
        resultado = cursor.fetchall() if retornar else None
        if not retornar:
            conexao.commit()
        return resultado
    finally:
        cursor.close()
        conexao.close()


def preparar_colunas_admin():
    """Adiciona os campos administrativos em bancos existentes."""
    colunas = consultar("SHOW COLUMNS FROM usuarios LIKE 'is_admin'", retornar=True)
    if not colunas:
        consultar("ALTER TABLE usuarios ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0")
    colunas = consultar("SHOW COLUMNS FROM usuarios LIKE 'banido'", retornar=True)
    if not colunas:
        consultar("ALTER TABLE usuarios ADD COLUMN banido TINYINT(1) NOT NULL DEFAULT 0")


def usuario_atual():
    if not session.get("usuario_id"):
        return None
    try:
        preparar_colunas_admin()
        usuarios = consultar(
            "SELECT id, nome, email, is_admin, banido FROM usuarios WHERE id = %s",
            (session["usuario_id"],), retornar=True,
        )
    except Error as erro:
        app.logger.warning("Falha ao verificar permissao da conta: %s", erro)
        return None
    if not usuarios or usuarios[0]["banido"]:
        session.clear()
        return None
    return usuarios[0]


def exigir_admin():
    usuario = usuario_atual()
    if not usuario or not usuario["is_admin"]:
        flash("Acesso permitido somente para administradores.", "erro")
        return None
    return usuario
 
 
@app.route("/")
def inicio():
    try:
        pontos = consultar(
            "SELECT id, nome, descricao, imagem FROM pontos_turisticos ORDER BY nome LIMIT 6",
            retornar=True,
        )
    except Error as erro:
        app.logger.warning("Não foi possível carregar os pontos: %s", erro)
        pontos = []
    usuario = usuario_atual() if session.get("usuario_id") else None
    return render_template("inicio.html", pontos=pontos, is_admin=bool(usuario and usuario["is_admin"]))
 
 
@app.route("/usuario", methods=["GET"])
def usuario():
    if not session.get("usuario_id"):
        return redirect(url_for("entrar"))
    try:
        contas = consultar("SELECT id, nome, email, criado_em FROM usuarios WHERE id = %s", (session["usuario_id"],), retornar=True)
    except Error as erro:
        app.logger.warning("Falha ao carregar conta: %s", erro)
        contas = []
    if not contas:
        session.clear()
        return redirect(url_for("entrar"))
    atual = usuario_atual()
    if not atual:
        return redirect(url_for("entrar"))
    email = contas[0]["email"]
    email_mascarado = email[:3] + "#" * max(0, len(email) - 3)
    return render_template("usuario.html", conta=contas[0], email_mascarado=email_mascarado, is_admin=bool(atual["is_admin"]))
 
 
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        if not nome or not email or not senha:
            flash("Preencha nome, e-mail e senha.", "erro")
        else:
            try:
                consultar("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, generate_password_hash(senha)))
                flash("Cadastro realizado com sucesso.", "sucesso")
                return redirect(url_for("entrar", next=request.form.get("next", "")))
            except Error as erro:
                app.logger.warning("Falha no cadastro: %s", erro)
                flash("Não foi possível concluir o cadastro. Verifique se o e-mail já está cadastrado.", "erro")
    return render_template("cadastro.html", next=request.args.get("next", ""))
 
 
@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "GET":
        return render_template("entrar.html", next=request.args.get("next", ""))
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")
    try:
        preparar_colunas_admin()
        usuarios = consultar(
            "SELECT id, nome, senha, banido FROM usuarios WHERE email = %s LIMIT 1",
            (email,), retornar=True,
        )
    except Error as erro:
        app.logger.warning("Falha no login: %s", erro)
        usuarios = []
    if usuarios and check_password_hash(usuarios[0]["senha"], senha) and not usuarios[0]["banido"]:
        session["usuario_id"] = usuarios[0]["id"]
        session["usuario_nome"] = usuarios[0]["nome"]
        proxima = request.form.get("next", "")
        if proxima.startswith("/") and not proxima.startswith("//") and "\\" not in proxima:
            return redirect(proxima)
        return redirect(url_for("inicio"))
    else:
        flash("E-mail/senha invalidos ou conta banida.", "erro")
    return redirect(url_for("entrar", next=request.form.get("next", "")))
 
 
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))
 
 
@app.route("/mapa", endpoint="mapa")
def exibir_mapa():
    mapa_html = montar_mapa()
    return render_template("mapa.html", mapa_html=mapa_html)


@app.route("/local/<int:local_id>", methods=["GET", "POST"])
def detalhe_local(local_id):
    if not 1 <= local_id <= len(LOCAIS):
        return render_template("local.html", local=None, avaliacoes=[], media=0), 404

    local = LOCAIS[local_id - 1]
    try:
        consultar(
            """CREATE TABLE IF NOT EXISTS avaliacoes_locais (
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
            )"""
        )
        colunas_usuario = consultar(
            "SHOW COLUMNS FROM avaliacoes_locais LIKE 'usuario_id'", retornar=True
        )
        if not colunas_usuario:
            # Migra a tabela criada pela versao anterior, preservando as avaliacoes existentes.
            consultar("ALTER TABLE avaliacoes_locais ADD COLUMN usuario_id INT NULL AFTER local_id")
        chave_usuario = consultar(
            """SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'avaliacoes_locais'
                 AND CONSTRAINT_NAME = 'fk_avaliacoes_usuario'""",
            retornar=True,
        )
        if not chave_usuario:
            consultar(
                """ALTER TABLE avaliacoes_locais
                   ADD CONSTRAINT fk_avaliacoes_usuario FOREIGN KEY (usuario_id)
                   REFERENCES usuarios(id) ON DELETE CASCADE"""
            )
    except Error as erro:
        app.logger.warning("Falha ao preparar a tabela de avaliacoes: %s", erro)

    if request.method == "POST":
        if request.form.get("acao") == "excluir_avaliacao":
            if not exigir_admin():
                return redirect(url_for("inicio"))
            try:
                consultar("DELETE FROM avaliacoes_locais WHERE id = %s AND local_id = %s", (request.form.get("avaliacao_id"), local_id))
                flash("Avaliação e comentário removidos deste local.", "sucesso")
            except Error as erro:
                app.logger.warning("Falha ao excluir avaliação: %s", erro)
                flash("Não foi possível remover a avaliação.", "erro")
            return redirect(url_for("detalhe_local", local_id=local_id) + "#avaliacoes")
        atual = usuario_atual()
        if not atual:
            flash("Entre ou cadastre-se para avaliar este lugar.", "erro")
            destino = url_for("detalhe_local", local_id=local_id) + "#avaliacoes"
            return redirect(url_for("entrar", next=destino))

        nome = session.get("usuario_nome", "Usuario")
        comentario = request.form.get("comentario", "").strip()
        try:
            nota = int(request.form.get("nota", ""))
        except ValueError:
            nota = 0
        if not comentario or nota not in range(1, 6):
            flash("Escreva um comentario e escolha uma nota de 1 a 5.", "erro")
        else:
            try:
                consultar(
                    "INSERT INTO avaliacoes_locais (local_id, usuario_id, nome, nota, comentario) VALUES (%s, %s, %s, %s, %s)",
                    (local_id, session["usuario_id"], nome[:120], nota, comentario),
                )
                flash("Avaliacao enviada. Obrigado por compartilhar sua experiencia!", "sucesso")
                return redirect(url_for("detalhe_local", local_id=local_id))
            except Error as erro:
                app.logger.warning("Falha ao salvar avaliacao: %s", erro)
                flash("Nao foi possivel salvar sua avaliacao agora.", "erro")

    try:
        avaliacoes = consultar(
            "SELECT id, usuario_id, nome, nota, comentario, criada_em FROM avaliacoes_locais WHERE local_id = %s ORDER BY criada_em DESC",
            (local_id,), retornar=True,
        )
    except Error as erro:
        app.logger.warning("Falha ao carregar avaliacoes: %s", erro)
        avaliacoes = []
    media = round(sum(int(item["nota"]) for item in avaliacoes) / len(avaliacoes), 1) if avaliacoes else 0
    rota = f'https://www.google.com/maps/dir/?api=1&destination={local["latitude"]},{local["longitude"]}'
    usuario = usuario_atual() if session.get("usuario_id") else None
    return render_template("local.html", local=local, local_id=local_id, avaliacoes=avaliacoes, media=media, rota=rota, is_admin=bool(usuario and usuario["is_admin"]))
 
 
@app.route("/ponto/<int:ponto_id>")
def detalhe_ponto(ponto_id):
    try:
        pontos = consultar(
            "SELECT id, nome, descricao, imagem, latitude, longitude FROM pontos_turisticos WHERE id = %s",
            (ponto_id,), retornar=True,
        )
    except Error as erro:
        app.logger.warning("Não foi possível carregar o ponto: %s", erro)
        pontos = []
    if not pontos:
        return render_template("ponto.html", ponto=None), 404
    return render_template("ponto.html", ponto=pontos[0])
 
 
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not exigir_admin():
        return redirect(url_for("inicio"))
    aba = request.args.get("aba", "pontos")
    if aba not in {"pontos", "comentarios", "avaliacoes", "usuarios"}:
        aba = "pontos"
    if request.method == "POST":
        acao = request.form.get("acao", "")
        try:
            if acao == "criar_ponto":
                nome = request.form.get("nome", "").strip()
                descricao = request.form.get("descricao", "").strip()
                imagem = request.form.get("imagem", "").strip() or None
                latitude = float(request.form.get("latitude", ""))
                longitude = float(request.form.get("longitude", ""))
                if not nome or not descricao or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                    raise ValueError
                consultar("INSERT INTO pontos_turisticos (nome, descricao, latitude, longitude, imagem) VALUES (%s, %s, %s, %s, %s)", (nome, descricao, latitude, longitude, imagem))
                flash("Ponto cadastrado.", "sucesso")
            elif acao == "excluir_ponto":
                consultar("DELETE FROM pontos_turisticos WHERE id = %s", (request.form.get("id"),))
                flash("Ponto excluído.", "sucesso")
            elif acao == "banir_usuario":
                consultar("UPDATE usuarios SET banido = 1, is_admin = 0 WHERE id = %s AND is_admin = 0", (request.form.get("id"),))
                flash("Conta banida.", "sucesso")
            elif acao == "desbanir_usuario":
                consultar("UPDATE usuarios SET banido = 0 WHERE id = %s AND is_admin = 0", (request.form.get("id"),))
                flash("Banimento removido.", "sucesso")
            else:
                flash("Ação inválida.", "erro")
        except (ValueError, Error) as erro:
            app.logger.warning("Falha em ação administrativa: %s", erro)
            flash("Confira os dados informados e tente novamente.", "erro")
        return redirect(url_for("admin", aba=aba))

    try:
        consultar(
            """CREATE TABLE IF NOT EXISTS avaliacoes_locais (
                id INT AUTO_INCREMENT PRIMARY KEY, local_id INT NOT NULL,
                usuario_id INT NULL, nome VARCHAR(120) NOT NULL,
                nota TINYINT NOT NULL, comentario TEXT NOT NULL,
                criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_avaliacoes_local (local_id)
            )"""
        )
        if aba == "pontos":
            pontos = consultar("SELECT id, nome, latitude, longitude FROM pontos_turisticos ORDER BY nome", retornar=True)
        else:
            pontos = []
        if aba in {"comentarios", "avaliacoes"}:
            avaliacoes = consultar("SELECT a.local_id, a.nome, a.nota, a.comentario, a.criada_em FROM avaliacoes_locais a ORDER BY a.local_id, a.criada_em DESC", retornar=True)
        else:
            avaliacoes = []
        usuarios = consultar("SELECT id, nome, email, banido FROM usuarios WHERE is_admin = 0 ORDER BY nome", retornar=True) if aba == "usuarios" else []
    except Error as erro:
        app.logger.warning("Falha ao carregar painel administrativo: %s", erro)
        flash("Não foi possível carregar os dados administrativos. Verifique a configuração do banco.", "erro")
        pontos, avaliacoes, usuarios = [], [], []
    return render_template("admin.html", aba=aba, pontos=pontos, avaliacoes=avaliacoes, usuarios=usuarios, locais=LOCAIS)

@app.route("/outras")
def outras():
    return render_template("outras.html")
 
 
if __name__ == "__main__":
    app.run(debug=True)
