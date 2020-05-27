import pathlib
import os
import pandas as pd
from datetime import datetime

def get_signal():
    buy_list = []
    sell_list = []
    date = ''

    directory = pathlib.Path.cwd() / 'csv_export'
    file_list = [file for file in os.listdir(directory) if file.endswith('.csv')]
    for csv in file_list:
        file = pd.read_csv(directory / csv)
        length = len(file.index)
        if file.loc[length-1, 'buy_sell'] == 'buy':
            buy_list.append(csv[:-4])
        if file.loc[length-1, 'buy_sell'] == 'sell':
            sell_list.append(csv[:-4])
        date = file.loc[length-1, 'date_time']

    return date, buy_list, sell_list


def print_signals(date, buy_list, sell_list):
    header = 'Colour Candlestick Signals for {} Market Close: \n=======================================================\n'.format(date)
    if len(buy_list) == 0:
        buy_message = 'Buy Signals: \n \tThere are no buy signals today\n'
    else:
        buy_message = 'Buy Signals: \n'
        for item in buy_list:
            hld, rt, classification = stock_summary(int(item))
            buy_message += '\t'
            buy_message += item
            buy_message += '\n'
            buy_message += '\t\tAvg Holding: '
            buy_message += str(hld)
            buy_message += '\n'
            buy_message += '\t\tAvg Return: '
            buy_message += str(rt)
            buy_message += '\n'
            buy_message += '\t\tClassification: '
            buy_message += str(classification)
            buy_message += '\n'
    if len(sell_list) == 0:
        sell_message = 'Sell Signals: \n \tThere are no sell signals today'
    else:
        sell_message = 'Sell Signals: \n'
        for item in sell_list:
            sell_message += '\t'
            sell_message += item
            sell_message += '\n'

    return header + buy_message + sell_message


def stock_summary(stock_code):
    prpe = [6, 12, 66, 101, 688, 883, 1044, 1113]
    neg = [1, 17, 19, 267, 386, 762, 941, 1997, 3328, 3988]
    nege = [2, 388, 823, 2313, 2382]
    directory = pathlib.Path.cwd() / 'trade_list'
    trade_summary = pd.read_csv(directory / 'trade_list.csv')
    trade_summary = trade_summary.loc[trade_summary['stock'] == stock_code]
    holding = 0
    count = 0
    pnl = 0
    classification = None
    for item in trade_summary.index:
        date_format = '%Y-%m-%d'
        d1 = datetime.strptime(trade_summary.loc[item, 'exit_time'], date_format)
        d0 = datetime.strptime(trade_summary.loc[item, 'entry_time'], date_format)
        delta = d1 - d0
        pnl += trade_summary.loc[item, 'pnl']
        delta = d1 - d0
        holding += int(delta.days)
        count += 1

        bt1 = pd.read_csv('trade_export/bt_2019-01-01.csv')
        bt2 = pd.read_csv('trade_export/bt_2018-01-01.csv')
        bt5 = pd.read_csv('trade_export/bt_2015-01-01.csv')
        bt10 = pd.read_csv('trade_export/bt_2010-01-01.csv')

        bh1 = pd.read_csv('trade_export/bh_2019-01-01.csv')
        bh1.columns = ['stock', 'returns']
        bh2 = pd.read_csv('trade_export/bh_2018-01-01.csv')
        bh2.columns = ['stock', 'returns']
        bh5 = pd.read_csv('trade_export/bh_2015-01-01.csv')
        bh5.columns = ['stock', 'returns']
        bh10 = pd.read_csv('trade_export/bh_2010-01-01.csv')
        bh10.columns = ['stock', 'returns']

        bt1 = bt1.loc[bt1['stock'] == item]
        bt1_out = 1
        for profit in bt1['pnl']:
            bt1_out *= (1 + profit)
        bt1_out -= 1

        bt2 = bt2.loc[bt2['stock'] == item]
        bt2_out = 1
        for profit in bt2['pnl']:
            bt2_out *= (1 + profit)
        bt2_out -= 1

        bt5 = bt5.loc[bt5['stock'] == item]
        bt5_out = 1
        for profit in bt5['pnl']:
            bt5_out *= (1 + profit)
        bt5_out -= 1

        bt10 = bt10.loc[bt10['stock'] == item]
        bt10_out = 1
        for profit in bt10['pnl']:
            bt10_out *= (1 + profit)
        bt10_out -= 1

        bh1 = bh1.loc[bh1['stock'] == item]
        bh2 = bh2.loc[bh2['stock'] == item]
        bh5 = bh5.loc[bh5['stock'] == item]
        bh10 = bh10.loc[bh10['stock'] == item]

        if stock_code in prpe:
            classification = 'Confident: Historically +ve Return, +ve Excess Return\n'
        elif stock_code in neg:
            classification = 'Mild: Historically -ve Return, +ve Excess Return\n'
        elif stock_code in nege:
            classification = 'Mild: Historically +ve Return, -ve Excess Return\n'
        else:
            classification = 'Mild\n'
    avg_holding = round(holding/count)
    avg_return = str(round(pnl/count*100, 3)) + '%'
    return avg_holding, avg_return, classification


if __name__ == '__main__':
    x, y, z = get_signal()
    print(print_signals(x, y, z))
