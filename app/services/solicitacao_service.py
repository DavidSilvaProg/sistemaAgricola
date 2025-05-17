from datetime import datetime
from flask import session, flash, render_template
from app.models.database import Database

class SolicitacaoService:
    def __init__(self):
        self.db = Database()

#manipula as operações relacionadas a solicitações
class SolicitacaoService:
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
                id_produto,
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

    def incluirRecebimento(self, id, data, produtos, frete, total, observacao):

        query = """
            INSERT INTO pedidos_recebidos
            (id_solicitacao, data_recebido, frete_recebido, total_recebido, observacao_recebido)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = (id, data, frete, total, observacao)
        ultimoId = (self.db.execute(query, data))
        self.incluirProdutosRecebidos(ultimoId, produtos)

    def incluirProdutosRecebidos(self, id, produtos):
        query = """
            INSERT INTO produtos_recebidos
            (nome_produto, quantidade_produto, id_recebido, valor_produto)
            VALUES (%s, %s, %s, %s)
        """
        data = [(produto['produto'], produto['quantidade'], id, produto['preco']) for produto in produtos]
        self.db.execute(query, data, varios=True)

    def verificaRecebido(self, id):
        query = """
            SELECT
                status_solicitacao
            FROM
                solicitacao_compras
            WHERE id_solicitacao = %s
        """
        resultado = self.db.execute(query, (id,), fetch=True)

        if resultado:
            return resultado[0]['status_solicitacao'] != "Recebido"
        return False

    def buscarSolicitacoesRecebidas(self, id=0, unica=False):
        condicao = "1=1"  # Começamos com uma condição sempre verdadeira
        params = []

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
                    u.nome_usuario,
                    pr.data_recebido
                FROM
                    solicitacao_compras sc
                JOIN setores s ON sc.id_setor = s.id_setor
                JOIN usuarios u ON sc.id_usuario = u.id_usuario
                JOIN pedidos_recebidos pr ON sc.id_solicitacao = pr.id_solicitacao
                WHERE {condicao}
            """

        resultado = self.db.execute(query, params, fetch=True)

        # Formata datas
        for solicitacao in resultado:
            solicitacao['data_solicitacao'] = solicitacao['data_solicitacao'].strftime("%d/%m/%Y") if solicitacao[
                'data_solicitacao'] else None
            solicitacao['data_recebido'] = solicitacao['data_recebido'].strftime("%d/%m/%Y") if solicitacao[
                'data_solicitacao'] else None

        return resultado