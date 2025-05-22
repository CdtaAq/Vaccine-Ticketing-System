import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import VaccineList from './components/VaccineList';
import { setAuthToken } from './api';

function App() {
  const [token, setToken] = useState(null);

  const handleLogin = token => {
    setToken(token);
    setAuthToken(token);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login onLogin={handleLogin} />} />
        <Route path="/vaccines" element={<VaccineList />} />
      </Routes>
    </Router>
  );
}

export default App;
