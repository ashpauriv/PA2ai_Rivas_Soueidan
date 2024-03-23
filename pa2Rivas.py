from typing import List, Optional
import numpy as np
import sys
import random

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
            or GameBoard.check_tie(board)
        )
    @staticmethod
    def check_rows(board, player) -> Optional[int]:
        for y in range(6):
            for x in range(4):
                if (
                    board[y, x] == board[y, x + 1] == board[y, x + 2] == board[y, x + 3] == player
                ):
                    return True
        return False
    @staticmethod
    def check_cols(board, player) -> Optional[int]:
        """Check for winner in columns.

        Args:
            board (np.ndarray): Board game.

        Returns:
            int | None: Winner id or None.
        """
        for x in range(7):  # Iterate over columns
            for y in range(3):  # Limit rows to prevent out-of-bounds access
                if (
                    board[y, x] == board[y + 1, x] == board[y + 2, x] == board[y + 3, x] == player
                ):
                    return True
        return False

    @staticmethod
    def check_diag(board, player) -> Optional[int]:
        """Check for winner in diagonals.

        Args:
            board (np.ndarray): Board game.

        Returns:
            int | None: Winner id or None.
        """
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
        """Check if board is a tie.

        Args:
            board (np.ndarray): Board game.

        Returns:
            bool: Game is a tie.
        """
        return np.all(board != 'O')
    
class Node:
    """Monte Carlo tree node class."""

    def __init__(self, parent: Optional["Node"], board: np.ndarray, player: str):
        self.q = 0  # sum of rollout outcomes
        self.n = 0  # number of visits
        self.parent = parent
        self.board = board
        self.player = player
        # no children have been expanded yet
        self.children: List["Node"] = []
        self.terminal = self.check_terminal()


    def check_terminal(self) -> bool:
        """Check whether node is a leaf.

        Returns:
            bool: Node is a leaf.
        """
        if GameBoard.check_rows(self.board, self.player):
            return True
        if GameBoard.check_cols(self.board, self.player):
            return True
        if GameBoard.check_diag(self.board, self.player):
            return True
        if GameBoard.check_tie(self.board):
            return True
        return False

    def add_children(self, children: dict) -> None:
        for child in children.values():
            self.children.append(child)


