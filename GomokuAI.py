from GomokuConst import SYMBOL_EMPTY, chain_num_default
from GomokuAbstract import GomokuHandler
import numpy as np


class GomokuAIToy:
    def __init__(self):
        pass

    def decide(self, board, current_player):
        rows, cols = board.shape
        for r in range(rows):
            for c in range(cols):
                if board[r, c] == SYMBOL_EMPTY:
                    return r, c


class GomokuAIScore:
    """Move by scoring each position"""

    def __init__(self, chain_num=chain_num_default):
        self.__chain_num = chain_num
        self._s = 1
        self._e = SYMBOL_EMPTY
        self._d = None
        s, e, d = self._s, self._e, self._d
        self._score_dict = \
            {(s, s, s, s, s): 1e8,
             (e, s, s, s, s, e): 1e7,

             (s, s, s, s, e): 1000000,
             (s, s, e, s, s): 990000,
             (s, e, s, s, s): 990000,
             (e, e, s, s, s, e): 980000,
             (e, s, e, s, s, e): 970000,

             (e, s, s, s, e): 100000,
             (s, s, s, e, e): 99000,
             (s, s, e, s, e): 90000,
             (s, e, s, s, e): 88000,
             (s, s, e, e, s): 86000,
             (s, e, s, e, s): 85000,

             (e, e, e, e, s, s): 50000,
             (e, e, e, s, s, e): 49000,
             (e, e, s, s, e, e): 48000,
             (e, e, e, s, e, s): 40000,
             (e, e, s, e, s, e): 39000,
             (e, e, s, e, e, s): 35000,
             (e, s, e, e, s, e): 33000,
             (e, s, e, e, e, s): 31000,
             (s, e, e, e, e, s): 30000,

             (e, e, e, s, s): 10000,
             (e, e, s, s, e): 9900,
             (e, e, s, e, s): 9000,
             (e, s, e, s, e): 8800,
             (e, s, e, e, s): 8000,
             (s, e, e, e, s): 7000,

             (s, e, e, e, e, e): 3000,
             (e, s, e, e, e, e): 2900,
             (e, e, s, e, e, e): 2800,

             (s, e, e, e, e): 1000,
             (e, s, e, e, e): 900,
             (e, e, s, e, e): 800,
             }
        self._patterns = self._scores = self._scores_sorted = self._patterns_sorted = None
        self.sort_patterns()
        # self._max_pattern_len = max([len(k) for k in self._score_dict.keys()])
        self._max_pattern_len = 6
        self._sum = False

    @property
    def s(self):
        return self._s

    @property
    def e(self):
        return self._e

    @property
    def d(self):
        return self._d

    @property
    def score_dict(self):
        return self._score_dict

    @property
    def max_pattern_len(self):
        return self._max_pattern_len

    @s.setter
    def s(self, s):
        self._s = s

    @e.setter
    def e(self, e):
        self._e = e

    @d.setter
    def d(self, d):
        self._d = d

    @score_dict.setter
    def score_dict(self, sd):
        self._score_dict = sd
        self.sort_patterns()

    @max_pattern_len.setter
    def max_pattern_len(self, mpl=None):
        if mpl is None:
            mpl = max([len(k) for k in self._score_dict.keys()])
        self._max_pattern_len = mpl

    def enable_sum(self):
        self._sum = True

    def disable_sum(self):
        self._sum = False

    def update_score_dict(self, sdu):
        self._score_dict.update(sdu)
        self.sort_patterns()

    def sort_patterns(self):
        self._patterns = list(self._score_dict.keys())
        self._scores = list(self._score_dict.values())
        self._scores_sorted = np.sort(self._scores)[-1::-1]
        idx_sorted_t = np.argsort(self._scores)
        self._patterns_sorted = [self._patterns[hh] for hh in idx_sorted_t[-1::-1]]

    def convert2norm(self, series, cp):
        series_new = series.copy()
        for hh in range(len(series_new)):
            st = series_new[hh]
            if st == cp:
                series_new[hh] = self._s
            elif st == SYMBOL_EMPTY:
                series_new[hh] = self._e
            elif st is not None:
                series_new[hh] = self._d
        return series_new

    @staticmethod
    def match_pattern(series_ori, pattern):
        flag_match = False
        for series in [series_ori, series_ori[-1::-1]]:
            for hh in range(len(series) - len(pattern) + 1):
                series_cut = series[hh:hh + len(pattern)]
                flag_match = series_cut == list(pattern)
                if flag_match:
                    break
            if flag_match:
                break
        return flag_match

    def score_pos(self, dict_series, cp):
        total_score = 0
        pattern_matched = {}
        for d, series in dict_series.items():
            series_c = self.convert2norm(series, cp)
            for hh in range(len(self._patterns_sorted)):
                pattern = self._patterns_sorted[hh]
                score = self._scores_sorted[hh]
                if self.match_pattern(series_c, pattern):
                    total_score += score
                    pattern_matched[d] = pattern
                    break
        return total_score, pattern_matched

    def get_series_pos(self, board, r, c, place=True, cp=SYMBOL_EMPTY, return_center=False):
        rows, cols = board.shape
        coor_cur = np.array((r, c))
        directions = np.array(((0, 1), (1, 0), (1, 1), (-1, 1)))
        dict_series = {}
        num_cand = 2 * self._max_pattern_len - 1
        pos_center = int((num_cand - 1) / 2)
        for d in directions:
            mpt = [None] * num_cand
            for hh in range(num_cand):
                step = hh - pos_center
                if place and (step == 0):
                    mpt[hh] = cp
                else:
                    pos = coor_cur + d * step
                    if (0 <= pos[0] < rows) and (0 <= pos[1] < cols):
                        mpt[hh] = board[pos[0], pos[1]]
            dict_series[tuple(d)] = mpt
        if return_center:
            return dict_series, pos_center
        else:
            return dict_series

    def decide(self, board, current_player):
        rows, cols = board.shape
        if np.all(board == SYMBOL_EMPTY):
            rd = int(rows / 2)
            cd = int(cols / 2)
            return rd, cd
        pd = np.unique(board)
        pa = np.append(pd, current_player)
        players = list(set(pa).difference({SYMBOL_EMPTY}))
        nump = len(players)
        mat_scores = np.zeros([rows, cols, nump])
        exn = self._max_pattern_len - 1
        for r in range(rows):
            for c in range(cols):
                if board[r, c] == SYMBOL_EMPTY:
                    box_t = board[max([0, r - exn]):min([r + exn + 1, rows]),
                            max([0, c - exn]):min([c + exn + 1, cols])]
                    if np.all(box_t == SYMBOL_EMPTY):
                        mat_scores[r, c, :] = 0
                    else:
                        dict_series, pos_center = self.get_series_pos(board, r, c, place=False, return_center=True)
                        for hh in range(nump):
                            p = players[hh]
                            if p == current_player:
                                den = 1
                            else:
                                den = nump
                            dict_series_t = dict_series.copy()
                            for k, v in dict_series.items():
                                vv = v.copy()
                                vv[pos_center] = p
                                dict_series_t[k] = vv
                            score_temp, pattern_matched = self.score_pos(dict_series_t, p)
                            score_temp_mod = score_temp - min(self._score_dict.values())
                            mat_scores[r, c, hh] += score_temp_mod
                else:
                    mat_scores[r, c, :] = -1
        if self._sum:
            mat_scores_m = np.sum(mat_scores, axis=2)
        else:
            mat_scores_m = np.max(mat_scores, axis=2)
        rd, cd = np.unravel_index(mat_scores_m.argmax(), mat_scores_m.shape)
        return rd, cd


