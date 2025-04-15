class choices:
    def __init__(self, player_hand: list, deck = list):
        self.player_hand = player_hand
        self.deck = deck

    def hit(self):
        self.player_hand.append(deal_card(self.deck))
    
    def stand(self):
        return True
