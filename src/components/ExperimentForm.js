import React, { useState } from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

const ExperimentForm = () => {
  // State hooks for form fields
  const [V0, setV0] = useState(100);
  const [Cg, setCg] = useState(0.6);
  const [C1, setC1] = useState(0.023);
  const [Rf, setRf] = useState(15);
  const [Rt, setRt] = useState(115);
  const [d, setD] = useState(30);

  // State hook for graph data
  const [graphData, setGraphData] = useState([['t', 'V']]);

  // State hook for modal visibility
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Replace this function with your own calculation logic
  const calculateGraphData = () => {
    let data = [];
    // ... insert your calculation logic here
    return data;
  };

  const handleFormSubmit = (event) => {
    event.preventDefault();
    const newGraphData = calculateGraphData();
    setGraphData(newGraphData);
    setIsModalOpen(true); // Show the modal with the graph
  };

  // Configure the Highcharts options
  const chartOptions = {
    title: {
      text: 'V - T Curve'
    },
    series: [{
      name: 'Voltage',
      data: graphData
    }],
    // Add other chart options here
  };

  return (
    <div>
      <form onSubmit={handleFormSubmit}>
        {/* Render your form fields here */}
        <input type="number" value={V0} onChange={(e) => setV0(parseFloat(e.target.value))} />
        {/* Include other form inputs similarly */}
        <button type="submit">Start</button>
      </form>

      {isModalOpen && (
        <div className="modal">
          <HighchartsReact
            highcharts={Highcharts}
            options={chartOptions}
          />
          <button onClick={() => setIsModalOpen(false)}>Close</button>
        </div>
      )}
    </div>
  );
};

export default ExperimentForm;
