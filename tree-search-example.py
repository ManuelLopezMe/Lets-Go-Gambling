import json

if __name__ == "__main__":
    # Example setup
    from Helpers.DeckHelper import Deck
    from Helpers.MetricsHelper import Hand
    from Helpers.AgentHelper import MCTSNode, SimAgent, print_node_statistics, simulate_action, get_legal_actions, collect_tree_data
    # Create a deck and deal hands
    shoe  = Deck(1)
    shoe.shuffle()
    player_hand = shoe.deal_hand()
    dealer_hand = shoe.deal_hand()
    splits_remaining = 0
    wager = 10
    bankroll = 100
    agent = SimAgent(num_simulations=100, c=1.41)
    action, root = agent.get_action([player_hand], 0, dealer_hand, shoe.game_deck(), splits_remaining, wager, bankroll)
    print(f"Agent chose action: {action}")
    print_node_statistics(root, 'misc/MCTS-example.txt')

    tree_data = collect_tree_data(root)
    with open("misc/mcts_tree.json", "w") as f:
        json.dump(tree_data, f, indent=2)
    print("Tree data saved to misc/mcts_tree.json")
        #break
