from GomokuConst import SYMBOL_EMPTY,chain_num_default
from GomokuAbstract import GomokuHandler
import numpy as np


class GomokuAIToy:
    def __init__(self):
        pass

    def decide(self,board,current_player):
        rows,cols = board.shape
        for r in range(rows):
            for c in range(cols):
                if board[r,c]==SYMBOL_EMPTY :
                    return r,c


class GomokuAIAlpha:
    def __init__(self,chain_num=chain_num_default):
        self.__chain_num=chain_num
        pass

    def get_series_pos(self, board, r, c, rows, cols):
        coor_cur = np.array((r, c))
        directions = np.array(((0, 1), (1, 0), (1, 1), (-1, 1)))
        series = {}
        for d in directions:
            num_cand = 2 * self.__chain_num - 1
            mpt = [None]*num_cand
            for hh in range(num_cand):
                step = hh-self.__chain_num+1
                pos = coor_cur + d*step
                if (0<=pos[0]<rows) and (0<=pos[1]<cols):
                    mpt[hh] = board[pos[0],pos[1]]
            series[tuple(d)] = mpt
        return series

    def decide(self,board,current_player):
        rows, cols = board.shape

        pass

