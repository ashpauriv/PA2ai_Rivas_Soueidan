from typing import List, Optional
import numpy as np
import sys
import random
import math

class GameBoard:
    """Connect4 game board class."""

    def __init__(self, board):
        self.board = np.array(board)

    def make_move(self, col, player):
        """Make a move on the board."""
        if self.board[0, col] != 'O':
            raise ValueError("Column is full")
        
        for row in range(6):
            if self.board[row, col] == 'O':
                self.board[row][col] = 'Y' if player == 'Y' else 'R'
                return
        raise ValueError("Column is full")

    @staticmethod
    def check_win(board, player) -> bool:
        """Check for a win condition for the given player."""
        return (
            GameBoard.check_rows(board, player)
            or GameBoard.check_cols(board, player)
            or GameBoard.check_diag(board, player)
        )

    @staticmethod
    def check_rows(board, player) -> bool:
        for y in range(6):
            for x in range(4):
                if (
                    board[y, x] == board[y, x + 1] == board[y, x + 2] == board[y, x + 3] == player
                ):
                    return True
        return False

    @staticmethod
    def check_cols(board, player) -> bool:
        for x in range(7):
            for y in range(3):
                if (
                    board[y, x] == board[y + 1, x] == board[y + 2, x] == board[y + 3, x] == player
                ):
                    return True
        return False

    @staticmethod
    def check_diag(board, player) -> bool:
        for y in range(3, 6):
            for x in range(4):
                if (
                    board[y, x] == board[y - 1, x + 1] == board[y - 2, x + 2] == board[y - 3, x + 3] == player
                ):
                    return True
        for y in range(3, 6):
            for x in range(3, 7):
                if (
                    board[y, x] == board[y - 1, x - 1] == board[y - 2, x - 2] == board[y - 3, x - 3] == player
                ):
                    return True
        return False

    @staticmethod
    def check_tie(board) -> bool:
        """Check if board is a tie."""
        return np.all(board != 'O')
    
class Node:
    """Monte Carlo tree node class."""

    def __init__(self, parent: Optional["Node"], board: np.ndarray, player: str, last_move_col: int):
        self.q = 0  # sum of rollout outcomes
        self.n = 0  # number of visits
        self.parent = parent
        self.board = board
        self.player = player
        self.last_move_col = last_move_col
        self.children: List["Node"] = []
        self.terminal = self.check_terminal()


    def check_terminal(self) -> bool:
        """Check whether node is a leaf."""
        if GameBoard.check_win(self.board, self.player):
            return True
        if GameBoard.check_tie(self.board):
            return True
        return False

    def add_children(self, children: dict) -> None:
        for child in children.values():
            self.children.append(child)

    def do_move(self, col: int) -> None:
        """Make a move on the board."""
        GameBoard.make_move(self.board, col, self.player)
        self.player = 'R' if self.player == 'Y' else 'Y'

    def undo_move(self) -> None:
        """Undo the last move."""
        last_row = 0
        for row in range(6):
            if self.board[row, self.last_move_col] != 'O':
                last_row = row
        self.board[last_row][self.last_move_col] = 'O'
        self.player = 'R' if self.player == 'Y' else 'Y'

class ConnectFourAlgorithm:
    def __init__(self, game: GameBoard, player: str):
        self.game = game
        self.player = player
        self.root = Node(None, game.board.copy(), player, -1)

    def ur(self):
        legal_moves = [col for col in range(7) if self.game.board[5][col] == 'O']
        if not legal_moves:
            return None
        return random.choice(legal_moves)

    def pmcgs(self, player, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.board[5][col] == 'O']
        if not legal_moves:
            return None, None

        results = {}
        for col in legal_moves:
            total_wins = 0
            total_visits = 0
            for _ in range(simulations):
                new_game = GameBoard(self.game.board.copy())
                new_game.make_move(col, player)
                result = self.rollout(new_game, player)
                total_visits += 1
                if result == 1:  # Player wins
                    total_wins += 1

            wi = total_wins
            ni = total_visits
            win_ratio = wi / ni if ni > 0 else 0
            results[col] = {'wi': wi, 'ni': ni, 'win_ratio': win_ratio}

        if mode == "Verbose":
            for col, result in results.items():
                print(f"Column {col + 1}: wi: {result['wi']}, ni: {result['ni']}, Win Ratio: {result['win_ratio']:.2f}")

        best_move = max(results, key=lambda x: results[x]['win_ratio'])
        
        return best_move, results


    def uct(self, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.board[5, col] == 'O']
        if not legal_moves:
            return None

        results = {}
        exploration_param = math.sqrt(2)

        for col in legal_moves:
            total_wins = 0
            total_simulations = 0
            for _ in range(simulations):
                new_game = GameBoard(self.game.board.copy())
                new_game.make_move(col, self.player)
                result = self.rollout(new_game, self.player)
                total_simulations += 1
                if result == 1:  # Player wins
                    total_wins += 1

            ni = total_simulations
            if ni == 0:
                ucb_value = float('inf')
            else:
                wi = total_wins
                ucb_value = (wi / ni) + exploration_param * math.sqrt(math.log(simulations) / ni)

            results[col] = ucb_value

            if mode == 'Verbose':
                print(f"Column {col + 1}: UCB Value: {ucb_value:.2f}")

        if not results:
            return None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            print(f"Best move: {best_move + 1}, UCB Value: {results[best_move]:.2f}")

        return best_move


    def rollout(self, game, player):
        current_player = player
        max_iterations = 1000  # Limit the number of iterations for the rollout
        iterations = 0

        while iterations < max_iterations:
            if GameBoard.check_win(game.board, current_player):
                return 1 if current_player == player else -1
            elif GameBoard.check_tie(game.board):
                return 0
            current_player = 'R' if current_player == 'Y' else 'Y'
            iterations += 1

        # If the loop exceeds the maximum iterations, consider it a draw
        return 0

def read_board(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    algorithm = lines[0].strip()
    player = lines[1].strip()
    board = [list(line.strip()) for line in lines[2:]]

    return algorithm, player, board

def print_board(board):
    for row in board:
        print(" ".join(row))

def main():
    if len(sys.argv) != 4:
        print("Usage: python connect_four.py <input_file> <Verbose/Brief/None> <number_of_simulations>")
        sys.exit(1)

    filename = sys.argv[1]
    mode = sys.argv[2]
    simulations = int(sys.argv[3])

    algorithm, player, board = read_board(filename)
    print("Algorithm from file:", repr(algorithm))
    game = GameBoard(board)
    algorithm_obj = ConnectFourAlgorithm(game, player)
    print(player)
    print_board(board)
    if algorithm == 'UR':
        move = algorithm_obj.ur()
        print(f"Move selected for UR: {move}")
    elif algorithm == 'PMCGS':
        move, results = algorithm_obj.pmcgs(player, simulations, mode)
        print(f"Move selected for PMCGS: {move}")
        if mode == 'Verbose':
            print("Results:")
            for col, result in sorted(results.items()):
                print(f"Column {col + 1}: wi: {result['wi']}, ni: {result['ni']}, Win Ratio: {result['win_ratio']:.2f}")
    elif algorithm == 'UCT':
        move = algorithm_obj.uct(simulations, mode)
        print(f"Move selected for UCT: {move}")
    else:
        print("Unknown algorithm")

if __name__ == "__main__":
    main()

