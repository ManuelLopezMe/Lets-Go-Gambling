from Game_Engine import PlayHand
from MCTS_MDP_Agent import *
from DeckHelper import *
from metrics import *

# A copy of the game engine file adapted to run on our MCTS-MDP agent
class SimGame:
    """
    Integrates the MCTS agent into the Blackjack game.
    """
    def __init__(self, num_simulations=1000, mcts_c=1.41):
        self.active_deck = None
        self.rounds_played = 0
        self.bankroll = 100
        self.num_rounds = 10
        self.agent = SimAgent(num_simulations, mcts_c)

    def _deal_cards(self):
        player_hand = self.active_deck.deal_hand()
        dealer_hand = self.active_deck.deal_hand()
        return player_hand, dealer_hand

    def _get_wager(self):
        """
        Since we're not discounting, we'll play a constant wager of $5.00 for a starting $100 budget
        """    
        return 5
    
    def _check_reshuffle(self):
        if len(self.active_deck.game_deck()) <= round(
            len(self.active_deck.all_cards()) * 0.2 # Might change it so that it's a random percentage using np.random
        ):
            self.active_deck.shuffle()

    def get_player_action(self, player_hand, dealer_hand, deck, splits_remaining):
        return self.agent.get_action(player_hand, dealer_hand, deck, splits_remaining)
        
    def play_round(self, wager, player_hand, dealer_hand):
        player_value = Hand(player_hand).compute_value()
        dealer_value = Hand(dealer_hand).compute_value()
        hand_results = [] 

        if player_value == 21:
            print("Blackjack! You win!")
            return wager

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
                    and len(hand_results) + len(hands_queue) < 4 
                ):
                    right_hand = [current_hand.pop()]
                    right_hand.append(self.active_deck.game_deck().pop())
                    left_hand = current_hand
                    left_hand.append(self.active_deck.game_deck().pop())
                    print(f"Right hand: {right_hand}")
                    print(f"Left hand: {left_hand}")

                    hands_queue.append((right_hand, current_wager))
                    hands_queue.append((left_hand, current_wager))
                    break
                else:
                    print("Invalid action. Please choose hit, stand, double, or split.")

        dealer_value = PlayHand(None, dealer_hand, self.active_deck.game_deck()).dealer_turn()

        payouts = []  
        for current_hand, current_wager in hands_queue:
            player_value = Hand(current_hand).compute_value()
            payouts.append(self._determine_payout(player_value, dealer_value, current_wager, "stand"))

        return sum(hand_results + payouts)

    def _determine_payout(self, player_value, dealer_value, wager, action):

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

    def play_game(self, num_decks=2):  
        self.active_deck = Deck(num_decks)
        self.active_deck.shuffle()

        while self.rounds_played < self.num_rounds and self.bankroll > 0:
            wager = self._get_wager()

            self.bankroll -= wager

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

if __name__ == "__main__":
    # Play with the MCTS-MDP agent
    game = PlayGame(num_simulations=1000, mcts_c=1.41) # c should = sqrt(2) when payouts are between the range [0,1]
    game.play_game()
    print("Thanks for playing!")