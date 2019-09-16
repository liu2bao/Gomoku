import pygame
import os
import numpy as np
from GomokuConst import rows_default, cols_default, COLORS_ALL

LINE_WIDTH = 1
BORDER_WIDTH = LINE_WIDTH * 2
LINE_COLOR = BORDER_COLOR = BLACK = (0, 0, 0)
BIAS_PIVOT_X = BIAS_PIVOT_Y = 4
RATE_STONE = 0.8
MBX = MBY = 2
LABEL_X = 'x'
LABEL_Y = 'y'


class GomokuPainter:
    def __init__(self, h, w, r=rows_default, c=cols_default, ip=None):
        self._height = h
        self._width = w
        self._rows = r
        self._cols = c
        self._img_path = ip
        self._background_img = None
        self._mbx = MBX
        self._mby = MBY
        self._bpx = BIAS_PIVOT_X
        self._bpy = BIAS_PIVOT_Y
        self._coords = {}
        self._intervals = {}
        self.update_board_coords()
        self.__screen = None
        #self.__colors_stones = {SYMBOL_BLACK: (0, 0, 0), SYMBOL_WHITE: (255, 255, 255)}
        self.__colors_stones = COLORS_ALL
        self.__rate_stone = RATE_STONE

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def img_path(self):
        return self._img_path

    @property
    def h(self):
        return self._height

    @property
    def w(self):
        return self._width

    @property
    def r(self):
        return self._rows

    @property
    def c(self):
        return self._cols

    @property
    def i(self):
        return self._img_path

    @property
    def coords_x(self):
        return self._coords[LABEL_X]

    @property
    def coords_y(self):
        return self._coords[LABEL_Y]

    @property
    def interval_x(self):
        return self._intervals[LABEL_X]

    @property
    def interval_y(self):
        return self._intervals[LABEL_Y]

    @property
    def colors_stones(self):
        return self.__colors_stones

    @height.setter
    def height(self, h):
        self._height = h
        self.update_board_coords()

    @width.setter
    def width(self, w):
        self._width = w
        self.update_board_coords()

    @rows.setter
    def rows(self, r):
        self._rows = r
        self.update_board_coords()

    @cols.setter
    def cols(self, c):
        self._cols = c
        self.update_board_coords()

    @img_path.setter
    def img_path(self, i):
        self._img_path = i
        self.feed_bg()

    @colors_stones.setter
    def colors_stones(self,colors_stones):
        #TODO: check
        self.__colors_stones = colors_stones

    def update_board_coords(self):
        paras = {LABEL_X: (self._width, self._cols, self._mbx), LABEL_Y: (self._height, self._rows, self._mby)}
        for l, p in paras.items():
            full_len, n, mb = p
            total_lines = n + mb * 2
            interval = full_len / (total_lines - 1)
            self._coords[l] = (np.arange(n) + mb) * interval
            self._intervals[l] = interval

    def init_screen(self):
        self.__screen = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption("Gomoku")
        self.feed_bg()

    def feed_bg(self):
        if isinstance(self._img_path, str) and os.path.isfile(self._img_path):
            self._background_img = pygame.image.load(self._img_path).convert()

    def get_screen(self):
        return self.__screen

    def refresh_bg(self):
        self.__screen.blit(self._background_img, (0, 0))

    def get_bg_img(self):
        return self._background_img

    def draw_border(self):
        vertices = [(self.coords_x[0], self.coords_y[0]), (self.coords_x[0], self.coords_y[-1]),
                    (self.coords_x[-1], self.coords_y[-1]), (self.coords_x[-1], self.coords_y[0])]
        nvb = len(vertices)
        for idx_t in range(nvb):
            idx_t_end = idx_t + 1
            if idx_t_end >= nvb:
                idx_t_end = idx_t_end % nvb
            pygame.draw.line(self.__screen, BORDER_COLOR, vertices[idx_t], vertices[idx_t_end], BORDER_WIDTH)

    def draw_grids(self):
        labels = [LABEL_X, LABEL_Y]
        for h in range(len(labels)):
            label_t = labels[h]
            lc = labels[1 - h]
            coors_t = self._coords[label_t]
            coors_t_c = self._coords[lc]
            boundary = [coors_t_c[0], coors_t_c[-1]]
            for c in coors_t:
                if label_t == LABEL_X:
                    line_t = ((c, boundary[0]), (c, boundary[1]))
                else:
                    line_t = ((boundary[0], c), (boundary[1], c))
                pygame.draw.line(self.__screen, LINE_COLOR, line_t[0], line_t[1], LINE_WIDTH)

    def draw_pivots(self):
        mx = int(self._cols/2)
        my = int(self._rows/2)
        for xs in [self._bpx-1,mx,self._cols-self._bpx]:
            for ys in [self._bpy-1,my,self._rows-self._bpy]:
                pygame.draw.circle(self.__screen,LINE_COLOR,
                                   [int(p) for p in [self._coords[LABEL_X][xs],self._coords[LABEL_Y][ys]]],
                                   int(LINE_WIDTH*3))

    def draw_stone(self, row, col, color):
        w_t = self._intervals[LABEL_X] * self.__rate_stone
        h_t = self._intervals[LABEL_Y] * self.__rate_stone
        x_t = self._coords[LABEL_X][col]
        y_t = self._coords[LABEL_Y][row]
        rect_t = [x_t - w_t / 2, y_t - h_t / 2, w_t, h_t]
        pygame.draw.ellipse(self.__screen, color, rect_t)
        # r_t = min(w_t,h_t)/2
        # pygame.draw.circle(self.__screen,color,[int(round(x_t)),int(round(y_t))],int(round(r_t)))

    def judge_valid_player(self,player):
        f = 0<=player<len(self.__colors_stones)
        return f

    def draw_board(self, board):
        cols, rows = board.shape
        for r in range(rows):
            for c in range(cols):
                player = board[r,c]
                color_t = self.get_stone_color(player)
                if color_t:
                    self.draw_stone(r, c, color_t)
                c += 1
            r += 1

    def get_nearest_stone(self, x, y):
        if (x < self.coords_x[0] - self.interval_x) or (x > self.coords_x[-1] + self.interval_x):
            col = -1
        else:
            col = np.argmin(np.abs(self._coords[LABEL_X] - x))
        if (y < self.coords_y[0] - self.interval_y) or (y > self.coords_y[-1] + self.interval_y):
            row = -1
        else:
            row = np.argmin(np.abs(self._coords[LABEL_Y] - y))
        return row, col

    def get_stone_color(self,player):
        if self.judge_valid_player(player):
            return self.__colors_stones[player]
        return None

    def paint_all(self,board=None):
        self.refresh_bg()
        self.draw_border()
        self.draw_grids()
        self.draw_pivots()
        if board is not None:
            self.draw_board(board)

