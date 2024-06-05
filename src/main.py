from src.Core.Board import Board
from src.Core.MoveGeneration import MoveGeneration
from src.Core.PrecomputedAttacks import PrecomputedAttacks
from src.Core.Move import Move

def main():
    board = Board()
    precomputed_attacks = PrecomputedAttacks()
    move_generator = MoveGeneration(board, precomputed_attacks)

    while(True):
        board.print_board()
        print(f"Player Turn: {board.turn}")

        moves = move_generator.generate_moves(board)
        
        if move_generator.in_check and len(moves) == 0:
            print("Checkmate!")
            break
        elif len(moves) == 0:
            print("Stalemate!")
            break
        
        move = user_input(board, moves)
        board.make_move(move)

def user_input(board: Board, moves: list[Move]) -> Move:        
    while True:
        notation = input("Enter the move in chess notation (e.g., e2e4): ")

        if notation == 'm':
            board.print_moves(moves)
        else:
            start_file = ord(notation[0]) - ord('a')
            start_rank = int(notation[1]) - 1
            start_index = 8 * start_rank + start_file

            target_file = ord(notation[2]) - ord('a')
            target_rank = int(notation[3]) - 1
            target_index = 8 * target_rank + target_file
        
            for move in moves:
                if move.start_index == start_index and move.target_index == target_index:
                    return move

            print("Invalid move notation. Please try again.")

if __name__ == "__main__":
    main()