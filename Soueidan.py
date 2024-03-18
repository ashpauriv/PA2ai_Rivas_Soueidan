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
        self.board = [['0' for _ in range(7)] for _ in range(6)]

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def is_legal_move(self, col):
        return self.board[0][col] == '0'

    def make_move(self, col, player):
        for row in range(5, -1, -1):
            if self.board[row][col] == '0':
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
    
    def is_terminal_state(self):
        # Check for a win for either player
        if self.check_win('R'):
            print("Red wins.")
            return True
        elif self.check_win('Y'):
            print("Yellow wins.")
            return True
        # Check for a draw
        elif self.check_draw():
            print("It's a draw.")
            return True
        return False

    def check_draw(self):
        return all(self.board[0][col] != ' ' for col in range(7))

class ConnectFourAlgorithm:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.root = TreeNode()

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
        self.expand_node(self.root, simulations)

        if mode == "Verbose":
            for child in self.root.children:
                print(f"Column {child.move + 1}: {child.wi / child.ni:.2f}")

        best_move = max(self.root.children, key=lambda x: x.wi / x.ni)
        return best_move.move

    def uct(self, simulations, mode):
        self.expand_node(self.root, simulations)

        if mode == "Verbose":
            for child in self.root.children:
                print(f"Column {child.move + 1}: {child.wi / child.ni + math.sqrt(2 * math.log(self.root.ni) / child.ni):.2f}")

        best_move = max(self.root.children, key=lambda x: x.wi / x.ni + math.sqrt(2 * math.log(self.root.ni) / x.ni))
        return best_move.move

    def expand_node(self, node, simulations):
        legal_moves = [col for col in range(7) if node.game.is_legal_move(col)]

        for col in legal_moves:
            child_game = ConnectFourGame()
            child_game.board = [row[:] for row in node.game.board]  # Create a copy of the board
            child_game.make_move(col, self.player)

            child_node = TreeNode(game=child_game, parent=node, move=col)
            node.children.append(child_node)

            for _ in range(simulations):
                result = self.simulate(child_game)
                child_node.ni += 1
                if result == 1:  # Yellow wins
                    child_node.wi += 1

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
    with open(filename, 'r', encoding='utf-8-sig') as file:  # Specify the encoding to handle BOM
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
    print("filename:", filename)
    print("mode:", mode)
    print("simulations:", simulations)
    algorithm, player, board = read_board(filename)
    print("Algorithm from file:", repr(algorithm))
    print("algorithm:", algorithm)
    print("player:", player)
    game = ConnectFourGame()
    game.board = board
    algorithm_obj = ConnectFourAlgorithm(game, player)
    print("Board:")
    for row in board:
        print(' '.join(row))

    if algorithm == 'UR':
        move = algorithm_obj.ur()
        print(f"Move selected for UR: {move}")
    elif algorithm == 'PMCGS':
        move, results = algorithm_obj.pmcgs(simulations, mode)
        if mode == "Verbose":
            print(f"Column {move + 1}: {results[move]:.2f}")
        else:
            print(f"Move selected for PMCGS: {move}")
    elif algorithm == 'UCT':
        move = algorithm_obj.uct(simulations, mode)
        print(f"Move selected for UCT: {move}")
    else:
        print("Unknown algorithm")

    if game.is_terminal_state():
        print("Game over.")
        sys.exit(0)

if __name__ == "__main__":
    main()
