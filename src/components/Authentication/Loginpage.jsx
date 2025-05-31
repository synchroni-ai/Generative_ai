// import React, { useState } from "react";
// import {
//   Box,
//   Typography,
//   Alert,
//   Link,
//   Button,
//   IconButton
// } from "@mui/material";
// import { motion } from "framer-motion";
// import logo from "../../asessts/images/logo1.png";
// import sideImage from "../../asessts/images/Left.png";
// import Logo from "../../asessts/images/logo1.png";
// import topRightImage from "../../asessts/images/toprightcorner.png";
// // import sideImage from "../../asessts/images/left2.png";
// // import sideImage from "../asessts/images/left3.png";
// import Visibility from "@mui/icons-material/Visibility";
// import VisibilityOff from "@mui/icons-material/VisibilityOff";
// import { useNavigate } from "react-router-dom";
// import { adminAxios } from '../../asessts/axios/index';
// import { CircularProgress } from '@mui/material';
// import "./../../asessts/css/login.css";

// const LoginPage = () => {
//   // const [togglePassword, setTogglePassword] = useState(false);
//   const [showPassword, setShowPassword] = useState(false);
//   const [username, setUsername] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   const handleLogin = async (e) => {
//     e.preventDefault();
//     setLoading(true);
//     setError("");

//     try {
//       const response = await adminAxios.post("/api/v1/auth/token", {
//         username,
//         password,
//       });

//       const { access_token } = response.data;
//       const expiryTime = new Date().getTime() + 30 * 60 * 1000; // 30 mins

//       localStorage.setItem("token", access_token);
//       localStorage.setItem("tokenExpiry", expiryTime);
//       localStorage.setItem("isLoggedIn", "true");

//       navigate("/dashboard");
//     } catch (err) {
//       setError("Invalid username or password");
//     } finally {
//       setLoading(false);
//     }
//   };


//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", overflowY: "hidden", overflowX: "hidden" }}>
//       {/* Top-left logo */}
//       {/* <Box
//     component="img"
//     src={Logo}
//     alt="AI Logo"
//     sx={{
//       position: "absolute",
//       top: 16,
//       left: 16,
//       height: 40,
//       width: "auto",
//       zIndex: 1000,
//     }}
//   /> */}
//       {/* ✅ Left side with background color */}
//       <Box
//         sx={{
//           flex: 1,
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           backgroundColor: "#FFFDF8", // ← Add your desired background color
//         }}
//       >
//         <Box
//           sx={{
//             flex: 1,
//             display: "flex",
//             alignItems: "center",
//             justifyContent: "center",
//             position: "relative",
//           }}
//         >
//           {/* Image as background */}
//           <div
//             style={{
//               backgroundImage: `url(${sideImage})`,
//               backgroundRepeat: "no-repeat",
//               backgroundSize: "contain",
//               backgroundPosition: "center",
//               height: "98vh",   // ✅ Set exact height
//               width: "350px",    // ✅ Set exact width
//               // border: "1px solid #f5f5f5",
//             }}
//           />
//         </Box>
//       </Box>
//       {/* Right Form with Animation */}
//       <div
//         style={{
//           flex: 1,
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           padding: "48px 32px",
//           position: "relative", // 🔑 Needed for positioning the top-right image
//         }}
//       >
//         <img
//           src={topRightImage} // replace with your image variable or path
//           alt="Top Right Decoration"
//           style={{
//             position: "absolute",
//             top: 0,
//             right: 0,
//             width: 100,     // Adjust size as needed
//             height: "auto",
//             zIndex: 1,
//           }}
//         />
//         <div className="login-box">
//           {/* <Box display="flex" justifyContent="center" mb={3}>
//             <img src={logo} alt="Logo" style={{ height: 40 }} />
//           </Box> */}
//           <Box textAlign="left" mb={3}>
//             {/* Heading */}
//             <Typography variant="h6" sx={{ fontWeight: 400 }}>
//               Welcome to
//             </Typography>

