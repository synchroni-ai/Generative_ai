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
const [selectedLLM, setSelectedLLM] = useState('');
const [temperature, setTemperature] = useState(0.5);
const [selectedHistoryDocDetails, setSelectedHistoryDocDetails] = useState(null);



// const triggerTestCaseGeneration = async (configId) => {
//   if (!configId) return;

//   setGeneratedResults([]);
//   setActiveTab('Results');
//   setGenerationLoading(true);
//   setProgress(0);

//   const startTime = Date.now();
//   let simulatedProgress = 0;

//   const progressInterval = setInterval(() => {
//     simulatedProgress = Math.min(simulatedProgress + 1, 95);
//     setProgress(simulatedProgress);
//   }, 500);

//   let jobId;

//   try {
//     // Trigger generation and capture job_id
//     const response = await adminAxios.post(`/api/v1/generation/run/${configId}`, null, {
//       headers: {
//         Authorization: `Bearer ${token}`,
//       },
//     });

//     jobId = response.data?.job_id;
//     if (!jobId) {
//       throw new Error("Job ID not returned from generation API");
//     }

//   } catch (err) {
//     clearInterval(progressInterval);
//     setGenerationLoading(false);
//     return;
//   }

//   // Poll every 3 seconds using jobId
//   pollingIdRef.current = setInterval(async () => {
//     try {
//       const res = await adminAxios.get(`/api/v1/results/${jobId}`, {
//         headers: { Authorization: `Bearer ${token}` },
//       });

//       const status = res.data?.status;
//       const results = res.data?.results || {};

//       if (status === 'completed') {
//         clearInterval(pollingIdRef.current);
//         clearInterval(progressInterval);

//         // Smooth transition to 100%
//         let quickProgress = simulatedProgress;
//         const finishInterval = setInterval(() => {
//           quickProgress += 5;
//           setProgress(Math.min(quickProgress, 100));

//           if (quickProgress >= 100) {
//             clearInterval(finishInterval);
//             const endTime = Date.now();
//             const elapsedSeconds = ((endTime - startTime) / 1000).toFixed(2);
//             console.log(`✅ Generation completed in ${elapsedSeconds} seconds`);

//             setGeneratedResults(results);  // or process results if needed
//             setGenerationLoading(false);
//           }
//         }, 50);
//       }
//     } catch (err) {
//     }
//   }, 3000);
// };


const triggerTestCaseGeneration = async (configId) => {
  if (!configId) return;
  
  setSelectedHistoryDoc(null);       // ✅ Reset history mode
  setFromHistory(false);             // ✅ Reset history mode
  setGeneratedResults([]);
  setActiveTab('Results');
  setGenerationLoading(true);
  setProgress(0);

  const startTime = Date.now();
  let simulatedProgress = 0;

  const progressInterval = setInterval(() => {
    simulatedProgress = Math.min(simulatedProgress + 1, 95);
    setProgress(simulatedProgress);
  }, 500);

  try {
    const docsStatus3 = selectedDocs.filter(doc => doc.status === 3);
    const docsStatusNot3 = selectedDocs.filter(doc => [0, 1, 2].includes(doc.status));

    const allResults = {};

    // ✅ 1. Handle already generated (status === 3)
    if (docsStatus3.length > 0) {
      const docIds = docsStatus3.map(doc => doc.file_id).join(',');
      const res = await adminAxios.get(`/api/v1/testcases?document_ids=${docIds}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const resultMap = res.data?.results || {};
      Object.assign(allResults, resultMap);
    }

    // ✅ 2. Handle generation needed (status 0,1,2)
    if (docsStatusNot3.length > 0) {
      const genRes = await adminAxios.post(`/api/v1/generation/run/${configId}`, null, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const jobId = genRes.data?.job_id;
      if (!jobId) throw new Error("Job ID not returned");

      pollingIdRef.current = setInterval(async () => {
        try {
          const pollRes = await adminAxios.get(`/api/v1/results/${jobId}`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          const status = pollRes.data?.status;
          const results = pollRes.data?.results || {};

          if (status === 'completed') {
            clearInterval(pollingIdRef.current);
            clearInterval(progressInterval);

            let quickProgress = simulatedProgress;
            const finishInterval = setInterval(() => {
              quickProgress += 5;
              setProgress(Math.min(quickProgress, 100));

              if (quickProgress >= 100) {
                clearInterval(finishInterval);
                const endTime = Date.now();
                const elapsedSeconds = ((endTime - startTime) / 1000).toFixed(2);
                console.log(`✅ Generation completed in ${elapsedSeconds} seconds`);

                setGeneratedResults({ ...allResults, ...results });
                setGenerationLoading(false);
              }
            }, 50);
          }
        } catch (err) {
          console.error("❌ Polling error:", err);
        }
      }, 3000);
    } else {
      // Only status 3 docs — no polling needed
      clearInterval(progressInterval);
      setProgress(100);
      setGeneratedResults(allResults);
      setGenerationLoading(false);
    }

  } catch (err) {
    clearInterval(progressInterval);
    setGenerationLoading(false);
    console.error("❌ Generation trigger error:", err);
  }
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
 const handleHistoryDocSelect = async (doc) => {
  try {
    const res = await adminAxios.get(`/api/v1/history/document/${doc.id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const results = res.data;
    if (results && results.status === 'completed') {
      setSelectedHistoryDoc(doc);           // set selected doc
      setGeneratedResults(results);         // set results for TestCaseTable
      setFromHistory(true);                 // track it came from history
      setDrawerOpen(false);                 // close drawer
      setActiveTab('Results');              // go to Results
    } else {
      console.warn('⚠️ History doc not in completed state:', results);
    }
  } catch (err) {
    console.error("❌ Error fetching history document:", err);
  }
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
            ? 'var(--primary-blue)'
            : 'gray',
          borderBottom: activeTab === tab
            ? '2px solid var(--primary-blue)'
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
   selectedLLM={selectedLLM}
  setSelectedLLM={setSelectedLLM}
  temperature={temperature}
  setTemperature={setTemperature}
/>
          : <TestCaseTable
  selectedDocs={selectedDocs}
  selectedHistoryDoc={selectedHistoryDoc}
    selectedHistoryDocDetails={selectedHistoryDocDetails}  // ✅ NEW
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
            width: "30%",
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
