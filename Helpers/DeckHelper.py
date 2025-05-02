import numpy as np

suits = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.shoe = suits*4*num_decks

    def shuffle(self):
        self.shoe = suits*4*self.num_decks
        np.random.shuffle(self.shoe)
    
    
    def deal_hand(self):
        return [self.shoe.pop(), self.shoe.pop()]
    
    def game_deck(self):
        return self.shoe
    
    def all_cards(self):
        total = suits*4*self.num_decks
        return total
