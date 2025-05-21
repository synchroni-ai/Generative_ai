// import React, { useState } from 'react';
// import { Box, Typography, IconButton } from '@mui/material';
// import ArrowBackIcon from '@mui/icons-material/ArrowBack';
// import history from "./../../asessts/images/history.png";
// import Configuration from './Configuration';
// import TestCaseTable from './Result'; // Import the Results component

// const UIUXConfigurator = () => {
//   const [activeTab, setActiveTab] = useState('Configuration');

//   return (
//     <Box fontFamily="'Poppins', sans-serif" sx={{ padding: '24px 0px', scrollbarWidth: "thin" }}>
//       {/* Header */}
//       <Box display="flex" alignItems="flex-start" mb={3}>
//         <IconButton sx={{ mt: '2px', mr: 2 }}>
//           <ArrowBackIcon />
//         </IconButton>
//         <Box>
//           <Typography fontWeight={600} fontSize={24} mb={1}>
//             Complete UI/UX Project Assets – Wireframes...
//           </Typography>
//           <Typography fontSize={14} color="text.secondary">
//             A consolidated collection of design flows, screen layouts, content plans, and feedback documents for LMS and CMS modules.
//           </Typography>
//         </Box>
//       </Box>

//       <hr />

//       {/* Tabs */}
//       <Box display="flex" alignItems="center" justifyContent="space-between" mt={3} mb={3} sx={{ backgroundColor: "#f5f5f5", padding: "10px 40px" }}>
//         <Box display="flex">
//           {['Configuration', 'Results'].map((tab) => (
//             <Box
//               key={tab}
//               px={2}
//               py={1}
//               onClick={() => setActiveTab(tab)}
//               sx={{
//                 fontSize: 14,
//                 fontWeight: 500,
//                 color: activeTab === tab ? '#000080' : 'gray',
//                 borderBottom: activeTab === tab ? '2px solid #000080' : 'none',
//                 cursor: 'pointer',
//               }}
//             >
//               {tab}
//             </Box>
//           ))}
//         </Box>

//         {/* History Section */}
//         <Box display="flex" alignItems="center" gap={1} sx={{ cursor: 'pointer' }}>
//           <Typography fontSize={14} color="gray">History</Typography>
//           <img src={history} alt="History Icon" width={20} height={20} />
//         </Box>
//       </Box>

//       {/* Body: Conditional Rendering */}
//       {activeTab === 'Configuration' ? <Configuration /> : <TestCaseTable />}
//     </Box>
//   );
// };

// export default UIUXConfigurator;


import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Make sure this is imported at the top
import { useLocation } from "react-router-dom";
import { Box, Typography, IconButton, Drawer } from '@mui/material';  // Import Drawer
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import historyIcon from "./../../asessts/images/history.png";
import backarrowicon from "./../../asessts/images/backarrowicon.png";
import Configuration from './Configuration';
import TestCaseTable from './Result';
import History from './History';  // Import History component

