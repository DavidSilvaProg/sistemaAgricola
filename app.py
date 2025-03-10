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

solicitacao_service = Solicitacao()

#Página inicial
@app.route('/')
def index():
    # return render_template('index.html')
    return redirect(url_for('pedidos'))

#Página de pedidos
@app.route('/pedidos')
def pedidos():
    solicitacoes = solicitacao_service.buscar_solicitacoes()[::-1] #inverte a lista
    return render_template('pedidos.html', pedidos = solicitacoes)

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
    return render_template('pedidos.html', setores=setores)

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