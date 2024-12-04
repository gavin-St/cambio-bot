import random
from game import Game, Flip
from card import Card
from player import Player

class Game_DebugMode(Game):
    DEBUG_ROUND_LIMIT = 9

    def __init__(self):
        super().__init__()
    
    def run_game(self):
        print("\n\n")
        print(f"Starting the game in debug mode with {len(self.players)} players and {len(self.deck)} cards in deck.")
        round = 0
        end_game = False

        # Main game loop
        while round < self.DEBUG_ROUND_LIMIT and not end_game:
            round += 1
            print("\n")
            print(f"Round {round}:")

            for player in self.players:
                print("Player standings:")
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
                if played_card is None:
                    print("No card played?")
                    continue
                self.play_card_into_discard(played_card)

                # All players choose to possibly request card flip, game decides on only one flip or no flip if none requested
                flip = self.flip_card(played_card)
                if flip is not None:
                    print(f"Flip accepted: {flip}")
                    self.do_flip(flip)

                # Player uses card ability if drawn card is played immediately
                if played_card.id != drawn_card.id: 
                    continue
                self.use_card_ability(player, played_card)

                
        
        for player in self.players:
            print(f"Player {player.id} has {player.calc_points()} points.")

    def shuffle(self):
        print("Shuffling players and cards...")
        super().shuffle()
        # print(self.players)
        # print(self.deck)
    
    def deal_cards(self):
        print("Dealing cards...")
        super().deal_cards()
        # self.print_player_cards()

    def use_lock(self, player):
        lock = super().use_lock(player)
        if lock:
            print(f"Player {player.id} chooses to lock.")
        return lock

    def draw_card(self, player):
        drawn_card = super().draw_card(player)
        print(f"Player {player.id} draws card {drawn_card} from {"deck" if player.s_draw_from_deck() else "discard pile"}.")
        return drawn_card
    
    def play_drawn_card(self, player, drawn_card):
        played_card = super().play_drawn_card(player, drawn_card)
        if played_card is None:
            return None
        
        if played_card.id != drawn_card.id:
            print(f"Player {player.id} swapped own card {played_card} with drawn card {drawn_card}.")
        else:
            print(f"Player {player.id} did not swap cards and played {drawn_card} immediately.")
        return played_card
    
    def flip_card(self, played_card) -> Flip:
        requested_flips = []
        for player in self.players:
            flipped_card = player.s_flip_card(played_card)
            if flipped_card is not None:
                print(f"Player {player.id} requests to flip card {flipped_card}.")
                # gets index in list if flip is already requested, -1 otherwise
                existing_index = next((i for i, flip in enumerate(requested_flips) if flip.flipped_card.id == flipped_card.id), -1)
                is_current_flip_by_owner = player.id == flipped_card.owner.id
                if existing_index != -1:
                    # if flip already exists, randomly choose between existing flip and current flip
                    if random.randint(0,1) == 1: 
                        print(f"Card is already requested, player {player.id} wins flip request.")
                        requested_flips.pop(existing_index)
                        requested_flips.append(Flip(flipped_card, player.id, is_current_flip_by_owner))
                    else:
                        print(f"Card is already requested, player {player.id} loses flip request.")
                else:
                    print(f"Card is not requested yet, player {player.id} makes flip request.")
                    requested_flips.append(Flip(flipped_card, player.id, is_current_flip_by_owner))
                
        if len(requested_flips) == 0:
            print("No flips requested.")
            return None
        
        return random.choice(requested_flips)
    
    def flip_card_prioritize_owner(self, played_card) -> Flip:
        requested_flips = []
        for player in self.players:
            flipped_card = player.s_flip_card(played_card)
            if flipped_card is not None:
                print(f"Player {player.id} requests to flip card {flipped_card}.")
                existing_index = next((i for i, flip in enumerate(requested_flips) if flip.flipped_card.id == flipped_card.id), -1)
                is_current_flip_by_owner = player.id == flipped_card.owner.id
                if existing_index != -1:
                    if requested_flips[existing_index].is_flip_by_owner:
                        print(f"Card is already requested by owner, overrides new flip request.")
                        continue
                    # if current flip is by owner, replace existing flip with current flip
                    elif is_current_flip_by_owner:
                        print(f"Card is already requested, player {player.id} is the owner so overrides flip request.")
                        requested_flips.pop(existing_index)
                        requested_flips.append(Flip(flipped_card, player.id, True))
                    # otherwise randomly choose between existing flip and current flip
                    elif random.randint(0,1) == 1:
                        print(f"Card is already requested, both not owner, player {player.id} wins flip request.")
                        requested_flips.pop(existing_index)
                        requested_flips.append(Flip(flipped_card, player.id, is_current_flip_by_owner))
                else:
                    print(f"Card is not requested yet, player {player.id} makes flip request.")
                    requested_flips.append(Flip(flipped_card, player.id, is_current_flip_by_owner))
                
        if len(requested_flips) == 0:
            return None
        
        return random.choice(requested_flips)
    
    def do_flip(self, flip):
        player = self.get_player_by_id(flip.player_id)
        if flip.is_flip_by_owner:
            print(f"Player {flip.player_id} flipped their own card: {flip.flipped_card}.")
            player.remove_card(flip.flipped_card)
            self.play_card_into_discard(flip.flipped_card)
        else:
            print(f"Player {flip.player_id} flipped another player's card: {flip.flipped_card}.")
            other_player = flip.flipped_card.owner
            other_player.remove_card(flip.flipped_card)
            self.play_card_into_discard(flip.flipped_card)

            # player chooses which card to pass to other_player
            passed_card = player.s_pass_card()
            print(f"Player {flip.player_id} passes {passed_card} to other player: {other_player.id}.")
            player.remove_card(passed_card)
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
            self.print_player_cards()
    