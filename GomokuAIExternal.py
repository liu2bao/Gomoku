from GomokuConst import SYMBOL_EMPTY
from random import randint
import numpy as np

LEVEL_X = LEVEL_Y = 19
grade = 10
MAX = 1008611
ChainNum = 5

def Scan(chesspad, color, level_x=LEVEL_X, level_y=LEVEL_Y):
    shape = [[[0 for high in range(ChainNum)] for col in range(level_y)] for row in range(level_x)]
    # 扫描每一个点，然后在空白的点每一个方向上做出价值评估！！
    for i in range(level_x):
        for j in range(level_y):

            # 如果此处为空 那么就可以开始扫描周边
            if chesspad[i][j] == 0:
                m = i
                n = j
                # 如果上方跟当前传入的颜色参数一致，那么加分到0位！
                while n - 1 >= 0 and chesspad[m][n - 1] == color:
                    n -= 1
                    shape[i][j][0] += grade
                if n - 1 >= 0 and chesspad[m][n - 1] == 0:
                    shape[i][j][0] += 1
                if n - 1 >= 0 and chesspad[m][n - 1] == -color:
                    shape[i][j][0] -= 2
                m = i
                n = j
                # 如果下方跟当前传入的颜色参数一致，那么加分到0位！
                while (n + 1 < level_y and chesspad[m][n + 1] == color):
                    n += 1
                    shape[i][j][0] += grade
                if n + 1 < level_y and chesspad[m][n + 1] == 0:
                    shape[i][j][0] += 1
                if n + 1 < level_y and chesspad[m][n + 1] == -color:
                    shape[i][j][0] -= 2
                m = i
                n = j
                # 如果左边跟当前传入的颜色参数一致，那么加分到1位！
                while (m - 1 >= 0 and chesspad[m - 1][n] == color):
                    m -= 1
                    shape[i][j][1] += grade
                if m - 1 >= 0 and chesspad[m - 1][n] == 0:
                    shape[i][j][1] += 1
                if m - 1 >= 0 and chesspad[m - 1][n] == -color:
                    shape[i][j][1] -= 2
                m = i
                n = j
                # 如果右边跟当前传入的颜色参数一致，那么加分到1位！
                while (m + 1 < level_x and chesspad[m + 1][n] == color):
                    m += 1
                    shape[i][j][1] += grade
                if m + 1 < level_x and chesspad[m + 1][n] == 0:
                    shape[i][j][1] += 1
                if m + 1 < level_x and chesspad[m + 1][n] == -color:
                    shape[i][j][1] -= 2
                m = i
                n = j
                # 如果左下方跟当前传入的颜色参数一致，那么加分到2位！
                while (m - 1 >= 0 and n + 1 < level_y and chesspad[m - 1][n + 1] == color):
                    m -= 1
                    n += 1
                    shape[i][j][2] += grade
                if m - 1 >= 0 and n + 1 < level_y and chesspad[m - 1][n + 1] == 0:
                    shape[i][j][2] += 1
                if m - 1 >= 0 and n + 1 < level_y and chesspad[m - 1][n + 1] == -color:
                    shape[i][j][2] -= 2
                m = i
                n = j
                # 如果右上方跟当前传入的颜色参数一致，那么加分到2位！
                while (m + 1 < level_x and n - 1 >= 0 and chesspad[m + 1][n - 1] == color):
                    m += 1
                    n -= 1
                    shape[i][j][2] += grade
                if m + 1 < level_x and n - 1 >= 0 and chesspad[m + 1][n - 1] == 0:
                    shape[i][j][2] += 1
                if m + 1 < level_x and n - 1 >= 0 and chesspad[m + 1][n - 1] == -color:
                    shape[i][j][2] -= 2
                m = i
                n = j
                # 如果左上方跟当前传入的颜色参数一致，那么加分到3位！
                while (m - 1 >= 0 and n - 1 >= 0 and chesspad[m - 1][n - 1] == color):
                    m -= 1
                    n -= 1
                    shape[i][j][3] += grade
                if m - 1 >= 0 and n - 1 >= 0 and chesspad[m - 1][n - 1] == 0:
                    shape[i][j][3] += 1
                if m - 1 >= 0 and n - 1 >= 0 and chesspad[m - 1][n - 1] == -color:
                    shape[i][j][3] -= 2
                m = i
                n = j
                # 如果右下方跟当前传入的颜色参数一致，那么加分到3位！
                while m + 1 < level_x and n + 1 < level_y and chesspad[m + 1][n + 1] == color:
                    m += 1
                    n += 1
                    shape[i][j][3] += grade
                if m + 1 < level_x and n + 1 < level_y and chesspad[m + 1][n + 1] == 0:
                    shape[i][j][3] += 1
                if m + 1 < level_x and n + 1 < level_y and chesspad[m + 1][n + 1] == -color:
                    shape[i][j][3] -= 2
    return shape


