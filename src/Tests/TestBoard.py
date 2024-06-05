import unittest
from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core.PrecomputedAttacks import PrecomputedAttacks

attacks = PrecomputedAttacks()

class TestBoard(unittest.TestCase):
  def make_move_test(self, initial_fen, expected_fen, move_start, move_end, promoted_piece=None, is_enpassant=False):
    board = Board(FEN_string=initial_fen) if initial_fen is not None else Board()
    move_generator = MoveGeneration(board, attacks)
    moves = move_generator.generate_moves(board)

    for move in moves:
        if move.start_index == move_start and move.target_index == move_end:
          if (promoted_piece is not None and move.promoted_piece == promoted_piece):
            board.make_move(move)
            break
          elif (promoted_piece is not None):
            continue
          else:
            board.make_move(move)
            break
        elif (is_enpassant is not None and move.is_enpassant):
            board.make_move(move)
            break
        
    board2 = Board(FEN_string=expected_fen)

    self.assertEqual(board.occupied, board2.occupied)
    self.assertEqual(board.white_pieces, board2.white_pieces)
    self.assertEqual(board.black_pieces, board2.black_pieces)
    self.assertEqual(board.piece_list.white_pieces, board2.piece_list.white_pieces)
    self.assertEqual(board.piece_list.black_pieces, board2.piece_list.black_pieces)
    self.assertEqual(board.squares, board2.squares)
    self.assertEqual(board.current_game_state.castling_rights, board2.current_game_state.castling_rights)
    self.assertEqual(board.current_game_state.half_move_counter, board2.current_game_state.half_move_counter)
    self.assertEqual(board.current_game_state.enpassant_index, board2.current_game_state.enpassant_index)
  
  def unmake_move_test(self, initial_fen, move_start, move_end, promoted_piece=None, is_enpassant=False):
    board = Board(FEN_string=initial_fen) if initial_fen is not None else Board()
    move_generator = MoveGeneration(board, attacks)
    moves = move_generator.generate_moves(board)
    
    prev_board_occupied = board.occupied
    prev_board_squares = board.squares
    prev_white_pieces = board.white_pieces
    prev_black_pieces = board.black_pieces
    prev_piece_list_white_pieces = board.piece_list.white_pieces
    prev_piece_list_black_pieces = board.piece_list.black_pieces
    prev_board_castling_rights = board.current_game_state.castling_rights
    prev_board_half_move_counter = board.current_game_state.half_move_counter
    prev_board_enpassant_index = board.current_game_state.enpassant_index
    
    for move in moves:
        if move.start_index == move_start and move.target_index == move_end:
          if (promoted_piece is not None and move.promoted_piece == promoted_piece):
            board.make_move(move)
            board.unmake_move(move)
            break
          elif (promoted_piece is not None):
            continue
          else:
            board.make_move(move)
            board.unmake_move(move)
            break
        elif (is_enpassant is not None and move.is_enpassant):
            board.make_move(move)
            board.unmake_move(move)
            break
    
    self.assertEqual(prev_board_occupied, board.occupied)
    self.assertEqual(prev_board_squares, board.squares)
    self.assertEqual(prev_white_pieces, board.white_pieces)
    self.assertEqual(prev_black_pieces, board.black_pieces)
    self.assertEqual(prev_piece_list_white_pieces, board.piece_list.white_pieces)
    self.assertEqual(prev_piece_list_black_pieces, board.piece_list.black_pieces)
    self.assertEqual(prev_board_castling_rights, board.current_game_state.castling_rights)
    self.assertEqual(prev_board_half_move_counter, board.current_game_state.half_move_counter)
    self.assertEqual(prev_board_enpassant_index, board.current_game_state.enpassant_index)
  
  def test_basic_make_move(self):
    self.make_move_test(None, "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", 12, 28)
  
  def test_capture_move(self):
    self.make_move_test("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1", "rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", 28, 35)
    
  def test_king_side_castle(self):
    self.make_move_test("r1bqkbnr/ppp2ppp/2n1p3/1B1p4/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1", "r1bqkbnr/ppp2ppp/2n1p3/1B1p4/4P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 1", 4, 6)
  def test_queen_side_castle(self):
    self.make_move_test("r1bqkbnr/ppp2ppp/2n1p3/3p2B1/1P2P3/2NB1N2/PPP1QPPP/R3K2R w KQkq - 0 1", "r1bqkbnr/ppp2ppp/2n1p3/3p2B1/1P2P3/2NB1N2/PPP1QPPP/2KR3R b kq - 1 1", 4, 2)    
  def test_simple_promotion(self):
    self.make_move_test("r2qkbnr/1Ppppppp/2n5/8/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "rQ1qkbnr/2pppppp/2n5/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", 49, 57, promoted_piece='Q')
  
  def test_capture_promotion(self):
    self.make_move_test("r2qkbnr/1Ppppppp/2n5/8/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "Q2qkbnr/2pppppp/2n5/8/8/8/PPPP1PPP/RNBQKBNR b KQk - 0 1", 49, 56, promoted_piece='Q')
  
  def test_enpassant(self):
    self.make_move_test("rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 1", "rnbqkbnr/ppp1p1pp/5P2/3p4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", None, None, is_enpassant=True)

  def test_make_unmake_simple(self):
    self.unmake_move_test(None, 12, 28)

  def test_unmake_capture_move(self):
    self.unmake_move_test("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1", 28, 35)

  def test_unmake_promotion(self):
    self.unmake_move_test("rnbqkb1r/ppppp1Pp/8/8/8/8/PPPP2PP/RNBQKBNR w KQkq - 0 1", 54, 62, promoted_piece='Q')

  def test_unmake_capture_promotion(self):
    self.unmake_move_test("rnbqkb1r/ppppp1Pp/8/8/8/8/PPPP2PP/RNBQKBNR w KQkq - 0 1", 54, 61, promoted_piece='Q')
    
  def test_unmake_king_side_castle(self):
    self.unmake_move_test("rnbqk2r/pppppppp/1b3n2/8/8/1B3N2/PPPPPPPP/RNBQK2R w KQkq - 0 1", 4, 6)
  
  def test_unmake_queen_side_castle(self):
    self.unmake_move_test("rnbqk2r/pppppppp/1b3n2/8/3Q4/1BBN1N2/PPPPPPPP/R3K2R w KQkq - 0 1", 4, 2)
      
if __name__ == '__main__':
   unittest.main()