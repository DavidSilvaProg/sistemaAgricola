import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

#redireciona para a página principal
@app.route('/')
def index():
    #return render_template('index.html')
    return redirect(url_for('pedidos'))

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

@app.route('/cadastro')
def cadastro():
    produtos = buscar_produtos()
    setores = buscar_setores()
    return render_template('cadastro.html', produtos=produtos, setores=setores)

#quando o url chamar o action do html recebeSolicitacao ele executa a função
@app.route('/recebeSolicitacao.py', methods=['POST'])
def recebeSolicitacao():
    """
    Recebe os dados: nome e id_produto do formulário de solicitação de compra e grava no banco de dados
    :return:
    """
    nome = request.form['nome']
    setor = request.form['setor']
    idProduto = request.form['produto']
    quantidade = request.form['quantidade']
    prioridade = request.form['prioridade']
    incluiSolicitacao(nome, setor, idProduto, quantidade, prioridade)
    return redirect(url_for('pedidos'))

def conectaBanco():
    """
    Conecta com o banco de dados
    :return: conexão com o banco
    """
    load_dotenv()
    conexao = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conexao

def incluiSolicitacao(nome = '',setor = '', idProduto = 0, quantidade = 0, prioridade = ''):
    try:
        conexao = conectaBanco()
        cursor = conexao.cursor()
        dia = datetime.now().date()
        cursor.execute("""
                   INSERT INTO solicitacao_compras
                   (nome_solicitacao, setor_solicitacao, data_solicitacao, id_produto, quantidade_solicitacao, prioridade_solicitacao)
                   VALUES (%s, %s, %s, %s, %s, %s)
               """, (nome, setor, dia, idProduto, quantidade, prioridade))
        conexao.commit()
    except mysql.connector.Error as e:
        print(f'Erro no banco de dados: {e}')
        return []
    finally:
        cursor.close()
        conexao.close()

def buscar_produtos():
    try:
        conexao = conectaBanco()
        cursor = conexao.cursor()
        cursor.execute("SELECT id_produto, nome_produto FROM produtos")
        linhas = cursor.fetchall()
        if not linhas:
            print("Nenhum produto econtrado.")
            return []
        produtos = [{"id": linha[0], "nome": linha[1]} for linha in linhas]
        return produtos
    except mysql.connector.Error as e:
        print(f'Erro no banco de dados: {e}')
        return []
    finally:
        cursor.close()
        conexao.close()


def buscar_setores():
    try:
        conexao = conectaBanco()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM setores")
        linhas = cursor.fetchall()
        if not linhas:
            print(f'Nenhum setor encontrado.')
            return []
        setores = [{"id":linha[0], "nome":linha[1]} for linha in linhas]
        return setores
    except mysql.connector.Error as e:
        print(f'Erro no banco de dados: {e}')
        return[]
    finally:
        conexao.close()
        cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
