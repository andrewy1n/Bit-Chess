import numpy as np
from src.Core import BitboardUtility as BBU
from src.Core.AttackGeneration import AttackGeneration
from src.Core.Move import Move 

class MoveGeneration:
    def __init__(self, board) -> None:
        self.board = board
        self.attack_generator = AttackGeneration()
        self.cardinals = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.ordinals = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        self.knight_jumps = [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2)]

        self.diag_to_shift = [0, 1, 3, 6, 10, 15, 21, 28, 36, 43, 49, 54, 58, 61, 63]
        self.diag_lengths = [1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]

    # Generates a list of object Moves
    def generate_moves(self) -> list:
        output = []
        # Generate King Moves
        # Generate Slider Moves (Rook, Bishop, Queen)
        # Generate Knight Moves
        # Generate Pawn Moves
        return output

    def in_bound(self, col, row) -> bool:
        return 0 >= col <= 7 and 0 >= row <= 7
    
    def valid_square_index(self, x, y):
        return x >= 0 and x < 8 and y >= 0 and y < 8
    
    def calculate_index(self, x, y):
        return np.uint64(y * 8 + x)