from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core.PrecomputedAttacks import PrecomputedAttacks

class Perft:
    def __init__(self, FEN_string=None):
        self.board = Board(FEN_string=FEN_string) if FEN_string is not None else Board()
        self.attack_data = PrecomputedAttacks()
        self.move_generator = MoveGeneration(self.board, self.attack_data)

    def perft(self, depth):
        print()
        return self.perft_alg(depth, depth)

    def perft_alg(self, depth, current_depth):
        nodes = 0
        if current_depth == 0:
            return 1
        else:
            moves = self.move_generator.generate_moves(self.board)
            for m in moves:
                self.board.make_move(m)
                node_for_move = self.perft_alg(depth, current_depth - 1)
                nodes += node_for_move
                if current_depth == depth:
                    start_file = chr(ord('a') + (m.start_index % 8))
                    start_rank = str((m.start_index // 8) + 1)
                    target_file = chr(ord('a') + (m.target_index % 8))
                    target_rank = str((m.target_index // 8) + 1)
                    print(f"{start_file}{start_rank}{target_file}{target_rank}: {node_for_move}")
                self.board.unmake_move(m)
        return nodes