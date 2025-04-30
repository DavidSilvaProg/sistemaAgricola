from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.autenticacao_service import AutenticacaoService

bp_auth = Blueprint('auth', __name__)
autenticacao_service = AutenticacaoService()

#login de usuário
@bp_auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        if autenticacao_service.logar(email, senha):
            return redirect(url_for('solicitacao.solicitacoesCompra'))
        else:
            flash("E-mail ou senha incorretos", "error")
    return render_template("login.html")

#logout
@bp_auth.route('/logout')
def logout():
    autenticacao_service.logout()
    return redirect(url_for('auth.login'))
