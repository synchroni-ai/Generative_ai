// import React, { useState } from "react";
// import { TextField, Button, Box, Typography, Alert, Link } from "@mui/material";
// import logo from "../asessts/images/logo.png";
// import { useNavigate } from "react-router-dom";

// const LoginPage = () => {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   const handleLogin = (e) => {
//     e.preventDefault(); // Prevent default form refresh
//     if (username === "Admin" && password === "Admin@123") {
//       setError("");
      
//       // Create a token and store it with an expiry time (30 minutes from now)
//       const token = "dummyToken123";  // Replace this with a real JWT token if needed
//       const expiryTime = new Date().getTime() + 30 * 60 * 1000; // 30 minutes from now
//       localStorage.setItem("token", token);
//       localStorage.setItem("tokenExpiry", expiryTime);
//       localStorage.setItem("isLoggedIn", "true");
      
//       navigate("/dashboard"); // Redirect to the dashboard page
//     } else {
//       setError("Invalid username or password");
//     }
//   };

//   return (
//     <Box
//       sx={{
//         minHeight: "100vh",
//         display: "flex",
//         justifyContent: "center",
//         alignItems: "center",
//         px: 2,
//         flexDirection: "column",


        
//       }}
//     >
//       {/* Logo Section */}
//       <Box display="flex" alignItems="center" mb={2}>
//         <img src={logo} alt="Logo" style={{ height: "40px", marginRight: "10px" }} />
//       </Box>

//       {/* Login Card */}
//       <Box
//         display="flex"
//         bgcolor="white"
//         borderRadius={3}
//         overflow="hidden"
//         width="100%"
//         maxWidth="300px"
//         border={2}
//         borderColor="#e6e6e6"
//         p={4}
//       >
//         <form style={{ width: "100%" }} onSubmit={handleLogin}>
//           <Typography variant="h5" mb={2} fontWeight="bold" style={{ textAlign: "center" }}>
//             Login
//           </Typography>

//           <TextField
//             fullWidth
//             label="Username"
//             variant="outlined"
//             value={username}
//             onChange={(e) => setUsername(e.target.value)}
//             margin="normal"
//           />

//           <TextField
//             fullWidth
//             label="Password"
//             variant="outlined"
//             type="password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             margin="normal"
//           />

//           <Box display="flex" justifyContent="flex-end" mt={1} mb={2}>
//             <Link href="#" underline="hover">
//               Forgot Password?
//             </Link>
//           </Box>

//           {error && (
//             <Alert severity="error" sx={{ mb: 2 }}>
//               {error}
//             </Alert>
//           )}

//           <Button
//             type="submit"
//             fullWidth
//             variant="contained"
//             color="primary"
//             sx={{
//               mt: 1,
//               backgroundColor: "#00008B",
//               textTransform: "none",
//               fontWeight: "bold",
//               fontSize: "16px",
//             }}
//           >
//             Login now
//           </Button>

//           <Typography mt={2} textAlign="center">
//             Don’t Have An Account?{" "}
//             <Link href="#" underline="hover">
//               Sign Up
//             </Link>
//           </Typography>
//         </form>
//       </Box>
//     </Box>
//   );
// };

// export default LoginPage;


// import React, { useState } from "react";
// import {
//   TextField,
//   Button,
//   Box,
//   Typography,
//   Alert,
//   Link,
//   Paper,
// } from "@mui/material";
// import logo from "../asessts/images/logo.png";
// import sideImage from "../asessts/images/loginillustration1.png"; // ➜ Add a side image here
// import { useNavigate } from "react-router-dom";

// const LoginPage = () => {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   const handleLogin = (e) => {
//     e.preventDefault();
//     if (username === "Admin" && password === "Admin@123") {
//       const token = "dummyToken123";
//       const expiryTime = new Date().getTime() + 30 * 60 * 1000;
//       localStorage.setItem("token", token);
//       localStorage.setItem("tokenExpiry", expiryTime);
//       localStorage.setItem("isLoggedIn", "true");
//       navigate("/dashboard");
//     } else {
//       setError("Invalid username or password");
//     }
//   };

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex" }}>
//       {/* Left Section with Image */}
//       <Box
//         sx={{
//           flex: 1,
//           display: { xs: "none", md: "flex" },
//           backgroundImage: `url(${sideImage})`,
//           backgroundRepeat: "no-repeat",
//           backgroundSize: "cover",
//           backgroundPosition: "center",
//         }}
//       />

//       {/* Right Section with Form */}
//       <Box
//         component={Paper}
//         elevation={3}
//         sx={{
//           flex: 1,
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           px: 4,
//           py: 6,
//         }}
//       >
//         <Box sx={{ width: "100%", maxWidth: 400 }}>
//           <Box display="flex" justifyContent="center" mb={3}>
//             <img src={logo} alt="Logo" style={{ height: 40 }} />
//           </Box>

//           <Typography variant="h5" fontWeight="bold" mb={3} textAlign="center">
//             Login
//           </Typography>

//           <form onSubmit={handleLogin}>
//             <TextField
//               fullWidth
//               label="Username"
//               variant="outlined"
//               value={username}
//               onChange={(e) => setUsername(e.target.value)}
//               margin="normal"
//             />
//             <TextField
//               fullWidth
//               label="Password"
//               variant="outlined"
//               type="password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               margin="normal"
//             />
//             <Box display="flex" justifyContent="flex-end" mt={1}>
//               <Link href="#" underline="hover">
//                 Forgot Password?
//               </Link>
//             </Box>

//             {error && (
//               <Alert severity="error" sx={{ mt: 2 }}>
//                 {error}
//               </Alert>
//             )}

