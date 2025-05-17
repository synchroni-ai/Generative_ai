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
import { Box, Typography, IconButton, Drawer } from '@mui/material';  // Import Drawer
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import historyIcon from "./../../asessts/images/history.png";
import Configuration from './Configuration';
import TestCaseTable from './Result';
import History from './History';  // Import History component

const UIUXConfigurator = () => {
  const [activeTab, setActiveTab] = useState('Configuration');
  const [drawerOpen, setDrawerOpen] = useState(false);  // State for drawer open

  const toggleDrawer = (open) => () => {
    setDrawerOpen(open);
  };

  return (
    <Box fontFamily="'Poppins', sans-serif" sx={{ padding: '24px 0px', scrollbarWidth: "thin" }}>
      {/* Header */}
      <Box display="flex" alignItems="flex-start" mb={3}>
        <IconButton sx={{ mt: '2px', mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box>
          <Typography fontWeight={600} fontSize={24} mb={1}>
            Complete UI/UX Project Assets – Wireframes...
          </Typography>
          <Typography fontSize={14} color="text.secondary">
            A consolidated collection of design flows, screen layouts, content plans, and feedback documents for LMS and CMS modules.
          </Typography>
        </Box>
      </Box>

      <hr />

      {/* Tabs */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mt={3} mb={3} sx={{ backgroundColor: "#f5f5f5", padding: "10px 40px" }}>
        <Box display="flex">
          {['Configuration', 'Results'].map((tab) => (
            <Box
              key={tab}
              px={2}
              py={1}
              onClick={() => setActiveTab(tab)}
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
      {activeTab === 'Configuration' ? <Configuration /> : <TestCaseTable />}

      {/* Drawer for History */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
      >
        <Box sx={{ width: 400, p: 2, height: '100%', overflowY: 'auto' }}>
<History onClose={toggleDrawer(false)} />
        </Box>
      </Drawer>
    </Box>
  );
};

export default UIUXConfigurator;
