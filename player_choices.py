class Choices:
    def __init__(self, hand: list, deck = list):
        self.hand = hand
        self.deck = deck

    def hit(self):
        self.hand.append(deal_card(self.deck))
    
    def stand(self):
        pass
