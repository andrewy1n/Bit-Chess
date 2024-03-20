import unittest
from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core import BitboardUtility as BBU  
import numpy as np

board = Board()
move_generator = MoveGeneration(board)

class TestAttackGeneration(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
      super().__init__(methodName)

if __name__ == '__main__':
   unittest.main()