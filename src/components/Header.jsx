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
  ListItemIcon
} from "@mui/material";
import LogoutIcon from '../asessts/images/Logout.png';
import { useNavigate } from "react-router-dom";
import logo from "../asessts/images/logo.png";
import profilePic from "../asessts/images/profilelogo.png";

const Header = ({ onLogout }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();

  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);
  const handleLogout = () => {
    handleMenuClose();
    if (onLogout) {
      onLogout();
    }
    navigate("/");
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: "#fff",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        zIndex: 1300,
      }}
    >
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        {/* Logo on the left */}
        <Box display="flex" alignItems="center">
          <img
            src={logo}
            alt="Logo"
            style={{ height: "40px", marginRight: "10px" }}
          />
        </Box>

        {/* Profile avatar on the right */}
        <Box display="flex" alignItems="center" gap={1}>
          <IconButton>
            <Avatar
              alt="Profile"
              src={profilePic}
              sx={{ width: "28px", height: "28px" }}
            />
          </IconButton>
          <Typography
            variant="subtitle1"
            fontWeight="bold"
            sx={{ color: "black", cursor: "pointer" }}
            onClick={handleMenuOpen}
          >
            Admin
          </Typography>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
            PaperProps={{
              elevation: 4,
              sx: {
                mt: 0.5,
                borderRadius: 2,
                minWidth: 140,
                boxShadow: "0px 4px 16px rgba(0, 0, 0, 0.1)",
              },
            }}
          >
            <MenuItem
              onClick={handleLogout}
              sx={{
                px: 2,
                py: 1.3,
                fontWeight: 500,
                // color: "#333",
                // "&:hover": {
                //   backgroundColor: "#f0f0f0",
                // },
              }}
            >
              <ListItemIcon>
  <img
    src={LogoutIcon} // or your actual image path
    alt="Logout"
    style={{ width: 20, height: 20, objectFit: "contain" }}
  />
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