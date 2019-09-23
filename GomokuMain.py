import pygame
from GomokuPaint import GomokuPainter
from GomokuAbstract import GomokuHandler
from GomokuConst import SYMBOL_EMPTY, rows_default, cols_default, COLORS_ALL, TYPE_HUMAN, IP, chain_num_default
import numpy as np
import warnings

WIDTH = 600
HEIGHT = 600
GRID_WIDTH = int(WIDTH / 20)
GRID_HEIGHT = int(HEIGHT / 20)

class Gomoku:
    def __init__(self, h=HEIGHT, w=WIDTH, r=rows_default, c=cols_default, ip=IP,
                 player_alias=None, player_type=None, player_instances=None,
                 chain_num=chain_num_default):
        self.__rows = r
        self.__cols = c
        self.GP = GomokuPainter(h, w, r, c, ip)
        self.GH = GomokuHandler(r, c, mpn=len(player_alias), chain_num=chain_num)
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

    def start_game(self):
        self.GP.init_screen()
        FPS = 30
        clock = pygame.time.Clock()

        orders = self.GH.board.copy()
        running = True
        flag_win = False
        count = 0
        winner = None
        while running:
            clock.tick(FPS)

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            flag_over = np.all(self.GH.board != SYMBOL_EMPTY)
            if flag_over:
                print('tied')

            if (not flag_win) and (not flag_over):
                row = col = None
                if self.get_current_player_type() == TYPE_HUMAN:
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            row, col = self.GP.get_nearest_stone(*event.pos)
                else:
                    row, col = self.get_current_player_instance().decide(self.GH.board, self.GH.current_player)
                    # time.sleep(2)
                if all([k is not None for k in [row, col]]):
                    flag_win = self.GH.place_piece(row, col)
                    orders[row, col] = count
                    count += 1
                    if flag_win:
                        winner = self.GH.current_player
                        print('Player # %s wins' % self.current_player_alias)
                        # running = False
                        if self.player_type[self.GH.current_player] == TYPE_HUMAN:
                            print(orders)

            self.GP.paint_all(self.GH.board)

            if (not flag_win) and (not flag_over):
                if self.get_current_player_type() == TYPE_HUMAN:
                    x, y = pygame.mouse.get_pos()
                    row, col = self.GP.get_nearest_stone(x, y)
                    if col >= 0 and row >= 0:
                        if self.GH.board[row][col] == SYMBOL_EMPTY:
                            color_t = self.GP.get_stone_color(self.GH.current_player)
                            self.GP.draw_stone(row, col, color_t)

            pygame.display.flip()
        pygame.quit()
        return winner


if __name__ == '__main__':
    pass
