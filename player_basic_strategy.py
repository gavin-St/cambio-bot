from player import Player

class Player_Swap_Out_Known_Cards_Not_Known_By_Owner(Player):
    def __init__(self, id, game):
        super().__init__(id, game)

    def s_swap_card_with_drawn(self, drawn_card):
        for card in self.cards:
            if self.id in card.known:
                continue
            if len(card.known) > 0:
                return card
        return super().s_swap_card_with_drawn(drawn_card)
    
class Player_Swap_Out_All_Known_Cards(Player):
    def __init__(self, id, game):
        super().__init__(id, game)

    def s_swap_card_with_drawn(self, drawn_card):
        for card in self.cards:
            if any([player.id != self.id for player in self.game.players]):
                return card
        return super().s_swap_card_with_drawn(drawn_card)
    
    
class Player_Swap_Out_Known_Cards_Greater_Than_n(Player):
    def __init__(self, id, game, n):
        super().__init__(id, game)
        self.n = n

    def s_swap_card_with_drawn(self, drawn_card):
        for card in self.cards:
            if any([player.id != self.id for player in self.game.players]) and self.get_card_value(card) > self.n:
                return card
        return super().s_swap_card_with_drawn(drawn_card)

class Player_Swap_Known_Cards(Player):
    def __init__(self, id, game):
        super().__init__(id, game)

    def s_swap_cards(self):
        cards =  super().s_swap_cards()
        if cards[0] is not None:
            return cards
        own_card = self.get_max_own_card()
        if own_card is None or self.get_card_value(own_card) < 4: 
            return (None, None)
        for player in self.game.players:
            for other_card in player.cards:
                return (own_card, other_card)

        return (None, None)
    
class Player_Check_Already_Known(Player_Swap_Out_Known_Cards_Greater_Than_n):
    def __init__(self, id, game, n):
        super().__init__(id, game, n)
        self.n = n

    def s_check_other_card(self):
        for player in self.game.players:
            for card in player.cards:
                if card.owner.id != self.id and self.id not in card.known and player.id in card.known:
                    return card
        return super().s_check_other_card()
    
class Player_Check_Not_Known(Player_Swap_Out_Known_Cards_Greater_Than_n):
    def __init__(self, id, game, n):
        super().__init__(id, game, n)
        self.n = n

    def s_check_other_card(self):
        for player in self.game.players:
            for card in player.cards:
                if card.owner.id != self.id and self.id not in card.known and player.id not in card.known:
                    return card
        return super().s_check_other_card()