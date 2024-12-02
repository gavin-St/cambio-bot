class Card:
    def __init__(self, id, rank, suit, player_id):
        self.id = id
        self.rank = rank
        self.suit = suit
        self.owner = player_id
        # self.known is a list of player_ids that know the card
        self.known = [player_id]

    def __str__(self):
        return f"{self.rank} of {self.suit}"