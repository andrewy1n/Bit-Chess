from src.Core import BitboardUtility as BBU
from src.Core.Move import Move
from src.Core.GameState import GameState
from src.Core.PieceList import PieceList
from src.Core.PrecomputedAttacks import PrecomputedAttacks
import numpy as np

class Board:
    def __init__(self, FEN_string="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
        self.move_history = []
        self.game_state_history = []
        self.current_game_state = None        
        self.turn = 'w'
        self.full_moves = 1
        self.half_moves = 0
        self.piece_list = PieceList()
        
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
            enpassant_rank = 'abcdefgh'.index(enpassant_str[0])
            enpassant_file = int(enpassant_str[1]) - 1
            enpassant_pos = [enpassant_rank, enpassant_file]
        else:
            enpassant_pos = None
            
        self.current_game_state = GameState(enpassant_pos, castling_rights, self.half_moves)

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
                    piece_bb = self.bitboard_dict[c]
        
                    piece_bb |= square

                    self.bitboard_dict[c] = piece_bb
                    
                    if c.isupper():
                        self.white_pieces |= square
                    else:
                        self.black_pieces |= square
                    
                    self.piece_list.add_piece(c, (file_index, rank_index))
                    
                    self.occupied |= square

                    file_index += 1

        self.occupied90 = BBU.rotate_mirrored90c(self.occupied)
        self.occupied45R = BBU.rotate45(self.occupied)
        self.occupied45L = BBU.rotate45(self.occupied, is_right=False)                    
    
    #def getCurrentFEN(self):
                    
    def make_move(self, piece: str, start_coord: tuple, end_coord: tuple) -> None:
        piece_bb = self.bitboard_dict[piece]
        start_file, start_rank = start_coord[0], start_coord[1]
        end_file, end_rank = end_coord[0], end_coord[1]
        move_mask = BBU.FILES[start_file] & BBU.RANKS[start_rank] | BBU.FILES[end_file] & BBU.RANKS[end_rank]
        piece_bb ^= move_mask

        self.bitboard_dict[piece] = piece_bb
    
    #Prints basic text board
    def print_board(self):
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