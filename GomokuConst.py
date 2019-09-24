import os

rows_default = cols_default = 19
chain_num_default = 5

SYMBOL_WHITE = 1
SYMBOL_BLACK = 0
SYMBOL_EMPTY = -1
COLORS_ALL = [(0, 0, 0), (255, 255, 255), (0, 0, 255), (0, 255, 0),
              (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

BLACK = (0, 0, 0)
BLUE = (106, 159, 181)
WHITE = (255, 255, 255)

TYPE_HUMAN = 0
TYPE_AI = 1
IP = os.path.join('images', 'BG.jpg')
WIDTH = 600
HEIGHT = 600