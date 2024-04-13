class Move:
    def __init__(self, start_index, target_index) -> None:
        self.start_index = start_index
        self.target_index = target_index
        
        #Set to True if a pawn moves up two spaces
        self.enpassant_flag = False 
        self.is_enpassant = False

        self.is_king_side_castle = False
        self.king_side_rook = None

        self.is_queen_side_castle = False
        self.queen_side_rook = None

        self.is_promotion = False

        self.enpassant_square = None
        self.enpassant_pawn = None

        self.promoted_piece = None