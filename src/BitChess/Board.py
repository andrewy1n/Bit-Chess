from src.BitChess import BitboardUtility as BBU
from src.BitChess.Move import Move
from src.BitChess.GameState import GameState
from src.BitChess.PieceList import PieceList
import numpy as np

class Board:
    def __init__(self, FEN_string="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
        self.move_history = []
        self.game_state_history = []
        self.board_state_history = []
        self.current_game_state = None        
        self.turn = 'w'
        self.full_moves = 1
        self.half_moves = 0
        self.piece_list = PieceList()
        self.squares = ['.'] * 64

        # Uppercase notation -> White piece, lowercase -> black piece
        self.bitboard_dict = {
            'P' : np.uint64(0),
            'Q' : np.uint64(0),
            'K' : np.uint64(0),
            'N' : np.uint64(0),
            'B' : np.uint64(0),
            'R' : np.uint64(0),
            'p' : np.uint64(0),
            'q' : np.uint64(0),
            'k' : np.uint64(0),
            'n' : np.uint64(0),
            'b' : np.uint64(0),
            'r' : np.uint64(0),
        }
        
        # Add an all pieces Bitboard for checking blockers and if a piece exists at a position
        self.white_pieces = np.uint64(0)
        self.black_pieces = np.uint64(0)
        
        self.occupied = np.uint64(0)
        self.occupied90 = np.uint64(0)
        self.occupied45R = np.uint64(0)
        self.occupied45L = np.uint64(0)

        self.load_FEN_position(FEN_string)
        
    def load_FEN_position(self, fen: str):
        pos, turn, castling_rights, enpassant_str, *move_info = fen.split()

        self.turn = turn
        self.half_moves = int(move_info[0]) if move_info else 0
        self.full_moves = int(move_info[1]) if move_info else 1
        
        if enpassant_str != '-':
            enpassant_x = ord(enpassant_str[0]) - ord('a')
            enpassant_y = int(enpassant_str[1]) - 1
            enpassant_index = enpassant_y * 8 + enpassant_x
        else:
            enpassant_index = None
            
        self.current_game_state = GameState(enpassant_index, castling_rights, self.half_moves)
        self.game_state_history.append(self.current_game_state)

        file_index, rank_index = 0, 7
        
        for c in pos:
            if c == '/':
                file_index = 0
                rank_index -= 1
            else:
                if c.isnumeric():
                    file_index += int(c)
                else:
                    square = BBU.FILES[file_index] & BBU.RANKS[rank_index]
                    index = 8 * rank_index + file_index

                    piece_bb = self.bitboard_dict[c]
        
                    piece_bb |= square

                    self.bitboard_dict[c] = piece_bb
                    
                    self.squares[index] = c

                    if c.isupper():
                        self.white_pieces |= square
                    else:
                        self.black_pieces |= square
                    
                    self.piece_list.add_piece(c, index)
                    
                    self.occupied |= square

                    file_index += 1

        self.occupied90 = BBU.rotate_mirrored90c(self.occupied)
        self.occupied45R = BBU.rotate45(self.occupied)
        self.occupied45L = BBU.rotate45(self.occupied, is_right=False)                    
    
    #def getCurrentFEN(self):
                    
    def make_move(self, move: Move) -> None:
        new_enpassant_index = None
        new_castling_rights = self.current_game_state.castling_rights
        new_half_move_counter = self.current_game_state.half_move_counter
        
        moving_piece = self.squares[move.start_index]
        move.moving_piece = moving_piece
        moved_piece = move.promoted_piece if move.is_promotion else moving_piece
        captured_piece = self.squares[move.target_index]
        move.is_capture = captured_piece != "."

        new_ally_pieces = self.white_pieces if self.turn == 'w' else self.black_pieces
        new_enemy_pieces = self.black_pieces if self.turn == 'w' else self.white_pieces
        new_occupied = self.occupied

        if move.is_king_side_castle or move.is_queen_side_castle:
            king = moving_piece
            king_is_white = king.isupper()
            
            if move.is_king_side_castle:
                prev_rook_index = 7 if king_is_white else 63
                new_rook_index = 5 if king_is_white else 61
            elif move.is_queen_side_castle:
                prev_rook_index = 0 if king_is_white else 56
                new_rook_index = 3 if king_is_white else 59

            rook = self.squares[prev_rook_index]
            
            # Move rook in squares and piece list
            self.squares[prev_rook_index] = "."
            self.squares[new_rook_index] = rook

            new_occupied = BBU.move_bit(new_occupied, prev_rook_index, new_rook_index)
            self.bitboard_dict[rook] = BBU.move_bit(self.bitboard_dict[rook], prev_rook_index, new_rook_index)
            new_ally_pieces = BBU.move_bit(new_ally_pieces, prev_rook_index, new_rook_index)
            
            self.piece_list.remove_piece(rook, prev_rook_index)
            self.piece_list.add_piece(rook, new_rook_index)

        if move.is_enpassant:
            dir = 1 if self.turn == 'w' else -1
            pawn_index = move.enpassant_pawn_index - dir * 8
            pawn = self.squares[pawn_index]

            self.bitboard_dict[pawn] = BBU.delete_bit(self.bitboard_dict[pawn], pawn_index)
            new_enemy_pieces = BBU.delete_bit(new_enemy_pieces, pawn_index)
            new_occupied = BBU.delete_bit(new_occupied, pawn_index)
            self.squares[pawn_index] = "."
            self.piece_list.remove_piece(pawn, pawn_index)
        
        # If pawn moves forward 2 spaces, set enpassant index
        if moving_piece.lower() == 'p' \
            and abs(move.target_index - move.start_index) == 16:
            dir = 1 if self.turn == 'w' else -1
            new_enpassant_index = move.target_index - dir * 8

        # Move piece in board Squares
        self.squares[move.start_index] = "."
        self.squares[move.target_index] = moved_piece

        # Move piece in Piece List
        self.piece_list.remove_piece(moving_piece, move.start_index)

        if move.is_capture:
            self.bitboard_dict[captured_piece] = BBU.delete_bit(self.bitboard_dict[captured_piece], move.target_index)
            move.captured_piece = captured_piece
            new_enemy_pieces = BBU.delete_bit(new_enemy_pieces, move.target_index)
            new_occupied = BBU.delete_bit(new_occupied, move.target_index)
            self.piece_list.remove_piece(captured_piece, move.target_index) 
          
        self.piece_list.add_piece(moved_piece, move.target_index)

        # Move piece in bitboards
        new_occupied = BBU.move_bit(new_occupied, move.start_index, move.target_index)
        self.bitboard_dict[moving_piece] = BBU.move_bit(self.bitboard_dict[moving_piece], move.start_index, move.target_index)
        new_ally_pieces = BBU.move_bit(new_ally_pieces, move.start_index, move.target_index)

        # Delete from moving piece bitboard, add to promoted piece bitboard
        if move.is_promotion:
            replace_mask = BBU.set_square(np.uint64(0), move.target_index)
            self.bitboard_dict[moving_piece] ^= replace_mask
            self.bitboard_dict[moved_piece] |= replace_mask
        
        # Reset special occupied bitboards
        self.occupied = new_occupied
        self.white_pieces = new_ally_pieces if self.turn == 'w' else new_enemy_pieces
        self.black_pieces = new_ally_pieces if self.turn == 'b' else new_enemy_pieces
        self.occupied90 = BBU.rotate_mirrored90c(self.occupied)
        self.occupied45R = BBU.rotate45(self.occupied)
        self.occupied45L = BBU.rotate45(self.occupied, is_right=False)   
        
        # Adjust Castling Rights
        if moving_piece.lower() == 'k':
            rights_to_remove = 'KQ' if moving_piece.isupper() else 'kq'
            for right in rights_to_remove:
                new_castling_rights = new_castling_rights.replace(right, "")
        
        if moving_piece.lower() == 'r':
            if move.start_index == 0:
                new_castling_rights = new_castling_rights.replace('Q', "")
            elif move.start_index == 7:
                new_castling_rights = new_castling_rights.replace('K', "")
            elif move.start_index == 56:
                new_castling_rights = new_castling_rights.replace('q', "")
            elif move.start_index == 63:
                new_castling_rights = new_castling_rights.replace('k', "")
        
        if captured_piece.lower() == 'r':
            if move.target_index == 0:
                new_castling_rights = new_castling_rights.replace('Q', "")
            elif move.target_index == 7:
                new_castling_rights = new_castling_rights.replace('K', "")
            elif move.target_index == 56:
                new_castling_rights = new_castling_rights.replace('q', "")
            elif move.target_index == 63:
                new_castling_rights = new_castling_rights.replace('k', "")
        
        # Reset half move counter if a pawn is moved
        if moving_piece.lower() == 'p':
            new_half_move_counter = 0
        else:
            new_half_move_counter += 1
        
        # Add full move after black's move
        if self.turn == 'b':
            self.full_moves += 1
        
        self.turn = 'b' if self.turn == 'w' else 'w'

        self.move_history.append(move)
        new_state = GameState(new_enpassant_index, new_castling_rights, new_half_move_counter)
        self.game_state_history.append(new_state)
        self.current_game_state = new_state
    
    def unmake_move(self, move: Move):                
        moving_piece = move.moving_piece
        old_ally_pieces = self.white_pieces if self.turn == 'b' else self.black_pieces
        old_enemy_pieces = self.black_pieces if self.turn == 'b' else self.white_pieces
        old_occupied = self.occupied
        
        if move.is_king_side_castle or move.is_queen_side_castle:
            king = moving_piece
            king_is_white = king.isupper()
            
            if move.is_king_side_castle:
                prev_rook_index = 7 if king_is_white else 63
                new_rook_index = 5 if king_is_white else 61
            elif move.is_queen_side_castle:
                prev_rook_index = 0 if king_is_white else 56
                new_rook_index = 3 if king_is_white else 59

            rook = self.squares[new_rook_index]
            
            self.squares[new_rook_index] = "."
            self.squares[prev_rook_index] = rook

            old_occupied = BBU.move_bit(old_occupied, new_rook_index, prev_rook_index)
            self.bitboard_dict[rook] = BBU.move_bit(self.bitboard_dict[rook], new_rook_index, prev_rook_index)
            old_ally_pieces = BBU.move_bit(old_ally_pieces, new_rook_index, prev_rook_index)
            
            self.piece_list.remove_piece(rook, new_rook_index)
            self.piece_list.add_piece(rook, prev_rook_index)
        
        if move.is_promotion:
            replace_mask = BBU.set_square(np.uint64(0), move.target_index)
            self.bitboard_dict[move.promoted_piece] ^= replace_mask
            self.bitboard_dict[moving_piece] |= replace_mask
            self.piece_list.add_piece(moving_piece, move.target_index)
        
        # Move piece back to the starting square
        self.squares[move.start_index] = moving_piece
        self.squares[move.target_index] = "."
    
        # Update piece list
        self.piece_list.remove_piece(moving_piece, move.target_index)
        self.piece_list.add_piece(moving_piece, move.start_index)
    
        # Update bitboards
        old_occupied = BBU.move_bit(old_occupied, move.target_index, move.start_index)
        self.bitboard_dict[moving_piece] = BBU.move_bit(self.bitboard_dict[moving_piece], move.target_index, move.start_index)
        old_ally_pieces = BBU.move_bit(old_ally_pieces, move.target_index, move.start_index)

        if move.is_enpassant:
            dir = 1 if self.turn == 'b' else -1
            pawn_index = move.enpassant_pawn_index - dir * 8
            pawn = 'p' if moving_piece.isupper() else 'P'
            self.bitboard_dict[pawn] = BBU.set_square(self.bitboard_dict[pawn], pawn_index)
            old_enemy_pieces = BBU.set_square(old_enemy_pieces, pawn_index)
            old_occupied = BBU.set_square(old_occupied, pawn_index)
            self.squares[pawn_index] = pawn
            self.piece_list.add_piece(pawn, pawn_index)
        
        if move.is_capture:
            self.bitboard_dict[move.captured_piece] = BBU.set_square(self.bitboard_dict[move.captured_piece], move.target_index)
            old_enemy_pieces = BBU.set_square(old_enemy_pieces, move.target_index)
            old_occupied = BBU.set_square(old_occupied, move.target_index)
            self.piece_list.add_piece(move.captured_piece, move.target_index)
            self.squares[move.target_index] = move.captured_piece 
    
        # Update special occupied bitboards
        self.occupied = old_occupied
        self.white_pieces = old_ally_pieces if self.turn == 'b' else old_enemy_pieces
        self.black_pieces = old_ally_pieces if self.turn == 'w' else old_enemy_pieces
        self.occupied90 = BBU.rotate_mirrored90c(self.occupied)
        self.occupied45R = BBU.rotate45(self.occupied)
        self.occupied45L = BBU.rotate45(self.occupied, is_right=False)
    
        # Update game state
        self.turn = 'w' if self.turn == 'b' else 'b'

        if self.turn == 'b':
            self.full_moves -= 1

        self.move_history.pop()
        self.game_state_history.pop()
        self.current_game_state = self.game_state_history[-1]    
    
    # Prints basic text board from bitboard dicts
    def print_board_bb(self):
        for rank in range(7, -1, -1):
            row = ""
            for file in range(8):
                square = 8 * rank + file
                piece_char = '.'
                for piece, bitboard in self.bitboard_dict.items():
                    if bitboard & np.uint64(1 << square):
                        piece_char = piece
                        break
                row += piece_char + ' '
            print(row)
    
    def print_board(self):
        for rank in range(7, -1, -1):
            row = ""
            for file in range(8):
                index = 8 * rank + file
                piece_char = self.squares[index]
                row += piece_char + ' '
            print(row)
    
    def print_moves(self, moves: list[Move]):
        move_notations = []
        for move in moves:
            start_file = chr(ord('a') + (move.start_index % 8))
            start_rank = str((move.start_index // 8) + 1)
            target_file = chr(ord('a') + (move.target_index % 8))
            target_rank = str((move.target_index // 8) + 1)

            notation = f"{start_file}{start_rank}{target_file}{target_rank}"

            if move.is_promotion:
                promotion_piece = 'Q' if move.promoted_piece.lower() == 'q' else 'R' if move.promoted_piece.lower() == 'r' else 'B' if move.promoted_piece.lower() == 'b' else 'N'
                notation += "=" + promotion_piece

            move_notations.append(notation)
        print(", ".join(move_notations))
    
        