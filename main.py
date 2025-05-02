from Helpers.AgentHelper import *
from Helpers.DeckHelper import *
from Helpers.MetricsHelper import *
import json

# A copy of the game engine file adapted to run on our MCTS-MDP agent

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

        print("Simulated Dealers Hand: {dealer}".format(dealer=self.dealer_hand))
        return dealer_value

class SimGame:
    """
    Integrates the MCTS agent into the Blackjack game.
    """
    def __init__(self, num_simulations=1000, mcts_c=1.41, num_rounds = 50):
        self.active_shoe = None
        self.rounds_played = 0
        self.bankroll = 100
        self.num_rounds = num_rounds
        self.agent = SimAgent(num_simulations, mcts_c)
        self.simulation_results = [] 

    def _deal_cards(self):
        player_hand = self.active_shoe.deal_hand()
        dealer_hand = self.active_shoe.deal_hand()
        return player_hand, dealer_hand

    def _get_wager(self):
        """
        Since we're not discounting, we'll play a constant wager of $5.00 for a starting $100 budget
        """    
        return 5
    
    def _check_reshuffle(self):
        if len(self.active_shoe.game_deck()) <= round(
            len(self.active_shoe.all_cards()) * 0.2 # Might change it so that it's a random percentage using np.random
        ):
            self.active_shoe.shuffle()

    def get_player_action(self, player_hands, current_hand_idx, dealer_hand, deck, splits_remaining):
        return self.agent.get_action(player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, self._get_wager(), self.bankroll)
        
    def play_round(self, wager, player_hand, dealer_hand):
        player_value = Hand(player_hand).compute_value()
        dealer_value = Hand(dealer_hand).compute_value()
        hand_results = []
        node_stats = []  # Collect node statistics for this round
        max_splits = 3
        hands_queue = [(player_hand, wager, max_splits, [])]

        print(f"Player initial hand: {player_hand}, value: {player_value}")
        print(f"Dealer initial hand: {dealer_hand}, value: {dealer_value}")

        if player_value == 21:
            print("Blackjack! You win!")
            return wager, node_stats

        while hands_queue:
            current_hand, current_wager, splits_remaining, action_history = hands_queue.pop(0)
            player_value = Hand(current_hand).compute_value()

            while True:
                action = self.get_player_action(
                    [current_hand], 0, dealer_hand, self.active_shoe.game_deck(), splits_remaining
                )
                action_history = action_history + [action]

                # Collect node statistics
                node_stats.append({
                    "hand": current_hand,
                    "action": action,
                    "action_history": action_history,
                    "player_value": player_value,
                    "dealer_upcard": dealer_hand[0]
                })

                if action == "hit":
                    player_value = PlayHand(
                        current_hand, None, self.active_shoe.game_deck()
                    ).player_turn(action)
                    print(f"Player hits, hand: {current_hand}, value: {player_value}")
                    if player_value > 21:
                        print(f"You busted with {current_hand}!")
                        hand_results.append((-current_wager, action_history))
                        break
                elif action == "stand":
                    print(f"Standing with {current_hand}.")
                    hand_results.append((0, action_history))  # Tie results in 0 payout
                    break
                elif action == "double":
                    if current_wager * 2 > self.bankroll:
                        print("Insufficient bankroll to double down.")
                        continue
                    
                    current_wager *= 2
                    player_value = PlayHand(
                        current_hand, None, self.active_shoe.game_deck()
                    ).player_turn(action)
                    print(f"Player doubles, hand: {current_hand}, value: {player_value}")
                    if player_value > 21:
                        print(f"You busted with {current_hand}!")
                        hand_results.append((-current_wager, action_history))
                    else:
                        print(f"Standing with {current_hand}.")
                        hand_results.append((current_wager, action_history))
                    break
                elif (
                    action == "split"
                    and len(current_hand) == 2
                    and current_hand[0] == current_hand[1]
                    and splits_remaining > 0
                ):
                    right_hand = [current_hand.pop()]
                    right_hand.append(self.active_shoe.game_deck().pop())
                    left_hand = current_hand
                    left_hand.append(self.active_shoe.game_deck().pop())
                    print(f"Right hand: {right_hand}")
                    print(f"Left hand: {left_hand}")
                    hands_queue.append((right_hand, current_wager, splits_remaining - 1, action_history + ["split_right"]))
                    hands_queue.append((left_hand, current_wager, splits_remaining - 1, action_history + ["split_left"]))
                    break
                else:
                    print("Invalid action. Please choose hit, stand, double, or split.")

        # Dealer's turn
        dealer_value = PlayHand(None, dealer_hand, self.active_shoe.game_deck()).dealer_turn()
        final_dealer_hand = dealer_hand[:]  # Capture the final dealer's hand
        print(f"Dealer final hand: {final_dealer_hand}, value: {dealer_value}")

        payouts = []
        for result, action_history in hand_results:
            if result != 0:
                payouts.append(result)
            else:
                player_value = Hand(current_hand).compute_value()
                
                # Debugging: Print action history
                #print(f"Action history: {action_history}")
                # Debugging: Print the last action
                #if action_history:
                    #last_action = action_history[-1]
                #else:
                    #last_action = "none"  # Handle the case where action_history is empty 
                #print(f"Last action: {last_action}")
                
                payout = self._determine_payout(player_value, dealer_value, current_wager, action)
                print(f"Player value: {player_value}, Dealer value: {dealer_value}, Wager: {current_wager}, Payout: {payout}")
                payouts.append(payout)

        # Add final dealer hand and value to node statistics
        for stat in node_stats:
            stat["final_dealer_hand"] = final_dealer_hand
            stat["final_dealer_value"] = dealer_value

        total_payout = sum(payouts)
        print(f"Round payout: {total_payout}")
        return total_payout, node_stats

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
        self.active_shoe = Deck(num_decks)
        self.active_shoe.shuffle()

        initial_bankroll = self.bankroll # Store initial bankroll for this simulation run
        round_outcomes_list = [] # Store outcome for each round in this run
        node_statistics = []  # Collect node statistics for all rounds

        #print(f"Starting bankroll: {self.bankroll}")  # Debugging

        while self.rounds_played < self.num_rounds and self.bankroll > 0:
            wager = self._get_wager()

            #self.bankroll -= wager

            player_hand, dealer_hand = self._deal_cards()

            print(
                "Your Hand {Player} \n Dealer Upcard: {dealer}".format(
                    Player=player_hand, dealer=dealer_hand[0]
                )
            )
            payout, round_node_stats = self.play_round(wager, player_hand, dealer_hand)
            self.bankroll += payout

            print(f"Bankroll after round: {self.bankroll}")  # Debugging

            round_outcomes_list.append(payout) # Record payout for this round
            node_statistics.append(round_node_stats)  # Append node stats for this round

            self.rounds_played += 1
            self._check_reshuffle()
        
        self.simulation_results.append({
            'final_bankroll': self.bankroll,
            'rounds_played': self.rounds_played,
            'initial_bankroll': initial_bankroll,
            'round_outcomes': round_outcomes_list, # Store all round payouts
            'node_statistics': node_statistics  # Add node statistics to results
            # Add other metrics here
        })
        print(f"Simulation finished. Final bankroll: ${self.bankroll}")

if __name__ == "__main__":
    num_runs = 25
    num_sims = 1000
    all_simulation_data = [{
        "number_of_runs": num_runs,
        "number_of_simulation_iterations": num_sims
    }]

    for i in range(num_runs):
        print(f"Running simulation run {i+1}")
        game = SimGame(num_simulations=num_sims, mcts_c=1.41, num_rounds=50)
        game.play_game(num_decks=2)
        all_simulation_data.extend(game.simulation_results)

    #filename = input("Save file as: ") + '.json'
    filename = 'test-run-6.json'
    with open('data/' + filename, 'w') as f:
        json.dump(all_simulation_data, f, indent=2)

    print(f"Finished {num_runs} simulation runs. Results saved to {filename}")

