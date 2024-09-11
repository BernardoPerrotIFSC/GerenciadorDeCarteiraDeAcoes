from flask import flash
from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from . import admin
from sqlalchemy import desc
import yfinance as yf


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    nome = db.Column(db.String(150))

    def VerUsuario(usuario_id):
        return Usuario.query.filter_by(usuario_id=usuario_id).first()

class Carteira(db.model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    valor_pago = db.Column(db.Float, default=0.0)
    valor_atual = db.Column(db.Float, default=0.0)
    lucro_prejuizo = db.Column(db.Float, default=0.0)
    rentabilidade = db.Column(db.Float, default=0.0)
    total_dividendos = db.Column(db.Float, default=0.0)
    retorno_dividendos = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(8), default="zero")

    def VerCarteira(self, usuario_id):
        return Carteira.query.filter_by(usuario_id=usuario_id).first()

    def atualizarCarteira(self, valor_pago, valor_atual, lucro_prejuizo):
        self.valor_pago = valor_pago
        self.valor_atual = valor_atual
        self.lucro_prejuizo = round(valor_atual - valor_pago, 2)
        self.rentabilidade = round(lucro_prejuizo/valor_atual*100, 2)
        if lucro_prejuizo == 0:
            self.status = "zero"
        elif lucro_prejuizo > 0:
            self.status = "lucro"
        else:
            self.status = "prejuizo"
        
    def atualizarDividendos(self, valor_dividendos):
        if self.total_dividendos == 0:
            self.total_dividendos = valor_dividendos
        else:
            self.total_dividendos += valor_dividendos
        self.retorno_dividendos = round((self.total_dividendos/self.valor_pago)*100, 2)
        db.session.commit()

class Acao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ticker = db.Column(db.String(10))
    preco_medio = db.Column(db.Float)
    quantidade = db.Column(db.Integer)
    valor_pago = db.Column(db.Float)
    preco_atual = db.Column(db.Float)
    valor_atual = db.Column(db.Float)
    peso = db.Column(db.Float)
    lucro_prejuizo = db.Column(db.Float)
    rentabilidade = db.Column(db.Float)
    status = db.Column(db.String(10))
    investidor10 = db.Column(db.String)
    trading_view = db.Column(db.String)
    total_dividendos = db.Column(db.Float)
    retorno_dividendos = db.Column(db.Float)

    def verAcao(self, usuario_id):
        return Acao.query.filter_by(usuario_id=usuario_id).first()

    def atualizaAcao(self, valor_total_careira):
        ativo = yf.Ticker(self.ticker+".SA")
        self.preco_atual = round(ativo.history(period='1d')['Close'].iloc[0], 2)
        self.valor_atual = round(self.quantidade*self.preco, 2)
        self.lucro_prejuizo = round(self.valor_atual-self.valor_pago, 2)
        self.rentabilidade = round(self.lucro_prejuizo/self.valor_pago*100, 2)
        if self.lucro_prejuizo == 0:
            self.status = "zero"
        elif self.lucro_prejuizo > 0:
            self.status = "lucro"
        else:
            self.status = "prejuizo"
        self.peso = round((self.valor_atual/valor_total_careira)*100)
        db.session.commit()

    def editAcao(self, preco_medio, quantidade):
        self.preco_medio = preco_medio
        self.quantidade = quantidade
        db.session.commit()
        
    def removeAcaoCriaHist(self, preco_venda, quantidade, descricao, data_venda):
        if preco_venda <=0:
            flash("Preço ou quantidade não foram encontradas", category='error')
        elif quantidade > self.quantidade:
            flash("Ação ou quantidade não foram encontradas", category='error')
        elif quantidade <self.quantidade:
            return False
            #Funcao deve atualizar os dividendos primeiro
        elif quantidade == self.quantidade:
            #Funcao deve atualizar os dividendos primeiro
            return False
            

class CompraAcao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ticker = db.Column(db.String(10))
    preco_pago = db.Column(db.Float)
    quantidade = db.Column(db.Integer)
    valor_pago = db.Column(db.Float)
    descricao = db.String(db.String)
    data_compra = db.Column(db.Date)
    


admin.add_view(ModelView(Usuario, db.session))