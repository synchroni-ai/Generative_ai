// // components/Configuration.jsx
// import React, { useState, useEffect, useRef } from 'react';
// import {
//   Grid, Paper, Typography, IconButton, List, ListItem, ListItemIcon, Checkbox, ListItemText,
//   Box, Button, Divider
// } from '@mui/material';
// import { adminAxios } from '../../asessts/axios/index';
// import ExpandLessIcon from '@mui/icons-material/ExpandLess';
// import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
// import CircularProgress from '@mui/material/CircularProgress';
// import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
// import DeleteIcon from "./../../asessts/images/deleteicon.png";
// import NewDocumentModal from './AddDocumentModal';


// const Configuration = ({ selectedDocs, setSelectedDocs, selectedUseCase, setSelectedUseCase, selectedSubTypes, setSelectedSubTypes, onGenerate, dataSpaceId, generationId }) => {
//   // console.log("Received dataSpaceId:", dataSpaceId);
//   // console.log("Received generationId:", generationId);
//   const [documentsData, setDocumentsData] = useState([]);
//   const [collapsed, setCollapsed] = useState(false);
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [modalOpen, setModalOpen] = useState(false);

//   useEffect(() => {
//     const fetchDocuments = async () => {
//       try {
//         const response = await adminAxios.get(`/api/v1/data-spaces/${dataSpaceId}/documents/`);
//         const fetchedDocs = response.data;
//         setDocumentsData(fetchedDocs);
//         // setSelectedDocs([]);// Optional: preselect all on load
//       } catch (error) {
//         console.error("Error fetching documents for data space:", error);
//       }
//     };

//     if (dataSpaceId) {
//       fetchDocuments();
//     }
//   }, [dataSpaceId]);


//   const useCaseOptions = [
//     'Functional',
//     'Database',
//     'Test Cases',
//     'Wireframes',
//     'Backend Functionality',
//     'Frontend Code',
//   ];

//   const subTypes = [
//     'Functional',
//     'Non-Functional',
//     'Security',
//     'Compliance',
//     'Boundary',
//     'Performance'
//   ];


//   const documentsRef = useRef(null); // For outside click


//   const toggleDocument = (docId) => {
//     setSelectedDocs((prevSelected) =>
//       prevSelected.includes(docId)
//         ? prevSelected.filter((id) => id !== docId)
//         : [...prevSelected, docId]
//     );
//   };


//   const handleUseCaseSelect = (useCase) => {
//     setSelectedUseCase(useCase);
//     setSelectedSubTypes([]); // reset subtypes on use case change
//     setCollapsed(true); // Close Documents accordion
//   };

//   const toggleSubType = (type) => {
//     setSelectedSubTypes((prev) =>
//       prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
//     );
//   };

//   const pollingIdRef = useRef(null);



//   const handleGenerate = () => {
//     if (onGenerate) {
//       onGenerate(); // Parent handles actual API + navigation
//     }
//   };


//   // ⛔ Stop polling on unmount (e.g., reload or navigation away)
//   useEffect(() => {
//     return () => {
//       if (pollingIdRef.current) {
//         clearInterval(pollingIdRef.current);
//         console.log("⛔ Polling stopped on unmount");
//       }
//     };
//   }, []);

//   return (
//     <Box display="flex" flexDirection={{ xs: 'column', md: 'row' }} gap={6} mb={6} sx={{ padding: "0px 50px" }}>
//       {/* Left Section */}
//       <Box flex={1}>
//         {/* Documents */}
//         <Box
//           ref={documentsRef}
//           sx={{
//             padding: "8px 16px",
//             borderRadius: 3,
//             mb: 5,
//             border: '1px solid #EBEBEB', width: "80%"
//           }}
//         >
//           <Box
//             display="flex"
//             justifyContent="space-between"
//             alignItems="center"
//             mb={0}
//             sx={{ cursor: 'pointer' }}
//             onClick={() => setCollapsed(!collapsed)}
//           >
//             <Box display="flex" alignItems="center" gap={2}>
//               <Typography fontWeight={600} fontSize={18}>Documents</Typography>
//               <Button
//                 onClick={(e) => {
//                   e.stopPropagation();
//                   setModalOpen(true);
//                 }}
//                 variant="outlined"
//                 sx={{
//                   borderRadius: '30px',
//                   textTransform: 'none',
//                   color: '#000080',
//                   borderColor: 'transparent',
//                   bgcolor: '#f9f9f9',
//                   '&:hover': {
//                     bgcolor: '#f0f0f0',
//                   },
//                   '& .MuiButton-startIcon': {
//                     marginRight: '6px',
//                     '& svg': {
//                       fontSize: '18px', // 👈 reduce icon size here
//                     },
//                   },
//                 }}
//                 startIcon={<AddCircleOutlineIcon />}
//               // endIcon={<ArrowDropDownIcon />}
//               >
//                 New Document
//               </Button>
//               <NewDocumentModal open={modalOpen} onClose={() => setModalOpen(false)} />
//             </Box>

