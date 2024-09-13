from flask import flash, redirect, url_for
from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from . import admin
from sqlalchemy import desc
import yfinance as yf
import datetime


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    nome = db.Column(db.String(150))
    compra_acao = db.relationship('CompraAcao')
    acao = db.relationship('Acao')
    carteira = db.relationship('Carteira')

    def VerUsuario(usuario_id):
        return Usuario.query.filter_by(id=usuario_id).first()
    
    def addAcao(self, ticker, preco_pago, quantidade, descricao, data_compra_str):
        ticker = ticker.upper()
        acao_query = Acao.query.filter_by(ticker=ticker).filter_by(usuario_id=self.id).first()
        if acao_query:
            ativo = yf.Ticker(ticker+".SA")
            preco_atual = round(ativo.history(period='1d')['Close'].iloc[0], 2)
            valor_pago = round(preco_pago*quantidade, 2)
            acao_query.quantidade = acao_query.quantidade + quantidade
            acao_query.preco_medio = round((acao_query.valor_pago+valor_pago)/(acao.quantidade), 2)
            acao_query.valor_pago = round(acao_query.valor_pago + valor_pago, 2)
            acao_query.valor_atual = round(preco_atual*acao_query.quantidade, 2)
            acao_query.lucro_prejuizo = round(acao_query.valor_atual - acao.valor_pago, 2)
            acao_query.rentabilidade = round(acao_query.lucro_prejuizo/acao.valor_pago*100, 2)
            if acao_query.rentabilidade > 0:
                acao_query.status = "lucro"
            elif acao_query.rentabilidade == 0:
                acao_query.status = "zero"
            else:
                acao_query.status = "prejuizo"
            db.session.commit()

            data_compra = datetime.strptime(data_compra_str, '%Y-%m-%d')
            nova_compra = CompraAcao(ticker = ticker, preco_pago = preco_pago, quantidade = quantidade, valor_pago = valor_pago, data_compra = data_compra, usuario_id = self.id)
            hist_acao = Historico(usuario_id = self.id, ticker=ticker, descricao=descricao, quantidade=quantidade, preco = preco_pago, valor = valor_pago, tipo = "compra", data = data_compra)
            db.session.add(nova_compra)
            db.session.add(hist_acao)
            db.session.commit()
            flash(f"Mais {quantidade} acoes foram adicionadas a {acao.ticker}")
            return redirect(url_for('views.add_acao'))
        else:
            valor_pago = round(preco_pago*quantidade, 2)
            acao = yf.Ticker(ticker+".SA")
            preco_atual = round(acao.history(period='1d')['Close'].iloc[0], 2)
            valor_atual = round(preco_atual*quantidade, 2)
            lucro_prejuizo = round(valor_atual-valor_pago, 2)
            rentabilidade = round(lucro_prejuizo/valor_pago*100, 2)
            data_compra = datetime.strptime(data_compra_str, '%Y-%m-%d')
            if rentabilidade > 0:
                status = "lucro"
            elif rentabilidade == 0:
                status = "zero"
            else:
                status = "prejuizo"
            nova_compra = CompraAcao(ticker = ticker, preco_pago = preco_pago, quantidade = quantidade, valor_pago = valor_pago, data_compra = data_compra, usuario_id = self.id)
            acao = Acao(ticker = ticker, preco_medio = preco_pago, quantidade = quantidade, valor_pago = valor_pago, preco_atual = preco_atual, valor_atual= valor_atual,rentabilidade = rentabilidade, lucro_prejuizo=lucro_prejuizo, status = status, usuario_id = self.id)
            hist_acao = Historico(usuario_id = self.id, ticker=ticker, descricao=descricao, quantidade=quantidade, preco_pago = preco_pago, valor_pago = valor_pago, tipo = "compra", data = data_compra)
            db.session.add(hist_acao)
            db.session.add(acao)
            db.session.add(nova_compra)
            db.session.commit()
            flash(f"{ticker} adicionada a carteira", category='success')
            return redirect(url_for('views.add_acao'))

class Carteira(db.Model):
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
    
    def verAcoes(self, usuario_id):
        return Acao.query.filter_by(usuario_id=usuario_id)

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
    data_ultimo_dividendo = db.Column(db.Date)

    def histDividends(self):
        ativo = yf.Ticker(self.ticker+".SA")
        dividend_info = ativo.dividends
        data_compra_str = self.data_compra.strftime("%Y-%m-%d")
        filtered_dividends = dividend_info[dividend_info.index >= data_compra_str]
        filtered_dividends = filtered_dividends.iloc[::-1]

        # count = 0

        # for data, dividend in filtered_dividends.items():
        #     index += 1
        #     cash_yield = round((dividend / preco) * 100, 3)
            
        #     # Formata a data
        #     data_organizada = data.strftime("%d/%m/%Y")
            
        #     # Exibe informações de cada dividendo
        #     print(f'{index} - Dividendo: R$ {dividend}, Data: {data_organizada}, Yield no Preço atual: {cash_yield} %')
        #     print('--------')
            
        #     # Acumula o total de dividendos
        #     total = round(total + dividend, 4)

class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ticker = db.Column(db.String(10))
    preco_pago = db.Column(db.Float)
    quantidade = db.Column(db.Integer)
    valor_pago = db.Column(db.Float)
    descricao = db.Column(db.String)
    tipo = db.Column(db.String)
    data = db.Column(db.Date)

class HistOperacoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ticker = db.Column(db.String(10))
    preco_compra = db.Column(db.Float)
    quantidade_compra = db.Column(db.Integer)
    valor_compra = db.Column(db.Float)
    preco_venda = db.Column(db.Float)
    quantidade_venda = db.Column(db.Integer)
    lucro_prejuizo = db.Column(db.Float)
    rentabilidade = db.Column(db.Float)
    
class HistDividendos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ticker = db.Column(db.String(10))
    quantidade = db.Column(db.Integer)
    valor_por_acao = db.Column(db.Float)
    valor = db.Column(db.Float)
    data = db.Column(db.Date)

    




admin.add_view(ModelView(Usuario, db.session))