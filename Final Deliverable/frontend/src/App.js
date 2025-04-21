import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import SandwichReport from './components/SandwichDetails';
import './App.css';
import sandwichIcon from './sandwich.svg';

function App() {
  const [sandwichPositions, setSandwichPositions] = useState([]);
  const animationFrameRef = useRef(null);
  
  // Initialize sandwich positions with buffer zones
  useEffect(() => {
    const numSandwiches = 30;
    const bufferZone = 80; // Buffer zone in pixels
    const positions = [];
    
    // Create initial positions with buffer zones
    for (let i = 0; i < numSandwiches; i++) {
      let validPosition = false;
      let attempts = 0;
      let position;
      
      // Try to find a position that doesn't overlap with existing sandwiches
      while (!validPosition && attempts < 50) {
        const top = 10 + Math.random() * 80;
        const left = 10 + Math.random() * 80;
        
        // Check if this position is far enough from all other sandwiches
        validPosition = true;
        for (const existingPos of positions) {
          const distance = Math.sqrt(
            Math.pow((top - existingPos.top) * window.innerHeight / 100, 2) + 
            Math.pow((left - existingPos.left) * window.innerWidth / 100, 2)
          );
          
          if (distance < bufferZone) {
            validPosition = false;
            break;
          }
        }
        
        if (validPosition) {
          position = {
            top,
            left,
            rotation: Math.random() * 360,
            speed: 0.5 + Math.random() * 1.5,
            direction: Math.random() * Math.PI * 2,
            size: 0.8 + Math.random() * 0.4 // Random size for variety
          };
        }
        
        attempts++;
      }
      
      if (position) {
        positions.push(position);
      }
    }
    
    setSandwichPositions(positions);
    
    // Start animation loop
    const animate = () => {
      setSandwichPositions(prevPositions => {
        const newPositions = [...prevPositions];
        
        // First pass: update positions
        for (let i = 0; i < newPositions.length; i++) {
          const pos = newPositions[i];
          
          // Calculate new position
          const newTop = pos.top + Math.sin(pos.direction) * pos.speed * 0.05;
          const newLeft = pos.left + Math.cos(pos.direction) * pos.speed * 0.05;
          
          // Check for collisions with screen boundaries
          let direction = pos.direction;
          let top = newTop;
          let left = newLeft;
          
          if (newTop < 5 || newTop > 95) {
            direction = -direction;
            top = pos.top;
          }
          
          if (newLeft < 5 || newLeft > 95) {
            direction = Math.PI - direction;
            left = pos.left;
          }
          
          // Update position
          newPositions[i] = {
            ...pos,
            top,
            left,
            direction
          };
        }
        
        // Second pass: check for collisions between sandwiches
        for (let i = 0; i < newPositions.length; i++) {
          for (let j = i + 1; j < newPositions.length; j++) {
            const pos1 = newPositions[i];
            const pos2 = newPositions[j];
            
            const distance = Math.sqrt(
              Math.pow((pos1.top - pos2.top) * window.innerHeight / 100, 2) + 
              Math.pow((pos1.left - pos2.left) * window.innerWidth / 100, 2)
            );
            
            // Calculate collision threshold based on sandwich sizes
            const collisionThreshold = (bufferZone / 100) * (pos1.size + pos2.size) / 2;
            
            if (distance < collisionThreshold) {
              // Collision detected - calculate bounce direction
              
              // Calculate normal vector (perpendicular to collision)
              const nx = (pos1.top - pos2.top) / distance;
              const ny = (pos1.left - pos2.left) / distance;
              
              // Calculate relative velocity
              const relativeSpeedX = Math.sin(pos1.direction) * pos1.speed - 
                                    Math.sin(pos2.direction) * pos2.speed;
              const relativeSpeedY = Math.cos(pos1.direction) * pos1.speed - 
                                    Math.cos(pos2.direction) * pos2.speed;
              
              // Calculate dot product of relative velocity and normal
              const dotProduct = relativeSpeedX * nx + relativeSpeedY * ny;
              
              // Calculate new direction after bounce
              const newDirection1 = Math.atan2(
                Math.sin(pos1.direction) - 2 * dotProduct * nx,
                Math.cos(pos1.direction) - 2 * dotProduct * ny
              );
              
              const newDirection2 = Math.atan2(
                Math.sin(pos2.direction) + 2 * dotProduct * nx,
                Math.cos(pos2.direction) + 2 * dotProduct * ny
              );
              
              // Add a small random factor to make the bounce more natural
              const randomFactor1 = (Math.random() - 0.5) * 0.2;
              const randomFactor2 = (Math.random() - 0.5) * 0.2;
              
              // Update directions
              newPositions[i] = {
                ...newPositions[i],
                direction: newDirection1 + randomFactor1
              };
              
              newPositions[j] = {
                ...newPositions[j],
                direction: newDirection2 + randomFactor2
              };
              
              // Move sandwiches apart slightly to prevent sticking
              const overlap = collisionThreshold - distance;
              const moveX = nx * overlap * 0.5;
              const moveY = ny * overlap * 0.5;
              
              newPositions[i] = {
                ...newPositions[i],
                top: newPositions[i].top + moveY,
                left: newPositions[i].left + moveX
              };
              
              newPositions[j] = {
                ...newPositions[j],
                top: newPositions[j].top - moveY,
                left: newPositions[j].left - moveX
              };
              
              // Slightly increase speed after collision for more dynamic movement
              newPositions[i].speed = Math.min(newPositions[i].speed * 1.1, 3.0);
              newPositions[j].speed = Math.min(newPositions[j].speed * 1.1, 3.0);
            }
          }
        }
        
        // Third pass: update rotation
        for (let i = 0; i < newPositions.length; i++) {
          const pos = newPositions[i];
          const rotationSpeed = pos.speed * 2;
          newPositions[i] = {
            ...pos,
            rotation: pos.rotation + rotationSpeed
          };
        }
        
        return newPositions;
      });
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animationFrameRef.current = requestAnimationFrame(animate);
    
    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);
  
  // Render sandwiches based on their positions
  const sandwiches = sandwichPositions.map((pos, index) => (
    <div 
      key={index} 
      className="floating-sandwich"
      style={{
        backgroundImage: `url(${sandwichIcon})`,
        top: `${pos.top}%`,
        left: `${pos.left}%`,
        transform: `rotate(${pos.rotation}deg)`,
        transition: 'transform 0.1s ease-out',
        width: `${60 * pos.size}px`,
        height: `${60 * pos.size}px`
      }}
    />
  ));

  return (
    <Router>
      <div className="App">
        <div className="sandwich-background">
          {sandwiches}
        </div>
        <div className="content-wrapper">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/sandwich-report/:customerKey" element={<SandwichReport />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
