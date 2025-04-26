

import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./components/Loginpage";
import Dashboard from "./components/./Documentlist";
// ... import other components
import TokenChecker from "./components/./TokenChecker"; // Make sure the path is correct

function App() {
  return (
    <BrowserRouter>
      <TokenChecker>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </TokenChecker>
    </BrowserRouter>
  );
}

export default App;
