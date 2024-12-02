class Player:
    def __init__(self, id):
        self.id = player_id
        self.cards = []
        self.known_cards = []

    # Returns true to draw from deck, false to draw from discard pile
    def draw_card(self) -> bool:
        pass

    # Returns card id to swap with, -1 if no swap
    def swap_card(self, card) -> int:
        pass

    # Returns an owned card id to check, -1 if no cards to check
    def check_own_card(self, card) -> int:
        pass

    # Returns a card id owned by another player to check, -1 if no cards to check
    def check_other_card(self, card) -> int:
        pass

    # Returns a tuple of card ids to swap, (-1, -1) if no cards to swap
    def swap_cards(self) -> (int, int):
        pass

    #Returns a tuple of card ids to check and swap, (-1, -1, -1) if no cards to check and swap
    def check_and_swap_cards(self) -> (int, int, int):
        pass

    # Returns a card id to flip, -1 if no flip
    def flip_card(self, card) -> int:
        pass

    def should_lock(self) -> bool:
        pass