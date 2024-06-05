import numpy as np
import math
from src.Core import BitboardUtility as BBU

'''
Generates Precomputed Attacks for Opposing Players
'''
class PrecomputedAttacks:
    def __init__(self) -> None:
        self.cardinals = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.ordinals = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        self.knight_jumps = [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2)]

        self.diag_to_shift = [0, 1, 3, 6, 10, 15, 21, 28, 36, 43, 49, 54, 58, 61, 63]
        self.diag_lengths = [1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]
        
        # Will be initialized beforehand
        self.knight_attacks = np.zeros(64, dtype=np.uint64)
        self.white_pawn_attacks = np.zeros(64, dtype=np.uint64)
        self.black_pawn_attacks = np.zeros(64, dtype=np.uint64)
        self.king_moves = np.zeros(64, dtype=np.uint64)

        self.rank_attacks = np.zeros((64, 256), dtype=np.uint64)
        self.file_attacks = np.zeros((64, 256), dtype=np.uint64)

        self.diagR_attacks = np.zeros((64, 256), dtype=np.uint64)
        self.diagL_attacks = np.zeros((64, 256), dtype=np.uint64)

        self.align_mask = np.zeros((64, 64), dtype=np.uint64)

        for x in range(8):
            for y in range(8):
                self.process_square(x, y)
        
        self.generate_align_mask()

    def process_square(self, x: int, y: int):
        # King Attacks
        index = self.calculate_index(x, y)
        for i in range(4):
            card_x = x + self.cardinals[i][0]
            card_y = y + self.cardinals[i][1]
            diag_x = x + self.ordinals[i][0]
            diag_y = y + self.ordinals[i][1]

            if self.valid_square_index(card_x, card_y):
                card_target_index = self.calculate_index(card_x, card_y)
                self.king_moves[index] = BBU.set_square(self.king_moves[index], card_target_index)
            
            if self.valid_square_index(diag_x, diag_y):
                diag_target_index = self.calculate_index(diag_x, diag_y)
                self.king_moves[index] = BBU.set_square(self.king_moves[index], diag_target_index)
        
        # Knight Attacks
        for dx, dy in self.knight_jumps:
            knight_x = x + dx
            knight_y = y + dy

            if self.valid_square_index(knight_x, knight_y):
                knight_target_index = self.calculate_index(knight_x, knight_y)
                self.knight_attacks[index] = BBU.set_square(self.knight_attacks[index], knight_target_index)
        
        # Pawn Attacks
        if self.valid_square_index(x+1, y+1):
            white_pawn_right = self.calculate_index(x+1, y+1)
            self.white_pawn_attacks[index] = BBU.set_square(self.white_pawn_attacks[index], white_pawn_right)
            
        if self.valid_square_index(x-1, y+1):
            white_pawn_left = self.calculate_index(x-1, y+1)
            self.white_pawn_attacks[index] = BBU.set_square(self.white_pawn_attacks[index], white_pawn_left)
        
        if self.valid_square_index(x+1, y-1):
            black_pawn_right = self.calculate_index(x+1, y-1)
            self.black_pawn_attacks[index] = BBU.set_square(self.black_pawn_attacks[index], black_pawn_right)
        
        if self.valid_square_index(x-1, y-1):
            black_pawn_left = self.calculate_index(x-1, y-1)
            self.black_pawn_attacks[index] = BBU.set_square(self.black_pawn_attacks[index], black_pawn_left)
        
        self.generate_ortho_attacks(x, y)
        self.generate_diagonal_attacks(x, y)
    
    # Generates all Orthogonal Attacks(Rank and File Attacks)
    def generate_ortho_attacks(self, x: int, y: int):
        rank_index = self.calculate_index(x, y)
        file_index = self.calculate_index(y, x)
        
        rank_arr = self.rank_attacks[rank_index]
        file_arr = self.file_attacks[file_index]

        # Create all possible blocker configurations
        def generate_blockers(cur_file, blockers):

            # use blockers value as index, generate slider moves with normalized blockers shifted to correct row
            normalized_bb = self.generate_slider_moves(x, y, blockers << np.uint(y*8))

            rank_arr[blockers & np.uint64(255)] = normalized_bb
            file_arr[blockers & np.uint64(255)] = BBU.rotate_mirrored90c(normalized_bb)

            for file in range(cur_file, 8):
                # i cannot already be in blockers, and cannot be the same x position of the piece
                if not BBU.contains_square(blockers, file):
                    generate_blockers(file, BBU.set_square(blockers, file))
        
        generate_blockers(0, BBU.set_square(np.uint64(0), x))

    # Generates all diagonal attacks (Bishops and Queens)
    def generate_diagonal_attacks(self, x: int, y: int):
        diagR_index = self.calculate_index(x, y)
        diagL_index = self.calculate_index(7-y, x)

        diagR_arr = self.diagR_attacks[diagR_index]
        diagL_arr = self.diagL_attacks[diagL_index]
        
        # Create all possible blocker configurations on the diagonal
        def generate_blockers(cur_step, blockers):
            # generate diagonal moves based on current blockers and store into a bitboard
            normalized_bb = self.generate_diagonal_moves(x, y, blockers)

            # Calculate relative indices for left and right attacks, using 45 degree board rotations and shifts
            right_arr_index = BBU.rotate45(blockers) >> self.diag_to_shift[7-x+y]
            left_arr_index = BBU.rotate45(BBU.rotate90cc(blockers), is_right=False) >> self.diag_to_shift[7-x+y]

            # Set index of diagonal array to relative diagonal moves
            diagR_arr[right_arr_index] = normalized_bb
            diagL_arr[left_arr_index] = BBU.rotate90cc(normalized_bb)

            # Iterate through current step, up to 8 (this is overcounting)
            for step in range(cur_step, 8):
                # Index must be valid, cannot already contain a piece, and cannot be the same index as the current piece
                if self.valid_square_index(x + step, y + step):
                    # Generate new possible index
                    index = self.calculate_index(x + step, y + step)
                    
                    if not BBU.contains_square(blockers, index):
                    # Recurse with new step and new index
                        generate_blockers(step, BBU.set_square(blockers, index))
        
        generate_blockers(-min(x, y), BBU.set_square(np.uint64(0), diagR_index))

    # Generates moves as bitboard of left and right attacks
    def generate_slider_moves(self, x: int, y: int, blockers: np.uint64):
        moves_bb = np.uint64(0)
        # Moves right of piece
        right_bound = 8-x
        for dx in range(1, right_bound):
            if self.valid_square_index(x + dx, y):
                index = self.calculate_index(x + dx, y)
                # Include first blocker as possible capture
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        # Moves left of piece
        for dx in range(1, x+1):
            if self.valid_square_index(x - dx, y):
                index = self.calculate_index(x - dx, y)
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        return moves_bb
    
    # Generates diagonal moves along the right diagonal
    def generate_diagonal_moves(self, x: int, y: int, blockers: np.uint64):
        moves_bb = np.uint64(0)

        # Moves right of piece
        right_bound = 8-x
        for step in range(1, right_bound):
            if self.valid_square_index(x + step, y + step):
                index = self.calculate_index(x + step, y + step)
                # Include first blocker as possible capture
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        # Moves left of piece
        for step in range(1, x+1):
            if self.valid_square_index(x - step, y - step):
                index = self.calculate_index(x - step, y - step)
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        return moves_bb
    
    def generate_align_mask(self):
        for start_index in range(64):
            for end_index in range(64):
                start_x, end_x = start_index % 8, end_index % 8
                start_y, end_y = start_index // 8, end_index // 8
                delta_x, delta_y = end_x - start_x, end_y - start_y
                dir_x = int(math.copysign(1, delta_x)) if delta_x != 0 else 0
                dir_y = int(math.copysign(1, delta_y)) if delta_y != 0 else 0
                
                if start_index == 3 and end_index == 19:
                    print(dir_x, dir_y)
                
                for i in range(-8, 8):
                    x = start_x + i * dir_x
                    y = start_y + i * dir_y
                    if self.valid_square_index(x, y):
                        self.align_mask[start_index][end_index] |= np.uint64(1) << np.uint64(self.calculate_index(x, y))


    def generate_pawn_attacks_left(self, color, pawn_map):
        if color == 'w':
            return (pawn_map << np.uint64(9)) & ~BBU.FILES[0]
        else:
            return (pawn_map >> np.uint64(7)) & ~BBU.FILES[0] 
    
    def generate_pawn_attacks_right(self, color, pawn_map):
        if color == 'w':
            return (pawn_map << np.uint64(7)) & ~BBU.FILES[7]
        else:
            return (pawn_map >> np.uint64(9)) & ~BBU.FILES[7]
    
    def generate_pawn_attacks(self, color, pawn_map):
        return self.generate_pawn_attacks_left(color, pawn_map) | self.generate_pawn_attacks_right(color, pawn_map)

    def valid_square_index(self, x, y):
        return x >= 0 and x < 8 and y >= 0 and y < 8
    
    def calculate_index(self, x, y):
        return y * 8 + x