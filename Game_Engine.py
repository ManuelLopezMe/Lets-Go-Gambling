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

        # Use a queue to manage hands (iterative approach)
        hands_queue = [(player_hand, wager)]
        while hands_queue:
            current_hand, current_wager = hands_queue.pop(0)
            player_value = Hand(current_hand).compute_value()

            while True:
                action = input(f"Hit, stand, double, or split? ({current_hand}): ").lower()

                if action == "hit":
                    player_value = PlayHand(
                        current_hand, None, self.active_deck.game_deck()
                    ).player_turn(action)
                    if player_value > 21:
                        print(f"You busted with {current_hand}!")
                        hand_results.append(-current_wager)
                        break
                elif action == "stand":
                    print(f"Standing with {current_hand}.")
                    hand_results.append(0)  # No win/loss for standing
                    break
                elif action == "double":
                    current_wager *= 2
                    player_value = PlayHand(
                        current_hand, None, self.active_deck.game_deck()
                    ).player_turn(action)
                    if player_value > 21:
                        print(f"You busted with {current_hand}!")
                        hand_results.append(-current_wager)
                    else:
                        print(f"Standing with {current_hand}.")
                    break
                elif (
                    action == "split"
                    and len(current_hand) == 2
                    and current_hand[0] == current_hand[1]
                    and len(hand_results) + len(hands_queue) < 4  # Limit to 4 hands max
                ):
                    right_hand = [current_hand.pop()]
                    right_hand.append(self.active_deck.game_deck().pop())
                    left_hand = current_hand
                    left_hand.append(self.active_deck.game_deck().pop())
                    print(f"Right hand: {right_hand}")
                    print(f"Left hand: {left_hand}")

                    # Add split hands to the queue
                    hands_queue.append((right_hand, current_wager))
                    hands_queue.append((left_hand, current_wager))
                    break
                else:
                    print("Invalid action. Please choose hit, stand, double, or split.")

        # Process dealer's hand once after all player hands are resolved
        dealer_value = PlayHand(None, dealer_hand, self.active_deck.game_deck()).dealer_turn()

        # Calculate payouts for all hands
        payouts = []  # Temporary list to store payouts
        for current_hand, current_wager in hands_queue:
            player_value = Hand(current_hand).compute_value()
            payouts.append(self._determine_payout(player_value, dealer_value, current_wager, "stand"))

        return sum(hand_results + payouts)

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