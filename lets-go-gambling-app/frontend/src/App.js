import React, { useState } from 'react';
import './App.css';
import SimulationForm from './components/SimulationForm';

function App() {
    const [simulationResults, setSimulationResults] = useState(null);

    const handleSimulationSubmit = async (numRuns, numSims, filename) => {
        const response = await fetch('http://localhost:5000/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ num_runs: numRuns, num_sims: numSims, filename }),
        });

        if (response.ok) {
            const data = await response.json();
            setSimulationResults(data);
        } else {
            console.error('Error executing simulation:', response.statusText);
        }
    };

    return (
        <div className="App">
            <h1>Gambling Simulation</h1>
            <SimulationForm onSubmit={handleSimulationSubmit} />
            {simulationResults && (
                <div>
                    <h2>Simulation Results</h2>
                    <pre>{JSON.stringify(simulationResults, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

export default App;