from data_access import *
import pandas as pd
from candlestick_lib import *
from itertools import product
import numpy as np
import json

def next_open(date, stock_price):
    # Return the open price of the next day
    try:
        if (stock_price[stock_price['date_time'] == date].index.tolist())[0] + 1 <= len(stock_price):
            price = stock_price.loc[(stock_price[stock_price['date_time'] == date].index.tolist())[0] + 1, 'open']
            return price
    except:
        return
    else:
        return

def next_high(date, stock_price):
    # Return the high price of the next day
    try:
        if (stock_price[stock_price['date_time'] == date].index.tolist())[0] + 1 <= len(stock_price):
            price = stock_price.loc[(stock_price[stock_price['date_time'] == date].index.tolist())[0] + 1, 'high']
            return price
    except:
        return
    else:
        return

def next_low(date, stock_price):
    # Return the low price of the next day
    try:
        if (stock_price[stock_price['date_time'] == date].index.tolist())[0] + 1 <= len(stock_price):
            price = stock_price.loc[(stock_price[stock_price['date_time'] == date].index.tolist())[0] + 1, 'low']
            return price
    except:
        return
    else:
        return

def price_after_n_days(date, stock_price, n):
    # Return the close price of n days after the given date
    try:
        if (stock_price[stock_price['date_time'] == date].index.tolist())[0] + n <= len(stock_price):
            price = stock_price.loc[(stock_price[stock_price['date_time'] == date].index.tolist())[0] + n, 'close']
            return price
    except:
        return
    else:
        return

def date_after_n_days(date, stock_price, n):
    # Return the date of n trading days after the given date
    try:
        if (stock_price[stock_price['date_time'] == date].index.tolist())[0] + n <= len(stock_price):
            new_date = stock_price.loc[(stock_price[stock_price['date_time'] == date].index.tolist())[0] + n, 'date_time']
            return new_date
    except:
        return
    else:
        return

def performance(dfInput):
    df = dfInput.copy()
    annotateTargets = df.loc[df.iloc[:, -1] == True, ['date_time', 'open', 'close']]
    try:
        annotateTargets['next_open'] = annotateTargets.apply(lambda x: next_open(x.date_time, df), axis=1)
        annotateTargets['one_day_after'] = annotateTargets.apply(lambda x: price_after_n_days(x.date_time, df, 1), axis=1)
        annotateTargets['one_week_after'] = annotateTargets.apply(lambda x: price_after_n_days(x.date_time, df, 6), axis=1)
        annotateTargets['one_month_after'] = annotateTargets.apply(lambda x: price_after_n_days(x.date_time, df, 21), axis=1)
        annotateTargets['one_day_return'] = annotateTargets['close'] / annotateTargets['next_open'] - 1
        annotateTargets['one_week_return'] = annotateTargets['one_week_after'] / annotateTargets['next_open'] - 1
        annotateTargets['one_month_return'] = annotateTargets['one_month_after'] / annotateTargets['next_open'] - 1
        prob_one_day = len(annotateTargets.loc[annotateTargets['one_day_return'] > 0]) / (len(annotateTargets)
                                                                                        - annotateTargets.one_day_return.isna().sum())
        prob_one_week = len(annotateTargets.loc[annotateTargets['one_week_return'] > 0]) / (len(annotateTargets)
                                                                                            - annotateTargets.one_week_return.isna().sum())
        prob_one_month = len(annotateTargets.loc[annotateTargets['one_month_return'] > 0]) / (len(annotateTargets)
                                                                                            - annotateTargets.one_month_return.isna().sum())
        average_one_day = annotateTargets['one_day_return'].mean()
        average_one_week = annotateTargets['one_week_return'].mean()
        average_one_month = annotateTargets['one_month_return'].mean()
        return prob_one_day, prob_one_week, prob_one_month, average_one_day, average_one_week, average_one_month
    except:
        pass


def generate_trade_records(price_df, annotate_targets, n):
    # Generate Trading Records
    trade_records = []
    for date in list(annotate_targets.date_time):
        # if date for signal release with
        if (price_df[price_df['date_time'] == date].index.tolist())[0] + n > len(price_df):
            continue

        trading_details = {'date': date_after_n_days(date, price_df, n)}
        trading_details['price'] = next_open(date, price_df)
        trading_details['quantity'] = 100
        trading_details['action'] = 'B'
        trade_records.append(trading_details)

        trading_details = {'date': date_after_n_days(date, price_df, n)}
        trading_details['price'] = price_after_n_days(date, price_df, n)
        trading_details['quantity'] = 100
        trading_details['action'] = 'S'
        trade_records.append(trading_details)
    return trade_records

