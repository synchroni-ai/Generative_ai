

// import React from "react";
// import { BrowserRouter, Routes, Route } from "react-router-dom";
// import LoginPage from "./components/Loginpage";
// import Dashboard from "./components/./Documentlist";
// // ... import other components
// import TokenChecker from "./components/./TokenChecker"; // Make sure the path is correct

// function App() {
//   return (
//     <BrowserRouter>
//       <TokenChecker>
//         <Routes>
//           <Route path="/" element={<LoginPage />} />
//           <Route path="/dashboard" element={<Dashboard />} />
//         </Routes>
//       </TokenChecker>
//     </BrowserRouter>
//   );
// }

// export default App;


import React from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import LoginPage from "./components/Loginpage";
import Dashboard from "./components/Documentlist";
import TokenChecker from "./components/TokenChecker";
import Header from "./components/Header"; // ✅ Make sure this path is correct

// This wrapper lets us access hooks like useNavigate inside Header placement logic
const AppWrapper = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/");
  };

  // Optional: Only show header if not on login page
  const showHeader = location.pathname !== "/";

  return (
    <>
      {showHeader && <Header onLogout={handleLogout} />}
      <TokenChecker>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </TokenChecker>
    </>
  );
};

const App = () => (
  <BrowserRouter>
    <AppWrapper />
  </BrowserRouter>
);

export default App;
