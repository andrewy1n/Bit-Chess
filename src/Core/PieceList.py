class PieceList:
    def __init__(self) -> None:
        self.white_pieces = {}
        self.black_pieces = {}
        self.white_king_pos = None
        self.black_king_pos = None
    
    def add_piece(self, piece, pos):
        if piece.isupper():
            self.white_pieces[pos] = piece
            
            if piece == 'K':
                self.white_king_pos = pos
        else:
            self.black_pieces[pos] = piece

            if piece == 'k':
                self.black_king_pos = pos
    
    def remove_piece(self, piece, pos):
        if piece.isupper():
            self.white_pieces.pop(pos)
        else:
            self.black_pieces.pop(pos)
    
    def get_piece(self, pos, color):
        if color == 'w':
            return self.white_pieces[pos]
        else:
            return self.black_pieces[pos]
