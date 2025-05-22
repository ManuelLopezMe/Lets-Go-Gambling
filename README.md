# Lets-Go-Gambling

A research project exploring optimal Blackjack strategies using Monte Carlo Tree Search (MCTS) and Markov Decision Processes (MDP).

## Overview

This project implements and analyzes advanced AI techniques for Blackjack, focusing on decision-making and strategy optimization. The agent leverages MCTS and MDPs to learn and play Blackjack, with results compared to standard baselines.

## Features

- **Monte Carlo Tree Search (MCTS)** agent for Blackjack
- Markov Decision Process (MDP) modeling of the game
- Simulation and analysis of agent performance
- Playable Blackjack game engine
- Data and results for in-depth analysis

## Project Structure

- [`main.py`](main.py): Run simulations and adjust agent parameters.
- [`Helpers/AgentHelper.py`](Helpers/AgentHelper.py): Core MCTS algorithm and agent logic.
- [`Helpers/DeckHelper.py`](Helpers/DeckHelper.py): Deck and card utilities.
- [`Helpers/MetricsHelper.py`](Helpers/MetricsHelper.py): Metrics and evaluation tools.
- [`misc/Game_Engine.py`](misc/Game_Engine.py): Playable Blackjack game.
- [`Simulation_Analysis.ipynb`](Simulation_Analysis.ipynb): Data analysis and visualization.
- [`data/`](data/): Simulation data and results.
- [`Blackjack_Simulation_with_MDP_MCTS.pdf`](Blackjack_Simulation_with_MDP_MCTS.pdf): Full project report.

## Getting Started

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Run a simulation**
    ```
    python main.py
    ```
3. **Play the game manually**
    ``` 
    python misc/Game_Engine.py
    ```