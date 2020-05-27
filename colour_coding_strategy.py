import pandas as pd
import numpy as np
import mpl_finance
import matplotlib.pyplot as plt
import pathlib
from datetime import date
from candlestick_lib import *
from data_access import *
from colour_candlestick_signal import *
from utils.message_hub.app import *


def pnl_plotter(df, price, stock_code):
    plt_df = pd.DataFrame()
    underlying_df = price['close']
    underlying_df.index = price['date_time']
    underlying_df = underlying_df.pct_change().dropna()
    plt_df['underlying'] = np.cumproduct(underlying_df+1)
    plt_df['strategy'] = np.cumproduct(df['pnl'] + 1)
    plt_df['strategy'].ffill(inplace=True)
    plt_df['strategy'] = plt_df['strategy'].fillna(1)
    plt.plot(plt_df)
    plt.title(stock_code)
    plt.show()
    return(plt_df)


def colour_coding_plotter(input_df, stock_code, multiplier=0.2, formation_date=1):
    df = input_df.copy()
    horizontal = round(len(df)) / 20
    fig, ax = plt.subplots(figsize=(horizontal, 5))
    df['SD'] = df['close'].rolling(50).std()
    df['sdClosingPrice'] = df['close'].shift(1)
    df['multiplier'] = multiplier
    df['color'] = 'yellow'

    cp = CandlestickPattern(input_df)
    df['bullish_engulfing'] = cp.engulfing_pattern('bullish')
    df['bearish_engulfing'] = cp.engulfing_pattern('bearish')
    df['bullish_harami'] = cp.harami_pattern('bullish')
    df['bearish_harami'] = cp.harami_pattern('bearish')
    df['buy_sell'] = None

    trade_record = []

    for i in range(len(df)):
        if i < 49:
            continue
        if df.loc[i-1, 'color'] == 'yellow':
            if df.loc[i, 'close'] >= df.loc[i, 'sdClosingPrice'] + df.loc[i, 'multiplier'] * df.loc[i, 'SD']:
                df.loc[i, 'color'] = 'green'
            elif df.loc[i, 'close'] <= df.loc[i, 'sdClosingPrice'] - df.loc[i, 'multiplier'] * df.loc[i, 'SD']:
                df.loc[i, 'color'] = 'red'
            else:
                df.loc[i, 'color'] = 'yellow'
        elif df.loc[i-1, 'color'] == 'green':
            if df.loc[i, 'close'] <= df.loc[i, 'sdClosingPrice'] - df.loc[i, 'multiplier'] * df.loc[i, 'SD'] / 4 or \
                    df.loc[i, 'bullish_engulfing'] == 1 or df.loc[i, 'bullish_harami']:
                df.loc[i, 'color'] = 'yellow'
            elif df.loc[i, 'close'] >= df.loc[i, 'sdClosingPrice'] - df.loc[i, 'multiplier'] * df.loc[i, 'SD'] and not \
                    df.loc[i, 'bullish_engulfing'] == 1 and not df.loc[i, 'bearish_engulfing'] == 1 \
                    and not df.loc[i, 'bullish_harami'] and not df.loc[i, 'bearish_harami']:
                df.loc[i, 'color'] = 'green'
        elif df.loc[i-1, 'color'] == 'red':
            if df.loc[i, 'close'] <= df.loc[i, 'sdClosingPrice'] + df.loc[i, 'multiplier'] * df.loc[i, 'SD'] and not \
                    df.loc[i, 'bullish_engulfing'] == 1 and not df.loc[i, 'bearish_engulfing'] == 1 \
                    and not df.loc[i, 'bullish_harami'] and not df.loc[i, 'bearish_harami']:
                df.loc[i, 'color'] = 'red'
            elif df.loc[i, 'close'] >= df.loc[i, 'sdClosingPrice'] + df.loc[i, 'multiplier'] * df.loc[i, 'SD'] or \
                    df.loc[i, 'bearish_engulfing'] == 1 or df.loc[i, 'bearish_harami']:
                df.loc[i, 'color'] = 'yellow'
    df_name = stock_code + '.csv'

    temp = {'stock': None,
            'buy_sell': None,
            'position': 0,
            'entry_price': None,
            'entry_time': None,
            'exit_price': None,
            'exit_time': None,
            'pnl': None}
    temp['stock'] = stock_code
    for i in range(len(df)):
        if i < 49:
            continue
        if df.loc[i-2, 'color'] == 'red' and df.loc[i-1, 'color'] == 'yellow' and temp['position'] == 0:
            temp['position'] = 1
            temp['buy_sell'] = 'buy'
            temp['entry_price'] = df.loc[i, 'open']
            temp['entry_time'] = df.loc[i, 'date_time']
            df.loc[i, 'buy_sell'] = 'buy'
        if df.loc[i-2, 'color'] == 'green' and df.loc[i-1, 'color'] == 'yellow' and temp['position'] == 1:
            temp['position'] = 0
            temp['buy_sell'] = 'sell'
            df.loc[i, 'buy_sell'] = 'sell'
            temp['exit_price'] = df.loc[i, 'open']
            temp['exit_time'] = df.loc[i, 'date_time']
            temp['pnl'] = temp['exit_price'] - temp['entry_price']
            trade_record.append({'stock': temp['stock'],
                                 'entry_time': temp['entry_time'],
                                 'entry_price': temp['entry_price'],
                                 'exit_time': temp['exit_time'],
                                 'exit_price': temp['exit_price'],
                                 'pnl': (temp['exit_price'] - temp['entry_price'])/temp['entry_price']
                                 })
        if temp['buy_sell'] == 'sell':
            temp['buy_sell'] = None
            temp['position'] = 0
            temp['entry_time'] = None
            temp['entry_price'] = None
            temp['exit_time'] = None
            temp['exit_price'] = None
            temp['pnl'] = None

    df.to_csv(pathlib.Path.cwd() / 'csv_export' / df_name)
    mpl_finance.candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.6,
                                  colorup='green', colordown='red')
    temp['stock'] = None
    return trade_record


