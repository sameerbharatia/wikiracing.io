import React, { useState } from "react";
import Index from "./components/Index";
import NewGame from "./components/NewGame";
import JoinGame from "./components/JoinGame";
import Game from "./components/Game";
import WikiPage from "./components/WikiPage";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./App.css";

function App() {
  const [userName, setUserName] = useState("");
  const [roomCode, setRoomCode] = useState("");

  return (
    <Router>
      <div>
        <Routes>
          <Route
            path="/game/:room"
            element={<Game userName={userName} roomCode={roomCode} />}
          />

          <Route path="/join_game" element={<JoinGame setUserName={setUserName} setRoomCode={setRoomCode} />} />

          <Route path="/new_game" element={<NewGame setUserName={setUserName} setRoomCode={setRoomCode} />} />

          <Route path="/wiki/:wikiPage" element={<WikiPage roomCode={roomCode} />} />

          <Route path="/" element={<Index />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
