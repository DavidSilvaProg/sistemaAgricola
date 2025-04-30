from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("CHAVE_SESSION")

    from app.routes.solicitacao_routes import bp_solicitacao
    from app.routes.auth_routes import bp_auth
    from app.routes.admin_routes import bp_admin

    app.register_blueprint(bp_solicitacao)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_admin)

    return app