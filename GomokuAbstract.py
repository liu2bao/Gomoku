from GomokuConst import cols_default, rows_default, chain_num_default, SYMBOL_EMPTY
import numpy as np


class GomokuHandler:
    def __init__(self, r=rows_default, c=cols_default, board=None, mpn=2, chain_num=chain_num_default):
        if isinstance(board, np.ndarray):
            self._rows, self._cols = board.shape
            self._board = board
        else:
            self._rows = r
            self._cols = c
            self._board = np.ones([r, c], dtype=np.int) * SYMBOL_EMPTY
        self._current_player = 0
        self.__chain_num = chain_num
        self.__max_player_num = mpn

    @property
    def board(self):
        return self._board

    @property
    def current_player(self):
        return self._current_player

    @board.setter
    def board(self, board):
        if isinstance(board, np.ndarray):
            self._rows, self._cols = board.shape
            self._board = board

    @current_player.setter
    def current_player(self, player):
        if isinstance(player, int):
            if player < 0 or player >= self.__max_player_num:
                player %= self.__max_player_num
            self._current_player = player

    def alternate(self):
        self.current_player += 1

    def check_within_range(self, row, col):
        f = (0 <= row < self._rows) and (0 <= col < self._cols)
        return f

    def __place_piece(self, row, col, player):
        flag = False
        if self.check_within_range(row, col):
            if self._board[row, col] == SYMBOL_EMPTY:
                self._board[row, col] = player
                flag = True
        return flag

    def place_piece(self, row, col, judge=True):
        flag_win = None
        flag_success = self.__place_piece(row, col, self._current_player)
        if judge:
            flag_win = self.__judge_chain_pos(row, col, self._current_player)
            if flag_win:
                return flag_win
        if flag_success:
            self.alternate()
        return flag_win

    def get_series_pos(self,row,col):
        coor_cur = np.array((row,col))
        directions = np.array(((0, 1), (1, 0), (1, 1), (-1, 1)))
        series = {}
        for d in directions:
            num_cand = 2 * self.__chain_num - 1
            mpt = [None]*num_cand
            for hh in range(num_cand):
                step = hh-self.__chain_num+1
                pos = coor_cur + d*step
                if (0<=pos[0]<self._rows) and (0<=pos[1]<self._cols):
                    mpt[hh] = self._board[pos[0],pos[1]]
            series[tuple(d)] = mpt
        return series

    def __judge_chain_pos(self, row, col, player):
        directions = np.array(((0, 1), (1, 0), (1, 1), (-1, 1)))
        max_pos = {}
        for d in directions:
            mpt = []
            for sig in [-1, 1]:
                dr = d * sig
                step = 1
                while True:
                    rt = row + dr[0] * step
                    ct = col + dr[1] * step
                    flag_continue = False
                    if self.check_within_range(rt, ct):
                        if self._board[rt, ct] == player:
                            flag_continue = True
                    if not flag_continue:
                        break
                    step += 1
                mpt.append(sig * (step - 1))
            max_pos[tuple(d)] = mpt
        f = any([abs(v[1] - v[0]) + 1 >= self.__chain_num for v in max_pos.values()])
        return f
