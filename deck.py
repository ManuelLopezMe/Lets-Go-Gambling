import numpy as np
suits = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4

class Deck:
    def __init__(self):
        self.deck = suits*4

    def shuffle(self):
        np.random.shuffle(self.deck)
    
    def deal_card(self):
        return self.deck.pop()
