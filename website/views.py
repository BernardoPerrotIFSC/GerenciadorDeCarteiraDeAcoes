from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import *

views = Blueprint('views',__name__)

#HOME
@views.route('/')
@login_required
def home():
    return render_template("home.html", usuario=current_user)

@views.route('/carteira', methods=["GET","POST"])
def carteira():
    acoes = Acao.verAcoes(current_user)
    carteira = Carteira.VerCarteira(current_user)
    return render_template("carteira.html", usuario=current_user, acoes=acoes, carteira=carteira)