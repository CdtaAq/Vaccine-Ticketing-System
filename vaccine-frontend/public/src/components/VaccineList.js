import React, { useEffect, useState } from 'react';
import API from '../api';

const VaccineList = () => {
  const [vaccines, setVaccines] = useState([]);

  useEffect(() => {
    API.get('/vaccines').then(res => setVaccines(res.data));
  }, []);

  return (
    <div>
      <h2>Vaccines</h2>
      <ul>
        {vaccines.map(v => (
          <li key={v.id}>{v.name} by {v.manufacturer}</li>
        ))}
      </ul>
    </div>
  );
};

export default VaccineList;
