"use client";

import React, { useState, useEffect } from "react";

function USFJETT() {
  const [currentOccupancies, setCurrentOccupancies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCurrent, setLoadingCurrent] = useState(true);
  const [uploadedImage, setUploadedImage] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [occupancyScore, setOccupancyScore] = useState(null);
  const bookingLink = "https://calendar.lib.usf.edu/spaces"
  
  // Fetch current occupancies on form backend
  useEffect(() => {
    const fetchCurrentOccupancies = async() => {
      try {
        setLoadingCurrent(true);
        const response = await fetch("http://127.0.0.1:8000/api/current-occupancies"); // Add API endpoint here
        if (!response.ok) throw new Error("Failed to fetch current occupancies");

        const data = await response.json();
        setCurrentOccupancies(data);
      } catch (error) {
        console.error(error);
        alert("Failed to load occupancy data");
      } finally {
        setLoadingCurrent(false);
      }
    };

    fetchCurrentOccupancies();
  }, []);

  // Handle user image upload
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadedImage(file);
    setUploading(true);

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/upload-image", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to upload image");

      const data = await response.json();
      setOccupancyScore(data.percent_occupied);
    } catch (error) {
      console.error(error);
      alert("Failed to upload image");
    }
    finally {
      setUploading(false);
    }
  };

  // Function to get the color based on occupancy percentage
  const getMeterColor = (value) => {
    if (value <= 30) return "bg-green-500";
    if (value <= 70) return "bg-yellow-500";
    return "bg-red-500";
  };

  // HTML + Tailwind Structure
  return (
    <div className="flex flex-col items-center p-6 space-y-6">
      <h1 className="text-3xl font-bold text-green-600">USF JETT</h1>
      <p className="text-lg text-gray-600">
        The USF JETT app tells you currennt occupancy in these specific study areas
        and predicts future occupancy based on historical data.
      </p>
    

      {/* Current Occupancies */}
      <div className="w-full max-w-md space-y-4">
        <h2 className="text-xl font-bold text-green-800 text-center">Current Occupancy:</h2>
        {loadingCurrent ? (
          <p>Loading current occupancy...</p>
        ) : (
          <ul className="space-y-2">
            {currentOccupancies.map((building) => (
              <li
                key={building.building}
                className="flex items-center justify-between p-3 bg-black-100 rounded-lg shadow-md"
                >
                  <span className="font-semibold">{building.building}</span>
                  <span className="flex items-center space-x-2">
                    <span>{(building.percent_occupied || 0).toFixed(2)}% Occupied</span>
                    <div className="relative w-28 h-4 bg-gray-200 rounded-full">
                      <div
                        className={`absolute top-0 left-0 h-full rounded-full ${getMeterColor(building.percent_occupied)}`}
                        style={{ width: `${building.percent_occupied}%` }}
                      ></div>
                    </div>
                  </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Image Upload */}
      <div className="w-full max-w-md p-4 space-y-4 bg-gray-50 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-gray-800">Upload Your Own Study Area Image:</h2>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-100 file:text-green-700 hover:file:bg-green-200"/>
          {uploadedImage && (
            <div className="mt-4">
              <p className="text-sm text-gray-500"> Uploaded Image:</p>
              <img
                src={URL.createObjectURL(uploadedImage)}
                alt="Uploaded room"
                className="mt-2 w-full h-auto rounded-lg shadow-md"
                />
              </div>
          )}
          {uploading && <p className="text-sm text-gray-500 mt-2">Uploading...</p>}
          {occupancyScore !== null && (
            <div className="mt-4 p-4 bg-white border-gray-300 rounded-md shadow-md">
              <p className="text-lg font-bold text-green-700">
                {(occupancyScore || 0).toFixed(2)}% Occupied
              </p>
            </div>
          )}
      </div>   

      {/* Booking Link */}
      <div className="mt-6 flex justify-center items-center">
        <a href={bookingLink} target="_blank" rel="noopener noreferrer" className="text-green-500 text-center">
          <img src="/sai-kiran-belana-qTZ3N5G7YLg-unsplash.jpg" alt="Book a study space" className="w-64 h-auto"  />
          <p className="text-lg text-yellow-500">Book a study space</p>
        </a>
      </div>

    </div>
  );
}
export default USFJETT;