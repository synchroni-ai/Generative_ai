// import React, { useState } from "react";
// import {
//   AppBar,
//   Toolbar,
//   Box,
//   Typography,
//   IconButton,
//   Avatar,
//   Menu,
//   MenuItem,
//   ListItemIcon
// } from "@mui/material";
// import setting from '../asessts/images/settings.png';
// import support from '../asessts/images/support.png';
// import LogoutIcon from '../asessts/images/Logout.png';
// import { useNavigate } from "react-router-dom";
// import logo from "../asessts/images/logo.png";
// import profilePic from "../asessts/images/profilelogo.png";

// const Header = ({ onLogout }) => {
//   const [anchorEl, setAnchorEl] = useState(null);
//   const navigate = useNavigate();

//   const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
//   const handleMenuClose = () => setAnchorEl(null);
//   const handleLogout = () => {
//     handleMenuClose();
//     if (onLogout) {
//       onLogout();
//     }
//     navigate("/");
//   };

//   return (
//     <AppBar
//       position="fixed"
//       sx={{
//         backgroundColor: "#fff",
//         boxShadow: "none",
//         zIndex: 1300,
//         borderBottom:"2px solid #f5f5f5",
//         overflowY:"hidden"
//       }}
//     >
//       <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
//         {/* Logo on the left */}
//         <Box display="flex" alignItems="center">
//           <img
//             src={logo}
//             alt="Logo"
//             style={{ height: "33px", marginLeft:"10px" }}
//           />
//         </Box>

//         {/* Profile avatar on the right */}
//         <Box display="flex" alignItems="center" gap={1} mr={2}>
//         <IconButton
//   disableRipple
//   disableFocusRipple
//   sx={{
//     '&:hover': {
//       backgroundColor: 'transparent', // Remove grey hover effect
//     },
//   }}
// >
//   <Avatar
//     alt="Profile"
//     src={profilePic}
//     sx={{ width: "34px", height: "34px" }}
//   />
// </IconButton>

//           <Typography
//             variant="subtitle1"
//             fontWeight="bold"
//             sx={{ color: "black", cursor: "pointer" }}
//             onClick={handleMenuOpen}
//           >
//             Admin
//           </Typography>
//           <Menu
//   anchorEl={anchorEl}
//   open={Boolean(anchorEl)}
//   onClose={handleMenuClose}
//   anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
//   transformOrigin={{ vertical: "top", horizontal: "right" }}
//   MenuListProps={{
//     disablePadding: true,
//     disableListWrap: true,
//     autoFocusItem: false, // ⬅ disables automatic focus (which causes highlight)
//   }}
  
//   PaperProps={{
//     elevation: 4,
//     sx: {
//       mt: 2.5,
//       ml:2.5,
//       borderRadius: 3,
//       minWidth: 180,
//       boxShadow: "0px 4px 8px rgba(0,0,0,0.1)",
//       backgroundColor:"white",
//       border:"1px solid #f5f5f5",
//       p:1
//     },
//   }}
// >
//   <MenuItem onClick={handleMenuClose} sx={{color:"#8e8e8e"}}>
//     <ListItemIcon>
//       <img src={setting} alt="Settings" style={{ width: 20, height: 20 }} />
//     </ListItemIcon>
//     Settings
//   </MenuItem>

//   <MenuItem onClick={handleMenuClose} sx={{color:"#8e8e8e"}}>
//     <ListItemIcon>
//       <img src={support} alt="Support" style={{ width: 20, height: 20 }} />
//     </ListItemIcon>
//     Support
//   </MenuItem>

//   <MenuItem
//     onClick={handleLogout}
//     sx={{color:"#8e8e8e"}}
//   >
//     <ListItemIcon>
//       <img
//         src={LogoutIcon}
//         alt="Logout"
//         style={{ width: 20, height: 20, objectFit: "contain" }}
//       />
//     </ListItemIcon>
//     Logout
//   </MenuItem>
// </Menu>

//         </Box>
//       </Toolbar>
//     </AppBar>
//   );
// };

// export default Header;


import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Box,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  Divider,
  Badge
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import searchIcon from '../asessts/images/searchicon.png';
import notificationBell from '../asessts/images/notificationbellicon.png';
import setting from '../asessts/images/settings.png';
import support from '../asessts/images/support.png';
import LogoutIcon from '../asessts/images/Logout.png';
import {  useLocation,useNavigate } from "react-router-dom";
import logo from "../asessts/images/logo1.png";
import profilePic from "../asessts/images/profilelogo.png";