//             {/* Right side: Delete + Expand/Collapse icons */}
//             <Box display="flex" alignItems="center" gap={1}>
//               {selectedDocs.length > 0 && (
//                 <IconButton
//                   disableRipple
//                   size="small"
//                   onClick={(e) => {
//                     e.stopPropagation(); // Prevent collapsing on delete
//                     // handleDelete(); // Replace with your actual delete handler
//                   }}
//                 >
//                   <img src={DeleteIcon} width={18} height={18} alt="Delete" />
//                 </IconButton>
//               )}
//               <IconButton
//                 size="small"
//                 disableRipple
//                 disableFocusRipple
//                 sx={{ pointerEvents: 'none' }}
//               >
//                 {collapsed ? <ExpandMoreIcon /> : <ExpandLessIcon />}
//               </IconButton>
//             </Box>
//           </Box>


//           {!collapsed && (
//             <List sx={{ maxHeight: 300, overflow: 'auto', scrollbarWidth: "none", padding: '15px 25px' }}>
//               {/* Select All Checkbox */}
//               <ListItem disablePadding>
//                 <ListItemIcon>
//                   <Checkbox
//                     edge="start"
//                     indeterminate={
//                       documentsData.length > 0 &&
//                       selectedDocs.length > 0 &&
//                       selectedDocs.length < documentsData.length
//                     }
//                     checked={
//                       documentsData.length > 0 &&
//                       selectedDocs.length === documentsData.length
//                     }
//                     onChange={(e) => {
//                       setSelectedDocs(e.target.checked ? documentsData.map(doc => doc.file_id) : []);

//                     }}
//                     sx={{
//                       color: 'inherit',
//                       '&.Mui-checked': { color: '#000080' },
//                       '&.MuiCheckbox-indeterminate': { color: '#000080' },
//                       '& .MuiSvgIcon-root': { borderRadius: '4px' },
//                     }}
//                   />

//                 </ListItemIcon>
//                 <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary="Select All" />
//               </ListItem>

//               {/* Individual Checkboxes */}
//               {documentsData.map((doc) => (
//                 <ListItem key={doc.file_id} disablePadding>
//                   <ListItemIcon>
//                     <Checkbox
//                       edge="start"
//                       checked={selectedDocs.includes(doc.file_id)}
//                       onChange={() => toggleDocument(doc.file_id)}
//                       sx={{
//                         color: selectedDocs.includes(doc.file_id) ? '#000080' : '#c4c4c4',
//                         '&.Mui-checked': { color: '#000080' },
//                         '& .MuiSvgIcon-root': { borderRadius: '4px' },
//                       }}
//                     />
//                   </ListItemIcon>
//                   <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary={doc.file_name} />
//                 </ListItem>
//               ))}

//             </List>
//           )}
//         </Box>

//         {/* Use Cases */}
//         <Typography fontWeight={600} fontSize={18} mb={1} ml={2} sx={{ color: '#333' }}>
//           Use Cases
//         </Typography>
//         <Paper elevation={0}
//           sx={{
//             //  backgroundColor: '#F6F4FF', 
//             borderRadius: 3, p: 2, width: "80%", border: "1px solid #EBEBEB"
//           }}>
//           <Box
//             sx={{
//               display: 'grid',
//               gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(3, 1fr)' },
//               gap: 1.5,
//             }}
//           >
//             {useCaseOptions.map((useCase) => {
//               const isTestCases = useCase === 'Test Cases';
//               const isSelected = selectedUseCase === useCase;

