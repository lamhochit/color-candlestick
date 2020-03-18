from candlestick_lib import *
from data_access import *
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import mpl_finance
import numpy as np
from sklearn.linear_model import LinearRegression
import itertools


def output_signal_csv(df, feature_name=None, *argv):
    '''
    Saves the DataFrame object as csv file.
    '''
    # df columns: ['date_time', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Parameters', '5 Days', '10 Days', '15 Days', '20 Days']
    feature_name = str(feature_name)
    df.to_csv(feature_name + '.csv')


def test_strategy(price_data, strategy_name, sell_after_x_days):
    '''
    Input:
        price_data <pd.DataFrame>: A DataFrame object containing stock data.
        strategy_name <str>: The strategy name for finding the dedicated column. eg 'Morning Doji Star', 'Three Black Crows'.
        sell_after_x_days <int>: Selling after x days, excluding the day that the signal was triggered.

    Return:
        decision <pd.DataFrame>: Containing the record that when the signal is triggered or not triggered.
        trading_summary <pd.DataFrame>: Containing all the trading records, with two columns, ['Buy', 'Sell'], the buy price and the sell price.
        profit <int>: The amount of profit gained within the given data range and the strategy. Be aware that this is not the percentage and the currency being used. eg 100 means you earned $100 during the trading period.
    '''
    decision = pd.DataFrame()
    trading_summary = pd.DataFrame()

    if sell_after_x_days > len(price_data):
        raise ValueError(
            f'sell_after_x_days is greater than length of price_data (with length {len(price_data)})! Please specify a smaller number!')

    decision['date_time'] = price_data['date_time']
    decision['Buy'] = price_data[strategy_name].shift(1).fillna(False)
    decision['Sell'] = price_data[strategy_name].shift(sell_after_x_days).fillna(False)

    trading_summary['Triggered Date'] = price_data[price_data[strategy_name]]['date_time']

    try:
        buy_date = [np.nan for _ in range(len(trading_summary))]
        for i in range(len(trading_summary)):
            buy_date[i] = decision[decision['Buy']]['date_time'].values[i]
    except:
        pass
    finally:
        trading_summary['Buy Date'] = buy_date
    try:
        sell_date = [np.nan for _ in range(len(trading_summary))]
        for i in range(len(trading_summary)):
            sell_date[i] = decision[decision['Sell']]['date_time'].values[i]
    except:
        pass
    finally:
        trading_summary['Sell Date'] = sell_date
    trading_summary['Holding Period'] = sell_after_x_days

    try:
        # Buy stock on the next day at open price after the signal was detected. Selecting data by signals appeared t+1.
        buy = [np.nan for _ in range(len(trading_summary))]
        for i in range(len(price_data[decision['Buy']]['open'].values)):
            buy[i] = price_data[decision['Buy']]['open'].values[i]
    except:
        pass
    finally:
        trading_summary['Buy'] = buy
    try:
        # Sell stock after x days at close price
        sell = [np.nan for _ in range(len(trading_summary))]
        for i in range(len(price_data[decision['Sell']]['close'].values)):
            sell[i] = price_data[decision['Sell']]['close'].values[i]
    except:
        pass
    finally:
        trading_summary['Sell'] = sell

    trading_summary['Return'] = (trading_summary['Sell'] - trading_summary['Buy']) / trading_summary['Buy']

    profit = ((trading_summary['Sell'] - trading_summary['Buy']) / trading_summary['Buy']).mean()
    return decision, trading_summary, profit


