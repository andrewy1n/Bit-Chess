from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core.PrecomputedAttacks import PrecomputedAttacks
from src.Core import BitboardUtility as BBU  
import numpy as np

board = Board()
attacks = PrecomputedAttacks()
move_generator = MoveGeneration(board, attacks)

board.make_move('P', (3, 1), (3, 3))
board.print_board()
bb, ind = BBU.popLSB(board.occupied)

BBU.printBB(bb)