import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api'; // Flask backend URL

export const resetGame = async () => {
    return await axios.post(`${API_URL}/reset`);
};

export const getGameState = async () => {
    return await axios.get(`${API_URL}/state`);
};

export const runGame = async () => {
    return await axios.post(`${API_URL}/run`);
};
