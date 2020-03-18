from data_access import *
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import mpl_finance
import inspect
import seaborn as sns

# import talib

## Helper function
def helper_function(dfInput):
    df = dfInput.copy()
    df['Real Body'] = (df['close'] - df['open']).abs()
    df['Up Shadow'] = df['high'] - df[['close', 'open']].max(axis=1)
    df['Down Shadow'] = df[['close', 'open']].min(axis=1) - df['low']
    df['Trading Range'] = df['high'] - df['low']
    return df


def plot_figure_highlight(dfInput, Ticker_Code, formation_date=1):
    df = dfInput.copy()
    horiSize = round(len(df)) / 20
    fig, ax = plt.subplots(figsize=(horiSize, 5))
    mpl_finance.candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.6,
                                  colorup='green', colordown='red')
    annotateTargets = df.loc[df.iloc[:, -1] == True, ['date_time', 'close']]
    xdate = list(df['date_time'])
    for i in annotateTargets.index:
        pos1 = i - formation_date + 0.5
        pos2 = i + 0.5
        ax.axvspan(pos1, pos2, fill=True, alpha=0.3, color='yellow')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(horiSize))
    ax.xaxis.set_major_formatter(ticker.IndexFormatter(xdate))
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.title(df.columns[-1] + ': ' + Ticker_Code)


def param_list(f):
    def wrapper(*args, **kwargs):
        f_args = inspect.signature(f)
        parameters = [p for p in f_args.parameters.values() if p.name != 'self' and p.kind != p.VAR_KEYWORD]
        parameters = [p.name for p in parameters]
        eval(f'setattr({f.__qualname__}, "param", parameters)')
        eval(f'setattr({f.__qualname__}, "param_count", len(parameters))')

        # To ensure the inputting parameter shape matches the parameter shape as required by the strategy.
        if len(args) != eval(f'{f.__qualname__}.param_count') + 1:
            if len(args) > 1:
                print('Unmatch no. of parameters! Please check the amount of parameters inputted!')
            f_args = {k: v.default for k, v in f_args.parameters.items()}
        else:
            f_args = dict(f_args.bind(*args, **kwargs).arguments)
        f_args.pop('self')
        eval(f'setattr({f.__qualname__}, "param_dict", f_args)')

        return f(*args, **kwargs)

    return wrapper