def generate_trade_statistics(trade_records, annotate_targets, price_df, n, holding_time):
    trade_stat = {}
    initial_capital = 100000
    gain = 0
    loss = 0
    win = 0
    lose = 0
    num_of_win = 0
    num_of_lose = 0
    trade_stat['num_of_trade'] = len(trade_records)
    trade_stat['initial_trade_capital'] = initial_capital

    capital = initial_capital
    for trade in trade_records:
        if trade['action'] == 'B':
            capital -= trade['price'] * trade['quantity']
        if trade['action'] == 'S':
            capital += trade['price'] * trade['quantity']
    trade_stat['net_profit'] = capital - initial_capital

    for date in list(annotate_targets.date_time):
        if (price_df[price_df['date_time'] == date].index.tolist())[0] + n > len(price_df):
            continue

        if price_after_n_days(date, price_df, n) >= next_open(date, price_df):
            gain += 100 * (price_after_n_days(date, price_df, n) - next_open(date, price_df))
            num_of_win += 1
            win = max(100 * (price_after_n_days(date, price_df, n) - next_open(date, price_df)),
                      win)
        if price_after_n_days(date, price_df, n) < next_open(date, price_df):
            loss -= 100 * (price_after_n_days(date, price_df, n) - next_open(date, price_df))
            num_of_lose += 1
            lose = max(- 100 * (price_after_n_days(date, price_df, n) - next_open(date, price_df)),
                       lose)

        if holding_time != 'day_trading':
            drawdown = 0
            high_list = []
            low_list = []
            for k in range(n):
                high_list.append(next_high(date, price_data))
                low_list.append(next_low(date, price_data))
                date = date_after_n_days(date, price_data, 1)
            for k in range(n):
                for j in range(k, n):
                    drawdown = max(100 * (low_list[j] - high_list[k]), drawdown)
            trade_stat['max_drawdown'] = drawdown

    try:
        trade_stat['avg_winning_trade'] = gain / num_of_win
    except:
        trade_stat['avg_winning_trade'] = 'nan'
    try:
        trade_stat['avg_winning_trade'] = loss / num_of_lose
    except:
        trade_stat['avg_winning_trade'] = 'nan'
    trade_stat['largest_winning_trade'] = win
    trade_stat['largest_losing_trade'] = lose
    trade_stat['avg_holding_time_per_trade'] = 1
    return trade_stat


def buy_at(price ,at='open') :
    if price['entry_signal'] == True:
        return price[at]
    else :
        return None
def sell_at(price, at='close'):
    if price['exit_signal'] == True:
        return price[at]
    else:
        return None

