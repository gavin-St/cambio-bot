from card import Card

class Player:
    def __init__(self, id, game):
        self.id = id
        self.game = game
        self.cards = []
        self.known_cards = set()
    
    def reset(self):
        self.cards = []
        self.known_cards = []
    
    def calc_points(self):
        sum = 0
        for c in self.cards:
            sum += c.points
        return sum
    
    def __str__(self):
        card_ids = ', '.join(str(c.id) for c in self.cards) if self.cards else "No cards"
        known_card_ids = ', '.join(str(c.id) for c in self.known_cards) if self.known_cards else "No known cards"
        return (f"Player(ID={self.id}, Points={self.calc_points()}, "
                f"Cards=[{card_ids}], Known Cards=[{known_card_ids}])")
    
    def __repr__(self):
        return self.__str__()

## ----------- Override Strategy -----------

    # Returns true to draw from deck, false to draw from discard pile
    def draw_from_deck(self, deck, discard_pile) -> bool:
        pass

    # Returns a VALID card to swap with the drawn_card, -1 if no swap
    def swap_card(self, drawn_card) -> Card:
        pass

    # Returns a VALID owned card to check, None if no cards to check
    def check_own_card(self) -> Card:
        pass

    # Returns a VALID card id owned by another player to check, -1 if no cards to check
    def check_other_card(self) -> Card:
        pass

    def check_card_before_swap(self) -> Card:
        pass

    # Returns a VALID tuple of card to swap, (-1, -1) if no cards to swap
    def swap_cards(self) -> (Card, Card):
        pass

    # Returns a VALID card to flip, -1 if no flip
    def flip_card(self, card) -> Card:
        pass

    # Returns a VALID card to pass after flipping another player's card
    def pass_card(self) -> Card:
        pass

    def should_lock(self) -> bool:
        pass