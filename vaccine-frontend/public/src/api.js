import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000', // Your FastAPI backend
});

export const setAuthToken = token => {
  if (token) {
    API.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete API.defaults.headers.common['Authorization'];
  }
};

export default API;
