from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.services.autenticacao_service import AutenticacaoService
from app.services.solicitacao_service import SolicitacaoService
from werkzeug.security import generate_password_hash
from decimal import Decimal, ROUND_HALF_UP

bp_admin = Blueprint('admin', __name__)
autenticacao_service = AutenticacaoService()
solicitacao_service = SolicitacaoService()

#registro de novos usuários
@bp_admin.route('/cadastrarUsuario', methods=['GET', 'POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def cadastrarUsuario():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        nivel = request.form['nivel']
        solicitacao_service.cadastrar_usuario(nome, email, senha, nivel)

    return render_template("cadastrarUsuario.html", action_url=url_for('admin.cadastrarUsuario'))

@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/gravaEditarUsuario/<int:id>', methods=['POST'])
def gravaEditarUsuario(id):
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        nivel = request.form['nivel']
        solicitacao_service.editar_usuario(id, nome, email, senha, nivel)
    return render_template("cadastrarUsuario.html")


@bp_admin.route('/editarUsuario/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarUsuario(id):
    usuario_resultado = solicitacao_service.buscar_usuarios(id, unica=True)
    usuario = usuario_resultado[0] if usuario_resultado else None
    return render_template('cadastrarUsuario.html', usuario=usuario, action_url=url_for('admin.gravaEditarUsuario', id=id))

@bp_admin.route('/excluirUsuario/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def excluirUsuario(id):
    solicitacao_service.excluir_usuario(id)
    return redirect(url_for("admin.usuarios"))

@bp_admin.route('/usuarios')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def usuarios():
    usuarios = solicitacao_service.buscar_usuarios()[::-1] #inverte a lista
    return render_template('usuarios.html', usuarios = usuarios, nome=session['user_nome'])

@bp_admin.route('/editarStatusSolicitacao/<int:id>', methods=['POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarStatusSolicitacao(id):
    status = request.form['status']
    solicitacao_service.editarStatusSolicitacao(status, id)
    return redirect(url_for('solicitacao.solicitacoesCompra'))


#Página de cadastro de setores
@bp_admin.route('/cadastrarSetor', methods=['GET', 'POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def cadastrarSetor():
    if request.method == "POST":
        nome = request.form["nome"]
        solicitacao_service.cadastrar_setor(nome)
    return render_template("cadastrarSetor.html", setor=None, action_url=url_for('admin.cadastrarSetor'))


@bp_admin.route('/excluirSetor/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def excluirSetor(id):
    solicitacao_service.excluir_setor(id)
    return redirect(url_for("solicitacao.setores"))

@bp_admin.route('/editarSetor/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarSetor(id):
    setor_resultado = solicitacao_service.buscar_setores(id, unica=True)
    setor = setor_resultado[0] if setor_resultado else None
    return render_template('cadastrarSetor.html', setor=setor, action_url=url_for('admin.gravaEditarSetor', id=id))


@bp_admin.route('/gravaEditarSetor/<int:id>', methods=['POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def gravaEditarSetor(id):
    if request.method == "POST":
        nome = request.form["nome"]
        solicitacao_service.editar_setor(id,nome)
    return render_template("cadastrarSetor.html")

#Página de receber da solicitacao
@bp_admin.route('/receberSolicitacao/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def receberSolicitacao(id):
    solicitacao = solicitacao_service.buscar_solicitacoes(id, unica=True)
    produtos = solicitacao_service.buscar_produtos_solicitacao(id)
    return render_template('receberSolicitacao.html', solicitacao=solicitacao, produtos=produtos, action_url=url_for('admin.registrarRecebimentoSolicitacao', id=id))

@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/registrarRecebimentoSolicitacao/<int:id>', methods=['POST'])
def registrarRecebimentoSolicitacao(id):
    if request.method == "POST":
        if solicitacao_service.verificaRecebido(id):
            data = request.form["data_recebimento"]
            frete = request.form["valor_frete"]
            total = request.form["valor_total"]
            observacao = request.form["observacao"]
            produtos = []
            for chave, valor in request.form.items():
                if chave.startswith('produto'):
                    numero = chave.replace('produto', '')
                    unidade = request.form.get(f'unidade{numero}')
                    quantidade = request.form.get(f'quantidade{numero}')
                    preco = request.form.get(f'preco{numero}')
                    produtos.append({'produto': valor, 'quantidade': quantidade, 'unidade': unidade,'preco': preco})
            solicitacao_service.incluirRecebimento(id, data, produtos, frete, total, observacao)
            solicitacao_service.editarStatusSolicitacao('Recebido', id)
    return redirect(url_for("admin.solicitacoesRecebidas"))

#Página de solicitações de compra
@bp_admin.route('/solicitacoesRecebidas')
@autenticacao_service.nivel_required('administrador')
@autenticacao_service.login_required
def solicitacoesRecebidas():
    recebidas = solicitacao_service.buscarSolicitacoesRecebidas()[::-1] #inverte a lista
    return render_template('solicitacoesRecebidas.html', recebido = recebidas)


#Página de receber da solicitacao
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/detalhesSolicitacaoRecebida/<int:id>')
def detalhesSolicitacaoRecebida(id):
    solicitacao = solicitacao_service.buscarSolicitacoesRecebidas(id, unica=True)
    produtos = solicitacao_service.buscarProdutosRecebidos(id)
    for produto in produtos:
        produto['quantidade_produto'] = Decimal(str(produto['quantidade_produto']))
        valor_total = produto['valor_produto'] * produto['quantidade_produto']
        produto['valor_total'] = valor_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return render_template('detalhesSolicitacaoRecebida.html', solicitacao=solicitacao, produtos=produtos)

@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/api/recebidos')
def api_recebidos():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    dados = solicitacao_service.buscarSolicitacoesRecebidas(data_inicio=data_inicio, data_fim=data_fim)
    return jsonify(dados)

#Página lista de produtos
@bp_admin.route('/produtos')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def produtos():
    return render_template('produtos.html')

#PRODUTOS
@bp_admin.route('/cadastroProduto', methods=['GET', 'POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def cadastroProduto():
    #setores = solicitacao_service.buscar_setores()
    if request.method == "POST":
        produto = {}
        produto['nome_produto'] = request.form['nome_produto']
        produto['descricao_produto'] = request.form['descricao_produto']
        produto['codigo_interno_produto'] = request.form['codigo_interno_produto']
        produto['unidade_medida_produto'] = request.form['unidade_medida_produto']
        produto['preco_unitario_produto'] = request.form['preco_unitario_produto']
        #produto['categoria_id'] = request.form['categoria_id']
        produto['status_produto'] = request.form['status_produto']
        produto['fabricante_produto'] = request.form['fabricante_produto']
        produto['estoque_produto'] = request.form['estoque_produto']
        produto['estoque_minimo_produto'] = request.form['estoque_minimo_produto']

        solicitacao_service.cadastrar_produto(produto)
    return render_template("cadastroProduto.html", produto=None, action_url=url_for('admin.cadastroProduto'))


@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/api/produtos')
def api_produtos():
	pagina = int(request.args.get("page", 1))
	por_pagina = int(request.args.get("per_page", 10))
	busca = request.args.get("busca", "").lower()
	ocultar_inativos = request.args.get("ocultar_inativos", "true").lower() in ("true", "1", "yes")

	produtos = solicitacao_service.buscar_produtos(pagina, por_pagina, ocultar_inativos, busca)

	if busca:
		produtos = [p for p in produtos if busca in p["nome_produto"].lower() or busca in p["codigo_interno_produto"].lower()]

	total = solicitacao_service.contar_total_produtos(ocultar_inativos, busca)
	return jsonify({
		"produtos": produtos,
		"total": total,
		"pagina": pagina,
		"por_pagina": por_pagina
	})

@bp_admin.route('/editarProduto/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def editarProduto(id):
    produto_resultado = solicitacao_service.buscar_produto_unico(id)
    produto = produto_resultado[0] if produto_resultado else None
    return render_template('cadastroProduto.html', produto=produto, action_url=url_for('admin.gravaEditarProduto', id=id))

@bp_admin.route('/gravaEditarProduto/<int:id>', methods=['POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def gravaEditarProduto(id):
    if request.method == "POST":
        produto = {}
        produto['nome_produto'] = request.form['nome_produto']
        produto['descricao_produto'] = request.form['descricao_produto']
        produto['codigo_interno_produto'] = request.form['codigo_interno_produto']
        produto['unidade_medida_produto'] = request.form['unidade_medida_produto']
        produto['preco_unitario_produto'] = request.form['preco_unitario_produto']
        # produto['categoria_id'] = request.form['categoria_id']
        produto['status_produto'] = request.form['status_produto']
        produto['fabricante_produto'] = request.form['fabricante_produto']
        # produto['estoque_produto'] = request.form['estoque_produto']
        produto['estoque_minimo_produto'] = request.form['estoque_minimo_produto']

        solicitacao_service.editar_produto(produto, id)
    return render_template("cadastroProduto.html", produto = produto)

@bp_admin.route('/entradaProduto')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def entradaProduto():
    produtos = solicitacao_service.buscar_produtos_basico()
    return render_template('entradaProduto.html', produtos=produtos)

@bp_admin.route('/gravarEntradaProduto', methods=['POST'])
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def gravarEntradaProduto():
	id_produto = int(request.form['id_produto'])
	quantidade = float(request.form['quantidade'].replace(',', '.'))  # garante compatibilidade com vírgula
	descricao = request.form.get('descricao', '') or request.form.get('observacao', '')  # cobre ambos nomes
	id_usuario = session["user_id"]

	solicitacao_service.movimentacao_produto(id_produto, quantidade, descricao, id_usuario, 'Entrada')
	return redirect(url_for('admin.entradaProduto'))

#Página lista de produtos
@bp_admin.route('/movimentacaoProdutos')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def movimentacaoProdutos():
    return render_template('movimentacaoProdutos.html')

@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/api/movimentacaoProdutos')
def api_movimentacao_produtos():
	pagina = int(request.args.get("page", 1))
	por_pagina = int(request.args.get("per_page", 10))
	busca = request.args.get("busca", "").lower()

	movimentacoes = solicitacao_service.buscar_movimentacao_produtos(pagina, por_pagina, busca)
	total = solicitacao_service.contar_total_movimentacoes(busca)

	# Garante retorno com apenas os campos desejados
	movimentacoes_formatadas = [{
		"id_movimentacao": m["id_movimentacao"],
		"nome_produto": m["nome_produto"],
		"tipo_movimentacao": m["tipo_movimentacao"],
		"quantidade": m["quantidade"],
		"data_movimentacao": m["data_movimentacao"].strftime("%Y-%m-%d %H:%M:%S"),
		"nome_setor": m.get("nome_setor") or "—",
		"nome_usuario": m.get("nome_usuario") or "—"
	} for m in movimentacoes]

	return jsonify({
		"movimentacoes": movimentacoes_formatadas,
		"total": total,
		"pagina": pagina,
		"por_pagina": por_pagina
	})

@bp_admin.route('/api/movimentacaoDetalhes/<int:id>')
@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
def api_detalhes_movimentacao(id):
	resultado = solicitacao_service.detalhes_movimentacao_produto(id)
	return jsonify(resultado or {})