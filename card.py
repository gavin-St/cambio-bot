class Card:
    DISCARD_ID = "DISCARD"

    def __init__(self, id, rank, suit, points, player_id=-1):
        self.id = id
        self.rank = rank
        self.suit = suit
        self.points = points
        self.owner = player_id
        # self.known is a list of player_ids that know the card
        self.known = [player_id]

    def __str__(self):
        owner_str = f"Player {self.owner}" if self.owner != -1 else "No owner"
        known_str = ', '.join(map(str, self.known))
        return (f"Card(ID={self.id}, Rank={self.rank}, Suit={self.suit}, "
                f"Points={self.points}, Owner={owner_str}, Known by: [{known_str}])")

    def __repr__(self):
        return self.__str__()