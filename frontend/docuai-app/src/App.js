import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
import Login from "./components/Login";
import Signup from "./components/Signup";
import './App.css';  // Assuming you're using the same styling
import VerifyOTP from "./components/VerifyOTP";
import Dashboard from './components/Dashboard';
import Information from './components/Information'; 
import Use from './components/Use';
import Settings from './components/Settings';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/information" element={<Information />} />
        <Route path="/how-to-use" element={<Use />} />
        <Route path="*" element={<Home />} />
        <Route path="/settings" element={<Settings />} />

      </Routes>
    </Router>
  );
}

export default App;