//               return (
//                 <Button
//                   key={useCase}
//                   disableRipple
//                   onClick={() => handleUseCaseSelect(useCase)}
//                   disabled={!isTestCases}
//                   sx={{
//                     justifyContent: 'flex-start',
//                     color: isSelected ? '#0A0080' : isTestCases ? '#000' : '#aaa',
//                     fontSize: 14,
//                     fontWeight: isSelected ? 600 : 400,
//                     textTransform: 'none',
//                     px: 1,
//                     py: 1,
//                     borderRadius: 2,
//                     minWidth: 'unset',
//                     boxShadow: 'none',
//                     cursor: isTestCases ? 'pointer' : 'default',
//                   }}
//                 >
//                   <Box
//                     sx={{
//                       width: 16,
//                       height: 16,
//                       borderRadius: '50%',
//                       border: '1.5px solid',
//                       borderColor: isSelected ? '#0A0080' : isTestCases ? '#000' : '#aaa',
//                       display: 'flex',
//                       alignItems: 'center',
//                       justifyContent: 'center',
//                       mr: 1,
//                     }}
//                   >
//                     {isSelected && (
//                       <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#0A0080' }} />
//                     )}
//                   </Box>
//                   {useCase}
//                 </Button>
//               );
//             })}
//           </Box>
//         </Paper>

//         {/* Sub-types */}
//         {selectedUseCase && (
//           <>
//             <Typography fontWeight={600} fontSize={18} mt={4} ml={2} sx={{ color: '#333' }}>
//               Sub-types
//             </Typography>
//             <Paper elevation={0} sx={{ borderRadius: 3, p: 2 }}>
//               <Box display="flex" flexWrap="wrap" gap={2}>
//                 {subTypes.map((type) => (
//                   <Box key={type} display="flex" alignItems="center" width={{ xs: '50%', sm: '25%' }}>
//                     <Checkbox
//                       size="small"
//                       disableRipple
//                       checked={selectedSubTypes.includes(type)}
//                       onChange={() => toggleSubType(type)}
//                       sx={{
//                         color: selectedSubTypes.includes(type) ? '#000080' : '#c4c4c4',
//                         '&:hover': { backgroundColor: 'transparent' },
//                         '&.Mui-checked': { color: '#000080' },
//                         '& .MuiSvgIcon-root': { borderRadius: '4px' },
//                       }}
//                     />
//                     <Typography
//                       fontSize={14}
//                       fontWeight={400}
//                       sx={{ lineHeight: 1.75 }}
//                     >
//                       {type}
//                     </Typography>
//                   </Box>
//                 ))}
//               </Box>
//             </Paper>
//           </>
//         )}
//       </Box>

//       {/* Right Section */}
//       <Box
//         width={{ xs: '100%', md: '35%' }}
//         sx={{
//           position: { md: 'sticky' },
//           top: { md: 80 }, // adjust as needed based on your header height
//           alignSelf: 'flex-start', // ensures correct layout in flexbox
//         }}
//       >
//         <Typography fontSize={18} fontWeight={700} mb={1.5}>Configure Summary</Typography>
//         <Box sx={{ p: 2, borderRadius: 3, border: '1px solid #EBEBEB' }}>
//           <Box mb={2}>
//             <Typography fontSize={16} fontWeight={600} mb={2} sx={{ color: "#252525" }}>
//               Documents
//             </Typography>
//             {selectedDocs.map((id, idx) => {
//               const doc = documentsData.find(doc => doc.file_id === id);
//               return (
//                 <Typography key={idx} fontSize={14} sx={{ color: '#000080', fontWeight: 400, mb: "3px", ml: "15px" }}>
//                   {doc?.file_name || 'Unknown Document'}
//                 </Typography>
//               );
//             })}

//           </Box>
//           <Divider sx={{ my: 2 }} />
//           <Box>
//             <Typography fontSize={16} fontWeight={600} mb={1} sx={{ color: "#252525" }}>
//               Use cases
//             </Typography>
//             <Box sx={{
//               backgroundColor: '#FCFCFC', color: '#666', fontSize: 14, px: 1.5,
//               py: 0.5, borderRadius: '12px', fontWeight: 500, width: "80px", ml: '15px'
//             }}>
//               <Typography fontSize={14} fontWeight={500}>{selectedUseCase}</Typography>
//             </Box>
//           </Box>

