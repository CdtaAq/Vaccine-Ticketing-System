import React, { useState } from 'react';
import API from '../api';

const BookAppointment = () => {
  const [data, setData] = useState({
    vaccine_id: '',
    date: ''
  });

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e
