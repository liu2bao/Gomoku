import pygame
import os
from GomokuPaint import GomokuPainter
from GomokuAbstract import GomokuHandler
from GomokuConst import SYMBOL_EMPTY, rows_default, cols_default, COLORS_ALL
from GomokuAI import GomokuAIToy, GomokuAIScore, GomokuAIScoreAlpha
import numpy as np
import warnings
import time

WIDTH = 600
HEIGHT = 600
GRID_WIDTH = int(WIDTH / 20)
GRID_HEIGHT = int(HEIGHT / 20)
BLACK = [0, 0, 0]
TYPE_HUMAN = 0
TYPE_AI = 1
IP = os.path.join('images', 'BG.jpg')


class Gomoku:
    def __init__(self, h=HEIGHT, w=WIDTH, r=rows_default, c=cols_default, ip=IP,
                 player_alias=None, player_type=None, player_instances=None):
        self.__rows = r
        self.__cols = c
        self.GP = GomokuPainter(h, w, r, c, ip)
        self.GH = GomokuHandler(r, c, mpn=len(player_alias))
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

AInum = 2
# G = Gomoku(player_alias=['Me', 'AI'], player_type=[TYPE_HUMAN, TYPE_AI], player_instances=[None, GomokuAIToy()])
# G = Gomoku(player_alias=['AI1', 'AI2'], player_type=[TYPE_AI, TYPE_AI], player_instances=[GomokuAIToy(), GomokuAIToy()])
# G = Gomoku(player_alias=['P1', 'P2'], player_type=[TYPE_HUMAN, TYPE_HUMAN])
G = Gomoku(player_alias=['Me', 'AI'], player_type=[TYPE_HUMAN, TYPE_AI], player_instances=[None, GomokuAIScore()])
AI1 = GomokuAIScoreAlpha()
AI2 = GomokuAIScore()
# G = Gomoku(player_alias=['AI1', 'AI2'], player_type=[TYPE_AI, TYPE_AI], player_instances=[AI1,AI2])
# G = Gomoku(player_alias=['AI'+str(t) for t in range(AInum)], player_type=[TYPE_AI]*AInum, player_instances=[GomokuAIScore() for t in range(AInum)])
G.GP.init_screen()
screen = G.GP.get_screen()

'''
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gomoku")
'''

FPS = 30
clock = pygame.time.Clock()

background_img = G.GP.get_bg_img()


orders = G.GH.board.copy()
pygame.init()
pygame.mixer.init()
running = True
flag_win = False
count = 0
while running:
    # 设置屏幕刷新频率
    clock.tick(FPS)

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    flag_over = np.all(G.GH.board!=SYMBOL_EMPTY)
    if flag_over:
        print('tied')

    if (not flag_win) and (not flag_over):
        row = col = None
        if G.get_current_player_type() == TYPE_HUMAN:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = G.GP.get_nearest_stone(*event.pos)
        else:
            row, col = G.get_current_player_instance().decide(G.GH.board, G.GH.current_player)
            # time.sleep(2)
        if all([k is not None for k in [row, col]]):
            flag_win = G.GH.place_piece(row, col)
            orders[row,col] = count
            count += 1
            if flag_win:
                print('Player # %s wins' % G.current_player_alias)
                print(orders)

    # draw_background(screen)
    G.GP.paint_all(G.GH.board)

    if (not flag_win) and (not flag_over):
        if G.get_current_player_type() == TYPE_HUMAN:
            x, y = pygame.mouse.get_pos()
            row, col = G.GP.get_nearest_stone(x, y)
            if col >= 0 and row >= 0:
                if G.GH.board[row][col] == SYMBOL_EMPTY:
                    color_t = G.GP.get_stone_color(G.GH.current_player)
                    G.GP.draw_stone(row, col, color_t)

    pygame.display.flip()




