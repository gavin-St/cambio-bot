class Game:
    def __init__(self, players, cards):
        self.players = players
        self.cards = cards

    def run_game(self, players, cards):
        print(f"Starting the game with {len(self.players)} players and {len(self.cards)} cards.")

        
    def reset_game(self):
        self.players = []
        self.cards = []
        print("Game has been reset.")