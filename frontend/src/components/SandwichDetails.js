import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

function SandwichDetails() {
  const [sandwichDetails, setSandwichDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { userId } = useParams();

  useEffect(() => {
    const fetchSandwichDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/sandwich-details/${userId}/`);
        setSandwichDetails(response.data);
        setLoading(false);
      } catch (error) {
        setError('Failed to load sandwich details. Please try again later.');
        setLoading(false);
      }
    };

    fetchSandwichDetails();
  }, [userId]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="sandwich-details">
      <h2>Sandwich Unwrapped</h2>
      {sandwichDetails && (
        <div className="details-container">
          <div className="user-info">
            <h3>Welcome, {sandwichDetails.user.first_name} {sandwichDetails.user.last_name}!</h3>
          </div>
          <div className="sandwich-info">
            <h3>Your Sandwich Details</h3>
            {sandwichDetails.sandwich_details.map((sandwich) => (
              <div key={sandwich.id} className="sandwich-card">
                <h4>{sandwich.name}</h4>
                <p>{sandwich.description}</p>
                {/* Add more sandwich details as needed */}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SandwichDetails; 