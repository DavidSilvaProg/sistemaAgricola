import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("CHAVE_SESSION")

#gerencia a conexão com o banco de dados
class Database:
    def __init__(self):
        load_dotenv()
        self.conexao = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )

    def execute(self, query, params=None, fetch=False, varios=False):
        try:
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
            print(f"Erro no banco de dados: {e}")
        finally:
            cursor.close()

    def close(self):
        self.conexao.close()

#manipula as operações relacionadas a solicitações
class Solicitacao:
    def __init__(self):
        self.db = Database()

    def incluirSolicitacao(self, nome, setor, produtos, prioridade):

        query = """
            INSERT INTO solicitacao_compras
            (nome_solicitacao, id_setor, data_solicitacao, prioridade_solicitacao, status_solicitacao)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = (nome, setor, datetime.now().date(), prioridade,'Pendente')
        ultimoId = (self.db.execute(query, data))
        self.incluirProdutos(ultimoId, produtos)

    def incluirProdutos(self, id, produtos):
        query = """
            INSERT INTO produtos
            (nome_produto, quantidade_produto, id_solicitacao)
            VALUES (%s, %s, %s)
        """
        data = [(produto['produto'], produto['quantidade'], id) for produto in produtos]
        self.db.execute(query, data, varios=True)

    def buscar_setores(self):
        query = "SELECT id_setor, nome_setor FROM setores"
        return self.db.execute(query, fetch=True)

    def buscar_solicitacoes(self, id=0, unica=False):
        if session['nivel'] == 'administrador':
            query = """
                SELECT
                    sc.id_solicitacao,
                    sc.nome_solicitacao,
                    s.nome_setor,
                    sc.prioridade_solicitacao,
                    sc.status_solicitacao,
                    sc.data_solicitacao
                FROM
                    solicitacao_compras sc
                JOIN
                setores s ON sc.id_setor = s.id_setor
            """
            if unica:
                query += "WHERE sc.id_solicitacao = %s"
                resultado =  self.db.execute(query, (id,), fetch=True)
            else:
                resultado =  self.db.execute(query, fetch=True)

            #formata o horario
            for solicitacao in resultado:
                solicitacao['data_solicitacao'] = solicitacao['data_solicitacao'].strftime("%d/%m/%Y") if solicitacao['data_solicitacao'] else None
            return resultado
        else:
            query = """
                            SELECT
                                sc.id_solicitacao,
                                sc.nome_solicitacao,
                                s.nome_setor,
                                sc.prioridade_solicitacao,
                                sc.status_solicitacao,
                                sc.data_solicitacao
                            FROM
                                solicitacao_compras sc
                            JOIN
                                setores s ON sc.id_setor = s.id_setor
                            JOIN
                                usuarios u ON sc.id_usuario = u.id_usuario
                        """
            if unica:
                query += "WHERE sc.id_solicitacao = %s"
                resultado = self.db.execute(query, (id,), fetch=True)
            else:
                query += "WHERE u.id_usuario = %s"
                resultado = self.db.execute(query, (session["user_id"],),  fetch=True)

            # formata o horario
            for solicitacao in resultado:
                solicitacao['data_solicitacao'] = solicitacao['data_solicitacao'].strftime("%d/%m/%Y") if solicitacao[
                    'data_solicitacao'] else None
            return resultado

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

    def fechar_conexao(self):
        self.db.close()

class Autenticacao:
    def __init__(self):
        self.db = Database()

    def logar(self, email, senha):
        query = "SELECT * FROM usuarios WHERE email_usuario = %s"
        usuario = self.db.execute(query, (email,), fetch=True)
        for usuario in usuario:
            if usuario and check_password_hash(usuario["senha_usuario"], senha):
                print(usuario)
                session["user_id"] = usuario["id_usuario"]
                session["user_nome"] = usuario["nome_usuario"]
                session["nivel"] = usuario["nivel_usuario"]
                return True
            else:
                return False

    def verificar_login(self):
        if "user_id" in session:
            return True
        return redirect(url_for("login"))

    def cadastrar_usuario(self, nome, email, senha, nivel):
        query = 'SELECT * FROM usuarios WHERE email = %s'
        usuario = self.db.execute(query, (email,), fetch='True')
        if not usuario:
            query = 'INSERT INTO usuarios (nome_usuario, email_usuario, senha_usuario, nivel_usuario) VALUES (%s, %s, %s, %s)'
            data = (nome, email, senha, nivel)
            self.db.execute(query, data)
            flash("Cadastrado com sucesso!")
        else:
            flash("Usuário já cadastrado!", "error")
            return render_template("registrar.html")


solicitacao_service = Solicitacao()
autenticacao_service = Autenticacao()

#Página inicial
@app.route('/')
def index():
    if autenticacao_service.verificar_login():
        return redirect(url_for("login"))

#login de usuário
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        if autenticacao_service.logar(email, senha):
            return redirect(url_for('pedidos'))
        else:
            flash("E-mail ou senha incorretos", "error")
    return render_template("login.html")

#registro de novos usuários
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if autenticacao_service.verificar_login():
        if session['nivel'] == "administrador":
            if request.method == "POST":
                nome = request.form["nome"]
                email = request.form["email"]
                senha = generate_password_hash(request.form["senha"])
                nivel = request.form['nivel']
                autenticacao_service.cadastrar_usuario(nome, email, senha, nivel)
            return render_template("registrar.html")
        else:
            return redirect(url_for('pedidos'))

#Página de pedidos
@app.route('/pedidos')
def pedidos():
    if autenticacao_service.verificar_login():
        solicitacoes = solicitacao_service.buscar_solicitacoes()[::-1] #inverte a lista
        return render_template('pedidos.html', pedidos = solicitacoes, nome=session['user_nome'])

#Página de detalhes da solicitacao
@app.route('/detalhes/<int:id>')
def detalhes(id):
    solicitacao = solicitacao_service.buscar_solicitacoes(id, unica=True)
    produtos = solicitacao_service.buscar_produtos(id)
    return render_template('detalhes.html', solicitacao=solicitacao, produtos=produtos)


#Página de cadastro de solicitações de compras, carrega dados de produtos e setores
@app.route('/cadastro')
def cadastro():
    setores = solicitacao_service.buscar_setores()
    return render_template('cadastro.html', setores=setores)

#Recebe as solicitação de compra do formulário e grava no banco
@app.route('/recebeSolicitacao', methods=['POST'])
def recebeSolicitacao():
    nome = request.form['nome']
    setor = request.form['setor']
    produtos = []
    for chave, valor in request.form.items():
        if chave.startswith('produto'):
            numero = chave.replace('produto', '')
            quantidade = request.form.get(f'quantidade{numero}')
            produtos.append({'produto': valor, 'quantidade': quantidade})
    prioridade = request.form['prioridade']
    solicitacao_service.incluirSolicitacao(nome, setor, produtos, prioridade)
    return redirect(url_for('cadastro'))

#Executa a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)