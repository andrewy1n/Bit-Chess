class PieceList:
    def __init__(self) -> None:
        self.white_pieces = {}
        self.black_pieces = {}
        self.white_king_index = None
        self.black_king_index = None
    
    def add_piece(self, piece: str, index: int):
        if piece.isupper():
            self.white_pieces[index] = piece
            
            if piece == 'K':
                self.white_king_index = index
        else:
            self.black_pieces[index] = piece

            if piece == 'k':
                self.black_king_index = index
    
    def remove_piece(self, piece: str, index: int):
        if piece.isupper():
            self.white_pieces.pop(index)
        else:
            self.black_pieces.pop(index)