const UIUXConfigurator = () => {
    const location = useLocation();
  const selectedDoc = location.state?.doc; // Access doc from navigation state
    const taskId = location.state?.task_id; // ✅ extract task_id
    const fileId = location.state?.file_id;
    const token = localStorage.getItem("token");
  const [activeTab, setActiveTab] = useState('Results');
  const [drawerOpen, setDrawerOpen] = useState(false);  // State for drawer open
const [selectedHistoryDoc, setSelectedHistoryDoc] = useState(null);
const [fromHistory, setFromHistory] = useState(false); // NEW: track if Results tab is from History
const navigate = useNavigate(); // Inside your component

  const toggleDrawer = (open) => () => {
    setDrawerOpen(open);
  };
  const handleHistoryDocSelect = (doc) => {
  setSelectedHistoryDoc(doc);      // set selected doc
    setFromHistory(true); // Indicates Results came from History
  setDrawerOpen(false);            // close the drawer
  setActiveTab('Results');         // switch to Results tab
};


  return (
    <Box sx={{ height: '100vh', overflow: 'hidden' }}>
      {/* Header */}
<Box
  display="flex"
  alignItems="flex-start"
  borderBottom={"1px solid #8e8e8e"}
  sx={{
    width:"100%",
    position: "fixed", // or "fixed" if needed
    top: 0,
    backgroundColor: "white", // prevent transparency when scrolling
    zIndex: 1300, // keep above other elements
    padding: '10px 5px 0px 5px'
  }}
>
        <IconButton disableRipple sx={{ mt: '2px', mr: 1,ml:1 }} onClick={() => navigate(-1)}>
<img
    src={backarrowicon} // adjust path as needed
    alt="Back"
    width={20}
    height={20}
    style={{ objectFit: 'contain',backgroundColor:"#f9f9f9",padding:"5px",borderRadius:"50%" }}
  />        </IconButton>
        <Box>
          {/* <Typography fontWeight={600} fontSize={24} mb={1}>
             Complete UI/UX Project Assets – Wireframes...
           </Typography> */}
          <Typography fontWeight={600} fontSize={20} mb={0.5}>
  {selectedDoc?.file_name || "Untitled Document"}
</Typography>
          <Typography fontSize={12} color="text.secondary" mb={0.5} ml={2}>
            A consolidated collection of design flows, screen layouts, content plans, and feedback documents for LMS and CMS modules.
          </Typography>
        </Box>
      </Box>

      {/* <hr /> */}
       <Box
        sx={{
          marginTop: '68px', // same as header height
          height: 'calc(100vh - 68px)',
          overflowY: 'auto',
          scrollbarWidth:"thin",
        }}
      >

      {/* Tabs */}
      <Box display="flex" alignItems="center" justifyContent="space-between"  mb={3} sx={{ backgroundColor: "#f5f5f5", padding: "10px 40px" }}>
        <Box display="flex">
          {['Configuration', 'Results'].map((tab) => (
            <Box
              key={tab}
              px={2}
              py={1}
onClick={() => {
  setActiveTab(tab);
  if (tab === 'Results') {
    setSelectedHistoryDoc(null);  // reset history doc
    setFromHistory(false);        // indicates manual selection
  }
}}
              sx={{
                fontSize: 14,
                fontWeight: 500,
                color: activeTab === tab ? '#000080' : 'gray',
                borderBottom: activeTab === tab ? '2px solid #000080' : 'none',
                cursor: 'pointer',
              }}
            >
              {tab}
            </Box>
          ))}
        </Box>

        {/* History Section */}
        <Box
          display="flex"
          alignItems="center"
          gap={1}
          sx={{ cursor: 'pointer' }}
          onClick={toggleDrawer(true)}  // Open drawer on click
        >
          <Typography fontSize={14} color="gray">History</Typography>
          <img src={historyIcon} alt="History Icon" width={20} height={20} />
        </Box>
      </Box>

      {/* Body: Conditional Rendering */}
      {activeTab === 'Configuration' ? <Configuration /> : <TestCaseTable selectedHistoryDoc={selectedHistoryDoc} fromHistory={fromHistory}  taskId={taskId} token={token} fileId={fileId}/>}
</Box>
      {/* Drawer for History */}
        <Drawer
      anchor="right"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
      transitionDuration={{ enter: 1000, exit: 1000 }}
      PaperProps={{
        sx: {
          width: 420,
          height:"88%",
          padding:"10px 0px",
          borderRadius: '10px 0 0 10px',
          backgroundColor: 'white',
          marginTop:"66px"
        },
      }}
    >
        <Box sx={{ width: 400, height: '100%', overflowY: 'auto', }}>
<History onClose={toggleDrawer(false)} onSelectDoc={handleHistoryDocSelect} />
        </Box>
      </Drawer>
    </Box>
  );
};

export default UIUXConfigurator;
