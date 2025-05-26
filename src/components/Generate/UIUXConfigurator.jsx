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


import React, { useState,useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom'; // Make sure this is imported at the top
import { useLocation } from "react-router-dom";
import { Box, Typography, IconButton, Drawer } from '@mui/material';  // Import Drawer
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import historyIcon from "./../../asessts/images/history.png";
import backarrowicon from "./../../asessts/images/backarrowicon.png";
import Configuration from './Configuration';
import TestCaseTable from './Result';
import History from './History';  // Import History component
import { adminAxios } from '../../asessts/axios';

const UIUXConfigurator = () => {
  const location = useLocation();
  const selectedDoc = location.state?.doc; // Access doc from navigation state
  const taskId = location.state?.task_id; // ✅ extract task_id
  const fileId = location.state?.file_id;
  const dataSpaceId = location.state?.data_space_id;
  const generationId = location.state?.generation_id; // ✅ Add this
  const token = localStorage.getItem("token");
    const navigate = useNavigate();
const [progress, setProgress] = useState(0);  // progress from 0 to 100

  const [activeTab, setActiveTab] = useState('Configuration');
  const [drawerOpen, setDrawerOpen] = useState(false);  // State for drawer open
  const [selectedHistoryDoc, setSelectedHistoryDoc] = useState(null);
  const [fromHistory, setFromHistory] = useState(false); // NEW: track if Results tab is from History
  const [selectedSubTypes, setSelectedSubTypes] = useState([]);
  const [generatedResults, setGeneratedResults] = useState([]);
const [selectedDocs, setSelectedDocs] = useState([]);
const [selectedUseCase, setSelectedUseCase] = useState('');
  const pollingIdRef = useRef(null);
const [generationLoading, setGenerationLoading] = useState(false);
const [hasFetchedInitialResults, setHasFetchedInitialResults] = useState(false);

// const triggerTestCaseGeneration = async () => {
//   try {
//     setGeneratedResults([]);
//     setActiveTab('Results');
//     setGenerationLoading(true);
//     setProgress(0);

//     const payload = {
//       generation_id: generationId,
//       file_ids: selectedDocs,
//       types: selectedSubTypes.map(t => t.toLowerCase()),
//     };

//     const startTime = Date.now(); // ⏱️ Start timer

//     await adminAxios.post("/api/v1/test-case-batch/results/", payload);

//     let simulatedProgress = 0;

//     // Simulate gradual progress
//     const progressInterval = setInterval(() => {
//       simulatedProgress = Math.min(simulatedProgress + 1, 95);
//       setProgress(simulatedProgress);
//     }, 300);

//     // Poll every 2 seconds
//     pollingIdRef.current = setInterval(async () => {
//       try {
//         const res = await adminAxios.post("/api/v1/test-case-batch/results/", payload);
//         const latestResults = res.data.results || [];
//         const allDone = latestResults.every(r => r.status === 1);

//         if (allDone) {
//           clearInterval(pollingIdRef.current);
//           clearInterval(progressInterval);

//           // Rapidly animate to 100%
//           let quickProgress = simulatedProgress;
//           const finishInterval = setInterval(() => {
//             quickProgress += 5;
//             setProgress(Math.min(quickProgress, 100));

//             if (quickProgress >= 100) {
//               clearInterval(finishInterval);
//               const endTime = Date.now(); // ⏱️ Stop timer
//               const elapsedSeconds = ((endTime - startTime) / 1000).toFixed(2);
//               console.log(`✅ Test case generation completed in ${elapsedSeconds} seconds`);
              
//               setGeneratedResults(latestResults);
//               setGenerationLoading(false);
//             }
//           }, 50);
//         }
//       } catch (err) {
//         console.error("❌ Error while polling:", err);
//         clearInterval(pollingIdRef.current);
//         clearInterval(progressInterval);
//         setGenerationLoading(false);
//         setProgress(0);
//       }
//     }, 3000);
//   } catch (err) {
//     console.error("❌ Generation error:", err);
//     setGenerationLoading(false);
//     setProgress(0);
//   }
// };
const triggerTestCaseGeneration = async () => {
  setGeneratedResults([]);
  setActiveTab('Results');
  setGenerationLoading(true);
  setProgress(0);

  const payload = {
    generation_id: generationId,
    file_ids: selectedDocs,
    types: selectedSubTypes.map(t => t.toLowerCase()),
  };

  const startTime = Date.now();
  let simulatedProgress = 0;

  // Start progress bar simulation
  const progressInterval = setInterval(() => {
    simulatedProgress = Math.min(simulatedProgress + 1, 95);
    setProgress(simulatedProgress);
  }, 500);

  // Try initial trigger, but do not block if it fails
  try {
    await adminAxios.post("/api/v1/test-case-batch/results/", payload);
    console.log("🚀 Initial test case generation triggered.");
  } catch (err) {
    console.warn("⚠️ Initial trigger failed, starting polling anyway:", err.response?.data || err.message);
  }

  // Poll every 2 seconds to check if generation is complete
  pollingIdRef.current = setInterval(async () => {
    try {
      const res = await adminAxios.post("/api/v1/test-case-batch/results/", payload);
      const latestResults = res.data.results || [];
      const allDone = latestResults.every(r => r.status === 1);

      if (allDone) {
        clearInterval(pollingIdRef.current);
        clearInterval(progressInterval);

        // Smoothly transition to 100%
        let quickProgress = simulatedProgress;
        const finishInterval = setInterval(() => {
          quickProgress += 5;
          setProgress(Math.min(quickProgress, 100));

          if (quickProgress >= 100) {
            clearInterval(finishInterval);
            const endTime = Date.now();
            const elapsedSeconds = ((endTime - startTime) / 1000).toFixed(2);
            console.log(`✅ Test case generation completed in ${elapsedSeconds} seconds`);

            setGeneratedResults(latestResults);
            setGenerationLoading(false);
          }
        }, 50);
      }
    } catch (err) {
      console.error("❌ Polling error:", err.response?.data || err.message);
    }
  }, 3000);
};


  useEffect(() => {
    return () => {
      if (pollingIdRef.current) {
        clearInterval(pollingIdRef.current);
        console.log("⛔ Polling stopped on unmount");
      }
    };
  }, []);


  const fetchInitialTestCases = async () => {
  try {
    setGenerationLoading(true);
    const response = await adminAxios.get(`/api/v1/documents/${fileId}/get-test-cases/`);

    const results = response.data.results || [];
    setGeneratedResults(results);
    setHasFetchedInitialResults(true);
    console.log("✅ Initial results fetched successfully");
  } catch (err) {
    console.error("❌ Error fetching initial test cases:", err.response?.data || err.message);
  } finally {
    setGenerationLoading(false);
  }
};

const handleTabSwitch = async (tab) => {
  if (tab === 'Results') {
    setSelectedHistoryDoc(null);
    setFromHistory(false);

    // 🔁 Only fetch if not already generated
    if (!hasFetchedInitialResults && !generatedResults.length && fileId) {
      await fetchInitialTestCases(); // uses fileId from state
    }
  }
  setActiveTab(tab);
};



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
          width: "100%",
          position: "fixed", // or "fixed" if needed
          top: 0,
          backgroundColor: "white", // prevent transparency when scrolling
          zIndex: 1300, // keep above other elements
          padding: '10px 5px 0px 5px'
        }}
      >
        <IconButton disableRipple sx={{ mt: '2px', mr: 1, ml: 1 }} onClick={() => navigate(-1)}>
          <img
            src={backarrowicon} // adjust path as needed
            alt="Back"
            width={20}
            height={20}
            style={{ objectFit: 'contain', backgroundColor: "#f9f9f9", padding: "5px", borderRadius: "50%" }}
          />        </IconButton>
        <Box>
          {/* <Typography fontWeight={600} fontSize={24} mb={1}>
             Complete UI/UX Project Assets – Wireframes...
           </Typography> */}
          <Typography fontWeight={600} fontSize={20} mb={0.5}>
            {selectedDoc?.name || "Document"}
          </Typography>
          <Typography fontSize={12} color="text.secondary" mb={0.5} >
            {selectedDoc?.description || "Gen AI"}
          </Typography>
        </Box>
      </Box>

      {/* <hr /> */}
      <Box
        sx={{
          marginTop: '68px', // same as header height
          height: 'calc(100vh - 68px)',
          overflowY: 'auto',
          scrollbarWidth: "thin",
        }}
      >

        {/* Tabs */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3} sx={{ backgroundColor: "#f5f5f5", padding: "5px 50px" }}>
          <Box display="flex">
  {['Configuration', 'Results'].map((tab) => {
    const isResultsTab = tab === 'Results';
    // const isDisabled = isResultsTab && generatedResults.length === 0;
const isDisabled = false; // Always allow Results tab
    return (
      <Box
        key={tab}
        px={2}
        py={1}
        onClick={() => handleTabSwitch(tab)}
        sx={{
          fontSize: 14,
          fontWeight: 500,
          color: isDisabled
            ? '#bdbdbd'
            : activeTab === tab
            ? '#000080'
            : 'gray',
          borderBottom: activeTab === tab
            ? '2px solid #000080'
            : 'none',
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          pointerEvents: isDisabled ? 'none' : 'auto',
        }}
      >
        {tab}
      </Box>
    );
  })}
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
{/* <Box
  display="flex"
  alignItems="center"
  gap={1}
  sx={{
    cursor: 'not-allowed',
    opacity: 0.5,             // visually faded
    pointerEvents: 'none',   // disables click interaction
  }}
>
  <Typography fontSize={14} color="gray">History</Typography>
  <img src={historyIcon} alt="History Icon" width={20} height={20} />
</Box> */}

        </Box>

        {/* Body: Conditional Rendering */}
        {activeTab === 'Configuration' ? 
       <Configuration
  selectedDocs={selectedDocs}
  setSelectedDocs={setSelectedDocs}
  selectedUseCase={selectedUseCase}
  setSelectedUseCase={setSelectedUseCase}
  selectedSubTypes={selectedSubTypes}
  setSelectedSubTypes={setSelectedSubTypes}
  onGenerate={triggerTestCaseGeneration} // pass the trigger function
  dataSpaceId={dataSpaceId}
  generationId={generationId}
/>
          : <TestCaseTable
  selectedDocs={selectedDocs}
  selectedHistoryDoc={selectedHistoryDoc}
  fromHistory={fromHistory}
  taskId={taskId}
  token={token}
  fileId={fileId}
  selectedSubTypes={selectedSubTypes}
  results={generatedResults}
  generationLoading={generationLoading}
  progress={progress}
/>

        }</Box>
      {/* Drawer for History */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        transitionDuration={{ enter: 1000, exit: 1000 }}
        PaperProps={{
          sx: {
            width: "45%",
            height: "88%",
            padding: "10px 0px",
            borderRadius: '10px 0 0 10px',
            backgroundColor: 'white',
            marginTop: "66px"
          },
        }}
      >
        <Box sx={{ width: '100%', height: '100%', overflowY: 'auto', }}>
          <History onClose={toggleDrawer(false)} onSelectDoc={handleHistoryDocSelect} />
        </Box>
      </Drawer>
    </Box>
  );
};

export default UIUXConfigurator;
