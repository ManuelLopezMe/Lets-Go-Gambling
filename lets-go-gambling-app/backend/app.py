from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_runs = data.get('num_runs', 25)
    num_sims = data.get('num_sims', 1000)
    filename = data.get('filename', 'test-run.json')

    # Prepare the command to run the main.py script
    command = ['python', 'main.py', '--num_runs', str(num_runs), '--num_sims', str(num_sims), '--filename', filename]

    try:
        # Execute the main.py script
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500

        # Load the output JSON file
        output_filepath = os.path.join('data', filename)
        with open(output_filepath, 'r') as f:
            simulation_data = json.load(f)

        return jsonify(simulation_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)