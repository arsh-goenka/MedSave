import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = ({ onLogin, onSignup, setUserDetails }) => {
  const [isSignup, setIsSignup] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    email: '',
    role: 'non_profit',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUserDetails({
      name: formData.name,
      role: formData.role,
      address: formData.address,
      email: formData.email, // Include email from frontend input
    });

    const res = isSignup ? await onSignup(formData) : await onLogin();
    if (isSignup) {
      const rolePath = formData.role === 'pharmacy' ? '/rx' : '/nonprofit';
      navigate(rolePath);
    } else if (res && res.user && res.user.role) {
      const rolePath = res.user.role === 'pharmacy' ? '/rx' : '/nonprofit';
      navigate(rolePath);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-toggle">
          <button
            className={isSignup ? 'active' : ''}
            onClick={() => setIsSignup(true)}
          >
            Sign Up
          </button>
          <button
            className={!isSignup ? 'active' : ''}
            onClick={() => setIsSignup(false)}
          >
            Login
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {isSignup && (
            <>
              <input
                type="text"
                name="name"
                placeholder="Organization Name"
                value={formData.name}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="address"
                placeholder="Address"
                value={formData.address}
                onChange={handleChange}
                required
              />
              <div className="role-select">
                <label>
                  <input
                    type="radio"
                    name="role"
                    value="pharmacy"
                    checked={formData.role === 'pharmacy'}
                    onChange={handleChange}
                  /> Pharmacy
                </label>
                <label>
                  <input
                    type="radio"
                    name="role"
                    value="non_profit"
                    checked={formData.role === 'non_profit'}
                    onChange={handleChange}
                  /> NonProfit
                </label>
              </div>
            </>
          )}

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <button type="submit" className="submit-btn">
            {isSignup ? 'Create Account' : 'Log In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
