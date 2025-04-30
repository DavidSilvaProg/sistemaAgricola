from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.solicitacao_service import SolicitacaoService
from app.services.autenticacao_service import AutenticacaoService

bp_solicitacao = Blueprint('solicitacao', __name__)
solicitacao_service = SolicitacaoService()
autenticacao_service = AutenticacaoService()

#Página inicial
@bp_solicitacao.route('/')
@autenticacao_service.login_required
def index():
    return redirect(url_for("solicitacao.solicitacoesCompra"))

#Página de solicitações de compra
@bp_solicitacao.route('/solicitacoesCompra')
@autenticacao_service.login_required
def solicitacoesCompra():
    solicitacoes = solicitacao_service.buscar_solicitacoes()[::-1] #inverte a lista
    return render_template('solicitacoesCompra.html', pedidos = solicitacoes, nome=session['user_nome'])

#Página de detalhes da solicitacao
@bp_solicitacao.route('/detalhesSolicitacao/<int:id>')
@autenticacao_service.login_required
def detalhesSolicitacao(id):
    solicitacao = solicitacao_service.buscar_solicitacoes(id, unica=True)
    produtos = solicitacao_service.buscar_produtos(id)
    return render_template('detalhesSolicitacao.html', solicitacao=solicitacao, produtos=produtos)

#Página de cadastro de solicitações de compras, carrega dados de produtos e setores
@bp_solicitacao.route('/cadastroSolicitacao')
@autenticacao_service.login_required
def cadastroSolicitacao():
    setores = solicitacao_service.buscar_setores()
    return render_template('cadastroSolicitacao.html', setores=setores)

#Recebe as solicitação de compra do formulário e grava no banco
@bp_solicitacao.route('/cadastrarSolicitacao', methods=['POST'])
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
    return redirect(url_for('solicitacao.cadastroSolicitacao'))

@bp_solicitacao.route('/setores')
@autenticacao_service.login_required
def setores():
    setores = solicitacao_service.buscar_setores()[::-1] #inverte a lista
    return render_template('setores.html', setores = setores, nome=session['user_nome'])

