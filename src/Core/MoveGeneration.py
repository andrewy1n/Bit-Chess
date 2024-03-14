import numpy as np
from src.Core import BitboardUtility as BBU

class MoveGeneration:
    def __init__(self, board) -> None:
        self.board = board
        self.cardinals = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.ordinals = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        self.knight_jumps = [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2)]

        self.diag_to_shift = [0, 1, 3, 6, 10, 15, 21, 28, 36, 43, 49, 54, 58, 61, 63]
        self.diag_lengths = [1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]
        
        # Will be initialized beforehand
        self.knight_attacks = np.zeros((8, 8), dtype=np.uint64)
        self.white_pawn_attacks = np.zeros((8, 8), dtype=np.uint64)
        self.black_pawn_attacks = np.zeros((8, 8), dtype=np.uint64)
        self.king_moves = np.zeros((8, 8), dtype=np.uint64)

        self.rank_attacks = np.zeros((8, 8, 256), dtype=np.uint64)
        self.file_attacks = np.zeros((8, 8, 256), dtype=np.uint64)

        self.diagR_attacks = np.zeros((8, 8, 256), dtype=np.uint64)
        self.diagL_attacks = np.zeros((8, 8, 256), dtype=np.uint64)

        for x in range(8):
            for y in range(8):
                self.process_square(x, y)

    def process_square(self, x: int, y: int):
        # King Attacks
        for i in range(4):
            card_x = x + self.cardinals[i][0]
            card_y = y + self.cardinals[i][1]
            diag_x = x + self.ordinals[i][0]
            diag_y = y + self.ordinals[i][1]

            if self.valid_square_index(card_x, card_y):
                card_target_index = self.calculate_index(card_x, card_y)
                self.king_moves[x][y] |= np.uint64(1) << card_target_index
            
            if self.valid_square_index(diag_x, diag_y):
                diag_target_index = self.calculate_index(diag_x, diag_y)
                self.king_moves[x][y] |= np.uint64(1) << diag_target_index
        
        # Knight Attacks
        for dx, dy in self.knight_jumps:
            knight_x = x + dx
            knight_y = y + dy

            if self.valid_square_index(knight_x, knight_y):
                knight_target_index = self.calculate_index(knight_x, knight_y)
                self.knight_attacks[x][y] |= np.uint64(1) << knight_target_index
        
        # Pawn Attacks
        if self.valid_square_index(x+1, y+1):
            white_pawn_right = self.calculate_index(x+1, y+1)
            self.white_pawn_attacks[x][y] |= np.uint64(1) << white_pawn_right
            
        if self.valid_square_index(x-1, y+1):
            white_pawn_left = self.calculate_index(x-1, y+1)
            self.white_pawn_attacks[x][y] |= np.uint64(1) << white_pawn_left
        
        if self.valid_square_index(x+1, y-1):
            black_pawn_right = self.calculate_index(x+1, y-1)
            self.black_pawn_attacks[x][y] |= np.uint64(1) << black_pawn_right
        
        if self.valid_square_index(x-1, y-1):
            black_pawn_left = self.calculate_index(x-1, y-1)
            self.black_pawn_attacks[x][y] = np.uint64(1) << black_pawn_left
        
        self.generate_ortho_attacks(x, y)
        self.generate_diagonal_attacks(x, y)
    
    # Generates all Orthogonal Attacks(Rank and File Attacks)
    def generate_ortho_attacks(self, x: int, y: int):
        rank_arr = self.rank_attacks[x][y]
        file_arr = self.file_attacks[y][x]

        # Create all possible blocker configurations
        def generate_blockers(cur_file, blockers):

            # use blockers value as index, generate slider moves with normalized blockers shifted to correct row
            normalized_bb = self.generate_slider_moves(x, y, blockers << np.uint(y*8))

            rank_arr[blockers & np.uint64(255)] = normalized_bb
            file_arr[blockers & np.uint64(255)] = BBU.rotate_mirrored90c(normalized_bb)

            for file in range(cur_file, 8):
                # i cannot already be in blockers, and cannot be the same x position of the piece
                if not BBU.contains_square(blockers, file) and file != x:
                    generate_blockers(file, BBU.set_square(blockers, file))
        
        generate_blockers(0, np.uint64(0))

    # Generates all diagonal attacks (Bishops and Queens)
    def generate_diagonal_attacks(self, x: int, y: int):
        diagR_arr = self.diagR_attacks[x][y]
        diagL_arr = self.diagL_attacks[7-y][x]
        
        # Create all possible blocker configurations on the diagonal
        def generate_blockers(cur_step, blockers):
            # generate diagonal moves based on current blockers and store into a bitboard
            normalized_bb = self.generate_diagonal_moves(x, y, blockers)

            # Calculate relative indices for left and right attacks, using 45 degree board rotations and shifts
            right_arr_index = BBU.rotate45_shift(blockers, self.diag_to_shift[7-x+y])
            left_arr_index = BBU.rotate45_shift(BBU.rotate90cc(blockers), self.diag_to_shift[7-x+y], is_right=False)

            # Set index of diagonal array to relative diagonal moves
            diagR_arr[right_arr_index] = normalized_bb
            diagL_arr[left_arr_index] = BBU.rotate90cc(normalized_bb)

            # Iterate through current step, up to 8 (this is overcounting)
            for step in range(cur_step, 8):
                # Generate new possible index
                index = self.calculate_index(x + step, y + step)
                # Index must be valid, cannot already contain a piece, and cannot be the same index as the current piece
                if self.valid_square_index(x + step, y + step) and \
                    not BBU.contains_square(blockers, index) and \
                        index != self.calculate_index(x, y):
                    # Recurse with new step and new index
                    generate_blockers(step, BBU.set_square(blockers, index))
        
        generate_blockers(-min(x, y), np.uint64(0))

    # Generates moves as bitboard of left and right attacks
    def generate_slider_moves(self, x: int, y: int, blockers: np.uint64):
        moves_bb = np.uint64(0)
        # Moves right of piece
        right_bound = 8-x
        for dx in range(1, right_bound):
            index = self.calculate_index(x + dx, y)
            if self.valid_square_index(x + dx, y):
                # Include first blocker as possible capture
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        # Moves left of piece
        for dx in range(1, x+1):
            index = self.calculate_index(x - dx, y)
            if self.valid_square_index(x - dx, y):
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
            index = self.calculate_index(x + step, y + step)
            if self.valid_square_index(x + step, y + step):
                # Include first blocker as possible capture
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        # Moves left of piece
        for step in range(1, x+1):
            index = self.calculate_index(x - step, y - step)
            if self.valid_square_index(x - step, y - step):
                if BBU.contains_square(blockers, index):
                    moves_bb = BBU.set_square(moves_bb, index)
                    break
                
                moves_bb = BBU.set_square(moves_bb, index)
        
        return moves_bb

    def valid_square_index(self, x, y):
        return x >= 0 and x < 8 and y >= 0 and y < 8
    
    def calculate_index(self, x, y):
        return np.uint64(y * 8 + x)

    # Generates a list of object Moves
    def generate_moves(self) -> list:
        output = []
        # Generate King Moves
        # Generate Slider Moves (Rook, Bishop, Queen)
        # Generate Knight Moves
        # Generate Pawn Moves
        return output
    
    def generate_pawn_attacks(self, color):
        pawn_map = self.board.bitboard_dict["P"] if color == 'w' else self.board.bitboard_dict["p"]

        if color == 'w':
            return (pawn_map << np.uint64(9)) & ~BBU.FILES[0] | (pawn_map << np.uint64(7)) & ~BBU.FILES[7]
        else:
            return (pawn_map >> np.uint64(7)) & ~BBU.FILES[0] | (pawn_map >> np.uint64(9)) & ~BBU.FILES[7]

    
    def generate_attack_map(self):
        

        pass

    def in_bound(self, col, row) -> bool:
        return 0 >= col <= 7 and 0 >= row <= 7