class CandlestickPattern:
    def __init__(self, stock_data):
        self.stock_data = self.feature_stock_data(stock_data)
        self.date_time_ = stock_data.date_time.values
        self.open_ = stock_data.open.values
        self.high_ = stock_data.high.values
        self.low_ = stock_data.low.values
        self.close_ = stock_data.close.values
        self.volume_ = stock_data.volume.values

    @staticmethod
    def feature_stock_data(price_df):
        price_df['Real Body'] = (price_df['close'] - price_df['open']).abs()
        price_df['Up Shadow'] = price_df['high'] - price_df[['close', 'open']].max(axis=1)
        price_df['Down Shadow'] = price_df[['close', 'open']].min(axis=1) - price_df['low']
        price_df['Trading Range'] = price_df['high'] - price_df['low']
        price_df = pd.concat([price_df, price_df.shift(1).add_suffix('_1'), price_df.shift(2).add_suffix('_2')], axis=1)
        return price_df

    # Three Black Crows :  Leo Strategy 1
    @param_list
    def three_black_crows(self):
        df = self.stock_data.copy()
        df['Three Black Crows'] = False

        # Condition 1: Three black candlesticks
        df['down'] = (df['open'] - df['close']) > 0
        df['three_down'] = df['down'] & df['down'].shift(1) & df['down'].shift(2)
        # Condition 2: Lower low than previous
        df['lower_low'] = (df['low'] - df['low'].shift(1)) < 0
        df['three_lower_low'] = df['lower_low'] & df['lower_low'].shift(1) & df['lower_low'].shift(2)
        # Condition 3: Close lower than last low
        df['low_close'] = df['close'] - df['low'].shift(1) < 0
        df['three_low_close'] = df['low_close'] & df['low_close'].shift(1) & df['low_close'].shift(2)
        # Condition 4: Longer or similar real bodies
        df['three_real_body'] = ((df['Real Body'] - df['Real Body'].shift(1)) >= 0) & \
                                ((df['Real Body'].shift(1) - df['Real Body'].shift(2)) >= 0)
        # Condition 5: Open lower than last open
        df['low_open'] = (df['open'] - df['open'].shift(1)) < 0
        df['three_low_open'] = df['low_open'] & df['low_open'].shift(1) & df['low_open'].shift(2)

        df['Three Black Crows'] = df['three_down'] & df['lower_low'] & df['low_close'] & df['three_real_body'] & \
                                  df['three_low_open']

        return df['Three Black Crows']

    # Three White Solider : Leo Strategy 1
    @param_list
    def three_white_soldiers(self):
        df = self.stock_data.copy()
        df['Three White Soldiers'] = False

        # Condition 1: Three white candlesticks
        df['up'] = (df['open'] - df['close']) < 0
        df['three_up'] = df['up'] & df['up'].shift(1) & df['up'].shift(2)
        # Condition 2: Higher high than previous
        df['higher_high'] = (df['high'] - df['high'].shift(1)) > 0
        df['three_higher_high'] = df['higher_high'] & df['higher_high'].shift(1) & df['higher_high'].shift(2)
        # Condition 3: Close higher than last high
        df['high_close'] = df['close'] - df['high'].shift(1) > 0
        df['three_high_close'] = df['high_close'] & df['high_close'].shift(1) & df['high_close'].shift(2)
        # Condition 4: Longer or similar real bodies
        df['three_real_body'] = ((df['Real Body'] - df['Real Body'].shift(1)) >= 0) & \
                                ((df['Real Body'].shift(1) - df['Real Body'].shift(2)) >= 0)
        # Condition 5: Open higher than last open
        df['high_open'] = (df['open'] - df['open'].shift(1)) > 0
        df['three_high_open'] = df['high_open'] & df['high_open'].shift(1) & df['high_open'].shift(2)

        df['Three White Soldiers'] = df['three_up'] & df['higher_high'] & df['high_close'] & df['three_real_body'] & \
                                  df['three_high_open']

        return df['Three White Soldiers']

    # Exhaustion Gap
    @param_list
    def exhaustion_gap(self):
        df = self.stock_data.copy()
        df['exhaustion_gap'] = False

        # Condition 1: Three black candlesticks
        df['down'] = (df['open'] - df['close']) > 0
        df['three_down'] = df['down'] & df['down'].shift(1) & df['down'].shift(2)
        # Condition 2: Open lower than previous close
        df['gap_down_open'] = (df['open'] - df['close'].shift(1)) < 0
        df['three_gap_down'] = df['gap_down_open'] & df['gap_down_open'].shift(1) & df['gap_down_open'].shift(2)
        # Condition 3: Volume Increase
        df['volume_decrease'] = (df['volume'] - df['volume'].shift(1)*1.05) <= 0
        df['three_volume_decrease'] = df['volume_decrease'] & df['volume_decrease'].shift(1) & df['volume_decrease'].shift(3)

        df['exhaustion_gap'] = df['three_down'] & df['three_gap_down'] & df['volume_decrease']
        return df['exhaustion_gap']

    # Evening Star : Leo Strategy 1
    @param_list
    def evening_star(self):
        df = self.stock_data.copy()
        df['signal'] = False
        df['gap_up'] = self.gap_up("open_close")
        df['gap_down'] = self.gap_down("open_close")
        df['gap_up_1'] = df['gap_up'].shift(1)
        # df['gap_up_1'] = df['gap_up_1'].fillna(False)
        # Gap Up From the first candle and then Gap Down From the Second Candle
        condition1 = (df['gap_up_1'] & df['gap_down'])
        # Bullish candle in the first candle and Bearish candle in the third candle
        condition2 = (df['close_2'] > df['open_2']) & (df['open'] > df['close'])
        # The First Candle is long and white.
        # Third Condition : it has a short Real Body that is below the First Candle (In case is a Doji, the is called “Evening Doji Star”);
        df['min_real_body'] = df[['Real Body_2', 'Real Body_1', 'Real Body']].min(axis=1)
        condition3 = df['min_real_body'] == df['Real Body_1']
        # Forth condition : The Third Candle is long and black; it has the Close below the midpoint of the Real Body of the First Candle. It has the Open below the Second Candle.
        # df['pct_real_body_2'] = df['Real Body_2']/ df['Trading Range_2']
        # df['pct_real_body'] = df['Real Body'] / df['Trading Range']
        # condition4 = (df['pct_real_body_2'] > 0.6) & (df['pct_real_body'] > 0.6)
        df.loc[condition1 & condition2 & condition3, ['signal']] = True
        return df.loc[:, 'signal'].values

    @param_list
    def morning_star(self):
        df = self.stock_data.copy()
        df['signal'] = False

    @param_list
    def engulfing_pattern(self, type_of_pattern='bullish'):
        # – General Description:
        # 1) The Real Body of the Second Candle “engulfs” the Real Body of the First Candle;
        # 2) The Second Candle has a different color from the First Candle;
        # 3) The volume of trades should be high during the formation of the Second Candle.
        df = self.stock_data.copy()
        df['signal'] = False
        if type_of_pattern == 'bullish':
            condition1 = (df['close'] > df['open'])  # bullish
            condition2 = (df['open_1'] > df['close_1'])  # bearish
            # condition3 = (df['close'] > df['high_1']) & (df['open'] < df['low_1'])
            condition3 = (df['close'] > df['open_1']) & (df['open'] < df['close_1'])
        elif type_of_pattern == 'bearish':
            condition1 = (df['open'] > df['close'])  # bearish
            condition2 = (df['open_1'] < df['close_1'])  # bullish
            condition3 = (df['open'] > df['close_1']) & (df['close'] < df['open_1'])

        df.loc[condition1 & condition2 & condition3, 'signal'] = True

        return df.loc[:, 'signal'].values

    @param_list
    def dark_cloud_cover(self):
        pass

    # Basic Candlestick Pattern (No indication when use them along)
    @param_list
    def gap_up(self, cond="high_low"):
        df = self.stock_data.copy()
        df['signal'] = False
        if cond == "high_low":
            condition1 = df['high_1'] < df['low']
        elif cond == "open_close":
            condition1 = df["high_1"] < df['open']
        df.loc[condition1, ['signal']] = True
        return df.loc[:, 'signal'].values

    @param_list
    def gap_down(self, cond="high_low"):
        df = self.stock_data.copy()
        df['signal'] = False
        if cond == "high_low":
            condition1 = df['low_1'] > df['high']
        elif cond == "open_close":
            condition1 = df['low_1'] > df['open']
        df.loc[condition1, ['signal']] = True
        return df.loc[:, 'signal'].values

    @param_list
    def doji(self, real_body_pct=0.2, down_body_pct=0.3, up_body_pct=0.3):
        df = self.stock_data.copy()
        df['signal'] = False
        df['pct_real_body'] = df['Real Body'] / df['Trading Range']
        df['pct_up_shadow'] = df['Up Shadow'] / df['Trading Range']
        df['pct_down_shadow'] = df['Down Shadow'] / df['Trading Range']
        condition1 = df['pct_real_body'] < real_body_pct
        condition2 = (df['pct_down_shadow'] > down_body_pct) & (df['pct_up_shadow'] > up_body_pct)
        df.loc[condition1 & condition2, ['signal']] = True
        return df.loc[:, 'signal'].values

    # Similar to doji
    @param_list
    def inverted_hammer(self, upper_limit_real_body_pct=0.3, lower_limit_real_body_pct=0.2, down_body_pct=0.1,
                        up_body_pct=0.6):
        df = self.stock_data.copy()
        df['signal'] = False
        df['pct_real_body'] = df['Real Body'] / df['Trading Range']
        df['pct_up_shadow'] = df['Up Shadow'] / df['Trading Range']
        df['pct_down_shadow'] = df['Down Shadow'] / df['Trading Range']
        condition1 = (upper_limit_real_body_pct > df['pct_real_body']) & (
                    df['pct_real_body'] > lower_limit_real_body_pct)
        condition2 = (df['pct_down_shadow'] > down_body_pct) & (df['pct_up_shadow'] > up_body_pct)
        df.loc[condition1 & condition2, ['signal']] = True
        return df.loc[:, 'signal'].values

    @param_list
    def hanging_man(self, upper_limit_real_body_pct=0.3, lower_limit_real_body_pct=0.2, down_body_pct=0.6,
                    up_body_pct=0.1):
        df = self.stock_data.copy()
        df['signal'] = False
        df['pct_real_body'] = df['Real Body'] / df['Trading Range']
        df['pct_up_shadow'] = df['Up Shadow'] / df['Trading Range']
        df['pct_down_shadow'] = df['Down Shadow'] / df['Trading Range']
        condition1 = (upper_limit_real_body_pct > df['pct_real_body']) & (
                df['pct_real_body'] > lower_limit_real_body_pct)
        condition2 = (df['pct_down_shadow'] > down_body_pct) & (df['pct_up_shadow'] > up_body_pct)
        df.loc[condition1 & condition2, ['signal']] = True
        return df.loc[:, 'signal'].values

    @param_list
    def shooting_star(self, up_shadow_pct=0.6, body_pct=0.35):
        df = self.stock_data.copy()
        df['signal'] = False
        df['pct_real_body'] = df['Real Body'] / df['Trading Range']
        df['pct_up_shadow'] = df['Up Shadow'] / df['Trading Range']
        condition = (df['pct_real_body'] <= body_pct) & (df['pct_up_shadow'] >= up_shadow_pct)
        df.loc[condition, ['signal']] = True
        return df.loc[:, 'signal'].values

    @param_list
    def harami_pattern(self, type_of_pattern='bullish'):
        # – General Description:
        # 1) The Real Body of the Second Candle “engulfs” the Real Body of the First Candle;
        # 2) The Second Candle has a different color from the First Candle;
        # 3) The volume of trades should be high during the formation of the Second Candle.
        df = self.stock_data.copy()
        df['signal'] = False
        if type_of_pattern == 'bullish':
            condition1 = (df['close'] > df['open'])  # bullish
            condition2 = (df['open_1'] > df['close_1'])  # bearish
            # condition3 = (df['close'] > df['high_1']) & (df['open'] < df['low_1'])
            condition3 = (df['close'] < df['open_1']) & (df['open'] > df['close_1'])
        elif type_of_pattern == 'bearish':
            condition1 = (df['open'] > df['close'])  # bearish
            condition2 = (df['open_1'] < df['close_1'])  # bullish
            condition3 = (df['open'] < df['close_1']) & (df['close'] > df['open_1'])

        df.loc[condition1 & condition2 & condition3, 'signal'] = True

        return df.loc[:, 'signal'].values


if __name__ == '__main__':
    stock_code = '700'
    price_data = get_stock_price(stock_code, location='hk', date_from='2008-01-01')
    cp = CandlestickPattern(price_data)
    # result_array = talib.CDL3BLACKCROWS(cp.open_, cp.high_, cp.low_, cp.close_)
    # result_array = cp.engulfing_pattern('bearish')
    result_array = cp.engulfing_pattern('bullish')
    price_data['Signal'] = result_array
    signal_df = price_data[price_data['Signal'] == True]
    plot_figure_highlight(price_data, stock_code)
    plt.show()
