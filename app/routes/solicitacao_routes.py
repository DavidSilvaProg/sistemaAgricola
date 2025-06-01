from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.services.solicitacao_service import SolicitacaoService
from app.services.autenticacao_service import AutenticacaoService
from datetime import date
from dateutil.relativedelta import relativedelta

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
    solicitacoes = solicitacao_service.buscar_solicitacoes(ocultar_recebidos=True, ocultar_cancelados=True)[::-1] #inverte a lista
    return render_template('solicitacoesCompra.html', pedidos = solicitacoes, nome=session['user_nome'])

#Página de detalhes da solicitacao
@bp_solicitacao.route('/detalhesSolicitacao/<int:id>')
@autenticacao_service.login_required
def detalhesSolicitacao(id):
    solicitacao = solicitacao_service.buscar_solicitacoes(id, unica=True)
    produtos = solicitacao_service.buscar_produtos_solicitacao(id)
    return render_template('detalhesSolicitacao.html', solicitacao=solicitacao, produtos=produtos)

#Página de cadastro de solicitações de compras, carrega dados de produtos e setores
@bp_solicitacao.route('/cadastroSolicitacao')
@autenticacao_service.login_required
def cadastroSolicitacao():
    setores = solicitacao_service.buscar_setores()
    produtos = solicitacao_service.buscar_produtos_basico()
    return render_template('cadastroSolicitacao.html', produtos=produtos, setores=setores)

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
            unidade = request.form.get(f'unidade{numero}')
            quantidade = request.form.get(f'quantidade{numero}')
            produtos.append({'produto': valor, 'quantidade': quantidade, 'unidade': unidade})
    prioridade = request.form['prioridade']
    id = session["user_id"]
    solicitacao_service.incluirSolicitacao(nome, setor, produtos, prioridade, id)
    return redirect(url_for('solicitacao.cadastroSolicitacao'))

@bp_solicitacao.route('/setores')
@autenticacao_service.login_required
def setores():
    setores = solicitacao_service.buscar_setores()[::-1] #inverte a lista
    return render_template('setores.html', setores = setores, nome=session['user_nome'])

@bp_solicitacao.route('/api/solicitacoes')
@autenticacao_service.login_required
def api_solicitacoes():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    status = request.args.get('status')
    busca = request.args.get('busca', '').lower()
    ocultar_cancelados = request.args.get('ocultar_cancelados') == 'true'
    ocultar_recebidos = request.args.get('ocultar_recebidos') == 'true'

    resultado = solicitacao_service.buscar_solicitacoes(
        data_inicio = data_inicio,
        data_fim = data_fim,
        status = status,
        ocultar_cancelados = ocultar_cancelados,
        ocultar_recebidos = ocultar_recebidos,
        busca = busca
    )[::-1]

    return jsonify(resultado)