import unittest
from src.BitChess.Board import Board
from src.BitChess.MoveGeneration import MoveGeneration
from src.BitChess.PrecomputedAttacks import PrecomputedAttacks
from src.BitChess import BitboardUtility as BBU  
import numpy as np

attacks = PrecomputedAttacks()

class TestMoveGeneration(unittest.TestCase):
   def test_check_pin(self):
      board = Board(FEN_string="rnbqk1nr/pppppppp/8/8/1b6/8/PPPBPPPP/RN1QKBNR w KQkq - 0 1")
      move_generator = MoveGeneration(board, attacks)

      pin_ray = BBU.set_square_notation(np.uint64(0), [('c', 3), ('d', 2), ('b', 4), ('e', 1)])

      self.assertEqual(pin_ray, move_generator.pin_rays)
   
   def test_king_moves(self):
      board = Board(FEN_string="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
      move_generator = MoveGeneration(board, attacks)
      king_moves = []
      move_generator.generate_king_moves(king_moves)
      
      self.assertEqual(len(king_moves), 4)
   
   def test_slider_moves(self):
      board = Board(FEN_string="2N2B2/R4Kp1/2P4q/pP4p1/3p4/4R3/2bQ4/N4k2 w - - 0 1")
      move_generator = MoveGeneration(board, attacks)
      slider_moves = []
      move_generator.generate_slider_moves(slider_moves)
      
      self.assertEqual(len(slider_moves), 40)

   def test_sliders_pin(self):
      board = Board(FEN_string="3k4/8/3r4/7b/b7/3R1B2/2Q5/3K4 w - - 0 1")
      move_generator = MoveGeneration(board, attacks)
      slider_moves = []
      move_generator.generate_slider_moves(slider_moves)

      self.assertEqual(len(slider_moves), 9)
   
   def test_knight_moves(self):
      board = Board(FEN_string="4k3/8/8/8/7q/6N1/2N5/4K3 w - - 0 1")
      move_generator = MoveGeneration(board, attacks)
      knight_moves = []
      move_generator.generate_knight_moves(knight_moves)

      self.assertEqual(len(knight_moves), 5)
   
   def test_check_ray(self):
      board = Board(FEN_string="4k3/4q3/8/7B/2R5/8/2N4Q/4K3 w - - 0 1")
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)
      
      self.assertEqual(len(moves), 9)
   
   def test_pawn_push(self):
      board = Board()
      move_generator = MoveGeneration(board, attacks)
      pawn_push_moves = []
      moves = move_generator.generate_pawn_moves(pawn_push_moves)
      
      self.assertEqual(len(moves), 16)
   
   def test_pawn_captures(self):
      board = Board(FEN_string="rnbqkbnr/p5pp/8/1ppppp2/2P1P3/8/8/RNBQKBNR w KQkq e6 0 1")
      move_generator = MoveGeneration(board, attacks)
      pawn_push_moves = []
      moves = move_generator.generate_pawn_moves(pawn_push_moves)
      
      self.assertEqual(len(moves), 4)
   
   def test_pawn_promotions(self):
      board = Board(FEN_string="rn1qkbnr/p1P3pp/8/1ppppp2/8/8/8/RNBQKBNR w KQkq - 0 1")
      move_generator = MoveGeneration(board, attacks)
      pawn_push_moves = []
      moves = move_generator.generate_pawn_moves(pawn_push_moves)

      self.assertEqual(len(moves), 12)
   
   def test_pawn_enpassant(self):
      board = Board(FEN_string="rnbqkbnr/ppp2ppp/8/3Pp3/8/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 1")
      move_generator = MoveGeneration(board, attacks)
      pawn_push_moves = []
      moves = move_generator.generate_pawn_moves(pawn_push_moves)

      self.assertEqual(len(moves), 16)
   
   def test_pawn_black(self):
      board = Board(FEN_string="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
      move_generator = MoveGeneration(board, attacks)
      pawn_push_moves = []
      moves = move_generator.generate_pawn_moves(pawn_push_moves)
      
      self.assertEqual(len(moves), 16)
   
   def test_pawn_black_captures(self):
      board = Board(FEN_string="rnbqkbnr/8/8/3p4/2P1P3/8/PP1P1PPP/RNBQKBNR b KQkq - 0 1")
      move_generator = MoveGeneration(board, attacks)
      pawn_push_moves = []
      moves = move_generator.generate_pawn_moves(pawn_push_moves)

      self.assertEqual(len(moves), 3)
   
   def test_check_mate(self):
      board = Board(FEN_string="rnb1k1nr/pppppppp/8/2b5/8/8/PPPPPqPP/RNBQKBNR w KQkq - 0 1")
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)

      self.assertEqual(len(moves), 0)
      self.assertEqual(move_generator.in_check, True)
   
   def test_check_king_capture(self):
      board = Board(FEN_string="rnb1kbnr/pppppppp/8/8/8/8/PPPPPqPP/RNBQKBNR w KQkq - 0 1")
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)
      board.print_moves(moves)
      self.assertEqual(len(moves), 1)
      self.assertEqual(move_generator.in_check, True)

   def test_start_all_moves(self):
      board = Board()
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)

      self.assertEqual(len(moves), 20)
   
   def test_position_5_depth1(self):
      board = Board(FEN_string="rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)

      self.assertEqual(len(moves), 44)
   
   def test_position2_depth1(self):
      board = Board(FEN_string="r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -")
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)

      self.assertEqual(len(moves), 48)
   
   def test_position5_depth2_e1g1(self):
      board = Board(FEN_string="rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQ1RK1 b - - 1 8")
      move_generator = MoveGeneration(board, attacks)
      moves = move_generator.generate_moves(board)

      board.print_moves(moves)
      self.assertEqual(len(moves), 34)

if __name__ == '__main__':
   unittest.main()