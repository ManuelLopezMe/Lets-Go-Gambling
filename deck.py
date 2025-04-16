import numpy as np
from player_choices import *
suits = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4

class Deck:
    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.deck = suits*4*num_decks

    def shuffle(self):
        np.random.shuffle(self.deck)
    
    def deal_card(self):
        return self.deck.pop()
    
    def deal_hand(self):
        return [self.deck.pop(), self.deck.pop()]