class ConnectFourAlgorithm:
    def __init__(self, game: GameBoard, player: str):
        self.game = game
        self.player = player
        self.root = Node(None, game.board.copy(), player)



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
            total_simulations = 0
            for _ in range(simulations):
                new_game = GameBoard(self.game.board.copy())
                new_game.make_move(col, self.player)
                result = self.rollout(new_game)
                total_simulations += 1
                if result == 1:  # Yellow wins
                    total_wins += 1

            ni = total_simulations
            if ni == 0:
                results[col] = None
            else:
                results[col] = total_wins / ni

            if mode == 'Verbose':
                print(f"Column {col + 1}: {results[col]:.2f}")
                print(f"wi: {total_wins}")
                print(f"ni: {ni}")
                print(f"Move selected: {col}")

        if not results:
            return None, None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            print(f"Best move: {best_move + 1}, Win ratio: {results[best_move]:.2f}")

        return best_move, results


    def uct(self, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.board[5, col] == 'O']
        if not legal_moves:
            return None

        results = {}

        for col in legal_moves:
            total_wins = 0
            total_simulations = 0
            for _ in range(simulations):
                new_game = ConnectFourAlgorithm(self.game, 'Y')
                new_game.make_move(col,self.player)
                result = self.simulate(new_game)
                total_simulations += 1
                if result == 1:  # Yellow wins
                    total_wins += 1

            ni = total_simulations
            if ni == 0:
                results[col] = float('inf')  # Setting to infinity to prioritize unexplored nodes
            else:
                results[col] = total_wins / ni

            if mode == 'Verbose':
                print(f"Column {col + 1}: {results[col]:.2f}")

        if not results:
            return None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            print(f"Best move: {best_move + 1}, Win ratio: {results[best_move]:.2f}")

        return best_move

    def rollout(self, game):
        current_player = 'Y'
        max_iterations = 1000  # Limit the number of iterations for the rollout
        iterations = 0

        while iterations < max_iterations:
            if GameBoard.check_win(game.board,current_player):
                return 1
            elif GameBoard.check_tie(game.board):
                return 0
            current_player = 'R' if current_player == 'Y' else 'Y'
            iterations += 1

        # If the loop exceeds the maximum iterations, consider it a draw
        return 0

    def simulate(self, game):
        current_player = 'Y'
        max_iterations = 1000  # Limit the number of iterations for the simulation
        iterations = 0

        while iterations < max_iterations:
            if GameBoard.check_win(game.board,current_player):
                return 1
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
'''
def play_game(algorithm1, algorithm2, simulations1, simulations2):
    game = ConnectFourAlgorithm()
    player1 = 'Y'
    player2 = 'R'
    algorithm_obj1 = ConnectFourAlgorithm(game, player1)
    algorithm_obj2 = ConnectFourAlgorithm(game, player2)
    while not game.check_win(player1) and not game.check_win(player2) and not game.check_draw():
        if player1 == 'Y':
            move = algorithm_obj1.__getattribute__(algorithm1)(simulations1, "None")
        else:
            move = algorithm_obj2.__getattribute__(algorithm2)(simulations2, "None")
        if move is not None:
            game.make_move(move, player1 if player1 == 'Y' else player2)
        player1, player2 = player2, player1
    if game.check_win('Y'):
        return 'Y'
    elif game.check_win('R'):
        return 'R'
    else:
        return 'Draw'

def run_tournament():
    algorithms = ['ur', 'pmcgs', 'uct']
    simulations = [500, 10000]
    results = {}
    for algorithm1 in algorithms:
        for simulation1 in simulations:
            for algorithm2 in algorithms:
                for simulation2 in simulations:
                    if algorithm1 == 'ur' and algorithm2 == 'ur':
                        continue
                    wins1 = 0
                    wins2 = 0
                    draws = 0
                    for _ in range(100):
                        winner = play_game(algorithm1, algorithm2, simulation1, simulation2)
                        if winner == 'Y':
                            wins1 += 1
                        elif winner == 'R':
                            wins2 += 1
                        else:
                            draws += 1
                    results[f"{algorithm1} ({simulation1}) vs {algorithm2} ({simulation2})"] = (wins1, wins2, draws)
    return results
'''
def print_results(results):
    print("Results:")
    print("{:<40} {:<10} {:<10} {:<10}".format("Matchup", "Player 1", "Player 2", "Draws"))
    for matchup, (wins1, wins2, draws) in results.items():
        print("{:<40} {:<10} {:<10} {:<10}".format(matchup, wins1, wins2, draws))

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
        game.make_move(move,player)
        if GameBoard.check_win(np.array(board), 'Y'):
            print("Yellow wins!")
        elif GameBoard.check_win(np.array(board), 'R'):
            print("Red wins!")
        elif GameBoard.check_tie(np.array(board)):
            print("It's a draw!")
    elif algorithm == 'PMCGS':
        move, results = algorithm_obj.pmcgs(player, simulations, mode)
        print(f"Move selected for PMCGS: {move}")
        if mode == 'Verbose':
            print(f"Results: {results}")
        if GameBoard.check_win(np.array(board), 'Y'):
            print("Yellow wins!")
        elif GameBoard.check_win(np.array(board), 'R'):
            print("Red wins!")
        elif GameBoard.check_tie(np.array(board)):
            print("It's a draw!")
    elif algorithm == 'UCT':
        move = algorithm_obj.uct(simulations, mode)
        print(f"Move selected for UCT: {move}")
        if GameBoard.check_win(np.array(board), 'Y'):
            print("Yellow wins!")
        elif GameBoard.check_win(np.array(board), 'R'):
            print("Red wins!")
        elif GameBoard.check_tie(np.array(board)):
            print("It's a draw!")
    else:
        print("Unknown algorithm")

if __name__ == "__main__":
    main()
