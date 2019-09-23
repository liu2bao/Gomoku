from GomokuMain import Gomoku
from GomokuConst import TYPE_HUMAN, TYPE_AI, chain_num_default
from GomokuAI import GomokuAIToy, GomokuAIScore, GomokuAIScoreAlpha, GomokuAIScoreBeta
import pygame

chain_num = 5
AInum = 2
# G = Gomoku(player_alias=['Me', 'AI'], player_type=[TYPE_HUMAN, TYPE_AI], player_instances=[None, GomokuAIToy()])
# G = Gomoku(player_alias=['AI1', 'AI2'], player_type=[TYPE_AI, TYPE_AI], player_instances=[GomokuAIToy(), GomokuAIToy()])
# G = Gomoku(player_alias=['P1', 'P2'], player_type=[TYPE_HUMAN, TYPE_HUMAN])
# G = Gomoku(player_alias=['Me', 'AI'], player_type=[TYPE_HUMAN, TYPE_AI], player_instances=[None, GomokuAIScore()])
AI1 = GomokuAIScoreAlpha()
AI2 = GomokuAIScoreBeta(chain_num,layer=2)
G = Gomoku(player_alias=['AI1', 'AI2'], player_type=[TYPE_AI, TYPE_AI], player_instances=[AI1, AI2],
           chain_num=chain_num)
# G = Gomoku(player_alias=['AI'+str(t) for t in range(AInum)], player_type=[TYPE_AI]*AInum, player_instances=[GomokuAIScore() for t in range(AInum)])
pygame.init()
winner = G.start_game()
print(winner)
pygame.quit()