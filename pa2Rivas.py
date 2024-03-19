import sys
import random
import math

class TreeNode:
    def __init__(self, game=None, parent=None, move=None):
        self.game = game  # Store the game state
        self.parent = parent
        self.move = move
        self.wi = 0  # Number of wins
        self.ni = 0  # Number of simulations
        self.children = []

class ConnectFourGame:
    def __init__(self):
        self.board = [['O' for _ in range(7)] for _ in range(6)]

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def is_legal_move(self, col):
        return self.board[0][col] == 'O'

    def make_move(self, col, player):
        for row in range(5, -1, -1):
            if self.board[row][col] == 'O':
                self.board[row][col] = player
                break

    def check_win(self, player):
        # Check for a win in all directions
        for row in range(6):
            for col in range(7):
                if self.check_line(row, col, 1, 0, player) or \
                   self.check_line(row, col, 0, 1, player) or \
                   self.check_line(row, col, 1, 1, player) or \
                   self.check_line(row, col, 1, -1, player):
                    return True
        return False

    def check_line(self, row, col, delta_row, delta_col, player):
        for _ in range(4):
            if not (0 <= row < 6) or not (0 <= col < 7) or self.board[row][col] != player:
                return False
            row += delta_row
            col += delta_col
        return True

    def check_draw(self):
        return all(not self.is_legal_move(col) for col in range(7))

class ConnectFourAlgorithm:
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def ur(self):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]
        if not legal_moves:
            return None
        return random.choice(legal_moves)

    def pmcgs(self, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]
        if not legal_moves:
            return None, None

        results = {}
        c = math.sqrt(2)  # Exploration parameter

        for col in legal_moves:
            total_wins = 0
            total_simulations = 0
            for _ in range(simulations):
                new_game = ConnectFourGame()
                new_game.board = [row[:] for row in self.game.board]
                new_game.make_move(col, self.player)
                result = self.rollout(new_game)
                total_simulations += 1
                if result == 1:  # Yellow wins
                    total_wins += 1

            ni = total_simulations
            Ni = sum(results.values()) + ni
            if ni == 0:
                results[col] = float('inf')  # Setting to infinity to prioritize unexplored nodes
            else:
                results[col] = total_wins / ni + c * math.sqrt(math.log(Ni) / ni)

            if mode == 'Verbose':
                print(f"Column {col + 1}: {results[col]:.2f}")
                print(f"wi: {total_wins}")
                print(f"ni: {ni}")
                print(f"Move selected: {col}")

        if not results:
            return None, None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            print("NODE ADDED" if col == best_move else "")
        elif mode == "Brief":
            print(f"Best move: {best_move + 1}, Win ratio: {results[best_move]:.2f}")

        return best_move, results


    def rollout(self, game):
        current_player = self.player
        max_iterations = 1000  # Limit the number of iterations for the rollout
        iterations = 0

        while iterations < max_iterations:
            if game.check_win(current_player):
                return 1 if current_player == 'Y' else -1
            elif game.check_draw():
                return 0
            current_player = 'R' if current_player == 'Y' else 'Y'
            iterations += 1

        # If the loop exceeds the maximum iterations, consider it a draw
        return 0

    def uct(self, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]
        if not legal_moves:
            return None

        results = {}
        c = math.sqrt(2)  # Exploration parameter

        for col in legal_moves:
            wins = 0
            total_simulations = 0
            for _ in range(simulations):
                new_game = ConnectFourGame()
                new_game.board = [row[:] for row in self.game.board]
                new_game.make_move(col, self.player)
                result = self.simulate(new_game)
                total_simulations += 1
                if result == 1:  # Yellow wins
                    wins += 1

            ni = total_simulations
            Ni = sum(results.values()) + ni
            if ni == 0:
                results[col] = float('inf')  # Setting to infinity to prioritize unexplored nodes
            else:
                results[col] = wins / ni + c * math.sqrt(math.log(Ni) / ni)

            if mode == 'Verbose':
                print(f"V{col + 1}: {results[col]:.2f}")

        if not results:
            return None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            for col, value in results.items():
                print(f"V{col + 1}: {value:.2f}")
            print(f"Best move: {best_move + 1}")
        elif mode == "Brief":
            print(f"Best move: {best_move + 1}")
        return best_move


    def simulate(self, game):
        current_player = self.player
        max_iterations = 1000  # Limit the number of iterations for the simulation
        iterations = 0

        while iterations < max_iterations:
            if game.check_win(current_player):
                return 1 if current_player == 'Y' else -1
            elif game.check_draw():
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
def play_game(algorithm1, algorithm2, simulations1, simulations2):
    game = ConnectFourGame()
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

def print_results(results):
    print("Results:")
    print("{:<40} {:<10} {:<10} {:<10}".format("Matchup", "Player 1", "Player 2", "Draws"))
    for matchup, (wins1, wins2, draws) in results.items():
        print("{:<40} {:<10} {:<10} {:<10}".format(matchup, wins1, wins2, draws))


def main():
    if len(sys.argv) == 4:
        filename = sys.argv[1]
        mode = sys.argv[2]
        simulations = int(sys.argv[3])
        algorithm, player, board = read_board(filename)
        game = ConnectFourGame()
        game.board = board
        algorithm_obj = ConnectFourAlgorithm(game, player)

        if algorithm == 'UR':
            move = algorithm_obj.ur()
            print(f"Move selected for UR: {move}")
        elif algorithm == 'PMCGS':
            move, _ = algorithm_obj.pmcgs(simulations, mode)
            if mode == "Verbose":
                print(f"Column {move + 1}: {_[move]:.2f}")
            else:
                print(f"Move selected for PMCGS: {move}")
        elif algorithm == 'UCT':
            move = algorithm_obj.uct(simulations, mode)
            print(f"Move selected for UCT: {move}")
        else:
            print("Unknown algorithm")
    else:
        results = run_tournament()
        print_results(results)

if __name__ == "__main__":
    main()
