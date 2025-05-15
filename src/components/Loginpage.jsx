import React, { useState } from "react";
import {
  Box,
  Typography,
  Alert,
  Link,
  Button
} from "@mui/material";
import { motion } from "framer-motion";
import logo from "../asessts/images/logo.png";
// import sideImage from "../asessts/images/left1.png";
import sideImage from "../asessts/images/left2.png";
// import sideImage from "../asessts/images/left3.png";
import { useNavigate } from "react-router-dom";
import { CircularProgress } from '@mui/material';
import "./../asessts/css/login.css";

const LoginPage = () => {
  // const [togglePassword, setTogglePassword] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === "Admin" && password === "Admin@123") {
      const token = "dummyToken123";
      const expiryTime = new Date().getTime() + 30 * 60 * 1000;
      localStorage.setItem("token", token);
      localStorage.setItem("tokenExpiry", expiryTime);
      localStorage.setItem("isLoggedIn", "true");
      navigate("/dashboard");
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex",overflowY:"hidden",overflowX:"hidden",backgroundColor:"#f5f5f5" }}>
      {/* Left Side Image with Animation */}
      <Box
  sx={{
    flex: 1,
    display: "flex",
    alignItems: "center", // vertically centers the child
    justifyContent: "center", // optional: horizontally center it too
  }}
>
<Box
  sx={{
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative", // important!
  }}
>
  {/* Image as background */}
  <div
    style={{
      backgroundImage: `url(${sideImage})`,
      backgroundRepeat: "no-repeat",
      backgroundSize: "contain",
      backgroundPosition: "center",
      height: "98vh",
      width: "100%",
      maxWidth: 500,
      border:"1px solid #f5f5f5"
      // borderColor:"#f5f5f5"
    }}
  />
</Box>
</Box>
      {/* Right Form with Animation */}
      <div
  style={{
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "48px 32px",
  }}
>
        <div className="login-box">
          {/* <Box display="flex" justifyContent="center" mb={3}>
            <img src={logo} alt="Logo" style={{ height: 40 }} />
          </Box> */}
          <Typography  fontWeight="bold" mb={4} textAlign="center" sx={{fontSize:"22px"}}>
            Unlock the Possibilities <br/> of Generative AI
          </Typography>

          <form onSubmit={handleLogin}>
          {/* <Box sx={{ maxWidth: 300, mx: "auto" }}> */}
          <div className="login-form-group">
  <input 
    className="login-form-control" 
    type="text" 
    placeholder="Username" 
    required 
    onChange={(e) => setUsername(e.target.value)} 
    value={username} 
  />
</div>

<div className="login-form-group" style={{ position: "relative",marginBottom:"20px" }}>
  <input 
    className="login-form-control" 
    type={showPassword ? "text" : "password"} 
    placeholder="Password" 
    required 
    onChange={(e) => setPassword(e.target.value)} 
    value={password} 
  />
</div>
      {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
  <Button
                fullWidth
                variant="contained"
                sx={{
                  marginTop: "16px",
                  borderRadius: "20px",
                  textTransform: "none",
                  height: "32px",
                  width: "200px",
                  backgroundColor: "#000080",
                  color: "white",
                  "&:hover": {
                    backgroundColor: "#000066",
                  },
                  "&.Mui-disabled": {
                    backgroundColor: "#000080",
                    color: "white",
                    opacity: 1,
                  },
                }}
                type="submit"
                disabled={loading}
              >
                {loading ? <CircularProgress size={16} color="inherit" /> : "Sign In"}
              </Button>

            <Typography mt={2} mb={2}textAlign="center" sx={{fontSize:"12px"}}>
              Don’t Have An Account?{" "}
              <Link href="#" underline="hover">
                Sign Up
              </Link>
            </Typography>
            <Box className="power" display="flex" justifyContent="center" alignItems="center" mb={3} mt={5}>
  <Typography sx={{ fontSize: "12px", mr: 1 }}>
    Powered by
  </Typography>
  <img src={logo} alt="Logo" style={{ height: 20 }} />
</Box>

          </form>
          </div>
</div>
    </Box>
  );
};

export default LoginPage;