def trading_annotation(df, strategy_name, ticker_code, params, uid, formation_date=1, dpi=None):
    '''
    df <pd.DataFrame>: a DataFrame object, containing 'Buy' and 'Sell' columns for annotation.
    strategy_name <str>: The strategy name for finding the dedicated column. eg 'Morning Doji Star', 'Three Black Crows'.
    params <dict / list? / pd.DataFrame?>: parameters for the dedicated strategy. Will be displayed in the exported chart.
    uid <str>: Thd unique id for the parameter combination. eg '001', '002'.
    formation_date <int>: To be decided whether include this or not.
    dpi <int>: The dpi of the exported image. If the image is not big and want a clearer image, user could try to set this option to 300 or 400.
               If the image is too large (displaying all historical data), just set dpi to None (default is 75).
    '''
    df = df.copy()
    ticker_code = str(ticker_code)
    h_size = len(df) // 20
    fig, ax = plt.subplots(dpi=dpi)
    mpl_finance.candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.6,
                                  colorup='green', colordown='red')
    signal_annotation = df[df[strategy_name]]
    buy_annotation = df[df['Buy']]
    sell_annotation = df[df['Sell']]

    # Annotating the graph.
    # Yellow indicates detection of the signal, Green indicates the buying action, Red indicates the selling action.
    for i in signal_annotation.index:
        pos1 = i - formation_date + 0.5
        pos2 = i + 0.5
        ax.axvspan(pos1, pos2, fill=True, alpha=0.3, color='yellow')
    for i in buy_annotation.index:
        pos1 = i - formation_date + 0.5
        pos2 = i + 0.5
        ax.axvspan(pos1, pos2, fill=True, alpha=0.3, color='green')
    for i in sell_annotation.index:
        pos1 = i - formation_date + 0.5
        pos2 = i + 0.5
        ax.axvspan(pos1, pos2, fill=True, alpha=0.3, color='red')
    ax.xaxis.set_major_formatter(ticker.IndexFormatter(df['date_time']))
    fig.autofmt_xdate()

    # Adding parameter dict to the graph.
    try:
        if type(params) == dict:
            for y, key in enumerate(params):
                ax.text(0.01, 0.9 - y / (2 * len(params)), f'{key}: {params[key]}', horizontalalignment='left',
                        verticalalignment='top', transform=ax.transAxes)
        if type(params) == list:
            for i in range(len(params)):
                ax.text(0.01, 0.9 - i / (2 * len(params)), f'{i}: {params[i]}', horizontalalignment='left',
                        verticalalignment='top', transform=ax.transAxes)
    except:
        pass
    plt.title(f'{strategy_name}: {ticker_code}')
    fig.savefig(f'graph_{ticker_code}_{strategy_name}_{uid}_.png')
    plt.show()


def discover_patterns(df, strategy_name, ticker_code, x_days_before, x_days_after):
    '''
    df <pd.DataFrame>: A DataFrame object. It should include stock data of a single ticker and with columns of applied strategy. User could combine stock data and applied strategy table by using "pd.concat([price_data, decision_df], axis=1)" to achieve this.
    strategy_name <str>: The name of the strategy name. It should be present in df columns. eg: 'Hammer', 'Morning Doji Star'.
    ticker_code <str>: The ticker code. Eg '66', '700'.
    x_days_before <int>: Number of days to be included before the signal was detected. (Excluded the day that the signal was triggered)
    x_days_after <int>: Number of days to be included after tha signal was detected. (Excluded the day that thE signal was triggered)

    Timeline:
    |<--- x_days_before --->|<- 1 Day (The day that the signal was triggered) ->|<--- x_days_after --->|

    Return:
        Relative strength of the strategy in the ticker code. The relative strength is calculated by the slope of linear regression, the trend after the signal was triggered divided by the trend before the signal was triggered.
        Relative strength would be negative if the trend before and after the signal was reversial, positive if both trends are at the same direction.
        If the trend after the signal changed more rapidly than the trend before the signal, the magnitude of the relative strength would be greater than 1 (which means the signal is more significant), else smaller than 1.
    '''
    ticker_code = str(ticker_code)

    # Observe the overall trend x days before and the trend x days after.
    relative_strength = []
    for signal_pos in df[df[strategy_name]].index:
        # try except to omit boundary error.
        try:
            X_before = np.arange(0, x_days_before).reshape(-1, 1)
            y_before = df['close'].iloc[signal_pos - x_days_before:signal_pos].to_numpy()  # excluded signal_pos
            X_after = np.arange(0, x_days_after).reshape(-1, 1)
            y_after = df['close'].iloc[signal_pos + 1:signal_pos + 1 + x_days_after].to_numpy()  # excluded signal_pos

            # Compare the strength of the trend before and after the signal. Trend before / trend after, and measure the strength of the signal.
            slope_before = LinearRegression().fit(X_before, y_before).coef_[0]
            slope_after = LinearRegression().fit(X_after, y_after).coef_[0]
            # if the slope of the linear regression is 0 or nan. (It really happened!)
            if slope_after / slope_before in [np.inf, np.nan]:
                relative_strength.append(0)
            else:
                relative_strength.append(slope_after / slope_before)
        except:
            pass
    return np.average(relative_strength)