if __name__ == '__main__':
    column_list = []
    master_list = []
    mult_dict = {}
    aggregate_trade = []
    buy_hold_returns = []
    for stock in ['1', '2', '3', '5', '6', '11', '12', '16', '17', '19', '27', '66', '83', '101', '151', '175', '267',
                  '288', '386', '388', '669', '688', '700', '762', '823', '857', '883', '939', '941', '1038', '1044',
                  '1088', '1093', '1109', '1113', '1177', '1299', '1398', '1928', '1997', '2007', '2018', '2313',
                  '2318','2319', '2382', '2388', '2628', '3328', '3988']:
        column_list.append(stock)
        excess_return_list = []
        # for stock in ['SPY']:
        stock_code = stock
        # sd = mult_dict[stock]
        sd = 0.6
        start_date = '2019-01-01'
        price_data = get_stock_price(stock_code, location='hk', date_from=start_date)

        data = colour_coding_plotter(price_data, stock_code, multiplier=sd)
        # plt.show()

        pnl = 1
        trade_count = 0
        win_count = 0
        for item in data:
            pnl *= (1 + item['pnl'])
            if item['pnl'] > 0:
                win_count += 1
            trade_count += 1

        data_df = pd.DataFrame(data)
        data_df.index = data_df['exit_time'].values
        # pnl_plotter(data_df, price_data, stock)

        aggregate_trade.append(data)

        print('Testing on ' + stock_code + ' from ' + start_date + ' Mult = ' + str(sd))
        print('================================')
        algo_return = (pnl - 1)*100
        bh_return = (price_data.loc[price_data.index[-1], 'close'] - price_data.loc[0, 'close']) / price_data.loc[0, 'close'] * 100
        print('Algorithm Return: ' + str(round(algo_return, 5)) + '%')
        print('Buy and Hold Return: ' + str(round(bh_return, 5)) + '%')
        print('Trade Count: ' + str(trade_count))
        if trade_count > 0:
            print('Win Rate: ' + str(round(win_count/trade_count*100)) + '%' + '\n')
        else:
            print('No trades \n')
        excess_return_list.append(algo_return - bh_return)
        buy_hold_returns.append(bh_return/100)
        master_list.append(excess_return_list)

        trade_list_df = []
        for item in aggregate_trade:
            df = pd.DataFrame(item)
            trade_list_df.append(df)
            df.index = df['entry_time']
        output_df = pd.concat(trade_list_df)
        output_df.index = output_df['entry_time'].values
        output_df.sort_index(inplace=True)
        output_df.to_csv('trade_list/trade_list.csv')

    pnl_output = 1
    for item in output_df['pnl']:
        pnl_output *= (1 + item)
    pnl_output -= 1
    print('================================')
    print('Total Return: ' + str(pnl_output*100) + '%')
    print('================================')

    output_name = 'bt_' + start_date + '.csv'
    output_df.to_csv(pathlib.Path.cwd() / 'trade_export' / output_name)

    bh_output = 'bh_' + start_date + '.csv'
    buy_hold_returns_df = pd.DataFrame(buy_hold_returns)
    buy_hold_returns_df.index = ['1', '2', '3', '5', '6', '11', '12', '16', '17', '19', '27', '66', '83', '101', '151', '175', '267',
                  '288', '386', '388', '669', '688', '700', '762', '823', '857', '883', '939', '941', '1038', '1044',
                  '1088', '1093', '1109', '1113', '1177', '1299', '1398', '1928', '1997', '2007', '2018', '2313',
                  '2318','2319', '2382', '2388', '2628', '3328', '3988']
    buy_hold_returns_df.to_csv(pathlib.Path.cwd() / 'trade_export' / bh_output)

    x, y, z = get_signal()
    msg = print_signals(x, y, z)

    MessageHubHelper = MessageHub()

    MessageHubHelper.add_message('slack', 'testing_slack', {'text': msg})
    # MessageHubHelper.add_message('telegram', '915653846', {'text': msg})
    MessageHubHelper.post_all()
