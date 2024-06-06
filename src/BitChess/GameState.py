class GameState:
    def __init__(self, enpassant_index, castling_rights, half_move_counter) -> None:
        self.enpassant_index = enpassant_index
        self.castling_rights = castling_rights
        self.half_move_counter = half_move_counter
    
    def has_king_side_castling(self, turn):
        if turn == 'w':
            return 'K' in self.castling_rights
        else:
            return 'k' in self.castling_rights
    
    def has_queen_side_castling(self, turn):
        if turn == 'w':
            return 'Q' in self.castling_rights
        else:
            return 'q' in self.castling_rights