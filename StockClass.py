import pandas as pd
import urllib.request
import json
import seaborn as sns
import plotly.express as px


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker

    def get_stock_candles(self):
        # Запрашиваются дневные свечи по инструменту с начала 2013 года
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}
        self.df_combined = pd.DataFrame(columns = ['open', 'close', 'high', 'low', 'value', 'volume', 'date', 'end']).set_index('date')
        
        for i in range(0, 5):
            query_string = f'http://iss.moex.com/iss/engines/stock/markets/shares/boards/tqbr/securities/{self.ticker}/candles.json?from=2013-01-01&interval=24&start={(i)*500}'
            
            with urllib.request.urlopen(query_string) as url:
                data = json.loads(url.read().decode())['candles']['data']
                
            df = pd.DataFrame(data, columns = ['open', 'close', 'high', 'low', 'value', 'volume', 'date', 'end']).set_index('date')
            self.df_combined = pd.concat([self.df_combined, df])
    
        return self.df_combined
    
    def indicators(self):
        # Рассчитываются индикаторы SMA50, SMA200 и RSI
        self.get_stock_candles()
        df = self.df_combined
        df['SMA50'] = df['close'].rolling(50, center = True).mean()
        df['SMA200'] = df['close'].rolling(200, center = True).mean()
        
        chg = df['close'].diff(1) / df['close'] * 100
        gain = chg.mask(chg < 0, 0)
        df['gain'] = gain
        loss = chg.mask(chg > 0, 0)
        df['loss'] = loss * (-1)        

        df['avg_gain'] = df['gain'].rolling(14).mean()
        df['avg_loss'] = df['loss'].rolling(14).mean()
        df['RSI'] = 100 - 100 / (1+ (df['avg_gain'] / df['avg_loss'] ))
        self.df_modified = df
        return self.df_modified
    
    def draw_plots(self):
        self.indicators()
        df = self.df_modified
        self.fig = px.line(df, x = df.index, y= [df.SMA50, df.SMA200, df.RSI])
        return self.fig    
    
    def correlation(self):
        self.indicators()
        df = self.df_modified[['SMA50','SMA200', 'RSI']]
        corr = df.corr()
        self.plot = sns.heatmap(df.corr(), annot=True)
        return self.plot
    
    if __name__ == '__main__':
        print('Имя модуля: ', __name__)

