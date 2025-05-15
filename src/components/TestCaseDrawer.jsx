import React from "react";
import {
  Drawer,
  Box,
  IconButton,Button
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

const TestCaseDrawer = ({ open, onClose, data, activeTab, setActiveTab, parseFormattedText }) => {
  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      transitionDuration={{ enter: 1000, exit: 1000 }}
      PaperProps={{
        sx: {
          width: "70%",
          padding: "0px 23px",
          height: "92%",
          top: "64px",
          transition: "transform 2s ease-in-out",
          transform: "translate(50%, 0%)",
          borderRadius: "20px 0px 0px 20px",
          scrollbarWidth:"thin"
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          position: "sticky",
          top: 0,
          backgroundColor: "#fff",
          zIndex: 1000,
          paddingY: 2,
          paddingX: 2,
        }}
      >
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
          <Box className="header-tabs-flex-wrapper" sx={{ display: "flex", gap: 2 }}>
            <Box className="header-dashboard-wrapper" ml={1}>
              <Box
                className={`header-dashboard ${activeTab === "testcase" ? "active" : ""}`}
                onClick={() => setActiveTab("testcase")}
              >
                Test Case
              </Box>
            </Box>
            <Box className="header-courses-wrapper">
              <Box
                className={`header-dashboard ${activeTab === "userstory" ? "active" : ""}`}
                onClick={() => setActiveTab("userstory")}
              >
                User Story
              </Box>
            </Box>
          </Box>
         <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
      {/* <Button 
      sx={{    color: 'white',
        backgroundColor:'#000080',
        textTransform:'none',
        borderRadius:'10px',
        padding:'4px 16px !important'
    }} >
        Export
      </Button> */}
      <IconButton onClick={onClose}>
        <CloseIcon />
      </IconButton>
    </Box>
        </Box>
      </Box>

      <Box sx={{ mt: 0, ml: 3, backgroundColor: "#f5f5f5", p: 2, borderRadius: "15px" }}>
        {parseFormattedText(data)}
      </Box>
    </Drawer>
  );
};

export default TestCaseDrawer;
