class Card:
    def __init__(self, id, rank, suit, points):
        self.id = id
        self.rank = rank
        self.suit = suit
        self.points = points
        self.owner = None
        # self.known is a list of player ids that know the card
        self.known = set()

    def __str__(self):
        owner_str = f"{self.owner.id}" if self.owner is not None else "No owner"
        known_str = ', '.join(map(str, self.known))
        return (f"Card(ID={self.id}, Rank={self.rank}, Suit={self.suit}, "
                f"Points={self.points}, Owner={owner_str}, Known by: [{known_str}])")

    def __repr__(self):
        return self.__str__()