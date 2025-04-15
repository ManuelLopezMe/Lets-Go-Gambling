card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': [1,11]}

class Hand:
    def __init__(self, hand: list):
        self.hand = hand
        self.hand_value = 0
        self.aces = 0
    
    def compute_value(self):
        for card in self.hand:
            if card == 'A':
                aces += 1
                self.hand_value += 11
            else:
                self.hand_value += card_values[card]
        while self.hand_value > 21 and aces:
            self.hand_value -= 10
            aces -= 1
        return self.hand_value

class PlayersBankroll:
    def __init__(self, bank = 100, wager = 5):
        self.bank = bank
        self.wager = wager
    
class 