import yfinance as yf
from datetime import datetime

def dividendos(ticker, data):
    ativo = yf.Ticker(ticker+".SA")
    dividend_info = ativo.dividends
    data_formatada = data.strftime("%Y-%m-%d")
    filtered_dividends = dividend_info[dividend_info.index >= data_formatada]
    total = 0
    count = -1
    index = 0
    total_dividendos = 0
    for i in filtered_dividends:
        dividendo = round(dividend_info.iloc[count], 4)
        dividendos = dividendos + dividendo
        data_div = dividend_info.index[count]
        data_div_organizada = data_div.strftime("%d-%m-%Y")
        cotacao_dividendo = round(ativo.history(start=data, end=data)['Close'].iloc[0], 2)
        cash_yield = round((dividendo/cotacao_dividendo)*100)
        print(f'Valor Dividendo: R$ {dividendo}')
        print(f'Data Dividendo: {data_div_organizada}')
        print(f'Cotacao data Dividendo: R$ {cotacao_dividendo}')
        print(f'CashYield: {cash_yield} %')
        count = count - 1
    print("------")
    print(f"Total pago por acao: R$ {total_dividendos}")
    
    
if __name__ == "__main__":
    dividendos("rani3", "2021-12-13")
    
