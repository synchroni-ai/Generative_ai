// import React from "react";
// import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
// import LoginPage from "./components/Authentication/Loginpage";
// import Dashboard from "./components/DocumentList/Documentlist";
// import TokenChecker from "./components/Authentication/TokenChecker";
// import Header from "./Layout/Header"; // ✅ Make sure this path is correct

// // This wrapper lets us access hooks like useNavigate inside Header placement logic
// const AppWrapper = () => {
//   const navigate = useNavigate();
//   const location = useLocation();

//   const handleLogout = () => {
//     localStorage.removeItem("isLoggedIn");
//     navigate("/");
//   };

//   // Optional: Only show header if not on login page
//   const showHeader = location.pathname !== "/";

//   return (
//     <>
//       {showHeader && <Header onLogout={handleLogout} />}
//       <TokenChecker>
//         <Routes>
//           <Route path="/" element={<LoginPage />} />
//           <Route path="/dashboard" element={<Dashboard />} />
//         </Routes>
//       </TokenChecker>
//     </>
//   );
// };

// const App = () => (
//   <BrowserRouter>
//     <AppWrapper />
//   </BrowserRouter>
// );

// export default App;



import React from 'react';
import GenAIUploader from './components/Upload/GenAi_Overview';
import UIUXConfigurator from './components/Generate/UIUXConfigurator';
import TestCaseTable from "./components/Generate/Result";
import Configuration from './components/Generate/Configuration';
import History from './components/Generate/History';
function App() {
  return (
    <div className="App">
     {/* <GenAIUploader /> */}
     <UIUXConfigurator />
     {/* <Configuration /> */}
     {/* <History /> */}
    {/* <TestCaseTable /> */}
    </div>
  );
}
 
export default App;