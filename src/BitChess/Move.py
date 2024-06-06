class Move:
    def __init__(self, start_index, target_index) -> None:
        self.start_index = start_index
        self.target_index = target_index

        self.moving_piece = None

        self.is_enpassant = False
        self.enpassant_pawn_index = None

        self.is_king_side_castle = False
        self.is_queen_side_castle = False

        self.is_promotion = False
        self.promoted_piece = None

        self.is_capture = False
        self.captured_piece = None
        