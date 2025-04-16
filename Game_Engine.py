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
        player_hand = self.active_deck.deal_hand()
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

    def play_round(self, wager, player_hand, dealer_hand):  # Removed deck argument
        player_value = Hand(player_hand).compute_value()  # Calculate player value

        dealer_value = Hand(dealer_hand).compute_value()  # Calculate dealer value

        if player_value == 21:
            print("Blackjack! You win!")
            return wager

        while player_value < 21:
            action = input("Hit, stand, double, or split? ").lower()

            if action == "hit":
                player_value = PlayHand(
                    player_hand, None, self.active_deck.game_deck()
                ).player_turn(
                    action
                )  # Pass game_deck()
                if player_value > 21:
                    print("You Busted")
                    return -wager  # Use negative for loss
            elif action == "stand":
                player_value = PlayHand(
                    player_hand, None, self.active_deck.game_deck()
                ).player_turn(
                    action
                )  # Pass game_deck()
                break  # Exit loop on stand
            elif action == "double":
                player_value = PlayHand(
                    player_hand, None, self.active_deck.game_deck()
                ).player_turn(
                    action
                )  # Pass game_deck()
                if player_value > 21:
                    print("You busted!")
                    return -2 * wager
                else:  # double down only allows one hit
                    dealer_value = PlayHand(
                        None, dealer_hand, self.active_deck.game_deck()
                    ).dealer_turn()  # Pass game_deck()

                    if player_value > dealer_value:
                        return 2 * wager
                    elif player_value == dealer_value:
                        return 0
                    else:
                        return -2 * wager
            elif (
                action == "split"
                and len(player_hand) == 2
                and player_hand[0] == player_hand[1]
            ):
                right_hand = [player_hand.pop()]
                right_hand.append(self.active_deck.game_deck().pop())  # Pass game_deck()
                left_hand = player_hand
                left_hand.append(self.active_deck.game_deck().pop())  # Pass game_deck()

                right_value = Hand(right_hand).compute_value()
                left_value = Hand(left_hand).compute_value()

                # play right hand first
                right_action = None
                left_action = None
                while right_value <= 21:
                    right_action = input("Hit, stand, or double? ").lower()

                    if right_action == "double":
                        right_value = PlayHand(
                            player_hand=right_hand,
                            dealer_hand=None,
                            deck=self.active_deck.game_deck(),
                        ).player_turn(
                            right_action
                        )  # Pass game_deck()
                        break
                    elif right_action == "hit":
                        right_value = PlayHand(
                            player_hand=right_hand,
                            dealer_hand=None,
                            deck=self.active_deck.game_deck(),
                        ).player_turn(
                            right_action
                        )  # Pass game_deck()
                    elif right_action == "stand":
                        right_value = PlayHand(
                            player_hand=right_hand,
                            dealer_hand=None,
                            deck=self.active_deck.game_deck(),
                        ).player_turn(
                            right_action
                        )  # Pass game_deck()
                        break

                # play left hand
                while left_value <= 21:
                    left_action = input("Hit, stand, or double? ").lower()

                    if left_action == "double":
                        left_value = PlayHand(
                            player_hand=left_hand,
                            dealer_hand=None,
                            deck=self.active_deck.game_deck(),
                        ).player_turn(
                            left_action
                        )  # Pass game_deck()
                        break
                    elif left_action == "hit":
                        left_value = PlayHand(
                            player_hand=left_hand,
                            dealer_hand=None,
                            deck=self.active_deck.game_deck(),
                        ).player_turn(
                            left_action
                        )  # Pass game_deck()
                    elif left_action == "stand":
                        left_value = PlayHand(
                            player_hand=left_hand,
                            dealer_hand=None,
                            deck=self.active_deck.game_deck(),
                        ).player_turn(
                            left_action
                        )  # Pass game_deck()
                        break

                dealer_value = PlayHand(
                    None, dealer_hand, self.active_deck.game_deck()
                ).dealer_turn()  # Pass game_deck()

                # Possible Payouts
                if left_value > dealer_value and right_value > dealer_value:
                    if left_action == "double" and right_action == "double":
                        return 4 * wager
                    elif left_action == "double" and right_action != "double":
                        return 3 * wager
                    else:
                        return 2 * wager
                elif (
                    left_value > dealer_value and right_value == dealer_value
                ) or (left_value == dealer_value and right_value > dealer_value):
                    if left_action == "double" or right_action == "double":
                        return 2 * wager
                    else:
                        return wager
                elif (
                    left_value > dealer_value and right_value < dealer_value
                ) or (left_value < dealer_value and right_value > dealer_value):
                    if left_action == "double" and right_action != "double":
                        return wager
                    elif left_action == "double" and right_action == "double":
                        return 0
                    elif left_action != "double" and right_action == "double":
                        return -wager
                    else:
                        return 0
                elif left_value == dealer_value and right_value > dealer_value:
                    if right_action == "double":
                        return wager
                    else:
                        return 0
                elif left_value < dealer_value and right_value < dealer_value:
                    if left_action == "double" and right_action != "double":
                        return wager
                    elif left_action == "double" and right_action == "double":
                        return 0
                    elif left_action != "double" and right_action == "double":
                        return -wager
                    else:
                        return 0
            else:
                print("Invalid action. Please choose hit, stand, double, or split.")

        dealer_value = PlayHand(
            None, dealer_hand, self.active_deck.game_deck()
        ).dealer_turn()  # Dealer's turn
        if player_value > dealer_value:
            if action == "double":
                return 2 * wager
            else:
                return wager
        elif player_value == dealer_value:
            return 0
        else:
            if action == "double":
                return -wager
            else:
                return -wager  # Should be -wager, not -2*wager (already doubled)

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