class TradePerformance :
    def __init__ (self, price_df, initial_capital=100000, initial_quantity=0, quantity=100):
        self.price_data = price_df
        self.initial_capital = initial_capital
        self.initial_quantity = initial_quantity
        self.quantity = quantity
        self.nav = self.initial_capital
        self.trade_records = []
        self.nav_reports = []
        self.profit_and_loss_records = []
        self.nav_df = None
        self.trade_record_book = None
        self.trade_stat = None

    def generate_trade_records(self):
        trade_records = []
        nav_reports = []
        for index, row in self.price_data.iterrows():
            # print(row)
            trade_record = {}
            nav_report = {}
            if row['entry_signal'] == True:
                self.initial_quantity = self.quantity + self.initial_quantity
                entry_price = row['entry_price']
                self.initial_capital = self.initial_capital - entry_price * self.quantity
                trade_record['trade_date'] = row['date_time']
                trade_record['open_position'] = self.initial_quantity
                trade_record['outstanding_capital'] = self.initial_capital
                trade_record['action'] = "B"
                trade_record['transaction_price'] = entry_price
                trade_record['transaction_quantity'] = self.quantity
                trade_records.append(trade_record)
                trade_record = {}

            if row['exit_signal'] == True:
                self.initial_quantity = self.initial_quantity - self.quantity
                exit_price = row['exit_price']
                self.initial_capital = self.initial_capital + exit_price * self.quantity
                trade_record['trade_date'] = row['date_time']
                trade_record['open_position'] = self.initial_quantity
                trade_record['outstanding_capital'] = self.initial_capital
                trade_record['action'] = "S"
                trade_record['transaction_price'] = exit_price
                trade_record['transaction_quantity'] = -self.quantity
                trade_records.append(trade_record)
                trade_record = {}

            self.nav = self.initial_capital + self.initial_quantity * row['close']
            nav_report['trade_date'] = row['date_time']
            nav_report['nav'] = self.nav
            nav_reports.append(nav_report)
        self.nav_reports = nav_reports
        self.trade_records = trade_records

    def process_trade_records(self):
        trade_record_book = pd.DataFrame(self.trade_records)
        trade_record_book['cumulative_sum_trade_record'] = trade_record_book.transaction_quantity.cumsum()
        trade_record_book['amount'] = trade_record_book['transaction_price'] * trade_record_book['transaction_quantity']
        trade_record_book['close_ref'] = trade_record_book['cumulative_sum_trade_record'] == 0
        trade_record_book['last_cumulative_sum_trade_record'] = trade_record_book.cumulative_sum_trade_record.shift(1)
        trade_record_book['profit_taking'] = trade_record_book['last_cumulative_sum_trade_record'] > trade_record_book[
            'cumulative_sum_trade_record']
        nav_df = pd.DataFrame(self.nav_reports)
        nav_df['previous_nav'] = nav_df.nav.shift(1)
        nav_df['floating_profit'] = nav_df['nav'] - nav_df['previous_nav']
        nav_df['cumulative_profit'] = nav_df['floating_profit'].cumsum().round(2)
        nav_df['high_water_level'] = nav_df['cumulative_profit'].cummax()
        nav_df['drawdown'] = nav_df['cumulative_profit'] - nav_df['high_water_level']
        self.nav_df = nav_df
        self.trade_record_book = trade_record_book

    def process_pnl(self):
        total_qty = 0
        avg_cost = 0

        for index, trade in self.trade_record_book.iterrows():
            # profit_and_loss = {}
            is_profit_taking = trade['profit_taking']
            trans_price = trade['transaction_price']
            trans_qty = trade['transaction_quantity']
            trade_date = trade['trade_date']
            if is_profit_taking:
                pnl = (trans_price - avg_cost) * abs(trans_qty)
                total_qty = total_qty + trans_qty
                # print("profit and loss ", pnl)
                self.profit_and_loss_records.append(
                    {"trade_date": trade_date, "profit_and_loss": pnl,
                     "pct_trade_pnl": pnl / (avg_cost * abs(trans_qty)) * 100}
                )
            else:
                total_cost = avg_cost * total_qty + trans_price * trans_qty
                total_qty = total_qty + trans_qty
                avg_cost = total_cost / total_qty
                # print("average cost ", avg_cost)

    def generate_trade_analysis_result(self):
        profit_and_loss_df = pd.DataFrame(self.profit_and_loss_records)
        profitable_trade_df = profit_and_loss_df[profit_and_loss_df.profit_and_loss > 0]
        unprofitable_trade_df = profit_and_loss_df[profit_and_loss_df.profit_and_loss <= 0]

        no_of_trade = len(profit_and_loss_df)
        no_of_profitable_trade = len(profitable_trade_df)
        no_of_loss_trade = len(unprofitable_trade_df)
        net_profit = round(profit_and_loss_df.profit_and_loss.sum())
        no_of_profitable_trade_in_pct = round(no_of_profitable_trade / no_of_trade * 100)
        no_of_loss_trade_in_pct = round(no_of_loss_trade / no_of_trade * 100)
        largest_trade_profit = round(max(profitable_trade_df.profit_and_loss))
        largest_trade_loss = round(min(unprofitable_trade_df.profit_and_loss))
        avg_trade_profit = round(profitable_trade_df.profit_and_loss.mean())
        avg_trade_loss = round(unprofitable_trade_df.profit_and_loss.mean())
        avg_trade_pnl = round(profit_and_loss_df.profit_and_loss.mean())
        max_drawdown = round(abs(self.nav_df.drawdown.min()))

        self.trade_stat = {
            "no_of_trade" : no_of_trade,
            "no_of_profitable_trade" : no_of_profitable_trade,
            "no_of_loss_trade" : no_of_loss_trade,
            "net_profit" : net_profit,
            "no_of_profitable_trade_in_pct" : no_of_profitable_trade_in_pct,
            "no_of_loss_trade_in_pct" : no_of_loss_trade_in_pct,
            "largest_trade_profit" : largest_trade_profit,
            "largest_trade_loss" : largest_trade_loss,
            "avg_trade_profit" : avg_trade_profit,
            "avg_trade_loss" : avg_trade_loss,
            "avg_trade_pnl" : avg_trade_pnl,
            "max_drawdown" : max_drawdown
        }

