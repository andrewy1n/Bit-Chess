class Move:
    def __init__(self, start_square, target_square) -> None:
        self.start_square = start_square
        self.start_pos = (start_square.file, start_square.rank)
        self.target_square = target_square
        self.target_pos = (target_square.file, target_square.rank)
        self.start_piece = start_square.occupying_piece
        self.target_piece = target_square.occupying_piece

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