import React, { useState } from 'react';
import API from '../api';

const AddVaccine = () => {
  const [vaccine, setVaccine] = useState({
    name: '',
    manufacturer: ''
  });

  const handleChange = (e) => {
    setVaccine({ ...vaccine, [e.target.name]: e.target.value });
  };