//           {selectedUseCase && (
//             <>
//               <Divider sx={{ my: 2 }} />
//               <Box>
//                 <Typography fontSize={16} fontWeight={600} mb={1} sx={{ color: "#252525" }}>
//                   Sub-types
//                 </Typography>
//                 <Box display="flex" flexWrap="wrap" gap={1}>
//                   {selectedSubTypes.map((type, idx) => (
//                     <Box key={idx} sx={{
//                       backgroundColor: '#FCFCFC', color: '#666', fontSize: 14,
//                       px: 1.5, py: 0.5, borderRadius: '12px', fontWeight: 500, ml: '15px'
//                     }}>
//                       {type}
//                     </Box>
//                   ))}
//                 </Box>
//               </Box>
//             </>
//           )}
//         </Box>

//         {/* Generate Button */}
//         <Box display="flex" justifyContent="flex-end" mt={3}>
//           <Button
//             variant="contained"
//             disabled={selectedSubTypes.length === 0 || selectedDocs.length === 0}
//             onClick={handleGenerate}
//             sx={{
//               backgroundColor: '#0A0080',
//               borderRadius: '999px',
//               fontSize: 14,
//               textTransform: 'none',
//               fontWeight: 500,
//               px: 3,
//               py: 1,
//               boxShadow: 'none',
//               '&:hover': { backgroundColor: '#07006B' },
//             }}
//           >
//             Generate
//           </Button>
//         </Box>
//       </Box>
//     </Box>

//   );
// };

// export default Configuration;




// components/Configuration.jsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Grid, Paper, Typography, IconButton, List, ListItem, ListItemIcon, Checkbox, ListItemText,
  Box, Button, Divider, Dialog,
  DialogTitle,
  DialogContent,
  DialogActions, Slider
} from '@mui/material';
import { Radio, FormControlLabel } from "@mui/material";
import { adminAxios } from '../../asessts/axios/index';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CircularProgress from '@mui/material/CircularProgress';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import DeleteIcon from "./../../asessts/images/deleteicon.png";
import NewDocumentModal from './AddDocumentModal';
import './configuration.css';


