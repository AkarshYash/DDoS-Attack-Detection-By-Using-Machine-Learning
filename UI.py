import React, { useState } from 'react';

function App() {
  const [prediction, setPrediction] = useState(null);

  const checkTraffic = async () => {
    const response = await fetch('/predict', { method: 'POST' });
    const data = await response.json();
    setPrediction(data.prediction);
  };

  return (
    <div>
      <h1>DDoS Protection System</h1>
      <button onClick={checkTraffic}>Check Traffic</button>
      {prediction && <p>Traffic Status: {prediction}</p>}
    </div>
  );
}
export default App;