const Header = ({ onLogout }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
    const location = useLocation();

  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);
  const handleLogout = () => {
    handleMenuClose();
    if (onLogout) {
      onLogout();
    }
    navigate("/");
  };
    const isActive = (path) => location.pathname === path;

  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: "#fff",
        boxShadow: "none",
        zIndex: 1300,
        borderBottom: "2px solid #f5f5f5",
        overflowY: "hidden"
      }}
    >
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        {/* Left: Logo */}
        <Box display="flex" alignItems="center" gap={30}>
          <img src={logo} alt="Logo" style={{ height: "33px", marginLeft: "10px" }} />
        

        {/* Center: Navigation Links */}
        <Box display="flex" alignItems="center" gap={6}>
  <Typography 
    onClick={() => navigate("/dashboard")}
    sx={{
      color: isActive("/dashboard") ? "#000080" : "#494949",
      fontWeight: isActive("/dashboard") ? 600 : 500,
      fontSize: "14px",
      cursor: "pointer",
    }}
  >
    Home
  </Typography>

  <Typography
    sx={{
      color: "#bdbdbd",          // lighter text to show it's disabled
      fontWeight: 500,
      fontSize: "14px",
      cursor: "not-allowed",     // indicates disabled behavior
      pointerEvents: "none",     // disables clicks
    }}
  >
    Tools
  </Typography>

  <Typography
    sx={{
      color: "#bdbdbd",
      fontWeight: 500,
      fontSize: "14px",
      cursor: "not-allowed",
      pointerEvents: "none",
    }}
  >
    Service
  </Typography>
</Box>

        </Box>

        {/* Right: Icons + Avatar */}
        <Box display="flex" alignItems="center" gap={1}>
          {/* Search (Image) */}
{/* <IconButton disableRipple>
  <img src={searchIcon} alt="Search" style={{ width: 20, height: 20 }} />
</IconButton> */}

{/* Notifications with red dot (Image) */}
<IconButton disableRipple>
  <Badge
    variant="dot"
    color="error"
    overlap="circular"
    sx={{
      "& .MuiBadge-dot": {
        top: 4,
        right: 4,
        width: 8,
        height: 8,
        borderRadius: "50%",
        border: "2px solid white",
      }
    }}
  >
    <img src={notificationBell} alt="Notifications" style={{ width: 20, height: 20 }} />
  </Badge>
</IconButton>

          {/* Divider */}
          <Divider orientation="vertical" flexItem sx={{ mx: 1, height: 28, borderColor: "#ccc",marginTop:"10px" }} />

          {/* Avatar + Admin Menu */}
          <IconButton disableRipple onClick={handleMenuOpen}>
            <Avatar src={profilePic} sx={{ width: 34, height: 34 }} />
          </IconButton>
          {/* <Typography
            variant="subtitle1"
            fontWeight="bold"
            sx={{ color: "black", cursor: "pointer" }}
            onClick={handleMenuOpen}
          >
            Admin
          </Typography> */}

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
            MenuListProps={{
              disablePadding: true,
              autoFocusItem: false,
            }}
            PaperProps={{
              elevation: 4,
              sx: {
                mt: 2.5,
                ml: 2.5,
                borderRadius: 3,
                minWidth: 180,
                boxShadow: "0px 4px 8px rgba(0,0,0,0.1)",
                backgroundColor: "white",
                border: "1px solid #f5f5f5",
                p: 1,
              },
            }}
          >
            {/* <MenuItem onClick={handleMenuClose} sx={{ color: "#8e8e8e" }}>
              <ListItemIcon>
                <img src={setting} alt="Settings" style={{ width: 20, height: 20 }} />
              </ListItemIcon>
              Settings
            </MenuItem>

            <MenuItem onClick={handleMenuClose} sx={{ color: "#8e8e8e" }}>
              <ListItemIcon>
                <img src={support} alt="Support" style={{ width: 20, height: 20 }} />
              </ListItemIcon>
              Support
            </MenuItem> */}

            <MenuItem onClick={handleLogout} sx={{ color: "#8e8e8e" }}>
              <ListItemIcon>
                <img src={LogoutIcon} alt="Logout" style={{ width: 20, height: 20, objectFit: "contain" }} />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
