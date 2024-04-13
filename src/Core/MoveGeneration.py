import numpy as np
from src.Core import BitboardUtility as BBU
from src.Core.Move import Move
from src.Core.PrecomputedAttacks import PrecomputedAttacks
from src.Core.Board import Board 

class MoveGeneration:
    def __init__(self, board: Board, attack_data: PrecomputedAttacks) -> None:
        self.board = board
        self.attack_data = attack_data

        self.diag_to_shift = [0, 1, 3, 6, 10, 15, 21, 28, 36, 43, 49, 54, 58, 61, 63]
        self.diag_lengths = [8, 7, 6, 5, 4, 3, 2, 1]

        self.in_check = False
        self.in_double_check = False

        # To be applied to pieces not including King
        self.check_ray_mask = np.uint64(0)
        self.pin_rays = np.uint64(0)
        self.enemy_attack_map = np.uint64(0)

        self.enemy_pieces = self.board.piece_list.white_pieces if self.board.turn == 'b' else self.board.piece_list.black_pieces
        self.ally_pieces_bb = self.board.white_pieces if self.board.turn == 'w' else self.board.black_pieces
        self.enemy_pieces_bb = self.board.white_pieces if self.board.turn == 'b' else self.board.black_pieces

        self.ally_king_bb = self.board.bitboard_dict['K'] if self.board.turn == 'w' else self.board.bitboard_dict['k']
        self.ally_king_pos = self.board.piece_list.white_king_pos if self.board.turn == 'w' else self.board.piece_list.black_king_pos
        self.ally_king_index = self.calculate_index(self.ally_king_pos[0], self.ally_king_pos[1])

        self.iterate_opposing_attacks()

    # Generates a list of object Moves
    def generate_moves(self, board) -> list:
        moves = []

        self.__init__(board, self.attack_data)

        # Generate King Moves
        self.generate_king_moves(moves)

        if not self.in_double_check:
            # Generate Slider Moves (Rook, Bishop, Queen)
            self.generate_slider_moves(moves)
            # Generate Knight Moves
            self.generate_knight_moves(moves)
            # Generate Pawn Moves

        return moves
    
    def generate_king_moves(self, moves: list):
        legal_mask =  ~(self.enemy_attack_map | self.ally_pieces_bb)
        king_moves = self.attack_data.king_moves[self.ally_king_index] & legal_mask
        
        while king_moves != 0:
            king_moves, target_index = BBU.popLSB(king_moves)
            moves.append(Move(self.ally_king_index, target_index))

        # Check for castling    
        if not self.in_check:
            castle_blockers = self.enemy_attack_map | self.board.occupied
            if self.board.current_game_state.has_king_side_castling(self.board.turn):
                castle_mask = BBU.WHITE_KINGSIDE_MASK if self.board.turn == 'w' else BBU.BLACK_KINGSIDE_MASK
                if castle_mask & castle_blockers == 0:
                    target_index = 6 if self.board.turn == 'w' else 62
                    move = Move(self.ally_king_index, target_index)
                    move.is_king_side_castle = True
                    moves.append(move)

            if self.board.current_game_state.has_queen_side_castling(self.board.turn):
                castle_mask = BBU.WHITE_QUEENSIDE_MASK_2 if self.board.turn == 'w' else BBU.BLACK_QUEENSIDE_MASK_2
                castle_block_mask = BBU.WHITE_QUEENSIDE_MASK if self.board.turn == 'w' else BBU.BLACK_QUEENSIDE_MASK
                if castle_mask & castle_blockers == 0 and castle_block_mask & self.board.occupied == 0:
                    target_index = 2 if self.board.turn == 'w' else 58
                    move = Move(self.ally_king_index, target_index)
                    move.is_queen_side_castle = True
                    moves.append(move)

    def generate_slider_moves(self, moves: list):
        rook = 'R' if self.board.turn == 'w' else 'r'
        queen = 'Q' if self.board.turn == 'w' else 'q'
        bishop = 'B' if self.board.turn == 'w' else 'b'
        orthogonal_sliders = self.board.bitboard_dict[rook] | self.board.bitboard_dict[queen] 
        diagonal_sliders = self.board.bitboard_dict[bishop] | self.board.bitboard_dict[queen]

        # Pinned pieces during check cannot move
        if self.in_check:
            orthogonal_sliders &= ~self.pin_rays
            diagonal_sliders &= ~self.pin_rays

        while orthogonal_sliders != 0:
            orthogonal_sliders, start_index = BBU.popLSB(orthogonal_sliders)
            
            orthogonal_moves = self.get_piece_attack(rook, start_index)

            orthogonal_moves &= ~(orthogonal_moves & self.ally_pieces_bb)

            if self.in_check:
                orthogonal_moves &= self.check_ray_mask

            # Piece is pinned
            if BBU.contains_square(self.pin_rays, start_index):
                # Piece can only move along the single pin ray
                orthogonal_moves &= self.attack_data.align_mask[self.ally_king_index][start_index]

            while orthogonal_moves != 0:
                orthogonal_moves, target_index = BBU.popLSB(orthogonal_moves)
                moves.append(Move(start_index, target_index))
        
        while diagonal_sliders != 0:
            diagonal_sliders, start_index = BBU.popLSB(diagonal_sliders)
            
            diagonal_moves = self.get_piece_attack(bishop, start_index)

            diagonal_moves &= ~(diagonal_moves & self.ally_pieces_bb)

            if self.in_check:
                diagonal_moves &= self.check_ray_mask

            # Piece is pinned
            if BBU.contains_square(self.pin_rays, start_index):
                # Piece can only move along the single pin ray
                diagonal_moves &= self.attack_data.align_mask[self.ally_king_index][start_index]

            while diagonal_moves != 0:
                diagonal_moves, target_index = BBU.popLSB(diagonal_moves)
                moves.append(Move(start_index, target_index))
    
    def generate_knight_moves(self, moves: list):
        knights = self.board.bitboard_dict['N'] if self.board.turn == 'w' else self.board.bitboard_dict['n']
        knights &= ~self.pin_rays
        
        while(knights != 0):
            knights, start_index = BBU.popLSB(knights)
            knight_moves = self.attack_data.knight_attacks[start_index]

            knight_moves &= ~(knight_moves & self.ally_pieces_bb)

            if self.in_check:
                knight_moves &= self.check_ray_mask
            
            while knight_moves != 0:
                knight_moves, target_index = BBU.popLSB(knight_moves)
                moves.append(Move(start_index, target_index))

    def generate_pawn_moves(self, moves: list):
        dir = 1 if self.board.turn == 'w' else -1
        push_offset = dir * 8
        pawns_bb = self.board.bitboard_dict['P'] if self.board.turn == 'w' else self.board.bitboard_dict['p']
        empty_sq = ~self.board.occupied
        promotion_rank = BBU.RANKS[7] if self.board.turn == 'w' else BBU.RANKS[0]
        double_push_rank = BBU.RANKS[4] if self.board == 'w' else BBU.RANKS[3]

        single_push = pawns_bb << np.uint64(push_offset) & empty_sq
        double_push = single_push << np.uint64(push_offset) & empty_sq & double_push_rank
        captures_left = self.attack_data.generate_pawn_attacks_left(self.board.turn, pawns_bb) & self.enemy_pieces_bb
        captures_right = self.attack_data.generate_pawn_attacks_right(self.board.turn, pawns_bb) & self.enemy_pieces_bb

        push_promotions = single_push & promotion_rank
        captures_left_promo = captures_left & promotion_rank
        captures_right_promo = captures_right & promotion_rank

        captures_left &= ~promotion_rank
        captures_right &= ~promotion_rank

        single_push_no_promo = single_push & ~promotion_rank

        if self.in_check:
            push_promotions &= self.check_ray_mask
            single_push_no_promo &= self.check_ray_mask
            double_push &= self.check_ray_mask
            captures_left_promo &= self.check_ray_mask
            captures_right_promo &= self.check_ray_mask
            captures_left &= self.check_ray_mask
            captures_right &= self.check_ray_mask

        # Single and Double Pushes
        while single_push_no_promo != 0:
            single_push_no_promo, target_index = BBU.popLSB(single_push_no_promo)
            start_index = target_index - push_offset
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                moves.append(Move(start_index, target_index))
        
        while double_push != 0:
            double_push, target_index = BBU.popLSB(double_push)
            start_index = target_index - push_offset*2
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                moves.append(Move(start_index, target_index))
        
        # Captures
        while captures_left != 0:
            captures_left, target_index = BBU.popLSB(captures_left)
            start_index = target_index - dir*7
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                moves.append(Move(start_index, target_index))
        
        while captures_right != 0:
            captures_right, target_index = BBU.popLSB(captures_right)
            start_index = target_index - dir*9
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                moves.append(Move(start_index, target_index))
        
        # Promotions
        while push_promotions != 0:
            push_promotions, target_index = BBU.popLSB(push_promotions)
            start_index = target_index - push_offset
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                self.generate_promotions(start_index, target_index, moves)
        
        while captures_left_promo != 0:
            captures_left_promo, target_index = BBU.popLSB(captures_left_promo)
            start_index = target_index - push_offset
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                self.generate_promotions(start_index, target_index, moves)
        
        while captures_right_promo != 0:
            captures_right_promo, target_index = BBU.popLSB(captures_right_promo)
            start_index = target_index - push_offset
            
            if not self.is_pinned(start_index) or self.is_aligned(start_index, target_index):
                self.generate_promotions(start_index, target_index, moves)
        
        # En passant
        if self.board.current_game_state.enpassant_pos is not None:
            target_rank = self.board.current_game_state.enpassant_pos[0]
            target_file = self.board.current_game_state.enpassant_pos[1]
            target_index = self.calculate_index(target_rank, target_file)
            captured_pawn_index = target_index - push_offset

            if not self.in_check or BBU.contains_square(self.check_ray_mask, captured_pawn_index):
                enp_pawns = pawns_bb & self.attack_data.generate_pawn_attatcks('w' if self.board.turn == 'b' else 'b', BBU.set_square(np.uint64(0), target_index))
                BBU.printBB(self.attack_data.generate_pawn_attatcks('w' if self.board.turn == 'b' else 'b', BBU.set_square(np.uint64(0), target_index)))
                print()
                BBU.printBB(pawns_bb)

                while enp_pawns:
                    enp_pawns, start_index = BBU.popLSB(enp_pawns)
                    if (not self.is_pinned(start_index) or self.is_aligned(start_index, target_index)) and \
                        not self.in_check_after_enpassant(start_index, target_index, captured_pawn_index):
                        move = Move(start_index, target_index)
                        move.is_enpassant = True
                        move.enpassant_pawn = captured_pawn_index
                        moves.append(move)

        return moves
    
    # Generates pawn promotion moves
    def generate_promotions(self, start_index: int, target_index: int, moves: list):
        promotion_pieces = ['N', 'B', 'R', 'Q']

        for piece in promotion_pieces:
            piece = piece.lower() if self.board.turn == 'b' else piece
            promotion_move = Move(start_index, target_index)
            promotion_move.promoted_piece = piece
            moves.append(promotion_move)

    # Goes through each attacks from opposition to look for checks and pin rays
    def iterate_opposing_attacks(self):
        self.in_check = False
        self.in_double_check = False
        
        attack_map = np.uint64(0)

        for pos, piece in self.enemy_pieces.items():
            x, y = pos[0], pos[1]
            index = self.calculate_index(x, y)
            attacks = self.get_piece_attack(piece, index)
            # AND out allied pieces of opposition
            attacks &= ~(attacks & self.enemy_pieces_bb)
            attack_map |= attacks

            is_slider = piece.lower() == 'r' or piece.lower() == 'b' or piece.lower() == 'q'
            is_orthogonal = piece.lower() == 'r' or piece.lower() == 'q'
            is_diagonal = piece.lower() == 'b' or piece.lower() == 'q'
            
            # Checks if king is being attacked
            if self.ally_king_bb & attacks != 0:
                if self.in_check:
                    self.in_double_check = True
                else:
                    self.in_check = True
                
                # Legal mask includes capturing the attacking piece
                BBU.set_square(self.check_ray_mask, index)
            
            # Check for possible pins and check rays
            if is_orthogonal:
                if self.ally_king_pos[0] == x:
                    self.check_pins(x, y, is_vertical=True)
                
                elif self.ally_king_pos[1] == y:
                    self.check_pins(x, y, is_vertical=False)
            
            if is_diagonal:
                # Piece and King are on the left-diagonal or right-diagonal
                if self.ally_king_pos[0] + self.ally_king_pos[1] == x + y or \
                    self.ally_king_pos[0] - self.ally_king_pos[1] == x - y:
                    self.check_pins(x, y, is_diagonal=True)
            
        self.enemy_attack_map |= attack_map
    
    # Gets precomputed attacks for piece
    def get_piece_attack(self, piece: str, index: int) -> np.uint64:
        attacks = np.uint64(0)
        x = index % 8
        y = index // 8
        
        if piece == 'p':
            attacks = self.attack_data.black_pawn_attacks[index]
        elif piece == 'P':
            attacks = self.attack_data.white_pawn_attacks[index]
        elif piece.lower() == 'n':
            attacks = self.attack_data.knight_attacks[index]
        elif piece.lower() == 'k':
            attacks = self.attack_data.king_moves[index]
        elif piece.lower() == 'r':
            rank_attacks = self.attack_data.rank_attacks[index][self.board.occupied >> np.uint64(y*8) & np.uint64(255)]
            file_attacks = self.attack_data.file_attacks[index][self.board.occupied90 >> np.uint64(x*8) & np.uint64(255)]
            attacks = rank_attacks | file_attacks
        elif piece.lower() == 'b':
            right_diagonal_attacks = self.attack_data.diagR_attacks[index][self.board.occupied45R >> self.diag_to_shift[7-x+y] & np.uint64(2**(self.diag_lengths[abs(x-y)])-1)]
            left_diagonal_attacks = self.attack_data.diagL_attacks[index][self.board.occupied45L >> self.diag_to_shift[14-x-y] & np.uint64(2**(self.diag_lengths[abs(7-x-y)])-1)]
            attacks = right_diagonal_attacks | left_diagonal_attacks
        elif piece.lower() == 'q': 
            rank_attacks = self.attack_data.rank_attacks[index][self.board.occupied >> np.uint64(y*8) & np.uint64(255)]
            file_attacks = self.attack_data.file_attacks[index][self.board.occupied90 >> np.uint64(x*8) & np.uint64(255)]
            right_diagonal_attacks = self.attack_data.diagR_attacks[index][self.board.occupied45R >> self.diag_to_shift[7-x+y] & np.uint64(2**(self.diag_lengths[abs(x-y)])-1)]
            left_diagonal_attacks = self.attack_data.diagL_attacks[index][self.board.occupied45L >> self.diag_to_shift[14-x-y] & np.uint64(2**(self.diag_lengths[abs(7-x-y)])-1)]
            attacks = rank_attacks | file_attacks | right_diagonal_attacks | left_diagonal_attacks

        return attacks
    
    # Checks if there is a pin given x, y and king position
    def check_pins(self, x: int, y: int, is_vertical=False, is_diagonal=False) -> None:
        ray_mask = np.uint64(0)
        is_pinned = False
        vert_dist = self.ally_king_pos[1] - y
        horz_dist = self.ally_king_pos[0] - x
        vert_dir = -1 if vert_dist < 0 else 1
        horz_dir = -1 if horz_dist < 0 else 1
        dist = vert_dist if is_vertical else horz_dist
        
        for i in range(abs(dist)+1):
            new_x = x + i*horz_dir if not is_vertical or is_diagonal else x
            new_y = y + i*vert_dir if is_vertical or is_diagonal else y
            index = self.calculate_index(new_x, new_y)
            ray_mask = BBU.set_square(ray_mask, index)
            
            if index == self.ally_king_index:
                # This means the King is being attacked and in check
                if not is_pinned:
                    self.check_ray_mask |= ray_mask
                    break
                else:
                    break
            
            elif BBU.contains_square(self.ally_pieces_bb, index):
                if not is_pinned: 
                    is_pinned = True
                else:
                    break
            
            elif BBU.contains_square(self.enemy_pieces_bb, index) and index != self.calculate_index(x, y):
                break
        
        if is_pinned:
            self.pin_rays |= ray_mask
    
    def is_pinned(self, index):
        return BBU.contains_square(self.pin_rays, index)
    
    def is_aligned(self, index1, index2):
        return self.attack_data.align_mask[index1][self.ally_king_bb] == self.attack_data.align_mask[index2][self.ally_king_bb]
    
    def in_check_after_enpassant(self, start_index, target_index, enp_capture_index):
        rook = 'R' if self.board.turn == 'b' else 'r'
        queen = 'Q' if self.board.turn == 'b' else 'q'
        enemy_orthogonal_sliders = self.board.bitboard_dict[rook] | self.board.bitboard_dict[queen]

        if enemy_orthogonal_sliders:
            masked_blockers = self.board.occupied ^ (np.uint64(1) << np.uint64(enp_capture_index) | np.uint64(1) << np.uint64(start_index) | np.uint64(1) << np.uint64(target_index))

            x, y = self.ally_king_pos
            index = self.ally_king_index
            rank_attacks = self.attack_data.rank_attacks[index][masked_blockers >> np.uint64(y*8) & np.uint64(255)]
            file_attacks = self.attack_data.file_attacks[index][BBU.rotate_mirrored90c(masked_blockers) >> np.uint64(x*8) & np.uint64(255)]

            return (rank_attacks | file_attacks) & enemy_orthogonal_sliders != 0
        
        return False


    
    def valid_square_index(self, x: int, y: int) -> bool:
        return x >= 0 and x < 8 and y >= 0 and y < 8
    
    def calculate_index(self, x: int, y: int) -> np.uint64:
        return y * 8 + x
    