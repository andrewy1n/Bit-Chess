import unittest
from src.Core.Board import Board
from src.Core.PrecomputedAttacks import PrecomputedAttacks as AttackGeneration
from src.Core import BitboardUtility as BBU  
import numpy as np

board = Board()
attack_generator = AttackGeneration()

class TestAttackGeneration(unittest.TestCase):
   # Test knight moves on D4
   def test_knight_moves(self):
      available_moves = BBU.set_square_notation(np.uint64(0), [('c', 2), ('b', 3), ('b', 5), ('c', 6), ('e', 6), ('f', 5), ('f', 3), ('e', 2)])

      BBU.printBB(available_moves)
      print()

      knight_moves = attack_generator.knight_attacks[27]

      BBU.printBB(knight_moves)
      print()
      
      self.assertEqual(available_moves, knight_moves)
   
   # Test King moves on D4
   def test_king_moves(self):
      available_moves = BBU.set_square_notation(np.uint64(0), [('d', 3), ('d', 5), ('c', 4), ('e', 4), ('c', 3), ('e', 3), ('c', 5), ('e', 5)])

      BBU.printBB(available_moves)
      print()

      king_moves = attack_generator.king_moves[27]

      BBU.printBB(king_moves)
      print()
      
      self.assertEqual(available_moves, king_moves)
   
   # Black pawn attacks on D4
   def test_black_pawn_attacks(self):
      available_moves = BBU.set_square_notation(np.uint64(0), [('c', 3), ('e', 3)])

      BBU.printBB(available_moves)
      print()

      attacks = attack_generator.black_pawn_attacks[27]

      BBU.printBB(attacks)
      print()
      
      self.assertEqual(available_moves, attacks)
   
   # Test blockers for rank attacks, assuming piece is on position D4
   # Blockers are on C4 and H4
   def test_rank_blockers_to_attack(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('c', 4), ('h', 4), ('d', 4)])
      BBU.printBB(sample_blockers)
      print()
      
      rank_moves = BBU.set_square_notation(np.uint64(0), [('c', 4), ('e', 4), ('f', 4), ('g', 4), ('h', 4)])
      BBU.printBB(rank_moves)
      print()

      move_gen_rank_moves = attack_generator.rank_attacks[27][sample_blockers >> np.uint64(24) & np.uint64(255)]
      BBU.printBB(move_gen_rank_moves)
      
      self.assertEqual(rank_moves, move_gen_rank_moves)
    
   # Test blockers for file attacks, assuming piece is on position D4 with blockers on D1 and D6
   def test_file_blockers_to_attack(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('d', 1), ('d', 6), ('d', 4)])
      BBU.printBB(sample_blockers)
      print()
      
      file_moves = BBU.set_square_notation(np.uint64(0), [('d', 1), ('d', 2), ('d', 3), ('d', 5), ('d', 6)])
      BBU.printBB(file_moves)
      print()

      move_gen_file_moves = attack_generator.file_attacks[27][BBU.rotate_mirrored90c(sample_blockers) >> np.uint64(24) & np.uint64(255)]
      BBU.printBB(move_gen_file_moves)
      
      self.assertEqual(file_moves, move_gen_file_moves)
   
   # Test available moves for a rook on H4, blockers on H3, H7, E4
   def test_rook_attacks(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('h', 3), ('h', 7), ('e', 4), ('h', 4)])
      BBU.printBB(sample_blockers)
      print()

      valid_moves = BBU.set_square_notation(np.uint64(0),[('h', 3), ('h', 5), ('h', 6), ('h', 7), ('g', 4), ('f', 4), ('e', 4)])
      BBU.printBB(valid_moves)
      print()

      rank_moves = attack_generator.rank_attacks[31][sample_blockers >> np.uint64(24) & np.uint64(255)]
      file_moves = attack_generator.file_attacks[31][BBU.rotate_mirrored90c(sample_blockers) >> np.uint64(56) & np.uint64(255)]
      BBU.printBB(rank_moves | file_moves)

      self.assertEqual(rank_moves | file_moves, valid_moves)
   
   # Test diagonal move generator function, for moves along the right diagonal
   def test_diagonal_move_function(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('b', 2), ('g', 7), ('d', 4)])
      BBU.printBB(sample_blockers)
      print()
      moves = BBU.set_square_notation(np.uint64(0), [('b', 2), ('c', 3), ('e', 5), ('f', 6), ('g', 7)])
      BBU.printBB(moves)
      print()

      moves_generated = attack_generator.generate_diagonal_moves(3, 3, sample_blockers)
      BBU.printBB(moves_generated)
      print()

      self.assertEqual(moves, moves_generated)
   
   # Test diagonal right attacks on D4 and blockers B2 and G7
   def test_diagonal_right_moves(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('b', 2), ('g', 7), ('d', 4)])
      BBU.printBB(sample_blockers)
      print()
      moves = BBU.set_square_notation(np.uint64(0), [('b', 2), ('c', 3), ('e', 5), ('f', 6), ('g', 7)])
      BBU.printBB(moves)
      print()

      moves_generated = attack_generator.diagR_attacks[27][BBU.rotate45(sample_blockers) >> 28 & np.uint64(255)]

      BBU.printBB(moves_generated)
      print()

      self.assertEqual(moves, moves_generated)
   
   # Test bishop attacks C5 blockers on E3, B6, A3, and F8
   def test_bishop_attacks(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('e', 3), ('b', 6), ('a', 3), ('f', 8), ('c', 5)])
      BBU.printBB(sample_blockers)
      print()

      moves = BBU.set_square_notation(np.uint64(0), [('b', 6), ('d', 4), ('e', 3), ('a', 3), ('b', 4), ('d', 6), ('e', 7), ('f', 8)])
      BBU.printBB(moves)
      print()

      right_diagonal = attack_generator.diagR_attacks[34][BBU.rotate45(sample_blockers) >> attack_generator.diag_to_shift[9] & np.uint64(255)]
      left_diagonal = attack_generator.diagL_attacks[34][BBU.rotate45(sample_blockers, is_right=False) >> attack_generator.diag_to_shift[8] & np.uint64(127)]

      BBU.printBB(right_diagonal | left_diagonal)
      print()

      self.assertEqual(right_diagonal | left_diagonal, moves)
   
   # Test bishop attacks on F8, blockers on G7, H6
   def test_bishop_attacks2(self):
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('f', 8), ('g', 7), ('h', 6)])
      BBU.printBB(sample_blockers)
      print()

      moves = BBU.set_square_notation(np.uint64(0), [('g', 7), ('e', 7), ('d', 6), ('c', 5), ('b', 4), ('a', 3)])
      BBU.printBB(moves)
      print()

      right_diagonal = attack_generator.diagR_attacks[61][BBU.rotate45(sample_blockers) >> attack_generator.diag_to_shift[9] & np.uint64(2**(6)-1)]
      left_diagonal = attack_generator.diagL_attacks[61][BBU.rotate45(sample_blockers, is_right=False) >> attack_generator.diag_to_shift[2] & np.uint64(2**(3)-1)]

      BBU.printBB(right_diagonal | left_diagonal)
      print()

      self.assertEqual(right_diagonal | left_diagonal, moves)
   
   def test_diagonal(self):
      diag_lengths = [8, 7, 6, 5, 4, 3, 2, 1]
      sample_blockers = BBU.set_square_notation(np.uint64(0), [('a', 5)])

      moves = BBU.set_square_notation(np.uint64(0), [('e', 1), ('d', 2), ('c', 3), ('b', 4), ('b', 6), ('c', 7), ('d', 8)])

      x, y = 0, 4

      right_diagonal = attack_generator.diagR_attacks[32][BBU.rotate45(sample_blockers) >> attack_generator.diag_to_shift[7-x+y] & np.uint64(2**(diag_lengths[abs(x-y)])-1)]
      left_diagonal = attack_generator.diagL_attacks[32][BBU.rotate45(sample_blockers, is_right=False) >> attack_generator.diag_to_shift[14-x-y] & np.uint64(2**(diag_lengths[abs(7-x-y)])-1)]
      BBU.printBB(right_diagonal | left_diagonal)
      print()

      self.assertEqual(right_diagonal | left_diagonal, moves)



if __name__ == '__main__':
   unittest.main()