#Subject to change
def backtest(func, optimized_params, price_df):
    vals = optimized_params.values()
    keys = optimized_params.keys()
    trading_condition = []
    for instance in product(*vals):
        for holding_period in [0, 5, 20]:
            log = {}
            # holding_period = 4
            params_obj = dict(zip(keys, instance))
            print(params_obj)
            log['parameter'] = params_obj
            log['holding_period'] = holding_period
            signal_array = func(**params_obj)
            price_df['signal'] = signal_array
            price_df['entry_signal'] = price_data['signal'].shift(1)
            price_df['entry_price'] = price_data.apply(lambda x: buy_at(x, 'open'), axis=1)
            price_df['exit_signal'] = price_data['entry_signal'].shift(holding_period)
            price_df['exit_price'] = price_data.apply(lambda x: sell_at(x, 'close'), axis=1)
            try:
                trade_performance = TradePerformance(price_df)
                trade_performance.generate_trade_records()
                trade_performance.process_trade_records()
                trade_performance.process_pnl()
                trade_performance.generate_trade_analysis_result()

                log['trade_stat'] = trade_performance.trade_stat
                log['trade_records'] = trade_performance.trade_records
                log['nav_reports'] = trade_performance.nav_reports
                log['profit_and_loss_records'] = trade_performance.profit_and_loss_records
                log['signal_records'] = trade_performance.price_data.to_dict('records')
            except Exception as e :
                log['error'] = e
            trading_condition.append(log)
    return trading_condition


def output_excel(trade_condition_list, file_out='output.xlsx'):
    try:
        df_list = []
        trade_excel_list = []
        nav_excel_list = []
        profit_and_loss_excel_list = []
        signal_excel_list = []
        for tc in trade_condition_list:
            parameters = {**tc['parameter'], **{'holding_period': tc['holding_period']}}
            try:
                df_list.append({**tc['parameter'], **tc['trade_stat'], **{'holding_period': tc['holding_period']}})
            except:
                df_list.append({**tc['parameter']})

            trade_df = pd.DataFrame(tc['trade_records'])
            nav_df = pd.DataFrame(tc['nav_reports'])
            profit_and_loss_df = pd.DataFrame(tc['profit_and_loss_records'])
            signal_df = pd.DataFrame(tc['signal_records'])
            # print(signal_df.columns)
            # print(parameters)

            for key in parameters.keys():
                trade_df.insert(1, key, parameters[key])
                nav_df.insert(1, key, parameters[key])
                profit_and_loss_df.insert(1, key, parameters[key])

                signal_df.insert(1, key, parameters[key])

            trade_excel_list.append(trade_df)
            nav_excel_list.append(nav_df)
            profit_and_loss_excel_list.append(profit_and_loss_df)
            signal_excel_list.append(signal_df)

        concat_df = pd.DataFrame(df_list)
        concat_trade_df = pd.concat(trade_excel_list)
        concat_nav_df = pd.concat(nav_excel_list)
        concat_pnl_df = pd.concat(profit_and_loss_excel_list)
        concat_signal_df = pd.concat(signal_excel_list)

        with pd.ExcelWriter(file_out, engine='xlsxwriter') as writer:
            concat_df.to_excel(writer, sheet_name='summary')
            concat_trade_df.to_excel(writer, sheet_name='trade')
            concat_nav_df.to_excel(writer, sheet_name='nav')
            concat_pnl_df.to_excel(writer, sheet_name='pnl')
            concat_signal_df.to_excel(writer, sheet_name='signal')

        writer.save()
        writer.close()
    except Exception as e:
        print(file_out, " cannot generate because ", e)
if __name__ == '__main__':
    # ticker_list = pd.read_csv('hsi_ticker.csv').ticker.tolist()

    params = {"first_day_pc_change": [0],
             "first_down_shadow_tol" : np.arange(0.1, 0.6, 0.1),
              # "first_down_shadow_tol" : [0.1],
              # "first_real_body_to_up_shadow_pc" : [0.5]}
              "first_real_body_to_up_shadow_pc": np.arange(0.1, 0.6, 0.1)}

    # ticker = 700
    location = 'hk'
    ticker_list = [3988]
    for ticker in ticker_list:
        price_data = get_stock_price(ticker, location=location, date_from='2017-01-01')

        cp = CandlestickPattern(price_data)
        function = cp.inverted_hammer
        tcs = backtest(function, params, price_data)

        output_excel(tcs, file_out='{ticker}_inverted_hammer.xlsx'.format(ticker=str(ticker)))










    # print(round(nav))
    # plot_figure_highlight(price_data, '700')
    # params = { "first_day_pc_change" : [0] ,
    #            "first_down_shadow_tol" : np.arange(0.1, 0.6, 0.1),
    #             "first_real_body_to_up_shadow_pc": np.arange(0.1, 0.6, 0.1)}
    #
    # result_json = generate_performance_json(function, params, price_data)
