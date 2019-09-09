import pygame
import os
from GomokuPaint import GomokuPainter
from GomokuAbstract import GomokuHandler
from GomokuConst import SYMBOL_EMPTY, rows_default, cols_default, COLORS_ALL
from GomokuAI import GomokuAIToy
import numpy as np
import warnings

WIDTH = 640
HEIGHT = 640
GRID_WIDTH = int(WIDTH / 20)
GRID_HEIGHT = int(HEIGHT / 20)
BLACK = [0, 0, 0]
TYPE_HUMAN = 0
TYPE_AI = 1


class Gomoku:
    def __init__(self, h, w, r=rows_default, c=cols_default, ip=None,
                 player_alias=None, player_type=None, player_instances=None):
        self.__rows = r
        self.__cols = c
        self.GP = GomokuPainter(h, w, r, c, ip)
        self.GH = GomokuHandler(r, c)
        if player_alias is None:
            player_alias = ['Black', 'White']
        if player_type is None:
            player_type = np.ones(len(player_alias), dtype=np.int) * TYPE_HUMAN
        if len(player_alias) > len(COLORS_ALL):
            warnings.warn('Not enough colors')
        self._player_alias = player_alias
        self._player_type = player_type
        self._player_instances = player_instances

    @property
    def player_alias(self):
        return self._player_alias

    @property
    def player_type(self):
        return self._player_type

    @property
    def player_instances(self):
        return self._player_instances

    @property
    def current_player_alias(self):
        return self._player_alias[self.GH.current_player]

    def get_current_player_type(self):
        return self.player_type[self.GH.current_player]

    def get_current_player_instance(self):
        return self.player_instances[self.GH.current_player]


# G = Gomoku(HEIGHT, WIDTH, ip=os.path.join('images', 'BG.jpg'),
#            player_alias=['Me', 'AI'], player_type=[TYPE_HUMAN, TYPE_AI],
#            player_instances=[None, GomokuAI()])
G = Gomoku(HEIGHT, WIDTH, ip=os.path.join('images', 'BG.jpg'),
           player_alias=['AI1', 'AI2'], player_type=[TYPE_AI, TYPE_AI],
           player_instances=[GomokuAIToy(), GomokuAIToy()])
G.GP.init_screen()
screen = G.GP.get_screen()

'''
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gomoku")
'''

FPS = 30
clock = pygame.time.Clock()

background_img = G.GP.get_bg_img()


def draw_background(surf):
    # 加载背景图片
    surf.blit(background_img, (0, 0))

    # 画网格线，棋盘为 19行 19列的
    # 1. 画出边框，这里 GRID_WIDTH = WIDTH // 20
    rect_lines = [
        ((GRID_WIDTH, GRID_WIDTH), (GRID_WIDTH, HEIGHT - GRID_WIDTH)),
        ((GRID_WIDTH, GRID_WIDTH), (WIDTH - GRID_WIDTH, GRID_WIDTH)),
        ((GRID_WIDTH, HEIGHT - GRID_WIDTH),
         (WIDTH - GRID_WIDTH, HEIGHT - GRID_WIDTH)),
        ((WIDTH - GRID_WIDTH, GRID_WIDTH),
         (WIDTH - GRID_WIDTH, HEIGHT - GRID_WIDTH)),
    ]
    for line in rect_lines:
        pygame.draw.line(surf, BLACK, line[0], line[1], 2)

    # 画出中间的网格线
    for i in range(17):
        pygame.draw.line(surf, BLACK,
                         (GRID_WIDTH * (2 + i), GRID_WIDTH),
                         (GRID_WIDTH * (2 + i), HEIGHT - GRID_WIDTH))
        pygame.draw.line(surf, BLACK,
                         (GRID_WIDTH, GRID_WIDTH * (2 + i)),
                         (HEIGHT - GRID_WIDTH, GRID_WIDTH * (2 + i)))

    # 画出棋盘中的五个点，围棋棋盘上为9个点，这里我们只画5个
    circle_center = [
        (GRID_WIDTH * 4, GRID_WIDTH * 4),
        (WIDTH - GRID_WIDTH * 4, GRID_WIDTH * 4),
        (WIDTH - GRID_WIDTH * 4, HEIGHT - GRID_WIDTH * 4),
        (GRID_WIDTH * 4, HEIGHT - GRID_WIDTH * 4),
        (GRID_WIDTH * 10, GRID_WIDTH * 10)
    ]
    for cc in circle_center:
        pygame.draw.circle(surf, BLACK, cc, 5)


pygame.init()
pygame.mixer.init()
running = True
flag_win = False
while running:
    # 设置屏幕刷新频率
    clock.tick(FPS)

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if not flag_win:
        row = col = None
        if G.get_current_player_type() == TYPE_HUMAN:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = G.GP.get_nearest_stone(*event.pos)
        else:
            row, col = G.get_current_player_instance().decide(G.GH.board, G.GH.current_player)
        if all([k is not None for k in [row, col]]):
            flag_win = G.GH.place_piece(row, col)
            if flag_win:
                print('Player # %s wins' % G.current_player_alias)

    # draw_background(screen)
    G.GP.refresh_bg()
    G.GP.draw_border()
    G.GP.draw_grids()
    G.GP.draw_pivots()
    G.GP.draw_board(G.GH.board)

    if not flag_win:
        if G.get_current_player_type() == TYPE_HUMAN:
            x, y = pygame.mouse.get_pos()
            row, col = G.GP.get_nearest_stone(x, y)
            if col >= 0 and row >= 0:
                if G.GH.board[row][col] == SYMBOL_EMPTY:
                    color_t = G.GP.get_stone_color(G.GH.current_player)
                    G.GP.draw_stone(row, col, color_t)

    pygame.display.flip()
