import copy # Deep copy lets us simulate actions without altering the game state
import math
from Game_Engine import PlayGame, PlayHand
from metrics import Hand  

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state  # (player_hand, dealer_hand, deck, splits_remaining, action_history)
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value = 0
        self.action_history = state[4]  # Keep track of actions taken to reach this state

def simulate_action(state, action):
    """
    Given a state and action, returns the next state after applying the action.
    State: (player_hand, dealer_hand, deck, splits_remaining, action_history)
    Action: "hit", "stand", "double", "split"
    """
    player_hand, dealer_hand, deck, splits_remaining, action_history = copy.deepcopy(state)
    action_history = action_history + [action]  # Append the current action

    if action == "hit":
        if len(deck) == 0:
            return (player_hand, dealer_hand, deck, splits_remaining, action_history)  # No cards left
        player_hand.append(deck.pop())
        return (player_hand, dealer_hand, deck, splits_remaining, action_history)

    elif action == "stand":
        # No change to player hand
        return (player_hand, dealer_hand, deck, splits_remaining, action_history)

    elif action == "double":
        if len(deck) == 0:
            return (player_hand, dealer_hand, deck, splits_remaining, action_history)
        player_hand.append(deck.pop())
        return (player_hand, dealer_hand, deck, splits_remaining, action_history)

    elif action == "split":
        if len(player_hand) == 2 and player_hand[0] == player_hand[1] and splits_remaining > 0 and len(deck) >= 2:
            left_hand = [player_hand[0], deck.pop()]
            right_hand = [player_hand[1], deck.pop()]
            return (left_hand, right_hand, dealer_hand, deck, splits_remaining - 1, action_history) # Changed to return both
        else:
                raise ValueError("Split not allowed")
                return (player_hand, dealer_hand, deck, splits_remaining, action_history)
    else:
        return (player_hand, dealer_hand, deck, splits_remaining, action_history)

def is_terminal(state):
    """
    Returns True if the state is terminal (player busts, stands, or after double).
    State: (player_hand, dealer_hand, deck, splits_remaining, action_history)
    """
    player_hand, dealer_hand, deck, splits_remaining, action_history = state
    player_value = PlayHand(player_hand, dealer_hand, deck).compute_value()

    if player_value >= 21:
        return True
    # Check for stand or double in action history
    elif action_history and (action_history[-1] == "stand" or action_history[-1] == "double"):
        return True
    else:
        return False

def get_legal_actions(state):
    """
    Returns a list of legal actions for the given state.
    State: (player_hand, deck, splits_remaining, action_history)
    Actions: "hit", "stand", "double", "split" (if allowed)
    """
    player_hand, deck, splits_remaining, action_history = state
    actions = ["hit", "stand"]
    if len(player_hand) == 2:
        actions.append("double")
        if player_hand[0] == player_hand[1] and splits_remaining > 0 and len(deck) >= 2:
            actions.append("split")
    return actions

def rollout(state):
    """
    Simulate a random playout from the given state until terminal, returning the final reward.
    Uses a basic strategy for the player, and dealer plays out according to rules.
    """
    player_hand, dealer_hand, deck, splits_remaining, action_history = copy.deepcopy(state)

    while not is_terminal((player_hand, dealer_hand, deck, splits_remaining, action_history)):
        actions = get_legal_actions((player_hand, dealer_hand, deck, splits_remaining, action_history))
        action = rollout_policy(player_hand, dealer_hand[0], actions)  # Pass the first dealer card
        player_hand, dealer_hand, deck, splits_remaining, action_history = simulate_action(
            (player_hand, dealer_hand, deck, splits_remaining, action_history), action
        )

    player_value = Hand(player_hand, dealer_hand, deck).compute_value()
    dealer_value = PlayHand(None, dealer_hand, deck).dealer_turn()  #  Use dealer_turn from PlayHand
    # Payoff: +1 win, 0 draw, -1 lose
    if player_value > 21:
        return -1
    elif dealer_value > 21:
        return 1
    elif player_value > dealer_value:
        return 1
    elif player_value < dealer_value:
        return -1
    else:
        return 0

def rollout_policy(player_hand, dealer_upcard, actions):
    """
    A basic blackjack strategy for the rollout phase.
    """
    player_value = Hand(player_hand).compute_value() # changed
    dealer_upcard_value = Hand([dealer_upcard]).compute_value()

    if "split" in actions and player_hand[0] == player_hand[1]:
        if player_hand[0] in [2, 3, 4, 5, 6, 7] and dealer_upcard_value in range(2, 8):
            return "split"
        elif player_hand[0] in [8] :
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
    elif player_value == 17 :
        return "stand"
    elif player_value > 17:
        return "stand"
    else:
        return "hit"  # Fallback

def mcts_search(root_state, num_simulations, c=1.41):
    """
    Performs MCTS search from the given root state.

    Args:
        root_state: The initial game state (player_hand, dealer_hand, deck, splits_remaining, action_history).
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
            for action in get_legal_actions(state):
                node.children[action] = MCTSNode(simulate_action(state, action), parent=node)
        # Simulation
        reward = rollout(state)
        # Backpropagation
        backpropagate(node, reward)
    # Choose best action
    best_action = max(root.children.items(), key=lambda item: item[1].value / item[1].visits)[0]
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

class SimAgent:
    def __init__(self, num_simulations=1000, c=1.41):
        self.num_simulations = num_simulations
        self.c = c

    def get_action(self, player_hand, dealer_hand, deck, splits_remaining):
        """
        Gets the best action from the MCTS agent.
        """
        # Initialize action history
        action_history = []
        root_state = (player_hand, dealer_hand, deck, splits_remaining, action_history)
        best_action = mcts_search(root_state, self.num_simulations, self.c)
        return best_action