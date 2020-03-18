@param_list
def abandoned_baby_up(self,
                      first_day_abs_pc_change=0,
                      third_day_abs_pc_change=0,
                      second_day_abs_pc_ret=0,
                      third_day_abs_pc_ret=0,
                      second_real_body_tol=0):
    df = self.stock_data.copy()
    df['Abandoned Baby Up'] = False
    for i in df.index:
        if i - 2 < 0:
            continue
        if (df.loc[i - 2, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 2, 'open'] and
                df.loc[i, 'close'] > (1 + third_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i - 1, 'close'] < (1 - second_day_abs_pc_ret) * df.loc[i - 2, 'close'] and
                df.loc[i, 'close'] > (1 + third_day_abs_pc_ret) * df.loc[i - 1, 'close'] and
                df.loc[i - 1, 'Real Body'] <= second_real_body_tol * df.loc[i - 1, 'open']):
            if (df.loc[i - 2, 'low'] > df.loc[i - 1, 'high'] and
                    df.loc[i - 1, 'high'] < df.loc[i, 'low']):
                df.loc[i, 'Abandoned Baby Up'] = True
    return df.iloc[:, -1].values


@param_list
def piercing_pattern_up(self,
                        first_day_abs_pc_change=0,
                        second_day_abs_pc_change=0,
                        second_day_abs_pc_ret=0,
                        second_close_position_in_first_body=0.5):
    df = self.stock_data.copy()
    df['Piercing Pattern'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        if (df.loc[i - 1, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i, 'close'] > second_close_position_in_first_body * df.loc[i - 1, 'Real Body'] +
                    df.loc[i - 1, 'open']):
                if df.loc[i, 'open'] < df.loc[i - 1, 'close'] < df.loc[i, 'close'] < df.loc[i - 1, 'open']:
                    df.loc[i, 'Piercing Pattern'] = True
    return df.iloc[:, -1].values


@param_list
def matching_low(self,
                 first_day_abs_pc_change=0,
                 second_day_abs_pc_change=0,
                 second_day_abs_pc_ret=0.001,
                 first_down_shadow_tol=0,
                 second_down_shadow_tol=0):
    df = self.stock_data.copy()
    df['Matching Low'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        if (df.loc[i - 1, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if df.loc[i - 1, 'open'] > df.loc[i, 'open']:
                if (df.loc[i - 1, 'Down Shadow'] <= first_down_shadow_tol * df.loc[i - 1, 'open'] and
                        df.loc[i, 'Down Shadow'] <= second_down_shadow_tol * df.loc[i, 'open']):
                    df.loc[i, 'Matching Low'] = True
    return df.iloc[:, -1].values


@param_list
def hammer(self,
           first_day_pc_change=0,
           first_real_body_to_down_shadow_pc=0.5,
           first_up_shadow_tol=0.005):
    df = self.stock_data.copy()
    df['Hammer'] = False
    for i in df.index:
        if df.loc[i, 'Real Body'] <= (1 - first_real_body_to_down_shadow_pc) * df.loc[i, 'Down Shadow']:
            if df.loc[i, 'Up Shadow'] <= first_up_shadow_tol * df.loc[i, 'open']:
                if ((first_day_pc_change < 0 and df.loc[i, 'close'] < (1 - first_day_pc_change) * df.loc[
                    i, 'open']) or
                        (first_day_pc_change >= 0 and df.loc[i, 'close'] > (1 + first_day_pc_change) * df.loc[
                            i, 'open'])):
                    df.loc[i, 'Hammer'] = True
    return df.iloc[:, -1].values


@param_list
def inverted_hammer(self,
                    first_day_pc_change=0,
                    first_down_shadow_tol=0.005,
                    first_real_body_to_up_shadow_pc=0.5):
    df = self.stock_data.copy()
    df['Inverted Hammer'] = False
    for i in df.index:
        if df.loc[i, 'Real Body'] <= first_real_body_to_up_shadow_pc * df.loc[i, 'Up Shadow']:
            if df.loc[i, 'Down Shadow'] <= first_down_shadow_tol * df.loc[i, 'open']:
                if ((first_day_pc_change < 0 and df.loc[i, 'close'] < (1 - first_day_pc_change) * df.loc[
                    i, 'open']) or
                        (first_day_pc_change >= 0 and df.loc[i, 'close'] > (1 + first_day_pc_change) * df.loc[
                            i, 'open'])):
                    df.loc[i, 'Inverted Hammer'] = True
    return df.iloc[:, -1].values


@param_list
def upside_tasuki_gap(self,
                      first_day_abs_pc_change=0,
                      second_day_abs_pc_change=0,
                      third_day_abs_pc_change=0,
                      second_day_abs_pc_ret=0,
                      third_day_abs_pc_ret=0):
    df = self.stock_data.copy()
    df['Upside Tasuki Gap'] = False
    for i in df.index:
        if i - 2 <= 0:
            continue
        if (df.loc[i - 2, 'close'] > (1 + first_day_abs_pc_change) * df.loc[i - 2, 'open'] and
                df.loc[i - 1, 'close'] > (1 + second_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] < (1 - third_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i - 1, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 2, 'close'] and
                df.loc[i, 'close'] < (1 - third_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i - 1, 'low'] > df.loc[i - 2, 'high'] and
                    df.loc[i - 2, 'close'] < df.loc[i, 'close'] < df.loc[
                        i - 1, 'open'] < df.loc[i, 'open'] < df.loc[i - 1, 'close']):
                df.loc[i, 'Upside Tasuki Gap'] = True
    return df.iloc[:, -1].values


@param_list
def engulfing_pattern_up(self,
                         first_day_abs_pc_change=0,
                         second_day_abs_pc_change=0,
                         second_day_abs_pc_ret=0,
                         first_to_second_real_body_abs_pc=0):
    df = self.stock_data.copy()
    df['Bullish Engulfing Pattern'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        if (df.loc[i - 1, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if df.loc[i, 'open'] < df.loc[i - 1, 'low'] < df.loc[i - 1, 'high'] < df.loc[i, 'close']:
                if df.loc[i - 1, 'Real Body'] < (1 - first_to_second_real_body_abs_pc) * df.loc[i, 'Real Body']:
                    df.loc[i, 'Bullish Engulfing Pattern'] = True
    return df.iloc[:, -1].values


@param_list
def engulfing_pattern_down(self,
                           first_day_abs_pc_change=0,
                           second_day_abs_pc_change=0,
                           second_day_abs_pc_ret=0,
                           first_to_second_real_body_abs_pc=0):
    df = self.stock_data.copy()
    df['Bearish Engulfing Pattern'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        if (df.loc[i - 1, 'close'] > (1 + first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if df.loc[i, 'close'] < df.loc[i - 1, 'low'] < df.loc[i - 1, 'high'] < df.loc[i, 'open']:
                if df.loc[i - 1, 'Real Body'] < (1 - first_to_second_real_body_abs_pc) * df.loc[i, 'Real Body']:
                    df.loc[i, 'Bearish Engulfing Pattern'] = True
    return df.iloc[:, -1].values


@param_list
def dragonfly_doji(self,
                   first_real_body_tol=0.001,
                   first_up_shadow_tol=0,
                   first_down_shadow_tol=0.02):
    df = self.stock_data.copy()
    df['Dragonfly Doji'] = False
    for i in df.index:
        if (df.loc[i, 'Real Body'] <= first_real_body_tol * df.loc[i, 'open'] and
                df.loc[i, 'Up Shadow'] <= first_up_shadow_tol * df.loc[i, 'open'] and
                df.loc[i, 'Down Shadow'] >= first_down_shadow_tol * df.loc[i, 'open']):
            df.loc[i, 'Dragonfly Doji'] = True
    return df.iloc[:, -1].values


@param_list
def in_neck(self,
            first_day_abs_pc_change=0,
            second_day_abs_pc_change=0,
            second_day_abs_pc_ret=0,
            second_to_first_close_diff_to_first_body_pc=0.15):
    df = self.stock_data.copy()
    df['In Neck'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        if (df.loc[i - 1, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i, 'open'] < df.loc[i - 1, 'close'] < df.loc[i, 'close'] and
                    df.loc[i, 'Up Shadow'] <= 2 * df.loc[i - 1, 'Real Body'] and
                    df.loc[i, 'Down Shadow'] <= 2 * df.loc[i - 1, 'Real Body']):
                if ((df.loc[i, 'close'] - df.loc[i - 1, 'close']) < second_to_first_close_diff_to_first_body_pc *
                        df.loc[i - 1, 'Real Body']):
                    df.loc[i, 'In Neck'] = True
    return df.iloc[:, -1].values


@param_list
def stick_sandwich_bullish(self,
                           first_day_abs_pc_change=0,
                           second_day_abs_pc_change=0,
                           third_day_abs_pc_change=0,
                           second_day_abs_pc_ret=0,
                           third_day_abs_pc_ret=0,
                           first_to_second_real_body_abs_pc=0,
                           third_to_first_close_abs_pc=0.1):
    df = self.stock_data.copy()
    df['Stick Sandwich Bullish'] = False
    for i in df.index:
        if i - 2 <= 0:
            continue
        if (df.loc[i - 2, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 2, 'open'] and
                df.loc[i - 1, 'close'] > (1 + second_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] < (1 - third_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i - 1, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 2, 'close'] and
                df.loc[i, 'close'] < (1 - third_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i - 1, 'low'] > df.loc[i - 2, 'close'] and
                    df.loc[i - 2, 'Real Body'] > (1 + first_to_second_real_body_abs_pc) * df.loc[
                        i - 1, 'Real Body']):
                if (df.loc[i, 'close'] < df.loc[i - 1, 'low'] < df.loc[i - 1, 'high'] < df.loc[i, 'open'] and
                        (1 - third_to_first_close_abs_pc) * df.loc[i - 2, 'close'] <= df.loc[
                            i, 'close'] <= (1 + third_to_first_close_abs_pc) * df.loc[i - 2, 'close']):
                    df.loc[i, 'Stick Sandwich Bullish'] = True
    return df.iloc[:, -1].values


@param_list
def stick_sandwich_bearish(self,
                           first_day_abs_pc_change=0,
                           second_day_abs_pc_change=0,
                           third_day_abs_pc_change=0,
                           second_day_abs_pc_ret=0,
                           third_day_abs_pc_ret=0,
                           first_to_second_real_body_abs_pc=0,
                           third_to_first_close_abs_pc=0.1):
    df = self.stock_data.copy()
    df['Stick Sandwich Bearish'] = False
    for i in df.index:
        if i - 2 <= 0:
            continue
        if (df.loc[i - 2, 'close'] > (1 + first_day_abs_pc_change) * df.loc[i - 2, 'open'] and
                df.loc[i - 1, 'close'] < (1 - second_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] > (1 + third_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i - 1, 'close'] < (1 - second_day_abs_pc_ret) * df.loc[i - 2, 'close'] and
                df.loc[i, 'close'] > (1 + third_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i - 1, 'high'] < df.loc[i - 2, 'close'] and
                    df.loc[i - 2, 'Real Body'] > (1 + first_to_second_real_body_abs_pc) * df.loc[
                        i - 1, 'Real Body']):
                if (df.loc[i, 'open'] < df.loc[i - 1, 'low'] < df.loc[i - 1, 'high'] < df.loc[i, 'close'] and
                        (1 - third_to_first_close_abs_pc) * df.loc[i - 2, 'close'] <= df.loc[
                            i, 'close'] <= (1 + third_to_first_close_abs_pc) * df.loc[i - 2, 'close']):
                    df.loc[i, 'Stick Sandwich Bearish'] = True
    return df.iloc[:, -1].values


@param_list
def bullish_homing_pigeon(self,
                          first_day_abs_pc_change=0,
                          second_day_abs_pc_change=0,
                          second_day_abs_pc_ret=0,
                          first_to_second_real_body_abs_pc=0):
    df = self.stock_data.copy()
    df['Bullish Homing Pigeon'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        if (df.loc[i - 1, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i - 1, 'close'] < df.loc[i, 'close'] < df.loc[i, 'open'] < df.loc[i - 1, 'open'] and
                    df.loc[i - 1, 'Real Body'] > (1 + first_to_second_real_body_abs_pc) * df.loc[i, 'Real Body']):
                df.loc[i, 'Bullish Homing Pigeon'] = True
    return df.iloc[:, -1].values


@param_list
def dark_cloud_cover(self,
                     first_day_abs_pc_change=0,
                     second_day_abs_pc_change=0,
                     second_day_abs_pc_ret=0,
                     second_open_position_higher_than_first_body=0,
                     second_close_position_in_first_body=0.5):
    df = self.stock_data.copy()
    df['Dark Cloud Cover'] = False
    for i in df.index:
        if i - 1 < 0:
            continue
        # Previous day is a up candle
        # Current day is a down candle
        # Current day open is higher than previous day close position
        # Current day close position smaller than previous day real body midpoint
        if (df.loc[i - 1, 'close'] > (1 + first_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_change) * df.loc[i, 'open'] and
                df.loc[i, 'close'] < (1 - second_day_abs_pc_ret) * df.loc[i - 1, 'close']):
            if (df.loc[i, 'open'] > (1 + second_open_position_higher_than_first_body) * df.loc[i - 1, 'close'] and
                    df.loc[i, 'close'] < second_close_position_in_first_body * df.loc[i - 1, 'Real Body'] +
                    df.loc[i - 1, 'open']):
                df.loc[i, 'Dark Cloud Cover'] = True
    return df.iloc[:, -1].values

   @param_list
    def three_line_strike_up(self,
                             first_day_abs_pc_change=0,
                             second_day_abs_pc_change=0,
                             third_day_abs_pc_change=0,
                             forth_day_abs_pc_change=0,
                             second_day_abs_pc_ret=0,
                             third_day_abs_pc_ret=0,
                             forth_day_abs_pc_ret=0,
                             forth_close_to_first_open_pc=0):
        df = self.stock_data.copy()
        df['Three Line Strike Up'] = False
        for i in df.index:
            if i - 3 < 0:
                continue
            if (df.loc[i - 3, 'close'] > (1 + first_day_abs_pc_change) * df.loc[i - 3, 'open'] and
                    df.loc[i - 2, 'close'] > (1 + second_day_abs_pc_change) * df.loc[i - 2, 'open'] and
                    df.loc[i - 1, 'close'] > (1 + third_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                    df.loc[i, 'close'] < (1 - forth_day_abs_pc_change) * df.loc[i, 'open']):
                if (df.loc[i - 2, 'close'] > (1 + second_day_abs_pc_ret) * df.loc[i - 3, 'close'] and
                        df.loc[i - 1, 'close'] > (1 + third_day_abs_pc_ret) * df.loc[i - 2, 'close'] and
                        df.loc[i, 'close'] < (1 - forth_day_abs_pc_ret) * df.loc[i - 1, 'close'] and
                        df.loc[i, 'close'] < (1 - forth_close_to_first_open_pc) * df.loc[i - 3, 'open']):
                    if df.loc[i, 'open'] > df.loc[i - 1, 'close']:
                        df.loc[i, 'Three Line Strike Up'] = True
        return df.iloc[:, -1].values

    @param_list
    def three_line_strike_down(self,
                               first_day_abs_pc_change=0,
                               second_day_abs_pc_change=0,
                               third_day_abs_pc_change=0,
                               forth_day_abs_pc_change=0,
                               second_day_abs_pc_ret=0,
                               third_day_abs_pc_ret=0,
                               forth_day_abs_pc_ret=0,
                               forth_close_to_first_open_pc=0):
        df = self.stock_data.copy()
        df['Three Line Strike Down'] = False
        for i in df.index:
            if i - 3 < 0:
                continue
            if (df.loc[i - 3, 'close'] < (1 - first_day_abs_pc_change) * df.loc[i - 3, 'open'] and
                    df.loc[i - 2, 'close'] < (1 - second_day_abs_pc_change) * df.loc[i - 2, 'open'] and
                    df.loc[i - 1, 'close'] < (1 - third_day_abs_pc_change) * df.loc[i - 1, 'open'] and
                    df.loc[i, 'close'] > (1 + forth_day_abs_pc_change) * df.loc[i, 'open']):
                if (df.loc[i - 2, 'close'] < (1 - second_day_abs_pc_ret) * df.loc[i - 3, 'close'] and
                        df.loc[i - 1, 'close'] < (1 - third_day_abs_pc_ret) * df.loc[i - 2, 'close'] and
                        df.loc[i, 'close'] > (1 + forth_day_abs_pc_ret) * df.loc[i - 1, 'close'] and
                        df.loc[i, 'close'] > (1 + forth_close_to_first_open_pc) * df.loc[i - 3, 'open']):
                    if df.loc[i, 'open'] < df.loc[i - 1, 'close']:
                        df.loc[i, 'Three Line Strike Down'] = True
        return df.iloc[:, -1].values
