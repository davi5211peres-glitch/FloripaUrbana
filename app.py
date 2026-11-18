from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
from config import MYSQL_CONFIG
from mapa import montar_mapa
 
app = Flask(__name__, template_folder="paginas", static_folder="arquivos", static_url_path="/static")
app.secret_key = "chave-local-floripa-urbana"
 
 
def conectar_banco():
    """Abre a conexÃ£o com o MySQL usando as configuraÃ§Ãµes de config.py."""
    return mysql.connector.connect(**MYSQL_CONFIG)
 
 
def consultar(sql, parametros=(), retornar=False):
    """Executa uma consulta e fecha cursor/conexÃ£o mesmo em caso de erro."""
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
 
 
@app.route("/")
def inicio():
    try:
        pontos = consultar(
            "SELECT id, nome, descricao, imagem FROM pontos_turisticos ORDER BY nome LIMIT 6",
            retornar=True,
        )
    except Error as erro:
        app.logger.warning("NÃ£o foi possÃ­vel carregar os pontos: %s", erro)
        pontos = []
    return render_template("inicio.html", pontos=pontos)
 
 
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
    return render_template("usuario.html", conta=contas[0])
 
 
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
                return redirect(url_for("inicio"))
            except Error as erro:
                app.logger.warning("Falha no cadastro: %s", erro)
                flash("NÃ£o foi possÃ­vel concluir o cadastro. Verifique se o e-mail jÃ¡ estÃ¡ cadastrado.", "erro")
    return render_template("cadastro.html")
 
 
@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "GET":
        return render_template("entrar.html")
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")
    try:
        usuarios = consultar(
            "SELECT id, nome, senha FROM usuarios WHERE email = %s LIMIT 1",
            (email,), retornar=True,
        )
    except Error as erro:
        app.logger.warning("Falha no login: %s", erro)
        usuarios = []
    if usuarios and check_password_hash(usuarios[0]["senha"], senha):
        session["usuario_id"] = usuarios[0]["id"]
        session["usuario_nome"] = usuarios[0]["nome"]
        return redirect(url_for("inicio"))
    else:
        flash("E-mail ou senha invÃ¡lidos.", "erro")
    return redirect(url_for("entrar"))
 
 
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))
 
 
@app.route("/mapa", endpoint="mapa")
def exibir_mapa():
    mapa_html = montar_mapa()
    return render_template("mapa.html", mapa_html=mapa_html)
 
 
@app.route("/ponto/<int:ponto_id>")
def detalhe_ponto(ponto_id):
    try:
        pontos = consultar(
            "SELECT id, nome, descricao, imagem, latitude, longitude FROM pontos_turisticos WHERE id = %s",
            (ponto_id,), retornar=True,
        )
    except Error as erro:
        app.logger.warning("NÃ£o foi possÃ­vel carregar o ponto: %s", erro)
        pontos = []
    if not pontos:
        return render_template("ponto.html", ponto=None), 404
    return render_template("ponto.html", ponto=pontos[0])
 
 
@app.route("/outras")
def outras():
    return render_template("outras.html")
 
 
if __name__ == "__main__":
    app.run(debug=True)
