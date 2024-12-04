import random
from game import Game, FlipRequest, Flip
from card import Card
from player import Player

class Game_DebugMode(Game):
    DEBUG_ROUND_LIMIT = 9
    DEFAULT_FLIP_REQUEST_WEIGHT = 1
    OWNER_FLIP_REQUEST_WEIGHT = 3
    DEFAULT_FLIP_WEIGHT = 1
    NON_CONTESTED_FLIP_WEIGHT = 2

    def __init__(self):
        super().__init__()
        
    def setup_game(self) -> None:
        self.deck = self.generate_deck()
        self.shuffle()
        self.deal_cards()
    
    def run_game(self):
        print("\n")
        print(f"Starting the game in debug mode with {len(self.players)} players and {len(self.deck)} cards in deck.")
        round = 0
        end_game = False

        # Main game loop
        while round < self.DEBUG_ROUND_LIMIT and not end_game:
            round += 1
            print("\n")
            print(f"Round {round}:")

            for player in self.players:
                print("Players summary:")
                self.print_players()

                print(f"Player {player.id}'s turn:")

                if self.locked_player is not None and self.locked_player.id == player.id:
                    print(f"Game has ended.")
                    end_game = True
                    break
            
                # Player chooses whether to lock
                if self.use_lock(player):
                    self.locked_player = player
                    continue
                
                # Player chooses to draw a card from deck or discard pile
                drawn_card = self.draw_card(player)

                # Player chooses to either swap cards or play the drawn card
                played_card = self.play_drawn_card(player, drawn_card)
                self.play_card_into_discard(played_card)

                # All players choose to possibly request card flip, game decides on only one flip or no flip if none requested
                flip = self.get_flip(played_card)
                if flip is not None:
                    print(f"Flip accepted: {flip}")
                    self.do_flip(flip)
                if self.is_player_w_no_cards():
                    print(f"Player {player.id} has no cards left, ending game.")
                    end_game = True
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
                    print(f"Player {player.id} has no cards left, ending game.")
                    end_game = True
            
            if round == self.DEBUG_ROUND_LIMIT:
                print(f"Game has reached max rounds.")
                end_game = True
        
        print("\n--------------------------------------------------------------")
        winner = self.calc_winner()
        print(f"Player {winner.id} wins in {round} rounds with {winner.calc_points()} points!")
        winner.total_wins += 1
        print("Point standings:")
        for player in self.players:
            player.total_points += player.calc_points()
            print(f"{player.id}: {player.calc_points()} points this game, {player.total_points} total.")
        print("--------------------------------------------------------------\n")
        self.total_rounds += round
    
    def shuffle(self):
        print("Shuffling players and cards...")
        super().shuffle()
        # print(self.players)
        # print(self.deck)
    
    def deal_cards(self):
        print("Dealing cards...")
        super().deal_cards()
        # self.print_player_cards()

    def deal_cards_all_known(self):
        print("Dealing cards with all known cards...")
        super().deal_cards_all_known()
        self.print_player_cards()

    def use_lock(self, player):
        lock = super().use_lock(player)
        if lock:
            print(f"Player {player.id} chooses to lock.")
        return lock

    def draw_card(self, player):
        draws_from_deck = player.s_draw_from_deck()
        drawn_card = super().draw_card(player)
        print(f"Player {player.id} draws card {drawn_card} from {"deck" if draws_from_deck else "discard pile"}.")
        return drawn_card
    
    def play_drawn_card(self, player, drawn_card):
        played_card = super().play_drawn_card(player, drawn_card)
        
        if played_card.id != drawn_card.id:
            print(f"Player {player.id} swapped own card {played_card} with drawn card {drawn_card}.")
        else:
            print(f"Player {player.id} did not swap cards and played {drawn_card} immediately.")
        return played_card
    
    def get_flip(self, played_card) -> Flip:
        flip_requests = {}

        # get all flip requests, and their probability to get chosen
        for player in self.players:
            requested_card = player.s_flip_card(played_card)
            if requested_card is None:
                continue
            flip_request_weight = self.OWNER_FLIP_REQUEST_WEIGHT if requested_card.owner.id == player.id else self.DEFAULT_FLIP_REQUEST_WEIGHT
            print(f"Player {player.id} requests to flip card {requested_card}, weight: {flip_request_weight}.")
            if requested_card in flip_requests:
                flip_requests[requested_card].players.append(player)
                flip_requests[requested_card].weights.append(flip_request_weight)
            else:
                flip_requests[requested_card] = FlipRequest([player],[flip_request_weight])

        if not flip_requests:
            print("No flips requested.")
            return None
        
        # resolve multiple flip requests on the same card
        flip_request_winners = []
        flip_request_winners_weights = []
        for card, flip_request in flip_requests.items():
            flip_request_winner = random.choices(flip_request.players, weights=flip_request.weights, k=1)[0]
            flip_request_winners.append(Flip(card, flip_request_winner))
            weight = self.NON_CONTESTED_FLIP_WEIGHT if len(flip_request.players) == 1 else self.DEFAULT_FLIP_WEIGHT
            flip_request_winners_weights.append(weight)
            print(f"Player {flip_request_winner.id} wins flip request for card {card}, weight: {weight}.")
        
        return random.choices(flip_request_winners, weights=flip_request_winners_weights, k=1)[0]
    
    def do_flip(self, flip):
        is_flip_by_owner = flip.flipped_card.owner.id == flip.player.id
        if is_flip_by_owner:
            print(f"Player {flip.player.id} flipped their own card: {flip.flipped_card}.")
            flip.player.remove_card(flip.flipped_card)
            self.play_card_into_discard(flip.flipped_card)
        else:
            print(f"Player {flip.player.id} flipped another player's card: {flip.flipped_card}.")
            other_player = flip.flipped_card.owner
            other_player.remove_card(flip.flipped_card)
            self.play_card_into_discard(flip.flipped_card)

            # player chooses which card to pass to other_player
            passed_card = flip.player.s_pass_card()
            if passed_card is None:
                return
            print(f"Player {flip.player.id} passes {passed_card} to other player: {other_player.id}.")
            flip.player.remove_card(passed_card)
            other_player.add_card(passed_card)

    def use_card_ability(self, player, played_card):
        if played_card.rank == "7" or played_card.rank == "8":
            checked_card = player.s_check_other_card()
            print(f"Player {player.id} checks other player's card: {checked_card}.")
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)

        elif played_card.rank == "9" or played_card.rank == "10":
            checked_card = player.s_check_own_card()
            print(f"Player {player.id} checks own card: {checked_card}.")
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)
        
        elif played_card.rank == "J" or played_card.rank == "Q":
            (card1, card2) = player.s_swap_cards()
            print(f"Player {player.id} swaps cards: {card1} with {card2}.")
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
            print(f"Player {player.id} checks card before swapping: {checked_card}.")
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)

            (card1, card2) = player.s_swap_cards()
            if card1 is None:
                return
            print(f"Player {player.id} swaps cards: {card1} with {card2}.")
            player1 = card1.owner
            player2 = card2.owner
            player1.remove_card(card1)
            player2.add_card(card1)
            player2.remove_card(card2)
            player1.add_card(card2)

    def reset_game(self):
        super().reset_game()
        print("Game has been reset.")
    