const Configuration = ({ selectedDocs, setSelectedDocs, selectedUseCase, setSelectedUseCase, selectedSubTypes, setSelectedSubTypes, onGenerate, dataSpaceId, generationId, selectedLLM, setSelectedLLM,selectedOpenAIVersion,setSelectedOpenAIVersion, temperature, setTemperature, }) => {
   const [documentsData, setDocumentsData] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [hasTouchedTemperature, setHasTouchedTemperature] = useState(false);

const fetchDocuments = async () => {
  try {
    const token = localStorage.getItem("token");

    const response = await adminAxios.get(`/api/v1/dataspaces/${dataSpaceId}/documents`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const fetchedDocs = response.data || [];

    // Log each document's status to the console
    fetchedDocs.forEach(doc => {
      console.log(`📄 ${doc.file_name} - Status: ${doc.status}`);
    });

    const mappedDocs = fetchedDocs.map(doc => ({
      file_id: doc._id,
      file_name: doc.file_name,
      status: doc.status, // Include status if you need to use it later
    }));

    setDocumentsData(mappedDocs);
  } catch (error) {
    console.error("Error fetching data space details:", error);
  }
};


  useEffect(() => {
    if (dataSpaceId) {
      fetchDocuments();
    }
  }, [dataSpaceId]);



  const handleDelete = async () => {
    if (!dataSpaceId || selectedDocs.length === 0) return;
    try {
      const token = localStorage.getItem("token");
      await adminAxios.delete(`/api/v1/dataspaces/${dataSpaceId}/documents/batch-delete`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        data: {
          document_ids: selectedDocs.map(doc => doc.file_id)
        }
      });
      // ✅ Refresh the document list from backend
      await fetchDocuments();
      // ✅ Clear selection
      setSelectedDocs([]);
    } catch (error) {
      console.error("❌ Error deleting documents:", error.response?.data || error.message);
      alert("Failed to delete selected documents.");
    }
  };



  const useCaseOptions = [
    'Functional',
    'Database',
    'Test Cases',
    'Wireframes',
    'Backend Functionality',
    'Frontend Code',
  ];

  const subTypes = [
    'Functional',
    'Non-Functional',
    'Security',
    'Compliance',
    'Boundary',
    'Performance'
  ];


  const documentsRef = useRef(null); // For outside click


  const toggleDocument = (doc) => {
  setSelectedDocs((prevSelected) => {
    const exists = prevSelected.find(d => d.file_id === doc.file_id);
    return exists
      ? prevSelected.filter((d) => d.file_id !== doc.file_id)
      : [...prevSelected, doc];
  });
};



  const handleUseCaseSelect = (useCase) => {
    setSelectedUseCase(useCase);
    setSelectedSubTypes([]); // reset subtypes on use case change
    setCollapsed(true); // Close Documents accordion
  };

  const toggleSubType = (type) => {
    setSelectedSubTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const pollingIdRef = useRef(null);



const handleGenerate = async () => {
  if (selectedDocs.length === 0 || selectedSubTypes.length === 0) return;

  // Dynamically prepare the config payload
  const config = {
    llm_model: selectedLLM === 'mistral' ? 'Mistral' : 'Openai',
    temperature: temperature,
    use_case: ['test case generation'],
    subtypes: selectedSubTypes.map(type =>
      type.toLowerCase().replace(/\s|-/g, '_')
    ),
  };

  // ✅ Conditionally add llm_version if OpenAI is selected
if (selectedLLM === 'openai' && selectedOpenAIVersion) {
  config.llm_version = selectedOpenAIVersion.toLowerCase().replace(/\s+/g, '-');
}

  const payload = {
    documents: selectedDocs.map(doc => doc.file_id),
    config,
  };

  try {
    const token = localStorage.getItem("token");

    const res = await adminAxios.post("/api/v1/configs", payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
    });

    const configId = res.data?.config_id;
    if (configId) {
      onGenerate(configId);  // pass to parent
    } else {
      alert("❌ Failed to create config. Please try again.");
    }
  } catch (err) {
    console.error("❌ Config creation failed:", err.response?.data || err.message);
    alert("Something went wrong while creating the configuration.");
  }
};




  // ⛔ Stop polling on unmount (e.g., reload or navigation away)
  useEffect(() => {
    return () => {
      if (pollingIdRef.current) {
        clearInterval(pollingIdRef.current);
        console.log("⛔ Polling stopped on unmount");
      }
    };
  }, []);

  return (
    <Box display="flex" flexDirection={{ xs: 'column', md: 'row' }} gap={6} mb={6} sx={{ padding: "0px 50px" }}>
      {/* Left Section */}
      <Box flex={1}>
        {/* Documents */}
        <Box ref={documentsRef} className="configuration_container">
          <Box
            className="configuration_header"
            onClick={() => setCollapsed(!collapsed)}
          >
            <Box className="configuration_titleRow">
              <Typography className="configuration_title">Documents</Typography>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  setModalOpen(true);
                }}
                variant="outlined"
                startIcon={<AddCircleOutlineIcon />}
                className="configuration_newButton"
              >
                Upload
              </Button>
              <NewDocumentModal open={modalOpen} onClose={() => setModalOpen(false)} dataSpaceId={dataSpaceId} fetchDocuments={fetchDocuments} />
            </Box>

            <Box className="configuration_iconRow">
              {selectedDocs.length > 0 && (
                <IconButton
                  disableRipple
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    setConfirmDeleteOpen(true); // open dialog instead of deleting
                  }}
                >
                  <img src={DeleteIcon} width={18} height={18} alt="Delete" />
                </IconButton>
              )}
              <IconButton
                size="small"
                disableRipple
                disableFocusRipple
                sx={{ pointerEvents: 'none' }}
              >
                {collapsed ? <ExpandMoreIcon /> : <ExpandLessIcon />}
              </IconButton>
            </Box>
          </Box>

          {!collapsed && (
            <List className="configuration_list">
              <ListItem disablePadding>
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    indeterminate={
                      documentsData.length > 0 &&
                      selectedDocs.length > 0 &&
                      selectedDocs.length < documentsData.length
                    }
                    checked={
                      documentsData.length > 0 &&
                      selectedDocs.length === documentsData.length
                    }
                    onChange={(e) => {
                      setSelectedDocs(
  e.target.checked ? [...documentsData] : []
);
                    }}
                    className="configuration_checkbox"
                  />
                </ListItemIcon>
                <ListItemText
                  primaryTypographyProps={{ fontSize: 14 }}
                  primary="Select All"
                />
              </ListItem>

              {documentsData.map((doc) => (
                <ListItem key={doc.file_id} disablePadding>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={selectedDocs.some((d) => d.file_id === doc.file_id)}
onChange={() => toggleDocument(doc)}
                      className={
                        selectedDocs.includes(doc.file_id)
                          ? "configuration_checkbox checked"
                          : "configuration_checkbox"
                      }
                    />
                  </ListItemIcon>
                  <ListItemText
                    primaryTypographyProps={{ fontSize: 14 }}
                    primary={doc.file_name}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>


        {/* Use Cases */}
        <Typography className="configuration_heading">Use Cases</Typography>

        <Paper elevation={0} className="configuration_usecaseWrapper">
          <Box className="configuration_usecaseGrid">
            {useCaseOptions.map((useCase) => {
              const isTestCases = useCase === 'Test Cases';
              const isSelected = selectedUseCase === useCase;

              return (
                <Button
                  sx={{ justifyContent: "left" }}
                  key={useCase}
                  disableRipple
                  onClick={() => handleUseCaseSelect(useCase)}
                  disabled={!isTestCases}
                  className={`configuration_usecaseButton ${isSelected ? 'selected' : ''} ${!isTestCases ? 'disabled' : ''
                    }`}
                >
                  <Box
                    className={`configuration_radioOuter ${isSelected ? 'selected' : ''} ${!isTestCases ? 'disabled' : ''
                      }`}
                  >
                    {isSelected && <Box className="configuration_radioInner" />}
                  </Box>
                  {useCase}
                </Button>
              );
            })}
          </Box>
        </Paper>


        {/* Sub-types */}
        {selectedUseCase && (
          <>
            <Typography className="configuration_subtypeHeading">
              Sub-types
            </Typography>

            <Paper elevation={0} className="configuration_subtypeWrapper">
              <Box className="configuration_subtypeGrid">
                {subTypes.map((type) => (
                  <Box key={type} className="configuration_subtypeItem">
                    <Checkbox
                      size="small"
                      disableRipple
                      checked={selectedSubTypes.includes(type)}
                      onChange={() => toggleSubType(type)}
                      className={`configuration_checkbox ${selectedSubTypes.includes(type) ? 'checked' : ''}`}
                    />
                    <Typography className="configuration_subtypeLabel">
                      {type}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </>
        )}

        {/* Additional Settings */}
       <Box mt={4}>
  <Typography className="configuration_subtypeHeading">Additional Settings</Typography>

  <Paper elevation={0} className="configuration_subtypeWrapper">
    {/* LLM Model Heading */}
    <Typography className="configuration_SettingsTitle" mb={1}>
      LLM Model
    </Typography>

    {/* Radio Buttons Row */}
    <Box display="flex" flexDirection="row" gap={4} alignItems="center" ml={3}>
      <FormControlLabel
        control={
          <Radio
            checked={selectedLLM === 'mistral'}
            onChange={() => setSelectedLLM('mistral')}
            value="mistral"
            name="llm-model"
            sx={{
              p: 0.5,
              '&.Mui-checked': { color: '#000080' },
              '& svg': { fontSize: 20 }
            }}
          />
        }
        label={<Typography fontSize={15}>Mistral</Typography>}
      />
      <FormControlLabel
        control={
          <Radio
            checked={selectedLLM === 'openai'}
            onChange={() => setSelectedLLM('openai')}
            value="openai"
            name="llm-model"
            sx={{
              p: 0.5,
              '&.Mui-checked': { color: '#000080' },
              '& svg': { fontSize: 20 }
            }}
          />
        }
        label={<Typography fontSize={15}>Open AI</Typography>}
      />
    </Box>

    {/* Conditional: Open AI Versions */}
    {selectedLLM === 'openai' && (
      <>
        <Typography className="configuration_SettingsTitle" mt={2}>
          Versions
        </Typography>
        <Box display="flex" flexDirection="row" gap={3} alignItems="center" ml={3} mt={1}>
          {['Gpt-3.5-Turbo', 'Gpt-4', 'Gpt-4o'].map((version) => (
            <FormControlLabel
              key={version}
              control={
                <Radio
                  checked={selectedOpenAIVersion === version}
                  onChange={() => setSelectedOpenAIVersion(version)}
                  value={version}
                  name="openai-version"
                  sx={{
                    p: 0.5,
                    '&.Mui-checked': { color: '#000080' },
                    '& svg': { fontSize: 18 }
                  }}
                />
              }
              label={<Typography fontSize={14}>{version}</Typography>}
            />
          ))}
        </Box>
      </>
    )}

    {/* Temperature Heading */}
    <Typography className="configuration_SettingsTitle" mt={3}>
      Temperature
    </Typography>

    {/* Slider Row */}
    <Box display="flex" alignItems="center" gap={2} mt={1} ml={3}>
      <Slider
        value={temperature}
        onChange={(e, newVal) => {
          setTemperature(newVal);
          setHasTouchedTemperature(true);
        }}
        min={0}
        max={1}
        step={0.1}
        sx={{
          width: 160,
          color: '#000080',
          '& .MuiSlider-thumb': {
            width: 20,
            height: 20,
          },
          '&:hover': {
            boxShadow: 'none',
            background: 'transparent',
          },
        }}
      />
      <Box
        sx={{
          minWidth: 40,
          px: 1,
          py: 0.5,
          border: '1px solid #ccc',
          borderRadius: '8px',
          textAlign: 'center',
          fontSize: '14px'
        }}
      >
        {temperature}
      </Box>
    </Box>
  </Paper>
</Box>

      </Box>

      {/* Right Section */}
      <Box className="configuration_summaryContainer">
        <Typography className="configuration_summaryTitle">Configure Summary</Typography>

        <Box className="configuration_summaryBox">
          {/* Documents */}
          <Box className="configuration_block">
            <Typography className="configuration_blockTitle">Documents</Typography>
            {selectedDocs.map((doc, idx) => (
  <Typography key={idx} className="configuration_itemText">
    {doc?.file_name || "Unknown Document"}
  </Typography>
))}
          </Box>

          <Divider className="configuration_divider" />

          {/* Use Case */}
          <Box className="configuration_block">
            <Typography className="configuration_blockTitle">Use cases</Typography>
            {selectedUseCase && (
              <Box className="configuration_chip" sx={{ width: "80px" }}>
                {selectedUseCase}
              </Box>
            )}
          </Box>

          {/* Subtypes */}
          {selectedUseCase && (
            <>
              <Divider className="configuration_divider" />
              <Box className="configuration_block">
                <Typography className="configuration_blockTitle">Sub-types</Typography>
                <Box className="configuration_chipGroup">
                  {selectedSubTypes.map((type, idx) => (
                    <Box key={idx} className="configuration_chip">
                      {type}
                    </Box>
                  ))}
                </Box>
              </Box>
            </>
          )}

          <Divider className="configuration_divider" />

<Box className="configuration_block">
  <Typography className="configuration_blockTitle">Additional Settings</Typography>

  {/* LLM Model Summary - show only if selected */}
 {selectedLLM && (
  <Box display="flex" alignItems="center" mt={1} ml={2}>
    <Typography className="configuration_summaryLabel">LLM Model:</Typography>
    <Box className="configuration_chip">
      {selectedLLM.toUpperCase()}
      {selectedLLM === 'openai' && selectedOpenAIVersion && (
        <> ({selectedOpenAIVersion.toUpperCase()})</>
      )}
    </Box>
  </Box>
)}


  {/* Temperature Summary - show only if user interacted */}
  {hasTouchedTemperature && (
  <Box display="flex" alignItems="center" mt={1} ml={2}>
    <Typography className="configuration_summaryLabel">Temperature:</Typography>
    <Box className="configuration_chip">
      {temperature}
    </Box>
  </Box>
)}
</Box>

        </Box>

        {/* Generate Button */}
        <Box className="configuration_generateButtonWrapper">
          <Button
            variant="contained"
            disabled={selectedSubTypes.length === 0 || selectedDocs.length === 0}
            onClick={handleGenerate}
            className="configuration_generateButton"
          >
            Generate
          </Button>
        </Box>
      </Box>


      <Dialog
        open={confirmDeleteOpen}
        onClose={() => setConfirmDeleteOpen(false)}
        PaperProps={{ sx: { borderRadius: 3, padding: "25px 16px" } }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight={600} mb={3}>Confirm Deletion</Typography>
        </DialogTitle>

        <DialogContent>
          <Typography mb={1}>
            Are you sure you want to delete the selected document{selectedDocs.length > 1 ? 's' : ''}?
          </Typography>
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() => setConfirmDeleteOpen(false)}
            sx={{ textTransform: 'none' }}
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              handleDelete();
              setConfirmDeleteOpen(false);
            }}
            color="error"
            variant="contained"
            sx={{ textTransform: 'none' }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>


    </Box>




  );
};

export default Configuration;
