import sys
import random
import math

class ConnectFourGame:
    def __init__(self):
        self.board = [[' ' for _ in range(7)] for _ in range(6)]

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def is_legal_move(self, col):
        return self.board[0][col] == ' '

    def make_move(self, col, player):
        for row in range(5, -1, -1):
            if self.board[row][col] == ' ':
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
        return all(self.board[0][col] != ' ' for col in range(7))

class ConnectFourAlgorithm:
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def ur(self):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]
        if not legal_moves:
            return None
        return random.choice(legal_moves)

    def pmcgs(self, simulations):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]

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
            results[col] = wins / simulations

        if not results:
            return None

        best_move = max(results, key=results.get)
        if mode == "Verbose":
            for col, value in results.items():
                print(f"Column {col + 1}: {value:.2f}")
        return best_move

    def uct(self, simulations):
        legal_moves = [col for col in range(7) if self.game.is_legal_move(col)]

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
        return best_move

    def simulate(self, game):
        # Simulate a game until it ends
        players = ['R', 'Y']
        current_player = players.index(self.player)
        while True:
            for player in players:
                if game.check_win(player):
                    return 1 if player == 'Y' else -1
                elif game.check_draw():
                    return 0

def read_board(filename):
    with open(filename, 'r') as file:
        algorithm = file.readline().strip()
        player = file.readline().strip()
        board = [list(line.strip()) for _ in range(6)]
    return algorithm, player, board

def main():
    if len(sys.argv) != 4:
        print("Usage: python connect_four.py <input_file> <Verbose/Brief/None> <number_of_simulations>")
        sys.exit(1)

    filename = sys.argv[1]
    mode = sys.argv[2]
    simulations = int(sys.argv[3])

    algorithm, player, board = read_board(filename)
    game = ConnectFourGame()
    game.board = board
    algorithm = ConnectFourAlgorithm(game, player)

    if algorithm == 'UR':
        move = algorithm.ur()
    elif algorithm == 'PMCGS':
        move = algorithm.pmcgs(simulations)
    elif algorithm == 'UCT':
        move = algorithm.uct(simulations)

    if move is None:
        print("No legal moves available.")
    else:
        print("FINAL Move selected:", move + 1)

if __name__ == "__main__":
    main()