//             <Button
//               type="submit"
//               fullWidth
//               variant="contained"
//               sx={{
//                 mt: 3,
//                 backgroundColor: "#00008B",
//                 textTransform: "none",
//                 fontWeight: "bold",
//                 fontSize: "16px",
//               }}
//             >
//               Login now
//             </Button>

//             <Typography mt={2} textAlign="center">
//               Don’t Have An Account?{" "}
//               <Link href="#" underline="hover">
//                 Sign Up
//               </Link>
//             </Typography>
//           </form>
//         </Box>
//       </Box>
//     </Box>
//   );
// };

// export default LoginPage;


// import React, { useState } from "react";
// import {
//   TextField,
//   Button,
//   Box,
//   Typography,
//   Alert,
//   Link,
//   Paper,
// } from "@mui/material";
// import { motion } from "framer-motion";
// import logo from "../asessts/images/logo.png";
// // import sideImage from "../asessts/images/left1.png";
// // import sideImage from "../asessts/images/left2.png";
// import sideImage from "../asessts/images/left3.png";
// import { useNavigate } from "react-router-dom";

// const LoginPage = () => {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   const handleLogin = (e) => {
//     e.preventDefault();
//     if (username === "Admin" && password === "Admin@123") {
//       const token = "dummyToken123";
//       const expiryTime = new Date().getTime() + 30 * 60 * 1000;
//       localStorage.setItem("token", token);
//       localStorage.setItem("tokenExpiry", expiryTime);
//       localStorage.setItem("isLoggedIn", "true");
//       navigate("/dashboard");
//     } else {
//       setError("Invalid username or password");
//     }
//   };

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex",overflowY:"hidden",overflowX:"hidden" }}>
//       {/* Left Side Image with Animation */}
//       <Box
//   sx={{
//     flex: 1,
//     display: "flex",
//     alignItems: "center", // vertically centers the child
//     justifyContent: "center", // optional: horizontally center it too
//   }}
// >
//   <motion.div
//     initial={{ y: 300, opacity: 0 }}
//     animate={{ y: 0, opacity: 1 }}
//     transition={{ duration: 3, ease: "easeOut" }}
//     style={{
//       backgroundImage: `url(${sideImage})`,
//       backgroundRepeat: "no-repeat",
//       backgroundSize: "contain",
//       backgroundPosition: "center",
//       height: "80vh",
//       width: "100%",
//       maxWidth: 500, // optional: controls the max width of the image container
//     }}
//   />
// </Box>


//       {/* Right Form with Animation */}
//       <motion.div
//         initial={{ x: 400, opacity: 0 }}
//         animate={{ x: 0, opacity: 1 }}
//         transition={{ duration: 3, ease: "easeOut" }}
//         style={{
//           flex: 1,
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           padding: "48px 32px",
//         }}
//       >
//         <Paper elevation={0} sx={{ width: "100%", maxWidth: 350, p: 4,border:"1px solid #e6e6e6" }}>
//           <Box display="flex" justifyContent="center" mb={3}>
//             <img src={logo} alt="Logo" style={{ height: 40 }} />
//           </Box>

//           <Typography variant="h5" fontWeight="bold" mb={3} textAlign="center">
//             Login
//           </Typography>

//           <form onSubmit={handleLogin}>
//           <Box sx={{ maxWidth: 300, mx: "auto" }}>
//             <TextField
//               fullWidth
//               label="Username"
//               variant="outlined"
//               value={username}
//               onChange={(e) => setUsername(e.target.value)}
//               margin="normal"
//             />
//             <TextField
//               fullWidth
//               label="Password"
//               variant="outlined"
//               type="password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               margin="normal"
//             />
            
//             {/* <Box display="flex" justifyContent="flex-end" mt={1}>
//               <Link href="#" underline="hover">
//                 Forgot Password?
//               </Link>
//             </Box> */}
//             </Box>

//             {error && (
//               <Alert severity="error" sx={{ mt: 2 }}>
//                 {error}
//               </Alert>
//             )}
// <Box sx={{ maxWidth: 200, mx: "auto" }}>

//             <Button
//               type="submit"
//               fullWidth
//               variant="contained"
//               sx={{
//                 mt: 3,
//                 backgroundColor: "#00008B",
//                 textTransform: "none",
//                 fontWeight: "bold",
//                 fontSize: "16px",
//               }}
//             >
//               Login
//             </Button>
//             </Box>

//             <Typography mt={2} textAlign="center">
//               Don’t Have An Account?{" "}
//               <Link href="#" underline="hover">
//                 Sign Up
//               </Link>
//             </Typography>
//           </form>
//         </Paper>
//       </motion.div>
//     </Box>
//   );
// };

// export default LoginPage;


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
import sideImage from "../asessts/images/left1.png";
// import sideImage from "../asessts/images/left2.png";
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
    <Box sx={{ minHeight: "100vh", display: "flex",overflowY:"hidden",overflowX:"hidden" }}>
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
      height: "80vh",
      width: "100%",
      maxWidth: 500,
    }}
  />

  {/* Logo overlay */}
  <img
    src={logo}
    alt="Logo"
    style={{
      position: "absolute",
      top: "100px", // adjust as needed
      left: "100px", // adjust as needed
      height: "33px", // adjust size
      zIndex: 2,
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
        {/* <Paper elevation={0} sx={{ width: "100%", maxWidth: 350, p: 4,border:"1px solid #e6e6e6" }}> */}
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

            <Typography mt={2} textAlign="center" sx={{fontSize:"12px"}}>
              Don’t Have An Account?{" "}
              <Link href="#" underline="hover">
                Sign Up
              </Link>
            </Typography>
          </form>
          </div>
        {/* </Paper> */}
</div>
    </Box>
  );
};

export default LoginPage;