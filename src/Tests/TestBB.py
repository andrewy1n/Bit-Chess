from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core import BitboardUtility as BBU  
import numpy as np

board = Board()
move_generator = MoveGeneration(board)

board.make_move('P', (3, 1), (3, 3))
board.print_board()

pawn_map = move_generator.generate_pawn_attacks('w')
print('White Pawn Map')
BBU.printBB(pawn_map)
print()



'''
for x, row in enumerate(move_generator.knight_attacks):
    for y, bb in enumerate(row):
        print(x, y)
        BBU.printBB(bb)
        print()

for index, bb in enumerate(move_generator.file_attacks[2][4]):
    if bb != 0:
        print(index)
        BBU.printBB(bb | move_generator.rank_attacks[2][4][index])
        print()
'''