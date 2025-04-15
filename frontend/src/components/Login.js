import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const formatPhoneNumber = (value) => {
    // Remove all non-digits
    const digits = value.replace(/\D/g, '');
    
    // Format as XXX-XXX-XXXX
    if (digits.length <= 3) {
      return digits;
    } else if (digits.length <= 6) {
      return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    } else {
      return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
    }
  };

  const handlePhoneNumberChange = (e) => {
    const formattedNumber = formatPhoneNumber(e.target.value);
    setPhoneNumber(formattedNumber);
    setError(''); // Clear error when user types
  };

  const getErrorMessage = (error) => {
    if (error.response?.data?.error_code) {
      switch (error.response.data.error_code) {
        case 'TABLE_NOT_FOUND':
          return 'Our customer database is currently being set up. Please try again in a few minutes.';
        case 'MISSING_COLUMNS':
          return 'Our customer database is being configured. Please try again in a few minutes.';
        case 'QUERY_ERROR':
          return 'We encountered an error while checking your phone number. Please try again.';
        case 'CONNECTION_ERROR':
          return 'We are having trouble connecting to our database. Please try again in a few minutes.';
        case 'UNEXPECTED_ERROR':
          return 'An unexpected error occurred. Please try again later.';
        default:
          return error.response.data.message || 'An error occurred. Please try again.';
      }
    }
    return 'An error occurred. Please try again.';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/login/', {
        phone_number: phoneNumber
      });
      
      const userData = response.data.user;
      if (!userData || !userData.customer_key) {
        throw new Error('Invalid response format: missing customer key');
      }
      
      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Redirect to sandwich report page with customer key
      navigate(`/sandwich-report/${userData.customer_key}`);
    } catch (error) {
      if (error.response?.status === 404) {
        setError('Phone number not found in our records. Please check and try again.');
      } else if (error.message === 'Invalid response format: missing customer key') {
        setError('Server response format error. Please try again.');
      } else {
        setError(getErrorMessage(error));
      }
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Welcome to Sandwich Unwrapped</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="phoneNumber">Phone Number:</label>
          <input
            type="text"
            id="phoneNumber"
            value={phoneNumber}
            onChange={handlePhoneNumberChange}
            placeholder="XXX-XXX-XXXX"
            maxLength="12"
            required
            disabled={isLoading}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}

export default Login; 