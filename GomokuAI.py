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


class GomokuAIScoreOld:
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
                flag_match = list(series_cut) == list(pattern)
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
        # TODO: row number not equal to column number?
        num_cand = min([2 * self._max_pattern_len - 1, rows, cols])
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
                            # score_temp_mod = score_temp/den
                            mat_scores[r, c, hh] += score_temp_mod
                else:
                    mat_scores[r, c, :] = -1
        if self._sum:
            mat_scores_m = np.sum(mat_scores, axis=2)
        else:
            mat_scores_m = np.max(mat_scores, axis=2)
        rd, cd = np.unravel_index(mat_scores_m.argmax(), mat_scores_m.shape)
        return rd, cd



class GomokuAIScore:
    """Move by scoring each position, incremental update"""

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
        self._directions = np.array(((0, 1), (1, 0), (1, 1), (-1, 1)))
        self._board = None
        self._score_mat = None
        self._players = None

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
                flag_match = list(series_cut) == list(pattern)
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
        dict_series = {}
        # TODO: row number not equal to column number?
        num_cand = min([2 * self._max_pattern_len - 1, rows, cols])
        pos_center = int((num_cand - 1) / 2)
        for d in self._directions:
            mpt = self.get_series_pos_single_direction(board, coor_cur, d, num_cand, pos_center, rows, cols)
            if place:
                mpt[pos_center] = cp
            dict_series[tuple(d)] = mpt
        if return_center:
            return dict_series, pos_center
        else:
            return dict_series

    @staticmethod
    def get_series_pos_single_direction(board, coor_cur, d, num_cand, pos_center, rows, cols):
        mpt = [None] * num_cand
        for hh in range(num_cand):
            step = hh - pos_center
            pos = coor_cur + d * step
            if (0 <= pos[0] < rows) and (0 <= pos[1] < cols):
                mpt[hh] = board[pos[0], pos[1]]
        return mpt

    def decide(self, board, current_player):
        rows, cols = board.shape
        num_cand = min([2 * self._max_pattern_len - 1, rows, cols])
        pos_center = int((num_cand - 1) / 2)
        if np.all(board == SYMBOL_EMPTY):
            rd = int(rows / 2)
            cd = int(cols / 2)
            return rd, cd
        pd = np.unique(board)
        pa = np.append(pd, current_player)
        players = list(set(pa).difference({SYMBOL_EMPTY}))
        numd = len(self._directions)
        if self._board is None:
            self._board = np.ones([rows,cols])*self._e
            self._players = players.copy()
            self._score_mat = np.zeros([rows,cols,len(self._players),numd])
        else:
            new_players = set(players).difference(set(self._players))
            if new_players:
                zeros_t = np.zeros([rows,cols,len(new_players),numd])
                self._score_mat = np.concatenate([self._score_mat,zeros_t],axis=2)
                self._players.extend(list(new_players))
        nump = len(self._players)
        idx_changed = np.argwhere(board!=self._board)
        exn = self._max_pattern_len - 1
        pos_check = []
        for pos0 in idx_changed:
            for ll in range(numd):
                d_search = self._directions[ll]
                for sig in [-1,1]:
                    for step in range(-exn+1,exn):
                        r,c = pos0+d_search*sig*step
                        if (0<=r<rows) and (0<=c<cols):
                            if board[r, c] == SYMBOL_EMPTY:
                                pos_check.append((r,c,ll))
                            else:
                                self._score_mat[r, c, :, ll] = -1
        for r,c,ll in set(pos_check):
            d_search = self._directions[ll]
            series_t = self.get_series_pos_single_direction(board=board, coor_cur=np.array((r, c)), d=d_search,
                                                            num_cand=num_cand, pos_center=pos_center,
                                                            rows=rows, cols=cols)
            for hh in range(nump):
                p = self._players[hh]
                if p == current_player:
                    den = 1
                else:
                    den = nump
                series_t_r = series_t.copy()
                series_t_r[pos_center] = p
                score_temp, pattern_matched = self.score_pos({tuple(d_search): series_t_r}, p)
                score_temp_mod = score_temp
                # score_temp_mod = score_temp/den
                self._score_mat[r, c, hh, ll] = score_temp_mod
        mat_scores_all_direction = np.sum(self._score_mat,axis=3)
        if self._sum:
            mat_scores_m = np.sum(mat_scores_all_direction, axis=2)
        else:
            mat_scores_m = np.max(mat_scores_all_direction, axis=2)
        rd, cd = np.unravel_index(mat_scores_m.argmax(), mat_scores_m.shape)
        self._board = board.copy()
        return rd, cd


