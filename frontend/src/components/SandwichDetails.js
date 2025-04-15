import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';

function SandwichReport() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { customerKey } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSandwichReport = async () => {
      if (!customerKey || customerKey === 'undefined') {
        setError('No customer information found. Please log in again.');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/api/customer/${customerKey}/sandwich-report/`);
        setReport(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching sandwich report:', error);
        setError(
          error.response?.data?.message || 
          'Failed to load your sandwich report. Please try again later.'
        );
        setLoading(false);
      }
    };

    fetchSandwichReport();
  }, [customerKey]);

  // If no customer key, redirect to login
  useEffect(() => {
    if (!customerKey || customerKey === 'undefined') {
      navigate('/');
    }
  }, [customerKey, navigate]);

  if (loading) {
    return <div className="loading">Loading your sandwich journey...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>{error}</p>
        <button onClick={() => navigate('/')} className="retry-button">
          Return to Login
        </button>
      </div>
    );
  }

  if (!report) {
    return <div className="error">No sandwich data found.</div>;
  }

  return (
    <div className="sandwich-report">
      <h2>Your Sandwich Unwrapped</h2>
      
      {/* Favorite Sandwich Section */}
      <div className="report-section favorite-sandwich">
        <h3>Your Favorite Sandwich</h3>
        <div className="section-content">
          <h4>{report.favorite_sandwich.name}</h4>
          <p>You've ordered this {report.favorite_sandwich.times_ordered} times!</p>
          <p>Calories per sandwich: {report.favorite_sandwich.calories}</p>
        </div>
      </div>

      {/* Order Stats Section */}
      <div className="report-section order-stats">
        <h3>Your Sandwich Journey</h3>
        <div className="section-content">
          <p>You've ordered on {report.order_stats.unique_days_ordered} different days</p>
          <p>Total sandwiches enjoyed: {report.order_stats.total_sandwiches}</p>
          <p>Total investment in happiness: ${report.order_stats.total_spent.toFixed(2)}</p>
        </div>
      </div>

      {/* Preferred Ordering Section */}
      <div className="report-section preferred-ordering">
        <h3>How You Like to Order</h3>
        <div className="section-content">
          <p>Your preferred method: {report.preferred_ordering.method}</p>
          <p>You've used this method {report.preferred_ordering.times_used} times</p>
        </div>
      </div>

      {/* Favorite Location Section */}
      <div className="report-section favorite-location">
        <h3>Your Home Away From Home</h3>
        <div className="section-content">
          <p>Most visited location: {report.favorite_location.address}</p>
          <p>In {report.favorite_location.city}</p>
          <p>You've visited this location {report.favorite_location.visits} times</p>
        </div>
      </div>

      {/* Order Timeline Section */}
      <div className="report-section order-timeline">
        <h3>Your Recent Sandwich History</h3>
        <div className="section-content timeline">
          {report.order_timeline.map((period, index) => (
            <div key={index} className="timeline-entry">
              <h4>{period.month} {period.year}</h4>
              <p>{period.sandwiches} sandwiches</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SandwichReport; 