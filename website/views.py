from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import *

views = Blueprint('views',__name__)

#HOME
@views.route('/')
@login_required
def home():
    return render_template("home.html", usuario=current_user)

@views.route('/carteira', methods=["GET","POST"])
@login_required
def carteira():
    acoes = Acao.query.filter_by(usuario_id=current_user.id)
    carteira = Carteira.query.filter_by(usuario_id=current_user.id).first()
    return render_template("Carteira/carteira.html", usuario=current_user, acoes=acoes, carteira=carteira)

@views.route('/add-acao', methods=["GET","POST"])
@login_required
def add_acao():
    if request.method == "POST":
        ticker = request.form.get('ticker')
        preco_pago = float(request.form.get('preco_pago'))
        quantidade = int(request.form.get('quantidade'))
        data_compra_str = request.form.get('dataCompra')
        descricao = request.form.get('descricao')
        Usuario.addAcao(current_user, ticker, preco_pago, quantidade, descricao, data_compra_str)

    return render_template("Carteira/add_acao.html", usuario=current_user)