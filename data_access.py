import io

import pandas as pd
import requests


def get_stock_price_from_old_source(stock_code, exchange='sehk', date_from=None):
    r = requests.get('http://data.invbots.com/api/stock_price_daily',
                     params={'stock_code': stock_code,
                             'exchange': exchange,
                             'date_from': date_from})

    df = pd.read_csv(io.StringIO(r.text))
    df = df.dropna(axis=0, how='all', subset=['open', 'high', 'low', 'close', 'adj_close', 'volume'])
    df = df.sort_values(by='date_time', ascending=True)
    df = df.reset_index(drop=True)
    return df


def get_stock_price_from_wind(ticker, location='hk', date_from=None):
    r = requests.get('http://api.invbots.com/data/v1/stock/{location}/{ticker}/price'.format(location=location, ticker=ticker),
                     params={'start_date': date_from})

    df = pd.DataFrame(r.json())
    df = df.dropna(axis=0, how='all', subset=['open', 'high', 'low', 'close',  'volume'])
    df = df.sort_values(by='date_time', ascending=True)
    df = df.reset_index(drop=True)
    return df


def get_stock_price (stock_code, location='hk', date_from=None):
    # switch btw source
    df = get_stock_price_from_wind(stock_code, location=location, date_from=date_from)
    return df


def symbol_sehk () :
    r = requests.get('http://178.128.217.137/api/v1/stocks/sehk')
    symbol_df = pd.DataFrame(r.json()['ticker'], columns=['ticker'])
    symbol_df = symbol_df[~symbol_df.ticker.str.contains('!')]
    return symbol_df


if __name__ == '__main__':

    # df = get_stock_price(700)
    # testing
    ticker_list = pd.read_csv('./ticker_list/Nasdaq100.csv').ticker.tolist()
    for ticker_ in ticker_list :
        print('ticker: ', ticker_)
        df = get_stock_price_from_wind(ticker_, 'us', date_from='2018-01-01')
        if len(df) == 0:
            print(ticker_, '-------------no data------------')
        else:
            print(ticker_, '-------------has data-----------')


