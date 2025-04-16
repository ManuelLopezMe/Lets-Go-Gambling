import numpy as np
from player_choices import *
from metrics import *
from deck import *

# create initial deck
deck = Deck(num_decks=2)
deck.shuffle()

class PlayGame:
    def __init__(self):
        pass
    
    def play_round(self, wager, player_hand, dealer_hand):
            value = Hand(player_hand)
            player_value = value.compute_value()
            
            value = Hand(player_hand)
            dealer_value = value.compute_value()
            
            if player_value == 21:
                 print('Blackjack! You win!')
                 return wager
                        
            while player_value < 21:
                action = input('Hit, stand, double, or split?').lower()

                if action == 'hit':
                    hand = PlayHand(player_hand, None, self.deck)
                    player_value=hand.player_turn(action)
                    if player_value > 21:
                        print("You Busted")
                        return 0 - wager
                if action == 'stand':
                    hand = PlayHand(player_hand, None, self.deck)
                    player_value=hand.player_turn(action)
                
                if action == 'double':
                    hand=PlayHand(player_hand, None, self.deck)
                    player_value=hand.player_turn(action)
                    if player_value > 21:
                        print('You busted!')
                        return 0 - (2*wager)
                    else:
                        while dealer_value < 21 or dealer_value <= player_value:
                            dealer_value=hand.dealer_turn()
                        if player_value > dealer_value:
                            return 2*wager
                        elif player_value == dealer_value:
                            return 0
                        elif player_value < dealer_value:
                            return 0 - (2*wager)

                if action == 'split' and len(player_hand)==2 and player_hand[0] == player_hand[1]:
                    right_hand = [player_hand.pop()].append(deck.pop())
                    left_hand = player_hand.append(deck.pop())
                    
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
                            return 4*wager
                        elif left_action == 'double' and right_action != 'double':
                            return 3*wager
                        else:
                            return 2*wager
                    if (left_value > dealer_value and right_value == dealer_value) or (left_value == dealer_value and right_value > dealer_value):
                        if left_action == 'double' or right_action == 'double':
                            return 2*wager
                        else:
                            return wager
                    if (left_value > dealer_value and right_value < dealer_value) or (left_value < dealer_value and right_value > dealer_value):
                        if left_action == 'double' and right_action != 'double':
                            return wager
                        elif left_action == 'double' and right_action == 'double':
                            return 0
                        if left_action != 'double' and right_action == 'double':
                            return 0 - wager
                        else:
                            return 0
                    if left_value == dealer_value and right_value > dealer_value:
                        if right_action == 'double':
                            return wager
                        else:
                            return 0
                    if left_value < dealer_value and right_value < dealer_value:
                        if left_action == 'double' and right_action != 'double':
                            return wager
                        elif left_action == 'double' and right_action == 'double':
                            return 0
                        if left_action != 'double' and right_action == 'double':
                            return 0 - wager
                        else:
                            return 0
                    
                while dealer_value < 21:
                    x, dealer_value=hand.dealer_turn()
                    if x == 'done':
                        break
                if player_value > dealer_value:
                    if action == 'double':
                        return 2*wager
                    else:
                        return wager
                elif player_value == dealer_value:
                    return 0
                elif player_value < dealer_value:
                    if action == 'double':
                        return 0 - (wager)
                    else:
                        return 0 - (2*wager)
    
    def play_game(self, bankroll=100, num_rounds=10, num_decks = 2):
        rounds_played = 0
        deck = Deck(num_decks)
        deck.shuffle()
        total_deck_size = len(deck)
        while (rounds_played <= num_rounds) or bankroll > 0:
            wager = int(input('select wager amount'))
            player_hand = deck.deal_hand()
            dealer_hand = deck.deal_hand()
            if wager > self.bankroll:
                print("Not enough to wager, enter amount less than ${bankroll}".format(bankroll))
                wager = int(input('select wager amount'))
            bankroll += self.play_round(wager, player_hand, dealer_hand)
            rounds_played += 1
            if len(deck) <= total_deck_size*.2:
                deck.shuffle()

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

PlayGame()
                    
print("Thanks for playing!")