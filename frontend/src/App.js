import React from 'react';
import ChatInterface from './components/SearchBar';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>DeepSeek</h1>
      <ChatInterface model="deepseek" />
    </div>
  );
}

export default App;
