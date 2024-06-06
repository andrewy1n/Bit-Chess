import unittest
from src.BitChess.Perft import Perft

class TestPERFT(unittest.TestCase):
    def test_default_pos(self):
        perft = Perft()
        self.assertEqual(perft.perft(1), 20)
        self.assertEqual(perft.perft(2), 400)
        self.assertEqual(perft.perft(3), 8902)
        #self.assertEqual(perft.perft(4), 197281)
        #self.assertEqual(perft.perft(5), 4865609)
    
    def test_pos_5(self):
        perft = Perft("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
        self.assertEqual(perft.perft(1), 44)
        self.assertEqual(perft.perft(2), 1486)
        self.assertEqual(perft.perft(3), 62379)
        #self.assertEqual(perft.perft(4), 2103487)
        #self.assertEqual(perft.perft(5), 89941194)
    
    def test_pos_2(self):
        perft = Perft("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -")
        self.assertEqual(perft.perft(1), 48)
        self.assertEqual(perft.perft(2), 2039)
        self.assertEqual(perft.perft(3), 97862)
    
    def test_pos_4(self):
        perft = Perft("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10")
        self.assertEqual(perft.perft(1), 46)
        self.assertEqual(perft.perft(2), 2079)
        self.assertEqual(perft.perft(3), 89890)
        self.assertEqual(perft.perft(4), 3894594)

if __name__ == '__main__':
    unittest.main()