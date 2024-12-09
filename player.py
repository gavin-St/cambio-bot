from card import Card

class Player:
    def __init__(self, id, game):
        self.id = id
        self.game = game
        self.total_points = 0
        self.total_wins = 0
        self.cards = []
        self.known_cards = []
    
    def reset(self):
        self.cards = []
        self.known_cards = []
    
    def calc_points(self):
        sum = 0
        for c in self.cards:
            sum += c.points
        return sum
    
    def get_max_own_card(self):
        max_card = None
        for card in self.cards:
            if max_card is None or self.get_card_value(card) > max_card.points:
                max_card = card
        return max_card
    
    def get_min_other_card(self):
        min_card = None
        for player in self.game.players:
            for card in player.cards:
                if card.owner.id == "DISCARD" or card.owner.id == self.id:
                    continue
                if self.game.locked_player is not None and card.owner.id == self.game.locked_player.id:
                    continue
                if min_card is None or self.get_card_value(card) < min_card.points:
                    min_card = card
        return min_card
    
    def get_card_index_by_card(self, card) -> int:
        return next(i for i, c in enumerate(self.cards) if c.id == card.id)
    
    def get_known_cards_index_by_card(self, card) -> int:
        return next((i for i, c in enumerate(self.known_cards) if c.id == card.id), -1)

    def remove_card(self, card):
        cards_index = self.get_card_index_by_card(card)
        self.cards.pop(cards_index)
        known_cards_index = self.get_known_cards_index_by_card(card)
        if known_cards_index != -1:
            self.known_cards.pop(known_cards_index)

    def add_card(self, card, known=False):
        self.cards.append(card)
        card.owner = self
        if known:
            self.known_cards.append(card)
            card.known.add(self.id)
    
    def add_card_all_known(self, card, players):
        self.cards.append(card)
        card.owner = self
        for player in players:
            player.known_cards.append(card)
            card.known.add(player.id)

    def __str__(self):
        card_values = ', '.join(str(c.rank) for c in self.cards) if self.cards else "No cards"
        card_ids = ', '.join(str(c.id) for c in self.cards) if self.cards else "No cards"
        known_card_ids = ', '.join(str(c.id) for c in self.known_cards) if self.known_cards else "No known cards"
        return (f"Player(ID={self.id}, Points={self.calc_points()}, "
                f"Card values=[{card_values}], Card ids=[{card_ids}], Known Cards=[{known_card_ids}])")
    
    def __repr__(self):
        return self.__str__()

## ----------- Override Strategy -----------

    def get_card_value(self, card):
        if self.id in card.known:
            return card.points
        return card.likely_value

    def calc_points_unknown(self):
        sum = 0
        for c in self.cards:
            sum += self.get_card_value(c)
        return sum

    # Returns true to draw from deck, false to draw from discard pile
    def s_draw_from_deck(self) -> bool:
        if self.id == "EMMA": print(self.game.discard_pile)
        return not self.game.discard_pile or self.s_replace_card_with_drawn(self.game.discard_pile[-1]) is None or self.game.discard_pile[-1].points > 3

    # Returns a VALID card to swap with the drawn_card, None if no swap
    def s_replace_card_with_drawn(self, drawn_card) -> Card:
        for card in self.known_cards:
            if card.owner.id == self.id and self.get_card_value(card) > drawn_card.points:
                return card
        return None

    # Returns a VALID owned card to check, None if no cards to check
    def s_check_own_card(self) -> Card:
        for card in self.cards:
            if self.id not in card.known:
                return card
        return None

    # Returns a VALID card id owned by another player to check, None if no cards to check
    def s_check_other_card(self) -> Card:
        for player in self.game.players:
            for card in player.cards:
                if card.owner.id != self.id and self.id not in card.known:
                    return card
        return None

    # Returns a VALID card to check before swapping, None if no cards to check
    def s_check_card_before_swap(self) -> Card:
        for player in self.game.players:
            for card in player.cards:
                if self.id not in card.known:
                    return card
        return None

    # Returns a VALID tuple of card to swap, (None, None) if no cards to swap
    def s_swap_cards(self) -> (Card, Card):
        max_card = self.get_max_own_card()
        min_card = self.get_min_other_card()
        if max_card is not None and min_card is not None and min_card.points < max_card.points:
            return (max_card, min_card)
        return (None, None)

    # Returns a VALID card to flip, None if no flip
    def s_flip_card(self, card) -> Card:
        for known_card in self.known_cards:
            if known_card.owner is None or known_card.owner.id == "DISCARD":
                continue
            if known_card.owner.id != self.id and known_card.rank == card.rank:
                return known_card
        for known_card in self.known_cards:
            if known_card.points < 1:
                continue
            if known_card.owner is None or known_card.owner.id == "DISCARD":
                continue
            if known_card.owner.id == self.id and known_card.rank == card.rank and known_card.points > 0:
                return known_card
        return None

    # Returns a VALID card to pass after flipping another player's card, None if no card to pass
    def s_pass_card(self) -> Card:
        return self.get_max_own_card()

    def s_should_lock(self) -> bool:
        return self.calc_points_unknown() <= 6