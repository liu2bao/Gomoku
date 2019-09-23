import os

rows_default = cols_default = 19
chain_num_default = 5

SYMBOL_WHITE = 1
SYMBOL_BLACK = 0
SYMBOL_EMPTY = -1
COLORS_ALL = [(0, 0, 0), (255, 255, 255), (0,0,255), (0,255,0), (255,255,0), (255,255,0)]

BLACK = [0, 0, 0]
TYPE_HUMAN = 0
TYPE_AI = 1
IP = os.path.join('images', 'BG.jpg')