class GomokuAIScoreAlpha(GomokuAIScore):
    def __init__(self, chain_num=chain_num_default):
        super(GomokuAIScoreAlpha, self).__init__(chain_num)
        s, e, d = self.s, self.e, self.d
        sdu = {
            (s, s, e, s, s, e, s, s): 1e7 * 0.99,
            (s, s, s, e, s, e, s, s, s): 1e7 * 0.98,
            (s, e, s, s, s, e, s): 1e7 * 0.97
        }
        self.update_score_dict(sdu)
        self.max_pattern_len = None


class GomokuPatternGenerator():
    def __init__(self, chain_num=chain_num_default, s=1, e=SYMBOL_EMPTY, d=None):
        self._chain_num = chain_num
        self._s = s
        self._e = e
        self._d = d

    @staticmethod
    def cat_pattern(pattern_1, pattern_2, f, len_1, len_2):
        L = 2 * len_1 + len_2 - 2
        P = [0] * L
        f = min(max(0, f), len_1 + len_2 - 2)
        p_2_l = len_1 - 1
        p_2_r = p_2_l + len_2
        P[p_2_l:p_2_r] = pattern_2
        P[f:f + len_1] = pattern_1
        cut_l = min(f, p_2_l)
        cut_r = max(f + len_1, p_2_r)
        cut_1_left = max(0, len_1 - f - 1)
        cut_1_right = min(len_1, len_1 + len_2 - f - 1)
        cut_2_left = max(0, f - len_1 + 1)
        cut_2_right = min(len_2, f + 1)
        P_cat = P[cut_l:cut_r]
        p1_o = pattern_1[cut_1_left:cut_1_right]
        p2_o = pattern_2[cut_2_left:cut_2_right]
        o_l = max(p_2_l, f) - cut_l
        o_r = min(p_2_r, f + len_1) - cut_l
        return P_cat, p1_o, p2_o, o_l, o_r

    @staticmethod
    def merge_patterns(pattern_1, pattern_2, e=SYMBOL_EMPTY):
        len_1 = len(pattern_1)
        len_2 = len(pattern_2)
        total_len = len_1 + len_2 - 1
        dict_patterns_new = {}
        for f in range(total_len):
            P_cat, p1_o, p2_o, o_l, o_r = GomokuPatternGenerator.cat_pattern(pattern_1, pattern_2, f, len_1, len_2)
            if p1_o==p2_o:
                if all([k!=e for k in p1_o]):
                    dict_patterns_new[tuple(P_cat)] = [o_l,o_r]
        return dict_patterns_new

    @staticmethod
    def merge_patterns_flip(pattern_1, pattern_2, e=SYMBOL_EMPTY):
        dict_patterns_new = {}
        for p1t in [pattern_1,pattern_1[-1::-1]]:
            dpn_t = GomokuPatternGenerator.merge_patterns(p1t,pattern_2,e)
            dict_patterns_new.update(dpn_t)
        return dict_patterns_new


if __name__=='__main__':
    p1 = [1, 0, 1, 1, 0, 1, 0, 1, 1]
    p2 = [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1]
    '''
    for i in range(len(p1) + len(p2)):
        pcat, p1o, p2o, oleft, oright = GomokuPatternGenerator.cat_pattern(p1, p2, i, len(p1), len(p2))
        print(str(i) + ' : ' + str(pcat) + '  ' + str(p1o) + '  ' + str(p2o)+'  '+str(oleft)+'  '+str(oright))
    '''
    p1 = [1,1,1,1,0]
    p2 = p1.copy()
    dict_patterns_new = GomokuPatternGenerator.merge_patterns_flip(p1,p2,0)
    print(dict_patterns_new)

    pass