def Sort(shape):
    for i in shape:
        for j in i:
            for x in range(ChainNum):
                for w in range(3, x - 1, -1):
                    if j[w - 1] < j[w]:
                        temp = j[w]
                        j[w - 1] = j[w]
                        j[w] = temp
    print("This Time Sort Done !")
    return shape


def Evaluate(shape, level_x=LEVEL_X, level_y=LEVEL_Y):
    for i in range(level_x):
        for j in range(level_y):

            if shape[i][j][0] == 4:
                return i, j, MAX
            shape[i][j][4] = shape[i][j][0] * 1000 + shape[i][j][1] * 100 + shape[i][j][2] * 10 + shape[i][j][3]
    max_x = 0
    max_y = 0
    max = 0
    for i in range(level_x):
        for j in range(level_y):
            if max < shape[i][j][4]:
                max = shape[i][j][4]
                max_x = i
                max_y = j
    print("the max is " + str(max) + " at ( " + str(max_x) + " , " + str(max_y) + " )")
    return max_x, max_y, max


def Autoplay(ch, m, n, level_x=LEVEL_X,level_y=LEVEL_Y):
    Ta = int((level_x - 1) / 2)
    Tb = int((level_y - 1) / 2)
    a1, b1 = [np.int32(np.round((np.random.rand(k)-0.5)*2)) for k in [Ta, Tb]]
    randa = randint(0, Ta-1)
    randb = randint(0, Tb-1)
    while m + a1[randa] >= 0 and m + a1[randa] < level_x and n + b1[randb] >= 0 and n + b1[randb] < level_y and \
            ch[m + a1[randa]][n + b1[randb]] != 0:
        randa = randint(0, Ta)
        randb = randint(0, Tb)
    return m + a1[randa], n + b1[randb]


def BetaGo(ch, m, n, color, times, level_x=LEVEL_X, level_y=LEVEL_Y):
    if times < 2:
        return Autoplay(ch, m, n, level_x, level_y)
    else:
        shape_P = Scan(ch, -color, level_x, level_y)
        shape_C = Scan(ch, color, level_x, level_y)
        shape_P = Sort(shape_P)
        shape_C = Sort(shape_C)
        max_x_P, max_y_P, max_P = Evaluate(shape_P, level_x, level_y)
        max_x_C, max_y_C, max_C = Evaluate(shape_C, level_x, level_y)
        if max_P > max_C and max_C < MAX:
            return max_x_P, max_y_P
        else:
            return max_x_C, max_y_C


class GomokuAIExt1:
    def __init__(self):
        self._times = 0
        self._Bn = None

    def decide(self, board, current_player):
        B = board.T.copy()
        eles = set(np.unique(B))
        opps = list(eles.difference({current_player, SYMBOL_EMPTY}))
        Bn = B.copy()
        if opps:
            opp = opps[0]
            Bn[B == opp] = 1
        Bn[B == current_player] = -1
        Bn[B == SYMBOL_EMPTY] = 0
        if self._Bn is None:
            self._Bn = np.zeros(Bn.shape)
        pos_change = np.argwhere(np.logical_and(self._Bn == 0, Bn == 1))
        level_x, level_y = Bn.shape
        if pos_change.size > 0:
            m, n = pos_change[0]
        else:
            m = int((level_x - 1) / 2)
            n = int((level_y - 1) / 2)
        x, y = BetaGo(Bn, m, n, -1, self._times, level_x=level_x, level_y=level_y)
        self._Bn = Bn
        self._times += 1
        return y, x
