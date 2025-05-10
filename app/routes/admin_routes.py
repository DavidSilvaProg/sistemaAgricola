from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.autenticacao_service import AutenticacaoService
from app.services.solicitacao_service import SolicitacaoService
from werkzeug.security import generate_password_hash

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
    produtos = solicitacao_service.buscar_produtos(id)
    return render_template('receberSolicitacao.html', solicitacao=solicitacao, produtos=produtos, action_url=url_for('admin.registrarRecebimentoSolicitacao', id=id))

@autenticacao_service.login_required
@autenticacao_service.nivel_required('administrador')
@bp_admin.route('/registrarRecebimentoSolicitacao/<int:id>', methods=['POST'])
def registrarRecebimentoSolicitacao(id):
    if request.method == "POST":
        if solicitacao_service.verificaRecebido(id):
            data = request.form["data_recebimento"]
            produtos = []
            for chave, valor in request.form.items():
                if chave.startswith('produto'):
                    numero = chave.replace('produto', '')
                    quantidade = request.form.get(f'quantidade{numero}')
                    preco = request.form.get(f'preco{numero}')
                    produtos.append({'produto': valor, 'quantidade': quantidade, 'preco': preco})
            solicitacao_service.incluirRecebimento(id, data, produtos)
            solicitacao_service.editarStatusSolicitacao('Recebido', id)
    return redirect(url_for("admin.solicitacoesRecebidas"))

#Página de solicitações de compra
@bp_admin.route('/solicitacoesRecebidas')
@autenticacao_service.login_required
def solicitacoesRecebidas():
    recebidas = solicitacao_service.buscarSolicitacoesRecebidas()[::-1] #inverte a lista
    return render_template('solicitacoesRecebidas.html', recebido = recebidas)
