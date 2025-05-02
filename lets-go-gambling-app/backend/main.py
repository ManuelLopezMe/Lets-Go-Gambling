from flask import Flask, request, jsonify
import json
import argparse
from main import SimGame

app = Flask(__name__)

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    num_runs = data.get('num_runs', 25)
    num_sims = data.get('num_sims', 1000)
    filename = data.get('filename', 'test-run.json')

    all_simulation_data = [{
        "number_of_runs": num_runs,
        "number_of_simulation_iterations": num_sims
    }]

    for i in range(num_runs):
        print(f"Running simulation run {i+1}")
        game = SimGame(num_simulations=num_sims, mcts_c=1.41, num_rounds=50)
        game.play_game(num_decks=2)
        all_simulation_data.extend(game.simulation_results)

    output_dir = 'data'
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(all_simulation_data, f, indent=2)

    return jsonify({"message": "Simulation completed", "results_file": filepath})

if __name__ == '__main__':
    app.run(debug=True)