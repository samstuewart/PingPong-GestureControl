import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Add styles here

const API_URL = "http://127.0.0.1:5000/api";

const App = () => {
  const [frame, setFrame] = useState(null);
  const [gameState, setGameState] = useState({});
  const [isGameRunning, setIsGameRunning] = useState(false);

  const fetchGameFrame = async () => {
    try {
      const response = await axios.post(`${API_URL}/run`);
      setFrame(response.data.frame);
      setGameState(response.data.game_state);
    } catch (error) {
      console.error("Error fetching game data:", error);
    }
  };

  const startGame = async () => {
    try {
      await axios.post(`${API_URL}/start`);
      setIsGameRunning(true);
    } catch (error) {
      console.error("Error starting game:", error);
    }
  };

  const resetGame = async () => {
    try {
      await axios.post(`${API_URL}/reset`);
      setIsGameRunning(false);
    } catch (error) {
      console.error("Error resetting game:", error);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchGameFrame, 100); // Fetch updates every 100ms
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <h1 className="title">Ping Pong Game</h1>
      <div className="game-container">
        {frame ? (
          <img
            src={`data:image/jpeg;base64,${frame}`}
            alt="Game Feed"
            className="game-feed"
          />
        ) : (
          <p>Loading game...</p>
        )}
      </div>
      <div className="controls">
        <button onClick={startGame} disabled={isGameRunning}>
          Start Game
        </button>
        <button onClick={resetGame}>Reset Game</button>
      </div>
      <div className="game-info">
        <p>Player 1 Score: {gameState.score ? gameState.score[0] : 0}</p>
        <p>Player 2 Score: {gameState.score ? gameState.score[1] : 0}</p>
        {gameState.gameOver && (
          <p className="winner">
            Winner: {gameState.winner}
          </p>
        )}
      </div>
    </div>
  );
};

export default App;
