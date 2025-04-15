import numpy as np
from player_choices import *
from metrics import *
from deck import *

# create initial deck
deck = Deck(num_decks=2)
deck.shuffle()

class PlayRound:
    def __init__(self, player_hand, dealer_hand, deck, wager, num):
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck
        self.wager = wager
        self.num = num
    
    def play_round(self):
            print("Round {num}".format(num=self.num))
            value = Hand(self.player_hand)
            player_value = value.compute_value()
            
            value = Hand(self.dealer_hand)
            dealer_value = value.compute_value()
            
            if player_value == 21:
                 print('Blackjack! You win!')
                 return self.wager
                        
            while player_value < 21:
                action = input('Hit, stand, double, or split?').lower()

                if action == 'hit':
                    hand = PlayHand(self.player_hand, None, self.deck)
                    player_value=hand.player_turn(action)
                    if player_value > 21:
                        print("You Busted")
                        return 0 - self.wager
                if action == 'stand':
                    hand = PlayHand(self.player_hand, None, self.deck)
                    player_value=hand.player_turn(action)
                
                if action == 'double':
                    hand=PlayHand(self.player_hand, None, self.deck)
                    player_value=hand.player_turn(action)
                    if player_value > 21:
                        print('You busted!')
                        return 0 - (2*self.wager)
                    else:
                        while dealer_value < 21 or dealer_value <= player_value:
                            dealer_value=hand.dealer_turn()
                        if player_value > dealer_value:
                            return 2*self.wager
                        elif player_value == dealer_value:
                            return 0
                        elif player_value < dealer_value:
                            return 0 - (2*self.wager)

                if action == 'split' and len(self.player_hand)==2 and self.player_hand[0] == self.player_hand[1]:
                    right_hand = [self.player_hand.pop()].append(deck.pop())
                    left_hand = self.player_hand.append(deck.pop())
                    
                    right_value = Hand(right_hand).compute_value()
                    left_value = Hand(left_hand).compute_value()

                    #play right hand first

                    right_action = None
                    left_action = None
                    while right_value <= 21: 
                        right_action = input('Hit, stand, or double?').lower()
                        if right_action == 'double':
                            right = PlayHand(player_hand=right_hand, None, self.deck)
                            right_value = right.player_turn(action)
                            break
                        if right_action == 'hit':
                            right = PlayHand(player_hand=right_hand, None, self.deck)
                            right_value=right.player_turn(action)
                        if right_action == 'stand':
                            right = PlayHand(player_hand=right_hand, None, self.deck)
                            right_value=right.player_turn(action)
                            break
                    

                    while left_value <= 21:
                        left_action = input('Hit, stand, or double?').lower()
                        if left_action == 'double':
                            left = PlayHand(left_hand=right_hand, None, self.deck)
                            left_value = right.player_turn(action)
                            break
                        if left_action == 'hit':
                            left = PlayHand(left_hand=right_hand, None, self.deck)
                            left_value=left.player_turn(action)
                        if left_action == 'stand':
                            left = PlayHand(left_hand=right_hand, None, self.deck)
                            left_value=left.player_turn(action)
                            break
                    while dealer_value < 21:
                        x, dealer_value=hand.dealer_turn()
                        if x == 'done':
                            break
                    if left_value > dealer_value and right_value > dealer_value:
                        if left_action == 'double' and right_action == 'double':
                            return 4*self.wager
                        elif left_action == 'double' and right_action != 'double':
                            return 3*self.wager
                        else:
                            return 2*self.wager
                    if (left_value > dealer_value and right_value == dealer_value) or (left_value == dealer_value and right_value > dealer_value):
                        if left_action == 'double' or right_action == 'double':
                            return 2*self.wager
                        else:
                            return self.wager
                    if (left_value > dealer_value and right_value < dealer_value) or (left_value < dealer_value and right_value > dealer_value):
                        if left_action == 'double' and right_action != 'double':
                            return self.wager
                        elif left_action == 'double' and right_action == 'double':
                            return 0
                        if left_action != 'double' and right_action == 'double':
                            return 0 - self.wager
                        else:
                            return 0
                    if left_value == dealer_value and right_value > dealer_value:
                        if right_action == 'double':
                            return self.wager
                        else:
                            return 0
                    if left_value < dealer_value and right_value < dealer_value:
                        if left_action == 'double' and right_action != 'double':
                            return self.wager
                        elif left_action == 'double' and right_action == 'double':
                            return 0
                        if left_action != 'double' and right_action == 'double':
                            return 0 - self.wager
                        else:
                            return 0
                    
                while dealer_value < 21:
                    x, dealer_value=hand.dealer_turn()
                    if x == 'done':
                        break
                if player_value > dealer_value:
                    if action == 'double':
                        return 2*self.wager
                    else:
                        return self.wager
                elif player_value == dealer_value:
                    return 0
                elif player_value < dealer_value:
                    if action == 'double':
                        return 0 - (self.wager)
                    else:
                        return 0 - (2*self.wager)
                


class PlayHand:
    def __init__(self, player_hand, dealer_hand, deck):
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck


    def player_turn(self, action):
        actions = Choices(self.player_hand)
        value = Hand(self.player_hand)
        
        if action == 'hit':
            actions.hit()
            player_value = value.compute_value()
            return player_value
        elif action == 'stand':
            player_value = value.compute_value()
            return player_value
        elif action == 'double':
            actions.hit()
            player_value = value.compute_value()
            if player_value > 21:
                print("You busted!")
                return player_value
            else:
                return player_value
       
    def dealer_turn(self):
        actions = Choices(self.dealer_hand)
        dealer_value = Hand(self.dealer_hand).compute_value()

        if dealer_value >= 17:
            actions.stand()
            return 'done', dealer_value
        if dealer_value < 17:
            actions.hit()
            dealer_value
            if dealer_value > 21:
                "Dealer busted!"
                return 'done', dealer_value

                  
                    
print("Thanks for playing!")