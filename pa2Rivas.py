import sys
import random
import math

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
            
        for col in legal_moves:
            new_game = ConnectFourGame()
            new_game.board = [row[:] for row in self.game.board]  # Create a copy of the board
            new_game.make_move(col, self.player)
            if new_game.check_win(self.player):
                return col
            
        return random.choice(legal_moves)

    def pmcgs(self, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]

        if simulations == 0:
            print("Error: Number of simulations cannot be zero.")
            return None, None

        results = {}
        for col in legal_moves:
            total_wins = 0
            for _ in range(simulations):
                new_game = ConnectFourGame()
                new_game.board = [row[:] for row in self.game.board]
                new_game.make_move(col, self.player)
                result = self.simulate(new_game)
                if result == 1:
                    total_wins += 1
            results[col] = total_wins / simulations
            if mode == 'Verbose':
                print(f"Column {col + 1}: {results[col]:.2f}")
                print(f"wi: {total_wins}")
                print(f"ni: {simulations}")
                print(f"Move selected: {col}")

        if not results:
            return None, None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            print("NODE ADDED" if col == best_move else "")
        elif mode == "Brief":
            print(f"Best move: {best_move + 1}, Win ratio: {results[best_move]:.2f}")
        return best_move, results



    def uct(self, simulations, mode):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]

        if simulations == 0:
            print("Error: Number of simulations cannot be zero.")
            return None

        results = {}
        for col in legal_moves:
            wins = 0
            for _ in range(simulations):
                new_game = ConnectFourGame()
                new_game.board = [row[:] for row in self.game.board]  # Create a copy of the board
                new_game.make_move(col, self.player)
                result = self.simulate(new_game)
                if result == 1:  # Yellow wins
                    wins += 1
            results[col] = wins / simulations + math.sqrt(2 * math.log(sum(results.values())) / results[col])

        if not results:
            return None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            for col, value in results.items():
                print(f"V{col + 1}: {value:.2f}")
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

def main():
    if len(sys.argv) != 4:
        print("Usage: python connect_four.py <input_file> <Verbose/Brief/None> <number_of_simulations>")

        sys.exit(1)

    filename = sys.argv[1]
    mode = sys.argv[2]
    simulations = int(sys.argv[3])
    print(filename)
    print(mode)
    print(simulations)
    algorithm, player, board = read_board(filename)
    print(algorithm)
    print(player)
    game = ConnectFourGame()
    game.board = board
    algorithm_obj = ConnectFourAlgorithm(game, player)
    print("Board:")
    for row in board:
        print(' '.join(row))

    if algorithm == 'UR':
        move = algorithm_obj.ur()
        print(f"Move selected: {move}")
    elif algorithm == 'PMCGS':
        move, results = algorithm_obj.pmcgs(simulations, mode)
        if mode == "Verbose":
            print(f"Column {move + 1}: {results[move]:.2f}")
        elif mode == "Brief":
            print(f"Best move: {move + 1}, Win ratio: {results[move]:.2f}")
        else:
            print(f"Move selected: {move}")
    elif algorithm == 'UCT':
        move = algorithm_obj.uct(simulations, mode)
    else:
        print("Unknown algorithm")

if __name__ == "__main__":
    main()
