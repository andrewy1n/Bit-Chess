class GameState:
    def __init__(self, enpassant_pos, castling_rights, half_move_counter) -> None:
        self.enpassant_pos = enpassant_pos
        self.castling_rights = castling_rights
        self.half_move_counter = half_move_counter