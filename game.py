import random
from card import Card
from player import Player

class Flip:
    def __init__(self, flipped_card, player_id, is_flip_by_owner):
        self.flipped_card = flipped_card
        self.player_id = player_id
        self.is_flip_by_owner = is_flip_by_owner

class Game:
    ROUND_LIMIT = 9

    def __init__(self):
        self.players = []
        self.deck = []
        self.discard_pile = []
        self.last_discarded = None
        self.locked_player = None

    def add_players(self, players):
        self.players = players

    def __str__(self):
        players_str = '\n'.join(f"Player {player.id}: {', '.join(str(card.id) for card in player.cards)}" 
                                for player in self.players)
        cards_str = '\n'.join(f"Card {card.id}: {card.rank} of {card.suit}" for card in self.deck)
        return f"Players:\n{players_str}\n\nCards:\n{cards_str}"
    
    def print_player_cards(self):
        for player in self.players:
            print(f"Player {player.id} has:")
            if player.cards:
                for card in player.cards:
                    print(f"  - Card {card.id}: {card.rank} of {card.suit}")
            else:
                print("  No cards.")
            print() 

    def generate_deck(self) -> list[Card]:
        cards = []
        for i in range(1, 11): 
            for j in range(1, 5):
                id = 4 * i + j
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
    
    def get_player_by_id(self, id) -> Player:
        return next((p for p in self.players if p.id == id), None)

    def get_player_card_index_by_card(self, card) -> int:
        player = self.get_player_by_id(card.owner)
        return next((i for i, c in enumerate(player.cards) if c.id == card.id), -1)

    def run_game(self):
        print(f"Starting the game with {len(self.players)} players and {len(self.deck)} cards.")
        
        # Shuffles player order and deck order
        self.shuffle()

        # Deals 4 cards to each player
        self.deal_cards()

        round = 0
        end_game = False

        # Main game loop
        while round < self.ROUND_LIMIT and not end_game:
            round += 1
            print(f"Round {round}:")

            for player in self.players:
                print(f"Player {player.id}'s turn:")
                print(player)

                if locked_player.id == player.id:
                    print(f"Game has ended.")
                    end_game = True
                    break
            
                # Player chooses whether to lock
                if self.use_lock(player):
                    locked_player = player.id
                    continue
                
                # Player chooses to draw a card from deck or discard pile
                drawn_card = self.draw_card(player)

                # Player chooses to either swap cards or play the drawn card
                played_card = self.play_drawn_card(player, drawn_card)
                
                self.last_discarded = played_card
                self.discard_pile.append(played_card)
                played_card.owner = Card.DISCARD_ID

                # All players choose to possibly request card flip, game decides on only one flip, or no flip if none requested
                flip = self.flip_card(played_card)
                if flip is not None:
                    self.last_discarded = played_card
                    self.discard_pile.append(played_card)
                    played_card.owner = Card.DISCARD_ID
                    if flip.is_flip_by_owner:
                        print(f"Player {flip.player_id} flipped their own card: {flip.flipped_card}.")
                        player.cards.pop(self.find) # HELP
                    else:
                        print(f"Player {flip.player_id} flipped another player's card: {flip.flipped_card}.")

                # Player uses card ability if drawn card is played immediately
                if played_card.id != drawn_card.id: 
                    continue
                self.use_card_ability(player, played_card)
    
    def shuffle(self) -> None:
        print("Shuffling players and cards...")
        random.shuffle(self.players)
        random.shuffle(self.deck)
        print(self.players)
        print(self.deck)

    def deal_cards(self) -> None:
        print("Dealing cards...")
        for player in self.players:
            player.cards.append(self.deck.pop())
            player.cards.append(self.deck.pop())
            # 2 cards are known to the player
            card = self.deck.pop()
            card.known = [player.id]
            player.cards.append(card)
            player.known_cards.append(card)
            card = self.deck.pop()
            card.known = [player.id]
            player.cards.append(card)
            player.known_cards.append(card)
        self.print_player_cards()
                    
    def use_lock(self, player) -> bool:
        lock = self.locked_player is not None and player.should_lock()
        if lock:
            print(f"Player {player.id} has locked.")
        return lock

    def draw_card(self, player) -> Card:
        drawn_card = self.deck.pop() if player.draw_from_deck(self.deck, self.discard_pile) else self.last_discarded
        print(f"Player {player.id} drew card {drawn_card} from {'deck' if player.draw_from_deck(self.deck, self.discard_pile) else 'discard pile'}.")
        return drawn_card

    def play_drawn_card(self, player, drawn_card) -> Card:
        swapped_card = player.swap_card(drawn_card)
        swapped_card_index = self.get_player_card_index_by_card(swapped_card)
        played_card = drawn_card if swapped_card_index == -1 else player.cards.pop(swapped_card_index)
        if swapped_card_index != -1:
            player.cards.append(drawn_card)
            print(f"Player {player.id} swapped card {played_card} with card {drawn_card}.")
            player.known_cards.append(drawn_card)
            drawn_card.known.add(player.id)
        else:
            print(f"Player {player.id} did not swap cards and played {drawn_card} immediately.")
        return played_card
    
    # We assume equal probability of any flip occuring, even if the player owns the card.
    # If 2 players request a flip of the same card, we first randomly choose who requests that card,
    #   then choose randomly between all other flips.
    # This is because irl, 2 people flipping the same card would have a lower individual chance of being first
    #  compared to a 3rd player flipping a different card.
    def flip_card(self, played_card) -> Flip:
        requested_flips = []
        for player in self.players:
            flipped_card = player.flip_card(played_card)
            if flipped_card is not None:
                # gets index in list if flip is already requested, -1 otherwise
                existing_index = next((i for i, flip in enumerate(requested_flips) if flip[0] == flipped_card.id), -1)
                is_current_flip_by_owner = player.id == flipped_card.owner
                if existing_index != -1:
                    # if flip already exists, randomly choose between existing flip and current flip
                    if random.randint(0,1) == 1: 
                        requested_flips.pop(existing_index)
                        requested_flips.append(Flip(flipped_card.id, player.id, is_current_flip_by_owner))
                else:
                    requested_flips.append(Flip(flipped_card.id, player.id, is_current_flip_by_owner))
                
        if len(requested_flips) == 0:
            print("No flips requested.")
            return None
        
        return random.choice(requested_flips)
    
    # We prioritize flips by the owner of the flipped card, same randomness as above
    def flip_card_prioritize_owner(self, played_card) -> Flip:
        requested_flips = []
        for player in self.players:
            flipped_card = player.flip_card(played_card)
            if flipped_card is not None:
                # gets index in list if flip is already requested, -1 otherwise
                existing_index = next((i for i, flip in enumerate(requested_flips) if flip[0] == flipped_card.id), -1)
                is_current_flip_by_owner = player.id == flipped_card.owner
                if existing_index != -1:
                    if requested_flips[existing_index].is_flip_by_owner:
                        continue
                    # if current flip is by owner, replace existing flip with current flip
                    elif is_current_flip_by_owner: 
                        requested_flips.pop(existing_index)
                        requested_flips.append(Flip(flipped_card.id, player.id, True))
                    # otherwise randomly choose between existing flip and current flip
                    elif random.randint(0,1) == 1: 
                        requested_flips.pop(existing_index)
                        requested_flips.append(Flip(flipped_card.id, player.id, is_current_flip_by_owner))
                else:
                    requested_flips.append(Flip(flipped_card.id, player.id, is_current_flip_by_owner))
                
        if len(requested_flips) == 0:
            print("No flips requested.")
            return None
        
        return random.choice(requested_flips)

    def use_card_ability(self, player, played_card):
        if played_card.rank == "7" or played_card.rank == "8":
            checked_card = player.check_own_card()
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)

        elif played_card.rank == "9" or played_card.rank == "10":
            checked_card = player.check_other_card()
            if checked_card is None:
                return
            player.known_cards.append(checked_card)
            checked_card.known.add(player.id)

    def reset_game(self) -> None:
        for p in self.players:
            p.reset()
        self.deck = self.generate_deck()
        self.discard_pile = []
        self.last_discarded = None
        self.locked_player = -1
        print("Game has been reset.")