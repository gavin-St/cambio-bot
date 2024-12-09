import random
from card import Card
from player import Player

# IMPLEMENT CHECK Flip - DONE
# PERCENTAGE OF FLIP Warning - DONE
# BETTER BASIC STRATEGY - DONE
# STORE CARD HISTORY 
# OWN FLIP PRIORITY - DONE
# CHANGE SWAP NAMES TO REPLACE
# REMOVE ROUND LIMIT
# ROUND BY ROUND LOCK STRATEGY, NEEDS TO MAKE CARD POINTS UNKNOWN TAKE A PLAYER NOT SELF

class Flip:
    def __init__(self, flipped_card, player):
        self.flipped_card = flipped_card
        self.player = player
    def __str__(self):
        return f"Flip(card={self.flipped_card}, player={self.player})"

class FlipRequest:
    def __init__(self, players=[], weights=[]):
        self.players = players
        self.weights = weights

class Game:
    ROUND_LIMIT = 20
    DISCARD_PILE_OWNER = Player("DISCARD", None)
    DEFAULT_FLIP_REQUEST_WEIGHT = 1
    OWNER_FLIP_REQUEST_WEIGHT = 3
    DEFAULT_FLIP_WEIGHT = 1
    NON_CONTESTED_FLIP_WEIGHT = 2

    def __init__(self, round_limit=20):
        self.ROUND_LIMIT = round_limit
        self.cur_round = 0
        self.end_game = False
        self.players = []
        self.deck = []
        self.discard_pile = []
        self.total_rounds = 0
        self.locked_player = None

    def reset_game(self) -> None:
        for p in self.players:
            p.reset()
        self.cur_round = 0
        self.end_game = False
        self.deck = []
        self.discard_pile = []
        self.last_discarded = None
        self.locked_player = None

    def add_players(self, players):
        self.players = players

    def __str__(self):
        players_str = "\n".join(str(player) for player in self.players)
        cards_str = "\n".join(str(card) for card in self.deck)
        return f"Players:\n{players_str}\n\nDeck:\n{cards_str}"
    
    def print_player_cards(self):
        for player in self.players:
            print(f"Player {player.id} has:")
            if player.cards:
                for card in player.cards:
                    print(f"  - Card {card.id}: {card.rank} of {card.suit}")
            else:
                print("  No cards.")
            print() 

    def print_players(self):
        players_str = "\n".join(str(player) for player in self.players)
        print(f"{players_str}\n")

    def generate_deck(self) -> list[Card]:
        cards = []
        for i in range(1, 11): 
            for j in range(1, 5):
                id = 4 * (i-1) + j
                rank = "A" if i == 1 else str(i)
                suit = "red" if j > 2 else "black"
                points = i
                cards.append(Card(id, rank, suit, points))

        for j in range(1, 5):
                suit = "red" if j > 2 else "black"
                cards.append(Card(40 + j, "J", suit, 10))
                cards.append(Card(44 + j, "Q", suit, 10))
        
        cards.append(Card(49, "K", "black", 15))
        cards.append(Card(50, "K", "black", 15))
        cards.append(Card(51, "K", "red", -1))
        cards.append(Card(52, "K", "red", -1))
        cards.append(Card(53, "Jok", "black", 0))
        cards.append(Card(54, "Jok", "red", 0))

        return cards
    
    def setup_game(self) -> None:
        self.deck = self.generate_deck()
        self.shuffle()
        self.deal_cards()
    
    def shuffle(self) -> None:
        random.shuffle(self.players)
        random.shuffle(self.deck)

    def deal_cards(self) -> None:
        for player in self.players:
            player.add_card(self.deck.pop())
            player.add_card(self.deck.pop())
            # 2 cards are known to the player
            player.add_card(self.deck.pop(), True)
            player.add_card(self.deck.pop(), True)
    
    def deal_cards_all_known(self):
        for player in self.players:
            player.add_card_all_known(self.deck.pop(), self.players)
            player.add_card_all_known(self.deck.pop(), self.players)
            player.add_card_all_known(self.deck.pop(), self.players)
            player.add_card_all_known(self.deck.pop(), self.players)
    
    def reshuffle_discard(self):
        self.deck = self.discard_pile
        random.shuffle(self.deck)
        self.discard_pile = []

    def play_card_into_discard(self, card) -> None:
        self.discard_pile.append(card)
        card.owner = self.DISCARD_PILE_OWNER

    def run_game(self):
        # Main game loop
        while self.cur_round < self.ROUND_LIMIT and not self.end_game:
            self.cur_round += 1
            # print(f"Round {round}:")

            for player in self.players:
                # print(f"\nPlayer {player.id}'s turn:")
                # self.print_players()
                if self.locked_player is not None and self.locked_player.id == player.id:
                    self.end_game = True
                    break
            
                # Player chooses whether to lock
                if self.use_lock(player):
                    self.locked_player = player
                    continue

                if len(self.deck) == 0:
                    self.reshuffle_discard()
                
                # Player chooses to draw a card from deck or discard pile
                drawn_card = self.draw_card(player)

                # Player chooses to either swap cards or play the drawn card
                played_card = self.play_drawn_card(player, drawn_card)
                self.play_card_into_discard(played_card)

                # All players choose to possibly request card flip, game decides on only one flip or no flip if none requested
                flip = self.get_flip(played_card)
                if flip is not None:
                    self.do_flip(flip)
                if self.is_player_w_no_cards():
                    self.end_game = True
                    break

                # Player uses card ability if drawn card is played immediately
                if played_card.id != drawn_card.id: 
                    continue
                self.use_card_ability(player, played_card)

                # Possible new flip requested after checking a card
                if flip is None:
                    flip = self.get_flip(played_card)
                    if flip is not None:
                        self.do_flip(flip)
                if self.is_player_w_no_cards():
                    self.end_game = True
                    break

            if self.cur_round == self.ROUND_LIMIT:
                self.end_game = True
        
        print("\n--------------------------------------------------------------")
        winner = self.calc_winner()
        print(f"Player {winner.id} wins in {self.cur_round} rounds with {winner.calc_points()} points!")
        winner.total_wins += 1
        # print("Point standings:")
        for player in self.players:
            player.total_points += player.calc_points()
            # print(f"{player.id}: {player.calc_points()} points this game, {player.total_points} total.")
        print("--------------------------------------------------------------\n")
        self.total_rounds += self.cur_round
    
    def is_player_w_no_cards(self) -> bool:
        for player in self.players:
            if len(player.cards) == 0:
                return True
        return False
    
    def calc_winner(self) -> Player:
        for player in self.players:
            if len(player.cards) == 0:
                return player
        winner = min(self.players, key=lambda p: p.calc_points())
        return winner
                    
    def use_lock(self, player) -> bool:
        return self.locked_player is None and player.s_should_lock()

    def draw_card(self, player) -> Card:
        draws_from_deck = player.s_draw_from_deck()
        drawn_card = self.deck.pop() if draws_from_deck else self.discard_pile.pop()
        if not draws_from_deck:
            for player in self.players:
                drawn_card.known.add(player.id)
                player.known_cards.append(drawn_card)
        
        # print(f"Player {player.id} draws card {drawn_card} from {"deck" if draws_from_deck else "discard pile"}.")
        return drawn_card

    def play_drawn_card(self, player, drawn_card) -> Card:
        swapped_card = player.s_replace_card_with_drawn(drawn_card)
        played_card = drawn_card if swapped_card is None else swapped_card
        if swapped_card is not None:
            player.remove_card(swapped_card)
            player.add_card(drawn_card, True)
        return played_card
    
    def get_flip(self, played_card) -> Flip:
        flip_requests = {}

        # get all flip requests, and their probability to get chosen
        for player in self.players:
            requested_card = player.s_flip_card(played_card)
            if requested_card is None:
                continue
            flip_request_weight = self.OWNER_FLIP_REQUEST_WEIGHT if requested_card.owner.id == player.id else self.DEFAULT_FLIP_REQUEST_WEIGHT
            if requested_card in flip_requests:
                flip_requests[requested_card].players.append(player)
                flip_requests[requested_card].weights.append(flip_request_weight)
            else:
                flip_requests[requested_card] = FlipRequest([player],[flip_request_weight])

        if not flip_requests:
            return None
        
        # resolve multiple flip requests on the same card
        flip_request_winners = []
        flip_request_winners_weights = []
        for card, flip_request in flip_requests.items():
            flip_request_winner = random.choices(flip_request.players, weights=flip_request.weights, k=1)[0]
            flip_request_winners.append(Flip(card, flip_request_winner))
            weight = self.NON_CONTESTED_FLIP_WEIGHT if len(flip_request.players) == 1 else self.DEFAULT_FLIP_WEIGHT
            flip_request_winners_weights.append(weight)
        
        return random.choices(flip_request_winners, weights=flip_request_winners_weights, k=1)[0]
    
    def do_flip(self, flip):
        is_flip_by_owner = flip.flipped_card.owner.id == flip.player.id
        if is_flip_by_owner:
            flip.player.remove_card(flip.flipped_card)
            self.play_card_into_discard(flip.flipped_card)
        else:
            other_player = flip.flipped_card.owner
            other_player.remove_card(flip.flipped_card)
            self.play_card_into_discard(flip.flipped_card)

            # player chooses which card to pass to other_player
            passed_card = flip.player.s_pass_card()
            if passed_card is None:
                return
            flip.player.remove_card(passed_card)
            other_player.add_card(passed_card)

    def use_card_ability(self, player, played_card):
        if played_card.rank == "7" or played_card.rank == "8":
            checked_card = player.s_check_own_card()
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)

        elif played_card.rank == "9" or played_card.rank == "10":
            checked_card = player.s_check_other_card()
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)
        
        elif played_card.rank == "J" or played_card.rank == "Q":
            (card1, card2) = player.s_swap_cards()
            if card1 is None:
                return
            player1 = card1.owner
            player2 = card2.owner
            player1.remove_card(card1)
            player2.add_card(card1)
            player2.remove_card(card2)
            player1.add_card(card2)
            
        elif played_card.rank == "K":
            checked_card = player.s_check_card_before_swap()
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)

            (card1, card2) = player.s_swap_cards()
            if card1 is None:
                return
            player1 = card1.owner
            player2 = card2.owner
            player1.remove_card(card1)
            player2.add_card(card1)
            player2.remove_card(card2)
            player1.add_card(card2)
        