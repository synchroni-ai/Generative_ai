import React, { useState } from "react";
import { TextField, Button, Box, Typography, Alert, Link } from "@mui/material";
import logo from "../asessts/images/logo.png";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault(); // Prevent default form refresh
    if (username === "Admin" && password === "Admin@123") {
      setError("");
      
      // Create a token and store it with an expiry time (30 minutes from now)
      const token = "dummyToken123";  // Replace this with a real JWT token if needed
      const expiryTime = new Date().getTime() + 30 * 60 * 1000; // 30 minutes from now
      localStorage.setItem("token", token);
      localStorage.setItem("tokenExpiry", expiryTime);
      localStorage.setItem("isLoggedIn", "true");
      
      navigate("/dashboard"); // Redirect to the dashboard page
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        px: 2,
        flexDirection: "column",


        
      }}
    >
      {/* Logo Section */}
      <Box display="flex" alignItems="center" mb={2}>
        <img src={logo} alt="Logo" style={{ height: "40px", marginRight: "10px" }} />
      </Box>

      {/* Login Card */}
      <Box
        display="flex"
        bgcolor="white"
        borderRadius={3}
        overflow="hidden"
        width="100%"
        maxWidth="300px"
        border={2}
        borderColor="#e6e6e6"
        p={4}
      >
        <form style={{ width: "100%" }} onSubmit={handleLogin}>
          <Typography variant="h5" mb={2} fontWeight="bold" style={{ textAlign: "center" }}>
            Login
          </Typography>

          <TextField
            fullWidth
            label="Username"
            variant="outlined"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
          />

          <TextField
            fullWidth
            label="Password"
            variant="outlined"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
          />

          <Box display="flex" justifyContent="flex-end" mt={1} mb={2}>
            <Link href="#" underline="hover">
              Forgot Password?
            </Link>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{
              mt: 1,
              backgroundColor: "#00008B",
              textTransform: "none",
              fontWeight: "bold",
              fontSize: "16px",
            }}
          >
            Login now
          </Button>

          <Typography mt={2} textAlign="center">
            Don’t Have An Account?{" "}
            <Link href="#" underline="hover">
              Sign Up
            </Link>
          </Typography>
        </form>
      </Box>
    </Box>
  );
};

export default LoginPage;



// import React, { useState } from "react";
// import { TextField, Button, Box, Typography, Alert, Link } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import logo from "../asessts/images/logo.png";
// import loginIllustration from "../asessts/images/loginillustration1.png"; // use your illustration image here

// const LoginPage = () => {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   const handleLogin = (e) => {
//     e.preventDefault();
//     if (username === "Admin" && password === "Admin@123") {
//       setError("");
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
//     <Box
//       sx={{
//         minHeight: "100vh",
//         display: "flex",
//         alignItems: "center",
//         justifyContent: "center",
//         backgroundColor: "#f9f9f9",
//         px: 2,
//         flexDirection: "column", // <-- Add this to stack logo + card vertically
//       }}
//     >
//        {/* Logo Box */}
//   <Box mb={2}>
//     <img src={logo} alt="Logo" style={{ height: "50px" }} />
//   </Box>
//       <Box
//         display="flex"
//         bgcolor="white"
//         borderRadius={3}
//         overflow="hidden"
//         width="100%"
//         maxWidth="900px"
//         boxShadow={3}
//       >
//         {/* Left Side - Illustration */}
//         <Box
//           sx={{
//             flex: 1,
//             display: { xs: "none", md: "flex" },
//             alignItems: "center",
//             justifyContent: "center",
//             backgroundColor: "#f5f5ff",
//             p: 4,
//           }}
//         >
//           <img src={loginIllustration} alt="Login Illustration" style={{ width: "100%", maxWidth: "350px" }} />
//         </Box>

//         {/* Right Side - Login Form */}
//         <Box
//           sx={{
//             flex: 1,
//             p: 4,
//             display: "flex",
//             flexDirection: "column",
//             justifyContent: "center",
//           }}
//         >
//           {/* <Box display="flex" justifyContent="center" mb={2}>
//             <img src={logo} alt="Logo" style={{ height: "40px" }} />
//           </Box> */}

//           <Typography variant="h5" mb={2} fontWeight="bold" textAlign="center">
//             Login to your account
//           </Typography>

//           <form onSubmit={handleLogin}>
//             <TextField
//               fullWidth
//               label="Email"
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
//               <Link href="#" underline="hover" fontSize="14px">
//                 Forgot ?
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
//                 "&:hover": {
//                   backgroundColor: "#00006b",
//                 },
//               }}
//             >
//               Login now
//             </Button>

//             <Typography mt={2} textAlign="center" fontSize="14px">
//               Don’t Have An Account?{" "}
//               <Link href="#" underline="hover" fontWeight="bold">
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
