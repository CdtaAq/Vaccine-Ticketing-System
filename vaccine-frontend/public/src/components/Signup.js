import React, { useState } from 'react';
import API from '../api';

const Signup = () => {
  const [form, setForm] = useState({ email: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.post('/signup', form);
      alert('Signup successful! Please login.');
    } catch (err) {
      alert('Signup failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-3 max-w-md