//             {/* Gradient Text */}
//             <Typography
//               variant="h5"
//               sx={{
//                 fontWeight: "bold",
//                 background: "linear-gradient(90deg, #8e2de2, #4a00e0)",
//                 WebkitBackgroundClip: "text",
//                 WebkitTextFillColor: "transparent",
//                 display: "inline-block",
//                 marginBottom: "10px"
//               }}
//             >
//               Generative AI
//             </Typography>
//             {/* Subtext */}
//             <Typography
//               variant="body2"
//               mt={2}
//               sx={{ color: "#888888", maxWidth: 320, margin: "0 auto", marginTop: '10px' }}
//             >
//               "A smart assistant to help you experiment, validate, and perfect your work using the latest in generative AI."
//             </Typography>

//           </Box>

//           <Typography
//             variant="subtitle1"

//             fontWeight={700}
//             sx={{ color: "#333", textAlign: "left", marginBottom: "10px",fontSize:"18px" }}
//           >
//             Login
//           </Typography>

//           <form onSubmit={handleLogin}>
//             {/* <Box sx={{ maxWidth: 300, mx: "auto" }}> */}
//             <div className="login-form-group">
//               <input
//                 className="login-form-control"
//                 type="text"
//                 placeholder="Username"
//                 required
//                 onChange={(e) => setUsername(e.target.value)}
//                 value={username}
//               />
//             </div>

//             <div className="login-form-group" style={{ position: "relative", marginBottom: "20px" }}>
//               <input
//                 className="login-form-control"
//                 type={showPassword ? "text" : "password"}
//                 placeholder="Password"
//                 required
//                 onChange={(e) => setPassword(e.target.value)}
//                 value={password}
//                     style={{ paddingRight: "36px" }} // space for icon
//               />
//               <IconButton
//               disableRipple
//     onClick={() => setShowPassword((prev) => !prev)}
//     sx={{
//       position: "absolute",
//       right: 8,
//       top: "50%",
//       transform: "translateY(-50%)",
//       color: "#aaa",
//       padding: "4px",
//     }}
//   >
//     {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
//   </IconButton>
//             </div>
//             {error && (
//               <Alert severity="error" sx={{ mt: 2 }}>
//                 {error}
//               </Alert>
//             )}
//             <Button
//               fullWidth
//               variant="contained"
//               sx={{
//                 marginTop: "16px",
//                 borderRadius: "20px",
//                 textTransform: "none",
//                 height: "32px",
//                 width: "200px",
//                 backgroundColor: "#000080",
//                 color: "white",
//                 "&:hover": {
//                   backgroundColor: "#000066",
//                 },
//                 "&.Mui-disabled": {
//                   backgroundColor: "#000080",
//                   color: "white",
//                   opacity: 1,
//                 },
//               }}
//               type="submit"
//               disabled={loading}
//             >
//               {loading ? <CircularProgress size={16} color="inherit" /> : "Sign In"}
//             </Button>

//             {/* <Typography mt={2} textAlign="center" sx={{fontSize:"12px"}}>
//               Don’t Have An Account?{" "}
//              <Link
//   href="#"
//   underline="hover"
//   onClick={(e) => e.preventDefault()} // prevent action
//   sx={{
//     pointerEvents: 'none',   // disable click
//     color: 'text.disabled',  // greyed out look
//     cursor: 'not-allowed',
//   }}
// >
//   Sign Up
// </Link>
//             </Typography> */}
//             <Box className="power" display="flex" justifyContent="center" alignItems="center" mb={3} mt={5}>
//               <Typography sx={{ fontSize: "12px", mr: 1 }}>
//                 Powered by
//               </Typography>
//               <img src={logo} alt="logo" style={{ height: 20 }} />
//             </Box>

//           </form>
//         </div>
//       </div>
//     </Box>
//   );
// };

// export default LoginPage;


