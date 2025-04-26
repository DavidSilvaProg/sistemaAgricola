import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("CHAVE_SESSION")

#gerencia a conexão com o banco de dados
class Database:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME")
        }
        self.conexao = None

    def _conectar(self):
        self.conexao = mysql.connector.connect(**self.db_config)

    def execute(self, query, params=None, fetch=False, varios=False):
        cursor = None
        try:
            self._conectar()

            cursor = self.conexao.cursor(dictionary=True)

            if varios:
                cursor.executemany(query, params if params else [])
                # Se precisar de todos os IDs
                #cursor.execute("SELECT LAST_INSERT_ID()")
                #return [row['LAST_INSERT_ID()'] for row in cursor.fetchall()]
            else:
                cursor.execute(query, params or ())

            if fetch:
                return cursor.fetchall()

            self.conexao.commit()
            return cursor.lastrowid

        except mysql.connector.Error as e:
            if self.conexao:
                self.conexao.rollback()
            print(f"Erro no banco de dados: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

            if self.conexao:
                self.conexao.close()

    def close(self):
        self.conexao.close()

#manipula as operações relacionadas a solicitações
class Solicitacao:
    def __init__(self):
        self.db = Database()

    def incluirSolicitacao(self, nome, setor, produtos, prioridade, id):

        query = """
            INSERT INTO solicitacao_compras
            (nome_solicitacao, id_setor, data_solicitacao, prioridade_solicitacao, status_solicitacao, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (nome, setor, datetime.now().date(), prioridade,'Solicitado', id)
        ultimoId = (self.db.execute(query, data))
        self.incluirProdutos(ultimoId, produtos)


    def buscar_solicitacoes(self, id=0, unica=False):
        condicao = "1=1"  # Começamos com uma condição sempre verdadeira
        params = []

        if session['nivel'] != 'administrador':
            condicao = "u.id_usuario = %s"
            params.append(session["user_id"])

        if unica:
            condicao += " AND sc.id_solicitacao = %s"
            params.append(id)

        query = f"""
                SELECT
                    sc.id_solicitacao,
                    sc.nome_solicitacao,
                    s.nome_setor,
                    sc.prioridade_solicitacao,
                    sc.status_solicitacao,
                    sc.data_solicitacao,
                    u.nome_usuario
                FROM
                    solicitacao_compras sc
                JOIN setores s ON sc.id_setor = s.id_setor
                JOIN usuarios u ON sc.id_usuario = u.id_usuario
                WHERE {condicao}
            """

        resultado = self.db.execute(query, params, fetch=True)

        # Formata datas
        for solicitacao in resultado:
            solicitacao['data_solicitacao'] = solicitacao['data_solicitacao'].strftime("%d/%m/%Y") if solicitacao[
                'data_solicitacao'] else None

        return resultado

    def editarStatusSolicitacao(self, status, id):
        query = """
                    UPDATE solicitacao_compras SET status_solicitacao = %s
                    WHERE id_solicitacao = %s
                """
        params = [status, id]
        return self.db.execute(query, params)

    def buscar_produtos(self, id=0):
        query = """
            SELECT
                nome_produto,
                quantidade_produto
            FROM
                produtos
            WHERE id_solicitacao = %s
        """
        return self.db.execute(query, (id,),  fetch=True)

    def incluirProdutos(self, id, produtos):
        query = """
            INSERT INTO produtos
            (nome_produto, quantidade_produto, id_solicitacao)
            VALUES (%s, %s, %s)
        """
        data = [(produto['produto'], produto['quantidade'], id) for produto in produtos]
        self.db.execute(query, data, varios=True)

    def buscar_usuarios(self, id=0, unica=False):
        condicao = "1=1"  # condição inicial
        params = []

        if unica and id is not None:
            condicao += " AND id_usuario = %s"
            params.append(id)

        query = f"""
                    SELECT
                        id_usuario,
                        nome_usuario,
                        email_usuario,
                        nivel_usuario
                    FROM
                        usuarios
                    WHERE {condicao}
                """
        resultado = self.db.execute(query, params, fetch=True)
        return resultado

    def cadastrar_usuario(self, nome, email, senha, nivel):
        query = 'SELECT * FROM usuarios WHERE email_usuario = %s'
        usuario = self.db.execute(query, (email,), fetch=True)
        if not usuario:
            query = 'INSERT INTO usuarios (nome_usuario, email_usuario, senha_usuario, nivel_usuario) VALUES (%s, %s, %s, %s)'
            data = (nome, email, senha, nivel)
            self.db.execute(query, data)
            flash("Cadastrado com sucesso!")
        else:
            flash("E-mail de usuário já cadastrado!", "error")
            return render_template("cadastrarUsuario.html")

    def editar_usuario(self, id, nome, email, senha, nivel):
        query = 'SELECT * FROM usuarios WHERE email_usuario = %s AND id_usuario != %s'
        data = (email, id)
        usuario = self.db.execute(query, data, fetch=True)
        if not usuario:
            query = """
                        UPDATE 
                            usuarios 
                        SET 
                            nome_usuario = %s, 
                            email_usuario = %s, 
                            senha_usuario = %s, 
                            nivel_usuario = %s 
                            WHERE id_usuario = %s
                    """
            data = (nome, email, senha, nivel, id)
            self.db.execute(query, data)
            flash("Editado com sucesso!")
        else:
            flash("E-mail de usuário já cadastrado!", "error")
            return render_template("cadastrarSetor.html")

    def excluir_usuario(self, id):
        query = 'DELETE FROM usuarios WHERE id_usuario = %s'
        self.db.execute(query, (id,) )

    def buscar_setores(self, id=0, unica=False):
        condicao = "1=1"  # condição inicial
        params = []

        if unica and id is not None:
            condicao += " AND id_setor = %s"
            params.append(id)

        query = f"""
                SELECT
                    id_setor, 
                    nome_setor
                FROM
                    setores
                WHERE {condicao}
            """

        resultado = self.db.execute(query, params, fetch=True)

        return resultado

    def cadastrar_setor(self, nome):
        query = 'SELECT * FROM setores WHERE nome_setor = %s'
        usuario = self.db.execute(query, (nome,), fetch=True)
        if not usuario:
            query = 'INSERT INTO setores (nome_setor) VALUES (%s)'
            self.db.execute(query, (nome,))
            flash("Cadastrado com sucesso!")
        else:
            flash("Setor já cadastrado!", "error")
            return render_template("cadastrarSetor.html")

    def editar_setor(self, id, nome):
        query = 'SELECT * FROM setores WHERE nome_setor = %s'
        usuario = self.db.execute(query, (nome,), fetch=True)
        if not usuario:
            query = 'UPDATE setores SET nome_setor = %s WHERE id_setor = %s'
            data = (nome, id)
            self.db.execute(query, data)
            flash("Editado com sucesso!")
        else:
            flash("Setor já cadastrado!", "error")
            return render_template("cadastrarSetor.html")

    def excluir_setor(self, id):
        query = 'DELETE FROM setores WHERE id_setor = %s'
        self.db.execute(query, (id,) )

class Autenticacao:
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
                return redirect(url_for("login"))
            return func(*args, **kwargs)
        return decorated_view

    def nivel_required(self, nivel_necessario):
        def decorator(func):
            @wraps(func)
            def decorated_view(*args, **kwargs):
                if "nivel" not in session or session["nivel"] != nivel_necessario:
                    return redirect(url_for("solicitacoesCompras"))
                return func(*args, **kwargs)
            return decorated_view
        return decorator

    def logout(self):
        session.clear()


solicitacao_service = Solicitacao()
autenticacao_service = Autenticacao()

#Página inicial
@app.route('/')
@autenticacao_service.login_required
def index():
    return redirect(url_for("solicitacoesCompra"))

#login de usuário
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        if autenticacao_service.logar(email, senha):
            return redirect(url_for('solicitacoesCompra'))
        else:
            flash("E-mail ou senha incorretos", "error")
    return render_template("login.html")

#registro de novos usuários
@app.route('/cadastrarUsuario', methods=['GET', 'POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def cadastrarUsuario():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        nivel = request.form['nivel']
        solicitacao_service.cadastrar_usuario(nome, email, senha, nivel)

    return render_template("cadastrarUsuario.html", action_url=url_for('cadastrarUsuario'))

@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@app.route('/gravaEditarUsuario/<int:id>', methods=['POST'])
def gravaEditarUsuario(id):
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        nivel = request.form['nivel']
        solicitacao_service.editar_usuario(id, nome, email, senha, nivel)
    return render_template("cadastrarUsuario.html")


@app.route('/editarUsuario/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarUsuario(id):
    usuario_resultado = solicitacao_service.buscar_usuarios(id, unica=True)
    usuario = usuario_resultado[0] if usuario_resultado else None
    return render_template('cadastrarUsuario.html', usuario=usuario, action_url=url_for('gravaEditarUsuario', id=id))

@app.route('/excluirUsuario/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def excluirUsuario(id):
    solicitacao_service.excluir_usuario(id)
    return redirect(url_for("usuarios"))

@app.route('/usuarios')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def usuarios():
    usuarios = solicitacao_service.buscar_usuarios()[::-1] #inverte a lista
    return render_template('usuarios.html', usuarios = usuarios, nome=session['user_nome'])


#logout
@app.route('/logout')
def logout():
    autenticacao_service.logout()
    return redirect(url_for('login'))

#Página de solicitações de compra
@app.route('/solicitacoesCompra')
@autenticacao_service.login_required
def solicitacoesCompra():
    solicitacoes = solicitacao_service.buscar_solicitacoes()[::-1] #inverte a lista
    return render_template('solicitacoesCompra.html', pedidos = solicitacoes, nome=session['user_nome'])

#Página de detalhes da solicitacao
@app.route('/detalhesSolicitacao/<int:id>')
@autenticacao_service.login_required
def detalhesSolicitacao(id):
    solicitacao = solicitacao_service.buscar_solicitacoes(id, unica=True)
    produtos = solicitacao_service.buscar_produtos(id)
    return render_template('detalhesSolicitacao.html', solicitacao=solicitacao, produtos=produtos)


#Página de cadastro de solicitações de compras, carrega dados de produtos e setores
@app.route('/cadastroSolicitacao')
@autenticacao_service.login_required
def cadastroSolicitacao():
    setores = solicitacao_service.buscar_setores()
    return render_template('cadastroSolicitacao.html', setores=setores)

#Recebe as solicitação de compra do formulário e grava no banco
@app.route('/cadastrarSolicitacao', methods=['POST'])
@autenticacao_service.login_required
def cadastrarSolicitacao():
    nome = request.form['nome']
    setor = request.form['setor']
    produtos = []
    for chave, valor in request.form.items():
        if chave.startswith('produto'):
            numero = chave.replace('produto', '')
            quantidade = request.form.get(f'quantidade{numero}')
            produtos.append({'produto': valor, 'quantidade': quantidade})
    prioridade = request.form['prioridade']
    id = session["user_id"]
    solicitacao_service.incluirSolicitacao(nome, setor, produtos, prioridade, id)
    return redirect(url_for('cadastroSolicitacao'))

@app.route('/editarStatusSolicitacao/<int:id>', methods=['POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarStatusSolicitacao(id):
    status = request.form['status']
    solicitacao_service.editarStatusSolicitacao(status, id)
    return redirect(url_for('solicitacoesCompra'))


#Página de cadastro de setores
@app.route('/cadastrarSetor', methods=['GET', 'POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def cadastrarSetor():
    if request.method == "POST":
        nome = request.form["nome"]
        solicitacao_service.cadastrar_setor(nome)
    return render_template("cadastrarSetor.html", setor=None, action_url=url_for('cadastrarSetor'))


@app.route('/excluirSetor/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def excluirSetor(id):
    solicitacao_service.excluir_setor(id)
    return redirect(url_for("setores"))

@app.route('/setores')
@autenticacao_service.login_required
def setores():
    setores = solicitacao_service.buscar_setores()[::-1] #inverte a lista
    return render_template('setores.html', setores = setores, nome=session['user_nome'])


@app.route('/editarSetor/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarSetor(id):
    setor_resultado = solicitacao_service.buscar_setores(id, unica=True)
    setor = setor_resultado[0] if setor_resultado else None
    return render_template('cadastrarSetor.html', setor=setor, action_url=url_for('gravaEditarSetor', id=id))


@app.route('/gravaEditarSetor/<int:id>', methods=['POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def gravaEditarSetor(id):
    if request.method == "POST":
        nome = request.form["nome"]
        solicitacao_service.editar_setor(id,nome)
    return render_template("cadastrarSetor.html")

#Executa a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)