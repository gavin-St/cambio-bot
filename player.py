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
    
    def get_card_index_by_card(self, card) -> int:
        return (i for i, c in enumerate(self.cards) if c.id == card.id)

    def remove_card(self, card):
        index = self.get_card_index_by_card(card)
        self.cards.pop(index)

    def add_card(self, card, known=False):
        self.cards.append(card)
        card.owner = self
        if known:
            self.known_cards.add(card)
            card.known.append(self)

    def __str__(self):
        card_values = ', '.join(str(c.rank) for c in self.cards) if self.cards else "No cards"
        card_ids = ', '.join(str(c.id) for c in self.cards) if self.cards else "No cards"
        known_card_ids = ', '.join(str(c.id) for c in self.known_cards) if self.known_cards else "No known cards"
        return (f"Player(ID={self.id}, Points={self.calc_points()}, "
                f"Card values=[{card_values}], Card ids=[{card_ids}], Known Cards=[{known_card_ids}])")
    
    def __repr__(self):
        return self.__str__()

## ----------- Override Strategy -----------

    # Returns true to draw from deck, false to draw from discard pile
    def s_draw_from_deck(self, deck, discard_pile) -> bool:
        pass

    # Returns a VALID card to swap with the drawn_card, None if no swap
    def s_swap_card(self, drawn_card) -> Card:
        pass

    # Returns a VALID owned card to check, None if no cards to check
    def s_check_own_card(self) -> Card:
        pass

    # Returns a VALID card id owned by another player to check, None if no cards to check
    def s_check_other_card(self) -> Card:
        pass

    # Returns a VALID card to check before swapping, None if no cards to check
    def s_check_card_before_swap(self) -> Card:
        pass

    # Returns a VALID tuple of card to swap, (None, None) if no cards to swap
    def s_swap_cards(self) -> (Card, Card):
        pass

    # Returns a VALID card to flip, None if no flip
    def s_flip_card(self, card) -> Card:
        pass

    # Returns a VALID card to pass after flipping another player's card, None if no card to pass
    def s_pass_card(self) -> Card:
        pass

    def s_should_lock(self) -> bool:
        pass