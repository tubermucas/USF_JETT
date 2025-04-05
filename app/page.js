"use client";

import React, { useState, useEffect } from "react";

function USFJETT() {
  const [days, setDays] = useState("");
  const [time, setTime] = useState("");
  const [currentOccupancies, setCurrentOccupancies] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCurrent, setLoadingCurrent] = useState(true);
  
  useEffect(() => {
    const fetchCurrentOccupancies = async() => {
      try {
        setLoadingCurrent(true);
        const response = await fetch(""); // Add API endpoint here
        if (!response.ok) throw new Error("Failed to fetch current occupancies");

        const data = await response.json();
        setCurrentOccupancies(data.occupancies);
      } catch (error) {
        console.error(error);
        alert("Failed to load occupancy data");
      } finally {
        setLoadingCurrent(false);
      }
    };

    fetchCurrentOccupancies();
  }, []);

  const handlePrediction = async () => {
    if (!days || !time) {
      alert("Please fill in all fields")
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("*Add API endpoint here*", {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days, time }),
      }); 

      if (!response.ok) throw new Error("Failed to fetch predictions.");
      
      const data = await response.json();
      setPredictions(data.predictions);
    } catch (error) {
      console.error(error);
      alert("Failed to fetch predictions");
    } finally {
      setLoading(false);
    }
  };

  const getMeterColor = (value) => {
    if (value <= 30) return "bg-green-500";
    if (value <= 70) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="flex flex-col items-center p-6 space-y-6">
      <h1 className="text-3x1 font-bold text-green-600">USF JETT</h1>
      <p className="text-lg text-gray-600">
        The USF JETT app tells you currennt occupancy in these specific study areas
        and predicts future occupancy based on historical data.
      </p>
    

      {/* Current Occupancies */}
      <div className="w-full max-w-md space-y-4">
        <h2 className="text-xl font-bold text-gray-800">Current Occupancy:</h2>
        {loadingCurrent ? (
          <p>Loading current occupancy...</p>
        ) : (
          <ul className="space-y-2">
            {currentOccupancies.map((building) => (
              <li
                key={building.building}
                className="flex items-center justify-between p-3 bg-gray-100 rounded-lg shadow-md"
                >
                  <span className="font-semibold">{building.building}</span>
                  <span className="flex items-center space-x-2">
                    <span>{building.occupancy}% Occupied</span>
                    <div className="relative w-28 h-4 bg-gray-200 rounded-full">
                      <div
                        className={`absolute top-0 left-0 h-full rounded-full $(getMeterColor(building.occupancy))`}
                        style={{ width: `${building.occupancy}%` }}
                      ></div>
                    </div>
                  </span>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Predictions / Schedule */}
      <div className="w-full max-w-md p-4 space-y-4 bg-gray-50 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-gray-800">Predict Capacity at:</h2>
        <div className="flex flex-col space-y-2">
          <input
            type="date"
            value={days}
            onChange={(e) => setDays(e.target.value)}
            className="p-2 border border-gray-300 rounded-lg"
          />
          <input
            type="time"
            value={time}
            onchange={(e) => setTime(e.target.value)}
            className="p-2 border border-gray-300 rounded-lg"
          />
        </div>
        <button
          onClick={handlePrediction}
          className="w-full px-4 py-2 text-white bg-blue-500 rounded-lg hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? "Predicting..." : "Predict Capacity"}
        </button>
      </div>

      {/* Prediction Section */}
      {predictions.length > 0 && (
        <div className="w-full max-w-md space-y-4">
          <h2 className="text-xl font-bold text-gray-800"> 
          Predicted Occupancy at {days}, {time}:
          </h2>
          <ul className="space-y-2">
            {predictions.map((building) => (
              <li
                key={building.building}
                className="flex items-center justify-between p-3 bg-gray-100 rounded-lg shadow-md"
              >
                <span className="font-semibold">{building.buiilding}</span>
                <span className="flex items-center space-x-2">
                  <span>{building.predicted_occupancy}% Occupied</span>
                  <div className="relative w-28 h-4 bg-gray-200 rounded-full">
                    <div
                      className={`absolute top-0 left-0 h-full rounded-full ${getMeterColor(building.predicted_occupancy)}`}
                      style={{ width: `${building.predicted_occupancy}%`,}}
                    ></div>
                  </div>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
export default USFJETT;