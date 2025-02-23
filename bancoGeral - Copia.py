import mysql.connector
from datetime import datetime
from flask import Flask, request, redirect, url_for


app = Flask(__name__)
@app.route('/bancoGeral.py', methods=['POST'])
def banco_geral():
    nome = request.form['nome']
    idProduto = request.form['id_produto']
    incluiSolicitacao(nome,idProduto)
    return redirect(url_for('index.html'))


def conectaBanco():
    conexao = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="agricola_db"
    )
    return conexao

# Configuração da conexão
def incluiSolicitacao(nome, idProduto):
    conexao = conectaBanco()
    #Cria um cursor para interagir com o banco
    cursor = conexao.cursor()

    dia = datetime.now().date()

    cursor.execute("INSERT INTO solicitacao_compras (nome_solicitacao, data_solicitacao, id_produto) VALUES (%s, %s, %s)", (nome,dia,idProduto))
    conexao.commit()
    cursor.close()
    conexao.close()


if __name__ == '__main__':
    app.run(debug=True)
    banco_geral()

#Seleciona dados da tabela
"""
cursor.execute("SELECT * FROM solicitacao_compras")
for linha in cursor.fetchall(): #joga o resultado em formato de lista para linha
    print(linha)

#fechar cursor e conexão
cursor.close()
conexao.close()
"""
