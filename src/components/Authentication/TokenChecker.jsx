import  { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const TokenChecker = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const checkToken = () => {
      const tokenExpiry = localStorage.getItem("tokenExpiry");
      const currentTime = new Date().getTime();

      if (tokenExpiry && currentTime > tokenExpiry) {
        // Token expired
        localStorage.removeItem("token");
        localStorage.removeItem("tokenExpiry");
        localStorage.removeItem("isLoggedIn");

        if (location.pathname !== "/") {
          navigate("/"); // Redirect to login page
        }
      }
    };

    // Check immediately on mount
    checkToken();

    // Then check every 10 seconds
    const interval = setInterval(checkToken, 10000);

    return () => clearInterval(interval); // Cleanup on unmount
  }, [location, navigate]);

  return children;
};

export default TokenChecker;
