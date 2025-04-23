// import React, { useEffect } from "react";
// import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
// import LoginPage from "./components/Loginpage";
// import Dashboard from "./components/Dashboard";

// const App = () => {

//   useEffect(() => {
//     const tokenExpiry = localStorage.getItem("tokenExpiry");
//     const currentTime = new Date().getTime();

//     if (tokenExpiry && currentTime > tokenExpiry) {
//       // If the token has expired, log the user out
//       localStorage.removeItem("token");
//       localStorage.removeItem("tokenExpiry");
//       localStorage.removeItem("isLoggedIn");
//       window.location.href = "/"; // Redirect to login page
//     }
//   }, []);

//   return (
//     <Router>
//       <Routes>
//         <Route path="/" element={<LoginPage />} />
//         <Route path="/dashboard" element={<Dashboard />} />
//       </Routes>
//     </Router>
//   );
// };

// export default App;


// import React, { useEffect } from "react";
// import { BrowserRouter as Router, Route, Routes, useLocation, useNavigate } from "react-router-dom";
// import LoginPage from "./components/Loginpage";
// import Dashboard from "./components/Dashboard";

// const TokenChecker = ({ children }) => {
//   const location = useLocation();
//   const navigate = useNavigate();

//   useEffect(() => {
//     const tokenExpiry = localStorage.getItem("tokenExpiry");
//     const currentTime = new Date().getTime();

//     if (tokenExpiry && currentTime > tokenExpiry) {
//       // Token expired
//       localStorage.removeItem("token");
//       localStorage.removeItem("tokenExpiry");
//       localStorage.removeItem("isLoggedIn");

//       if (location.pathname !== "/") {
//         navigate("/"); // Redirect to login page
//       }
//     }
//   }, [location, navigate]);

//   return children;
// };

// const App = () => {
//   return (
//     <Router>
//       <TokenChecker>
//         <Routes>
//           <Route path="/" element={<LoginPage />} />
//           <Route path="/dashboard" element={<Dashboard />} />
//         </Routes>
//       </TokenChecker>
//     </Router>
//   );
// };

// export default App;


import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./components/Loginpage";
import Dashboard from "./components/./Dashboard";
// ... import other components
import TokenChecker from "./components/./TokenChecker"; // Make sure the path is correct

function App() {
  return (
    <BrowserRouter>
      <TokenChecker>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          {/* Add your protected routes here */}
        </Routes>
      </TokenChecker>
    </BrowserRouter>
  );
}

export default App;
