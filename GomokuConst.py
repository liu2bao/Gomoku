import os

rows_default = cols_default = 19
# rows_default, cols_default = 12,20
chain_num_default = 5
sdgen = lambda x,y: (x-y,x,x+y)
cns_default = sdgen(chain_num_default,2)
rse_default = sdgen(rows_default,10)
cse_default = sdgen(cols_default,10)

SYMBOL_WHITE = 1
SYMBOL_BLACK = 0
SYMBOL_EMPTY = -1
BLACK = (0, 0, 0)
BLUE = (106, 159, 181)
WHITE = (255, 255, 255)
COLORS_ALL = [BLACK, WHITE, (0, 0, 255), (0, 255, 0),
              (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]


TYPE_HUMAN = 0
TYPE_AI = 1
IP = os.path.join('images', 'BG.jpg')
WIDTH = 600
HEIGHT = 600