import React, { useState } from "react";
import {
  Box,
  Typography,
  Alert,
  Button,
  IconButton
} from "@mui/material";
import logo from "../../asessts/images/logo1.png";
import sideImage from "../../asessts/images/Left.png";
import topRightImage from "../../asessts/images/toprightcorner.png";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { useNavigate } from "react-router-dom";
import { adminAxios } from '../../asessts/axios/index';
import { CircularProgress } from '@mui/material';
import "./../../asessts/css/login.css";

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // const handleLogin = async (e) => {
  //   e.preventDefault();
  //   setLoading(true);
  //   setError("");

  //   try {
  //     const response = await adminAxios.post("/api/v1/auth/token", {
  //       username,
  //       password,
  //     });

  //     const { access_token } = response.data;
  //     const expiryTime = new Date().getTime() + 30 * 60 * 1000;

  //     localStorage.setItem("token", access_token);
  //     localStorage.setItem("tokenExpiry", expiryTime);
  //     localStorage.setItem("isLoggedIn", "true");

  //     navigate("/dashboard");
  //   } catch (err) {
  //     setError("Invalid username or password");
  //   } finally {
  //     setLoading(false);
  //   }
  // };
const handleLogin = async (e) => {
  e.preventDefault();
  setLoading(true);
  setError("");

  const defaultUsername = "admin";
  const defaultPassword = "admin123";

  try {
    const response = await adminAxios.post("/api/v1/auth/token", {
      username,
      password,
    });

    const { access_token } = response.data;
    const expiryTime = new Date().getTime() + 30 * 60 * 1000;

    localStorage.setItem("token", access_token);
    localStorage.setItem("tokenExpiry", expiryTime);
    localStorage.setItem("isLoggedIn", "true");

    navigate("/dashboard");
  } catch (err) {
    // Fallback to default credentials if backend fails
    if (username === defaultUsername && password === defaultPassword) {
      localStorage.setItem("token", "fallback-token");
      localStorage.setItem("tokenExpiry", new Date().getTime() + 30 * 60 * 1000);
      localStorage.setItem("isLoggedIn", "true");

      navigate("/dashboard");
    } else {
      setError("Invalid username or password");
    }
  } finally {
    setLoading(false);
  }
};



  return (
    <Box className="loginpage_container">
      <Box className="loginpage_left">
        <Box className="loginpage_sideImageWrapper">
          <div
            className="loginpage_sideImage"
            style={{ backgroundImage: `url(${sideImage})` }}
          />
        </Box>
      </Box>

      <div className="loginpage_right">
        <img src={topRightImage} alt="Top Right Decoration" className="loginpage_topRightImage" />

        <div className="loginpage_box">
          <Box textAlign="left" mb={3}>
            <Typography variant="h6" className="loginpage_welcome">Welcome to</Typography>
            <Typography variant="h5" className="loginpage_gradientText">Generative AI</Typography>
            <Typography variant="body2" className="loginpage_subText">
              "A smart assistant to help you experiment, validate, and perfect your work using the latest in generative AI."
            </Typography>
          </Box>

          <Typography variant="subtitle1" className="loginpage_loginTitle">Login</Typography>

          <form onSubmit={handleLogin}>
            <div className="loginpage_formGroup">
              <input
                className="loginpage_input"
                type="text"
                placeholder="Username"
                required
                onChange={(e) => setUsername(e.target.value)}
                value={username}
              />
            </div>

            <div className="loginpage_formGroup loginpage_passwordWrapper">
              <input
                className="loginpage_input"
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                required
                onChange={(e) => setPassword(e.target.value)}
                value={password}
              />
              <IconButton
                disableRipple
                onClick={() => setShowPassword(prev => !prev)}
                className="loginpage_eyeIcon"
              >
                {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
              </IconButton>
            </div>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
            )}

            <Button
              fullWidth
              variant="contained"
              type="submit"
              disabled={loading}
              className="loginpage_button"
            >
              {loading ? <CircularProgress size={16} color="inherit" /> : "Sign In"}
            </Button>

            <Box className="loginpage_power">
              <Typography sx={{ fontSize: "12px", mr: 1 }}>Powered by</Typography>
              <img src={logo} alt="logo" style={{ height: 20 }} />
            </Box>
          </form>
        </div>
      </div>
    </Box>
  );
};

export default LoginPage;
