// import React from "react";
// import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
// import LoginPage from "./components/Authentication/Loginpage";
// import Dashboard from "./components/DocumentList/Documentlist";
// import TokenChecker from "./components/Authentication/TokenChecker";
// import Header from "./Layout/Header"; // ✅ Make sure this path is correct
// import UIUXConfigurator from './components/Generate/UIUXConfigurator';

// // This wrapper lets us access hooks like useNavigate inside Header placement logic
// const AppWrapper = () => {
//   const navigate = useNavigate();
//   const location = useLocation();

//   const handleLogout = () => {
//     localStorage.removeItem("isLoggedIn");
//     navigate("/");
//   };

//   // Optional: Only show header if not on login page
// const showHeader = !["/", "/uiux-configurator"].includes(location.pathname);

//   return (
//     <>
//       {showHeader && <Header onLogout={handleLogout} />}
//       <TokenChecker>
//         <Routes>
//           <Route path="/" element={<LoginPage />} />
//           <Route path="/dashboard" element={<Dashboard />} />
//           <Route path="/uiux-configurator" element={<UIUXConfigurator />} />
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

import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
  useLocation,
  Navigate,
  matchPath
} from "react-router-dom";
import LoginPage from "./components/Authentication/Loginpage";
import Dashboard from "./components/DocumentList/Documentlist";
import TokenChecker from "./components/Authentication/TokenChecker";
import Header from "./Layout/Header";
import Footer from "./Layout/Footer";
import UIUXConfigurator from "./components/Generate/UIUXConfigurator";
import "./App.css";


// ✅ Layout wrapper for header/footer visibility logic
const LayoutWrapper = ({ children }) => {
  const location = useLocation();

  // Paths where header/footer should be hidden
  const hideHeaderPaths = ["/", "/uiux-configurator"];
  const hideFooterPaths = ["/", "/uiux-configurator"];

  const shouldHideHeader = hideHeaderPaths.some((path) =>
    matchPath(path, location.pathname)
  );

  const shouldHideFooter = hideFooterPaths.some((path) =>
    matchPath(path, location.pathname)
  );

  return (
    <>
      {!shouldHideHeader && <Header />}
      {children}
      {!shouldHideFooter && <Footer />}
    </>
  );
};

const AppWrapper = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/");
  };

  return (
    <LayoutWrapper>
      <TokenChecker>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/uiux-configurator" element={<UIUXConfigurator />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </TokenChecker>
    </LayoutWrapper>
  );
};

const App = () => (
  <BrowserRouter>
    <AppWrapper />
  </BrowserRouter>
);

export default App;




// import React from 'react';
// import GenAIUploader from './components/Upload/GenAi_Overview';
// import UIUXConfigurator from './components/Generate/UIUXConfigurator';
// import TestCaseTable from "./components/Generate/Result";
// import Configuration from './components/Generate/Configuration';
// import History from './components/Generate/History';
// function App() {
//   return (
//     <div className="App">
//      <GenAIUploader />
//      {/* <UIUXConfigurator /> */}
//      {/* <Configuration /> */}
//      {/* <History /> */}
//     {/* <TestCaseTable /> */}
//     </div>
//   );
// }
 
// export default App;