import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

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

    def execute(self, query, params=None, fetch=False):
        try:
            cursor = self.conexao.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            self.conexao.commit()
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

    def incluir(self, nome, setor, id_produto, quantidade, prioridade):
        query = """
            INSERT INTO solicitacao_compras
            (nome_solicitacao, id_setor, data_solicitacao, id_produto, quantidade_solicitacao, prioridade_solicitacao, status_solicitacao)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data = (nome, setor, datetime.now().date(), id_produto, quantidade, prioridade,'Pendente')
        self.db.execute(query, data)

    def buscar_produtos(self):
        query = "SELECT id_produto, nome_produto FROM produtos"
        return self.db.execute(query, fetch=True)

    def buscar_setores(self):
        query = "SELECT id_setor, nome_setor FROM setores"
        return self.db.execute(query, fetch=True)

    def buscar_solicitacoes(self):
        query = """
            SELECT
                sc.id_solicitacao,
                p.nome_produto,
                s.nome_setor,
                sc.quantidade_solicitacao,
                sc.prioridade_solicitacao,
                sc.status_solicitacao,
                sc.data_solicitacao
            FROM
                solicitacao_compras sc
            JOIN
                produtos p ON sc.id_produto = p.id_produto
            JOIN
            setores s ON sc.id_setor = s.id_setor
        """
        return self.db.execute(query, fetch=True)

    def fechar_conexao(self):
        self.db.close()

solicitacao_service = Solicitacao()

#Página inicial
@app.route('/')
def index():
    # return render_template('index.html')
    return redirect(url_for('pedidos'))

#Página de pedidos
@app.route('/pedidos')
def pedidos():
    solicitacoes = solicitacao_service.buscar_solicitacoes()
    #formata as datas do resultado da query para o formato dd/mm/yyyy
    for pedidos in solicitacoes:
        pedidos['data_solicitacao'] = pedidos['data_solicitacao'].strftime("%d/%m/%Y") if pedidos['data_solicitacao'] else None
    return render_template('pedidos.html', pedidos = solicitacoes)

#Página de cadastro de solicitações de compras, carrega dados de produtos e setores
@app.route('/cadastro')
def cadastro():
    produtos = solicitacao_service.buscar_produtos()
    setores = solicitacao_service.buscar_setores()
    return render_template('cadastro.html', produtos=produtos, setores=setores)

#Recebe as solicitação de compra do formulário e grava no banco
@app.route('/recebeSolicitacao', methods=['POST'])
def recebeSolicitacao():
    nome = request.form['nome']
    setor = request.form['setor']
    id_produto = request.form['produto']
    quantidade = request.form['quantidade']
    prioridade = request.form['prioridade']

    solicitacao_service.incluir(nome, setor, id_produto, quantidade, prioridade)
    return redirect(url_for('pedidos'))

#Executa a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)