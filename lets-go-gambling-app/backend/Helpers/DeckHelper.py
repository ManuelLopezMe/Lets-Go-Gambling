# File: /lets-go-gambling-app/lets-go-gambling-app/backend/Helpers/DeckHelper.py

class Deck:
    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.cards = self.create_deck()
        self.shuffle()

    def create_deck(self):
        # Create a standard deck of cards
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        return [(rank, suit) for suit in suits for rank in ranks] * self.num_decks

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def deal_hand(self):
        return [self.cards.pop(), self.cards.pop()]

    def game_deck(self):
        return self.cards

    def all_cards(self):
        return self.cards

    def remaining_cards(self):
        return len(self.cards)