class GomokuAIScoreS:
    """Move by scoring each position, incremental update"""

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
                flag_match = list(series_cut) == list(pattern)
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
        # TODO: row number not equal to column number?
        num_cand = min([2 * self._max_pattern_len - 1, rows, cols])
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
                    else:
                        break
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
                            # score_temp_mod = score_temp/den
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


class GomokuAIScoreBeta(GomokuAIScore):
    def __init__(self, chain_num=chain_num_default, layer=2, max_pattern_len=None):
        super(GomokuAIScoreBeta, self).__init__(chain_num)
        GPG = GomokuPatternGenerator(chain_num, self.s, self.e, self.d)
        dict_scores = GPG.generate_scores(layer)
        self.score_dict = dict_scores
        self.max_pattern_len = max_pattern_len


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
            if p1_o == p2_o:
                if all([k != e for k in p1_o]):
                    dict_patterns_new[tuple(P_cat)] = [o_l, o_r]
        return dict_patterns_new

    @staticmethod
    def merge_patterns_flip(pattern_1, pattern_2, e=SYMBOL_EMPTY):
        dict_patterns_new = {}
        for p1t in [pattern_1, pattern_1[-1::-1]]:
            dpn_t = GomokuPatternGenerator.merge_patterns(p1t, pattern_2, e)
            dict_patterns_new.update(dpn_t)
        return dict_patterns_new

    def check_chain(self, pattern):
        mc = 0
        for i in range(len(pattern)):
            p = pattern[i]
            if p == self._s:
                mc += 1
                if mc >= self._chain_num:
                    return True
            else:
                mc = 0
        return False

    def generate_patterns(self, layer=1):
        key_0 = 0
        patterns_winning = {key_0: {tuple([self._s] * self._chain_num): [0, self._chain_num]}}
        patterns_puzzles = {}
        increase_keys = list(patterns_winning.keys())
        dict_keys_layers = {0: increase_keys}
        for l in range(layer):
            increase_keys_new = []
            patterns_puzzles_new = {}
            for ik in increase_keys:
                pattern_puzzle_t = []
                if ik in patterns_winning.keys():
                    pwt_s = patterns_winning[ik]
                    for pwt, ovpos in pwt_s.items():
                        for hh in range(ovpos[0], ovpos[1]):
                            if pwt[hh] == self._s:
                                pwtt = list(pwt)
                                pwtt[hh] = self._e
                                if (pwtt not in pattern_puzzle_t) and (pwtt[-1::-1] not in pattern_puzzle_t):
                                    pattern_puzzle_t.append(pwtt)
                patterns_puzzles_new[ik] = pattern_puzzle_t
            for k1, puzzle1 in patterns_puzzles_new.items():
                for dict2 in [patterns_puzzles_new, patterns_puzzles]:
                    for k2, puzzle2 in dict2.items():
                        kcomb = (k1, k2)
                        patterns_comb = {}
                        for p1 in puzzle1:
                            for p2 in puzzle2:
                                dict_patterns_new = self.merge_patterns_flip(p1, p2, self._e)
                                patterns_winning_new_valid = {p: o for p, o in dict_patterns_new.items()
                                                              if not self.check_chain(p)}
                                patterns_comb.update(patterns_winning_new_valid)
                        keys_comb_valid = []
                        keys_all_t = set(list(patterns_comb.keys()))
                        for p1 in patterns_comb.keys():
                            flag_valid_t = True
                            patterns_comb_diff = keys_all_t.difference({p1})
                            for pct in [patterns_comb_diff, patterns_winning.values()]:
                                for p2 in pct:
                                    if GomokuAIScore.match_pattern(p1, p2):
                                        flag_valid_t = False
                                        break
                                if not flag_valid_t:
                                    break
                            if flag_valid_t:
                                keys_comb_valid.append(p1)
                        patterns_comb_valid = {k: patterns_comb[k] for k in keys_comb_valid}
                        if patterns_comb_valid:
                            patterns_winning[kcomb] = patterns_comb_valid
                            increase_keys_new.append(kcomb)
            patterns_puzzles_new = {k: v for k, v in patterns_puzzles_new.items() if v}
            if patterns_puzzles_new:
                increase_keys = increase_keys_new.copy()
                patterns_puzzles.update(patterns_puzzles_new)
                dict_keys_layers[l + 1] = increase_keys_new
            else:
                break
        return patterns_winning, patterns_puzzles, dict_keys_layers

    def generate_scores(self, layer=1):
        dict_scores = {}
        patterns_winning, patterns_puzzles, dict_keys_layers = self.generate_patterns(layer)
        layers = list(dict_keys_layers.keys())
        layers.sort()
        M = 1e8
        dM = M / 10
        kz = 2
        kp = 10
        Nk = max(layers)
        for l in layers:
            ik = dict_keys_layers[l]
            st = M - dM / Nk * l
            stz = st / kz
            for kt in ik:
                if kt in patterns_winning.keys():
                    for pattern_t in patterns_winning[kt].keys():
                        dict_scores[pattern_t] = st
                if kt in patterns_puzzles.keys():
                    puzzles_t = patterns_puzzles[kt]
                    puzzles_r_ori = puzzles_t.copy()
                    stt = stz
                    while True:
                        puzzles_r_parent = []
                        for puzzle_t in puzzles_r_ori:
                            pnews_tuple = [tuple(k) for k in [puzzle_t, puzzle_t[-1::-1]]]
                            pin = set(pnews_tuple).intersection(set(dict_scores.keys()))
                            if pin:
                                flag_append = False
                                for ppin in pin:
                                    scomp = dict_scores[ppin]
                                    if scomp < stt:
                                        flag_append = True
                                        dict_scores[ppin] = stt
                                if flag_append:
                                    puzzles_r_parent.append(tuple(puzzle_t))
                            else:
                                dict_scores[tuple(puzzle_t)] = stt
                                puzzles_r_parent.append(tuple(puzzle_t))

                        puzzles_r = []
                        for p in puzzles_r_parent:
                            for hh in range(len(p)):
                                pc = list(p)
                                if pc[hh] == self._s:
                                    pc[hh] = self._e
                                    if not all([pcc == self._e for pcc in pc]):
                                        puzzles_r.append(pc)
                        stt /= kp
                        if not puzzles_r:
                            break
                        else:
                            puzzles_r_ori = puzzles_r.copy()

        dict_scores_filtered = dict_scores.copy()
        '''
        dict_scores_filtered = {}
        for p1 in dict_scores.keys():
            flag_overlap = False
            for p2 in set(dict_scores.keys()).difference({p1}):
                if GomokuAIScore.match_pattern(p1,p2):
                    s1, s2 = [dict_scores[k] for k in [p1,p2]]
                    if s2 > s1:
                        flag_overlap = True
                        break
            if not flag_overlap:
                dict_scores_filtered[p1] = dict_scores[p1]
        '''
        patterns = list(dict_scores_filtered.keys())
        scores = [dict_scores_filtered[p] for p in patterns]
        idx = np.argsort(scores)[-1::-1]
        dict_scores_sorted = {patterns[hh]: scores[hh] for hh in idx}

        keys_sorted = list(dict_scores_sorted.keys())
        values_sorted = list(dict_scores_sorted.values())
        idx_max = int(np.argmax(values_sorted))
        dict_scores_sorted[keys_sorted[idx_max]] *= 10
        return dict_scores_sorted


if __name__ == '__main__':
    GPG = GomokuPatternGenerator(5)
    ds = GPG.generate_scores(2)
    pw, pz, dkl = GPG.generate_patterns(2)
    print(pw)
    print(pz)
