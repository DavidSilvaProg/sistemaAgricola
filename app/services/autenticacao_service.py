from flask import redirect, url_for, session
from app.models.database import Database
from functools import wraps
from werkzeug.security import check_password_hash

class AutenticacaoService:
    def __init__(self):
        self.db = Database()

    def buscar_usuario_por_email(self, email):
        query = "SELECT * FROM usuarios WHERE email_usuario = %s"
        usuarios = self.db.execute(query, (email,), fetch=True)
        return usuarios[0] if usuarios else None

    def iniciar_sessao(self, usuario):
        session["user_id"] = usuario["id_usuario"]
        session["user_nome"] = usuario["nome_usuario"]
        session["nivel"] = usuario["nivel_usuario"]


    def logar(self, email, senha):
        usuario = self.buscar_usuario_por_email(email)
        if usuario and check_password_hash(usuario["senha_usuario"], senha):
            self.iniciar_sessao(usuario)
            return True
        return False

    def login_required(self, func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        return decorated_view

    def nivel_required(self, nivel_necessario):
        def decorator(func):
            @wraps(func)
            def decorated_view(*args, **kwargs):
                if "nivel" not in session or session["nivel"] != nivel_necessario:
                    return redirect(url_for("solicitacao.solicitacoesCompras"))
                return func(*args, **kwargs)
            return decorated_view
        return decorator

    def logout(self):
        session.clear()