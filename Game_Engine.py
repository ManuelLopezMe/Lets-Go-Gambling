import numpy as np
from metrics import *
from DeckHelper import *


class PlayGame:

    def __init__(self):
        self.active_deck = None  # Initialize in __init__
        self.rounds_played = 0  # Initialize here
        self.bankroll = 100  # Initialize here
        self.num_rounds = 10  # Initialize here

    def _deal_cards(self):
        """Deals initial cards to player and dealer."""
        player_hand = ['A', 'A'] ##self.active_deck.deal_hand()
        dealer_hand = self.active_deck.deal_hand()
        return player_hand, dealer_hand

    def _get_wager(self):
        """Gets wager from player, with validation."""
        while True:
            try:
                wager = int(input(f"Select wager amount (max ${self.bankroll}): $"))
                if 0 < wager <= self.bankroll:
                    return wager
                else:
                    print(
                        "Invalid wager. Please enter an amount greater than 0 and"
                        f" less than or equal to ${self.bankroll}."
                    )
            except ValueError:
                print("Invalid input. Please enter a valid integer for the wager.")

    def _check_reshuffle(self):
        """Reshuffles the deck if needed."""
        if len(self.active_deck.game_deck()) <= round(
            len(self.active_deck.all_cards()) * 0.2
        ):  # Use all_cards instead of shuffle()
            self.active_deck.shuffle()

    def play_round(self, wager, player_hand, dealer_hand):
        player_value = Hand(player_hand).compute_value()
        dealer_value = Hand(dealer_hand).compute_value()
        hand_results = []  # To store results of each hand

        if player_value == 21:
            print("Blackjack! You win!")
            return wager

        while True:  # Changed from 'while player_value < 21' to allow for split actions
            action = input("Hit, stand, double, or split? ").lower()

            if action == "hit":
                player_value = PlayHand(
                    player_hand, None, self.active_deck.game_deck()
                ).player_turn(action)
                if player_value > 21:
                    print("You Busted")
                    hand_results.append(-wager)  # Loss for this hand
                    break
            elif action == "stand":
                player_value = PlayHand(
                    player_hand, None, self.active_deck.game_deck()
                ).player_turn(action)
                break  # Exit loop on stand
            elif action == "double":
                player_value = PlayHand(
                    player_hand, None, self.active_deck.game_deck()
                ).player_turn(action)
                if player_value > 21:
                    print("You busted!")
                    hand_results.append(-2 * wager)  # Loss for this hand
                    break
                else:
                    dealer_value = PlayHand(
                        None, dealer_hand, self.active_deck.game_deck()
                    ).dealer_turn()
                    hand_results.append(self._determine_payout(player_value, dealer_value, wager, action))
                    break
            elif (
                action == "split"
                and len(player_hand) == 2
                and player_hand[0] == player_hand[1]
                and len(hand_results) < 4 # Limit to 4 hands max
            ):
                right_hand = [player_hand.pop()]
                right_hand.append(self.active_deck.game_deck().pop())
                print('Right hand: {right}'.format(right=right_hand))
                left_hand = player_hand
                left_hand.append(self.active_deck.game_deck().pop())
                print('Left hand: {left}'.format(left=left_hand))

                # Recursive calls for each hand after the split
                print("Playing your right hand first")
                hand_results.append(self.play_round(wager, right_hand, dealer_hand[:])) 
                print("Now playing your left hand: {left}".format(left=left_hand)) 
                hand_results.append(self.play_round(wager, left_hand, dealer_hand[:]))
                #break
            else:
                print("Invalid action. Please choose hit, stand, double, or split.")

        if not hand_results:  # If no split occurred
            dealer_value = PlayHand(
                None, dealer_hand, self.active_deck.game_deck()
            ).dealer_turn()
            hand_results.append(self._determine_payout(player_value, dealer_value, wager, action))

        return sum(hand_results)  # Sum up the results from all hands

    def _determine_payout(self, player_value, dealer_value, wager, action):
        """Helper function to determine payout."""

        if player_value > 21:
            return -wager if action != "double" else -2 * wager
        if dealer_value > 21:
            return wager if action != "double" else 2 * wager

        if player_value > dealer_value:
            return wager if action != "double" else 2 * wager
        elif player_value == dealer_value:
            return 0
        else:
            return -wager if action != "double" else -2 * wager

    def play_game(self, num_decks=2):  # Moved default args to __init__
        self.active_deck = Deck(num_decks)
        self.active_deck.shuffle()

        while self.rounds_played < self.num_rounds and self.bankroll > 0:
            wager = self._get_wager()
            player_hand, dealer_hand = self._deal_cards()

            print(
                "Your Hand {Player} \n Dealer Upcard: {dealer}".format(
                    Player=player_hand, dealer=dealer_hand[0]
                )
            )

            self.bankroll += self.play_round(wager, player_hand, dealer_hand)
            self.rounds_played += 1
            self._check_reshuffle()

        print(f"Game over! Final bankroll: ${self.bankroll}")


class PlayHand:

    def __init__(self, player_hand, dealer_hand, deck):
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck

    def player_turn(self, action):
        value = Hand(self.player_hand)

        if action in ("hit", "double"):  # Cleaned up the 'in' statement
            self.player_hand.append(self.deck.pop())
            player_value = value.compute_value()
            print(self.player_hand)
            return player_value
        elif action == "stand":
            player_value = value.compute_value()
            print(self.dealer_hand)
            return player_value
        else:
            return value.compute_value()

    def dealer_turn(self):
        dealer_value = Hand(self.dealer_hand).compute_value()
        print("Dealers Hand: {dealer}".format(dealer=self.dealer_hand))

        while dealer_value < 17:
            self.dealer_hand.append(self.deck.pop())
            dealer_value = Hand(self.dealer_hand).compute_value()  # Recalculate

        print("Final Dealers Hand: {dealer}".format(dealer=self.dealer_hand))
        return dealer_value

if __name__ == "__main__":
    PlayGame().play_game()
    print("Thanks for playing!")