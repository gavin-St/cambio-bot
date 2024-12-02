# cambio-bot

Rules:
- The objective of Cambio is to end with the lowest combined sum of points in their cards
- 54 card deck:
    - Ace = 1 point, 2 = 2 points, ... 10 = 10 points
    - Jack, Queen = 10 points
    - Black King = 15 points
    - Red King = -1 points
    - Joker = 0 points
- At the start of the game, each player is dealt 4 cards and may look at 2 of them
- Play starts with the rest of the deck put in the middle, and each player getting a turn clockwise
- Each turn, the player draws card either from the top of discard pile, OR from the top of the deck
- After looking at the drawn card, the player may swap one of their cards with the drawn card OR play the drawn card directly
    - We call "play"-ing a card the act of putting a card face up in the middle after each turn
    - After "play"-ing a card in the middle, it goes to the top of the discard pile
- Card abilities activate upon drawing the card & playing immediately (swapping and playing NULLifies the ability):
    - 7/8 = check own card
    - 9/10 = check another player's card
    - J/Q = swap any 2 cards
    - K = check any card, then swap any 2 cards
- A player can "flip" one of their own cards and play it in the middle if it is the same as the previously played card
- A player can also flip another player's cards and play it in the middle if it is the same as the previously played card
    - We call such an action a "flip", DISTINCT from a "play"
    - Flipped cards also go to the top of the discard pile
- Only one flip is allowed per played card
    - I.e. only one player may flip a card every turn
- If a player erroneously flips a card that does not match the previously played card, the player must unflip the card and draw an extra card from the deck
- On any turn, a player may "lock" their cards, ending their turn without drawing a card and preventing any other player from interacting with their cards in the next round
    - Upon the next time it is this player's turn, the game will end
    - Only one player may "lock" per game

We assume perfect information / reaction time Cambio:
- every player remembers perfectly each move played and each card that is revealed
- every player remembers perfectly which cards are known by what players
- if 2 or more players can simultaneously put down cards in the middle, it is a 50/50 regarding who is able to successfully flip
- if a card wants to be flipped by 2 or more players, and it belongs to one of the players attempting to flip, the owner will flip first

States tracked:
- each player's cards
    - the number of "card slots" each player has
    - for each card, track which other players know the identity
- each player's information state of the game
- cards discarded
    - this means we can also track the probability of drawing a particular card next
- who has "lock"-ed and if the current round is after a "lock" turn

Decisions:
- which card to draw
- whether to swap or play immediately
- which card to check for 7/8
- which card to check for 9/10
- which cards to swap for J/Q
- which card to check and which cards to swap for K
- when to flip own cards
- when to flip others cards
- when to lock