import copy # Deep copy lets us simulate actions without altering the game state
import math
from main import PlayHand
from Helpers.MetricsHelper import Hand  

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state  # (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history)
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value = 0
        self.action_history = state[5]  # Keep track of actions taken to reach this state
        self.best_action = None  # To store the best action
        self.uct_values = {}  # To store UCT values for each child action

def simulate_action(state, action):
    player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history = copy.deepcopy(state)
    action_history = action_history + [action]
    hand = player_hands[current_hand_idx]

    if action == "hit":
        hand.append(deck.pop())
        player_hands[current_hand_idx] = hand
        return (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history)

    elif action == "stand" or action == "double":
        # Move to next hand if any
        if current_hand_idx + 1 < len(player_hands):
            return (player_hands, current_hand_idx + 1, dealer_hand, deck, splits_remaining, action_history)
        else:
            return (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history)

    elif action == "split":
        card = hand[0]
        if len(hand) == 2 and hand[0] == hand[1] and splits_remaining > 0 and len(deck) >= 2:
            # Replace current hand with two new hands
            new_hand1 = [card, deck.pop()]
            new_hand2 = [card, deck.pop()]
            player_hands.pop(current_hand_idx)
            player_hands.insert(current_hand_idx, new_hand2)
            player_hands.insert(current_hand_idx, new_hand1)
            return (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining - 1, action_history)
        else:
            raise ValueError("Split not allowed")
    else:
        return (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history)

def is_terminal(state):
    player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history = state
    # Terminal if we've finished all hands
    return current_hand_idx >= len(player_hands)

def get_legal_actions(state, bankroll, wager):
    """
    Returns a list of legal actions for the given state.
    State: (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history)
    Actions: "hit", "stand", "double", "split" (if allowed)
    """
    player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history = state
    hand = player_hands[current_hand_idx]
    actions = ["hit", "stand"]
    if len(hand) == 2 and (wager*2) <= bankroll:
        actions.append("double")
        if hand[0] == hand[1] and splits_remaining > 0 and len(deck) >= 2:
            actions.append("split")
    return actions

def rollout(state, bankroll, wager):
    player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history = copy.deepcopy(state)
    rewards = []
    while current_hand_idx < len(player_hands):
        # Play out this hand
        while True:
            hand = player_hands[current_hand_idx]
            actions = get_legal_actions((player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history), bankroll, wager)
            action = rollout_policy(hand, dealer_hand[0], actions)
            player_hands, current_hand_idx_, dealer_hand, deck, splits_remaining, action_history = simulate_action(
                (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history), action
            )
            # If we moved to next hand, break
            if current_hand_idx_ != current_hand_idx:
                current_hand_idx = current_hand_idx_
                break
            # If terminal for this hand, break
            if action in ("stand", "double") or Hand(hand).compute_value() >= 21:
                break
        current_hand_idx += 1

    # Dealer plays out
    dealer_value = PlayHand(None, dealer_hand, deck).dealer_turn()
    # Score each hand
    for hand in player_hands:
        player_value = Hand(hand).compute_value()
        if player_value > 21:
            rewards.append(-1)
        elif dealer_value > 21:
            rewards.append(1)
        elif player_value > dealer_value:
            rewards.append(1)
        elif player_value < dealer_value:
            rewards.append(-1)
        else:
            rewards.append(0)
    return sum(rewards) / len(rewards)  # or sum(rewards) if you want total

def rollout_policy(player_hand, dealer_upcard, actions):
    """
    A basic blackjack strategy for the rollout phase.
    """
    player_value = Hand(player_hand).compute_value()
    dealer_upcard_value = Hand([dealer_upcard]).compute_value()

    if "split" in actions and player_hand[0] == player_hand[1]:
        if player_hand[0] in [2, 3, 4, 5, 6, 7] and dealer_upcard_value in range(2, 8):
            return "split"
        elif player_hand[0] in [8]:
            return "split"
        elif player_hand[0] == 9 and dealer_upcard_value in [3,4,5,6,8,9]:
            return "split"
        elif player_hand[0] == 'A':
            return "split"

    if player_value <= 11:
        if "double" in actions and player_value in [9,10,11] and 2 <= dealer_upcard_value <= 9:
            return "double"
        else:
            return "hit"
    elif 12 <= player_value <= 16:
        if dealer_upcard_value in range(4, 7):
            return "stand"
        else:
            return "hit"
    elif player_value == 17:
        return "stand"
    elif player_value > 17:
        return "stand"
    else:
        return "hit"  # Fallback

def mcts_search(root_state, num_simulations, bankroll, wager, c=1.41):
    """
    Performs MCTS search from the given root state.

    Args:
        root_state: The initial game state (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history).
        num_simulations: The number of MCTS simulations to perform.
        c: The exploration/exploitation balance parameter.
    Returns:
        The best action to take from the root state.
    """
    root = MCTSNode(root_state)
    for _ in range(num_simulations):
        node = root
        state = copy.deepcopy(root_state)
        # Selection
        while node.children:
            action, node = select_uct(node, c)
            state = simulate_action(state, action)
        # Expansion
        if not is_terminal(state):
            for action in get_legal_actions(state, bankroll, wager):
                node.children[action] = MCTSNode(simulate_action(state, action), parent=node)
        # Simulation
        reward = rollout(state, bankroll, wager)
        # Backpropagation
        backpropagate(node, reward)
    # Choose best action
    best_action = max(root.children.items(), key=lambda item: item[1].value / item[1].visits)[0]
    root.best_action = best_action  # Log the best action
    root.agent_hand = root_state[0]  # Log the agent's hand
    return best_action

def select_uct(node, c=1.41):
    """
    Selects the child node with the highest UCT value.
    Returns (action, child_node).
    """
    best_value = -float('inf')
    best_action = None
    best_child = None
    for action, child in node.children.items():
        if child.visits == 0:
            uct_value = float('inf')
        else:
            exploitation = child.value / child.visits
            exploration = c * math.sqrt(math.log(node.visits + 1) / child.visits)
            uct_value = exploitation + exploration
        node.uct_values[action] = uct_value  # Log UCT value
        if uct_value > best_value:
            best_value = uct_value
            best_action = action
            best_child = child
    return best_action, best_child

def backpropagate(node, reward):
    """
    Backpropagates the simulation result up the tree, updating visit and value counts.
    """
    while node is not None:
        node.visits += 1
        node.value += reward
        node = node.parent

""" def print_node_statistics(node):
    print("Node Statistics:")
    print(f"Best Action: {node.best_action}")
    print(f"Agent's Hand: {node.state[0]}")
    print("UCT Values:")
    for action, uct_value in node.uct_values.items():
        print(f"  Action: {action}, UCT Value: {uct_value}") """

class SimAgent:
    def __init__(self, num_simulations=1000, c=1.41):
        self.num_simulations = num_simulations
        self.c = c

    def get_action(self, player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, wager, bankroll):
        """
        Gets the best action from the MCTS agent.
        """
        # Initialize action history
        action_history = []
        root_state = (player_hands, current_hand_idx, dealer_hand, deck, splits_remaining, action_history)
        best_action = mcts_search(root_state, self.num_simulations, bankroll, wager, self.c)
        return best_action