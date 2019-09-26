from GomokuMain import Gomoku
from GomokuConst import TYPE_HUMAN, TYPE_AI, chain_num_default
from GomokuAI import GomokuAIToy, GomokuAIScore, GomokuAIScoreAlpha, GomokuAIScoreBeta
from GomokuAIExternal import GomokuAIExt1
from GomokuPeripheral import GomokuStarter
import pygame

options = {'Human': None,
           'ExtAI': lambda cn: GomokuAIExt1(),
           'NormalAI': lambda cn: GomokuAIScoreAlpha(cn),
           'SmartAI': lambda cn: GomokuAIScoreBeta(cn, layer=2)}

AItexts = list(options.keys())
AIs = list(options.values())
AItypes = [TYPE_HUMAN if options[k] is None else TYPE_AI for k in AItexts]

pygame.init()
GS = GomokuStarter(AItexts, 15, default_choices={0: 0, 1: 0})
flag_confirm = GS.start()
if flag_confirm:
    choices = GS.choices
    chain_num = GS.chain_num
    rows = GS.rows
    cols = GS.cols
    print(choices)
    idx_valid = [hh for hh in range(len(choices)) if choices[hh] is not None]
    choices_valid = [choices[hh] for hh in idx_valid]
    player_aliases = [GS.player_aliases[hh] for hh in idx_valid]
    player_types = [AItypes[c] for c in choices_valid]
    player_instances = [AIs[c](chain_num) if AIs[c] else None for c in choices_valid]

    G = Gomoku(player_alias=player_aliases,
               player_type=player_types,
               player_instances=player_instances,
               chain_num=chain_num,
               r=rows, c=cols)
    winner = G.start_game()
    print(winner)

pygame.quit()
