import unittest
from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core import BitboardUtility as BBU  
import numpy as np

class TestRotations(unittest.TestCase):
    def test_90cc(self):
        original_arr = BBU.uint_to_rep(np.uint64(0))
        original_arr[0][0] = 1
        original_bb = BBU.rep_to_uint(original_arr)
        BBU.printBB(original_bb)

        print()
        flipped_arr = BBU.uint_to_rep(np.uint64(0))
        flipped_arr[7][0] = 1
        flipped_bb = BBU.rep_to_uint(flipped_arr)
        BBU.printBB(flipped_bb)
        print()

        self.assertEqual(BBU.rotate90cc(original_bb), flipped_bb)
    
    def test_rotate45_r(self):
        diag_to_shift = [0, 1, 3, 6, 10, 15, 21, 28, 36, 43, 49, 54, 58, 61, 63]
        original_bb = BBU.set_square_notation(np.uint64(0), [('e', 5), ('f', 6), ('c', 3)])
        BBU.printBB(original_bb)
        
        print()
        original_bb = BBU.rotate45(original_bb) >> diag_to_shift[7]
        BBU.printBB(original_bb)
        print()

        altered_bb = BBU.set_square_notation(np.uint64(0), [('e', 1), ('f', 1), ('c', 1)])
        BBU.printBB(altered_bb)
        print()

        self.assertEqual(original_bb, altered_bb)
    
    def test_rotate45_l(self):
        diag_to_shift = [0, 1, 3, 6, 10, 15, 21, 28, 36, 43, 49, 54, 58, 61, 63]
        original_bb = BBU.set_square_notation(np.uint64(0), [('e', 3), ('f', 2), ('c', 5)])
        BBU.printBB(original_bb)
        print()

        BBU.printBB(BBU.rotate90cc(original_bb))
        print()
        original_bb = BBU.rotate45(original_bb, is_right=False) >> diag_to_shift[8]
        BBU.printBB(original_bb)
        print()

        altered_bb = BBU.set_square_notation(np.uint64(0), [('e', 1), ('f', 1), ('c', 1)])
        BBU.printBB(altered_bb)
        print()

        self.assertEqual(original_bb, altered_bb)

if __name__ == '__main__':
    unittest.main()