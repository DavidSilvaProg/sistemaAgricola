from datetime import datetime
from flask import session, flash, render_template
from app.models.database import Database
from datetime import date
from dateutil.relativedelta import relativedelta

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

    def buscar_solicitacoes(self, id=0, unica=False, data_inicio=None, data_fim=None,
                            status=None, ocultar_cancelados=False, ocultar_recebidos=False, busca=""):
        condicoes = []
        params = []

        if session['nivel'] != 'administrador':
            condicoes.append("u.id_usuario = %s")
            params.append(session["user_id"])

        if unica:
            condicoes.append("sc.id_solicitacao = %s")
            params.append(id)

        if data_inicio == None or data_inicio == '':
            data_inicio = date.today() - relativedelta(months=1)

        condicoes.append("sc.data_solicitacao >= %s")
        params.append(data_inicio)

        if data_fim:
            condicoes.append("sc.data_solicitacao <= %s")
            params.append(data_fim)

        if status:
            condicoes.append("sc.status_solicitacao = %s")
            params.append(status)

        if ocultar_cancelados:
            condicoes.append("sc.status_solicitacao != 'Cancelado'")

        if ocultar_recebidos:
            condicoes.append("sc.status_solicitacao != 'Recebido'")

        condicao_final = " AND ".join(condicoes) if condicoes else "1=1"

        query = f"""
            SELECT
                sc.id_solicitacao,
                sc.nome_solicitacao,
                s.nome_setor,
                sc.prioridade_solicitacao,
                sc.status_solicitacao,
                sc.data_solicitacao,
                u.nome_usuario
            FROM solicitacao_compras sc
            JOIN setores s ON sc.id_setor = s.id_setor
            JOIN usuarios u ON sc.id_usuario = u.id_usuario
            WHERE {condicao_final}
        """

        resultado = self.db.execute(query, params, fetch=True)

        # Busca por texto (manual no Python)
        if busca:
            resultado = [
                r for r in resultado
                if busca in str(r['nome_usuario']).lower()
                   or busca in str(r['nome_solicitacao']).lower()
                   or busca in str(r['nome_setor']).lower()
            ]

        for r in resultado:
            if r['data_solicitacao']:
                r['data_solicitacao'] = r['data_solicitacao'].strftime("%d/%m/%Y")

        return resultado

    def editarStatusSolicitacao(self, status, id):
        query = """
                    UPDATE solicitacao_compras SET status_solicitacao = %s
                    WHERE id_solicitacao = %s
                """
        params = [status, id]
        return self.db.execute(query, params)

    def buscar_produtos_solicitacao(self, id=0):
        query = """
            SELECT
                id_produto,
                nome_produto,
                unidade_produto,
                quantidade_produto
            FROM
                produtos_solicitacao
            WHERE id_solicitacao = %s
        """
        return self.db.execute(query, (id,),  fetch=True)

    def incluirProdutos(self, id, produtos):
        query = """
            INSERT INTO produtos_solicitacao
            (nome_produto, quantidade_produto, id_solicitacao, unidade_produto)
            VALUES (%s, %s, %s, %s)
        """
        data = [(produto['produto'], produto['quantidade'], id, produto['unidade']) for produto in produtos]
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
            (nome_produto, quantidade_produto, id_recebido, unidade_produto, valor_produto)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = [(produto['produto'], produto['quantidade'], id,produto['unidade'], produto['preco']) for produto in produtos]
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

    def buscarSolicitacoesRecebidas(self, id=0, unica=False, data_inicio=None, data_fim=None):
        condicao = "1=1"
        params = []

        if unica:
            condicao += " AND pr.id_recebido = %s"
            params.append(id)

        # Filtro por intervalo de datas
        if data_inicio == None or data_inicio == '':
                data_inicio = date.today() - relativedelta(months=1)

        if data_fim == None or data_fim == '':
            data_fim = datetime.now()

        condicao += " AND pr.data_recebido BETWEEN %s AND %s"
        params.extend([data_inicio, data_fim])

        query = f"""
            SELECT
                sc.id_solicitacao,
                sc.nome_solicitacao,
                s.nome_setor,
                sc.prioridade_solicitacao,
                sc.status_solicitacao,
                sc.data_solicitacao,
                u.nome_usuario,
                pr.id_recebido,
                pr.data_recebido,
                pr.total_recebido,
                pr.frete_recebido,
                pr.observacao_recebido
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
            solicitacao['data_solicitacao'] = (
                solicitacao['data_solicitacao'].strftime("%d/%m/%Y")
                if solicitacao['data_solicitacao'] else None
            )
            solicitacao['data_recebido'] = (
                solicitacao['data_recebido'].strftime("%d/%m/%Y")
                if solicitacao['data_recebido'] else None
            )

        return resultado

    def buscarProdutosRecebidos(self, id=0):
        query = """
            SELECT
                id_produto,
                unidade_produto,
                nome_produto,
                quantidade_produto,
                valor_produto
            FROM
                produtos_recebidos
            WHERE id_recebido = %s
        """
        return self.db.execute(query, (id,),  fetch=True)


    def cadastrar_produto(self, produto):
        hoje = date.today()
        query = """
    		INSERT INTO produtos (
    			nome_produto,
    			descricao_produto,
    			codigo_interno_produto,
    			unidade_medida_produto,
    			preco_unitario_produto,
    			categoria_id,
    			status_produto,
    			data_cadastro_produto,
    			fabricante_produto,
    			estoque_produto,
    			estoque_minimo_produto
    		)
    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    	"""

        data = (
            produto['nome_produto'],
            produto['descricao_produto'],
            produto['codigo_interno_produto'],
            produto['unidade_medida_produto'],
            produto['preco_unitario_produto'],
            0, #produto['categoria_id'],
            produto['status_produto'],
            hoje,  # data_cadastro_produto
            produto['fabricante_produto'],
            produto['estoque_produto'],
            produto['estoque_minimo_produto']
        )

        self.db.execute(query, data)

    def buscar_produtos(self, pagina=1, por_pagina=20, ocultar_inativos=False, busca=""):
        offset = (pagina - 1) * por_pagina

        condicoes = []
        parametros = []
        print(f"Mostra inativos: {ocultar_inativos}")
        if ocultar_inativos:
            condicoes.append("LOWER(status_produto) != 'inativo'")

        if busca:
            condicoes.append("(LOWER(nome_produto) LIKE %s OR LOWER(codigo_interno_produto) LIKE %s)")
            parametros += [f"%{busca}%", f"%{busca}%"]

        where_clause = "WHERE " + " AND ".join(condicoes) if condicoes else ""

        query = f"""
    		SELECT
    			id_produto,
    			nome_produto,
    			codigo_interno_produto,
    			unidade_medida_produto,
    			preco_unitario_produto,
    			estoque_produto,
    			estoque_minimo_produto,
    			status_produto,
    			data_cadastro_produto
    		FROM produtos
    		{where_clause}
    		ORDER BY nome_produto
    		LIMIT %s OFFSET %s
    	"""
        parametros += [por_pagina, offset]
        return self.db.execute(query, parametros, fetch=True)

    def contar_total_produtos(self, ocultar_inativos=False, busca=""):
        condicoes = []
        parametros = []

        if ocultar_inativos:
            condicoes.append("LOWER(status_produto) != 'inativo'")

        if busca:
            condicoes.append("(LOWER(nome_produto) LIKE %s OR LOWER(codigo_interno_produto) LIKE %s)")
            parametros += [f"%{busca}%", f"%{busca}%"]

        where_clause = "WHERE " + " AND ".join(condicoes) if condicoes else ""

        query = f"SELECT COUNT(*) AS total FROM produtos {where_clause}"

        resultado = self.db.execute(query, parametros, fetch=True)
        return resultado[0]["total"] if resultado else 0



