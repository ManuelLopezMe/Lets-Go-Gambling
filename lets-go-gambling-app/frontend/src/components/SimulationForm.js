import React, { useState } from 'react';

const SimulationForm = () => {
    const [numRuns, setNumRuns] = useState(25);
    const [numSims, setNumSims] = useState(1000);
    const [filename, setFilename] = useState('test-run.json');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = { num_runs: numRuns, num_sims: numSims, filename };

        try {
            const res = await fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await res.json();
            setResponse(result);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <h1>Simulation Parameters</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>
                        Number of Runs:
                        <input
                            type="number"
                            value={numRuns}
                            onChange={(e) => setNumRuns(e.target.value)}
                        />
                    </label>
                </div>
                <div>
                    <label>
                        Number of Simulations:
                        <input
                            type="number"
                            value={numSims}
                            onChange={(e) => setNumSims(e.target.value)}
                        />
                    </label>
                </div>
                <div>
                    <label>
                        Output Filename:
                        <input
                            type="text"
                            value={filename}
                            onChange={(e) => setFilename(e.target.value)}
                        />
                    </label>
                </div>
                <button type="submit">Run Simulation</button>
            </form>
            {response && (
                <div>
                    <h2>Simulation Results</h2>
                    <pre>{JSON.stringify(response, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default SimulationForm;