def print_report(df, strategy_name, decision_df, trading_summary_df, profit):
    print('-------------------------------------------------------')
    print('Strategy name:', strategy_name)
    print('-------------------------------------------------------')
    print('Time period: {} to {} ({} Days)'.format(df['date_time'].min(), df['date_time'].max(), (
                pd.to_datetime(df['date_time'].max()) - pd.to_datetime(df['date_time'].min())).days))
    try:
        print('No. of times of trading with a positive return: ', end='')
        print((trading_summary_df['Sell'] > trading_summary_df['Buy']).value_counts()[True])
    except:
        print(0)
    try:
        print('No. of times of trading with a negative return: ', end='')
        print((trading_summary_df['Sell'] < trading_summary_df['Buy']).value_counts()[True])
    except:
        print(0)
    try:
        print('No. of times of the appearance of the signal: ', end='')
        print(df[strategy_name].value_counts()[True])
    except:
        print(0)
    print('Total profit within the period:', profit)
    try:
        print('Average profit per trade: ', end='')
        print(profit / trading_summary_df.shape[0])
    #         print('No. of times of trading:', trading_summary_df.shape[0])
    except:
        print(0)
    print('-------------------------------------------------------')


def grid_search(price_data, strategy_name, sell_after_x_days, f, *args):
    '''
    Search for the best combination of the parameters to finetune candlestick patterns.

    Input:
        price_data <pd.DataFrame>: Stock data.
        strategy_name <str>: The name of the strategy.
        sell_after_x_days <int>: Selling the stock after holding for x days.
        f <function>: The function of the strategy. Eg
    '''
    # TODO: Add a function such that sell_after_x_days could be adjusted by programs automatically.
    log_table = []
    #         price_data = price_data.copy()
    #         price_data[strategy_name] = f(*args)
    for arg in itertools.product(*args):
        price_data[strategy_name] = f(*arg)
        _, _, profit = test_strategy(price_data, strategy_name, sell_after_x_days)
        signal_count = 0
        profit_per_signal = 0
        try:
            signal_count = price_data[strategy_name].value_counts()[True]
            profit_per_signal = profit / signal_count
        except:
            signal_count = 0
            profit_per_signal = 0
        log_table.append([*arg, signal_count, profit_per_signal, profit])
    log_table = pd.DataFrame(log_table)
    log_table.columns = [*(f.param), 'signal_count', 'profit_per_signal', 'Profit']
    return log_table


if __name__ == "__main__" :
    '''
    select feature
    Specify parameter ranges and increment
    Start testing with different combinations
    '''
    strategy_name = 'Exhaustion Gap'
    stock_code = '1299'
    params = []
    sell_after_x_days = 4
    uid = '001'
    dpi = 400
    x_days_before = 10
    x_days_after = 5
    price_data = get_stock_price(stock_code, location='hk', date_from='2015-01-01')
    cp = CandlestickPattern(price_data)


    # %%

    price_data[strategy_name] = cp.exhaustion_gap(*params)
    params = cp.exhaustion_gap.param_dict
    decision_df, trading_summary_df, profit = test_strategy(price_data, strategy_name, sell_after_x_days)
    trading_record = pd.merge(price_data, decision_df, left_on='date_time', right_on='date_time')

    trading_annotation(trading_record, strategy_name, stock_code, params, uid, dpi=dpi)
    trading_record.to_csv('trading_record.csv')
    trading_summary_df.to_csv('trading_summary.csv')
    print_report(price_data, strategy_name, decision_df, trading_summary_df, profit)
    print('Relative strength of the signal:',
          discover_patterns(pd.concat([price_data, decision_df], axis=1), strategy_name, stock_code, x_days_before,
                            x_days_after))
