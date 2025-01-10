import React from 'react';
import './ScoreDisplay.css';

const ScoreDisplay = ({ leftScore, rightScore }) => {
    return (
        <div className="score-container">
            <div className="score left">Left Player: {leftScore}</div>
            <div className="score right">Right Player: {rightScore}</div>
        </div>
    );
};

export default ScoreDisplay;
