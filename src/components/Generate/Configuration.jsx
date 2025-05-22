// components/Configuration.jsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Grid, Paper, Typography, IconButton, List, ListItem, ListItemIcon, Checkbox, ListItemText,
  Box, Button, Divider
} from '@mui/material';
import { adminAxios } from '../../asessts/axios/index';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const Configuration = ({ selectedSubTypes, setSelectedSubTypes, onGenerate, dataSpaceId }) => {
  console.log("Received dataSpaceId:", dataSpaceId);
  const [documentsData, setDocumentsData] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [collapsed, setCollapsed] = useState(false);


  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await adminAxios.get(`/api/v1/data-spaces/${dataSpaceId}/documents/`);
        const fetchedDocs = response.data.map(doc => doc.file_name);
        setDocumentsData(fetchedDocs);
        setSelectedDocs([]);// Optional: preselect all on load
      } catch (error) {
        console.error("Error fetching documents for data space:", error);
      }
    };

    if (dataSpaceId) {
      fetchDocuments();
    }
  }, [dataSpaceId]);
  // const documentsData = [
  //   'LMSDashboardWireframes-StructureSheet.xlsx',
  //   'designdocumentation.PDF',
  //   'CompleteUIScreenDesigns-FigmaExport.pdf',
  //   'UserJourneyFlows-LMSNavigationMap.pdf',
  //   'CourseContentOutline-WeeklyModules.docx',
  //   'AdminPanelUIDesign-VisualLayoutPreview.png',
  //   'DesignReviewFeedback-Iteration1.xlsx',
  // ];

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

  // State inside the component
  // const [selectedDocs, setSelectedDocs] = useState([
  //   'CompleteUIScreenDesigns-FigmaExport.pdf',
  //   'AdminPanelUIDesign-VisualLayoutPreview.png',
  //   'designdocumentation.PDF',
  //   'LMSDashboardWireframes-StructureSheet.xlsx',
  // ]);

  // const [collapsed, setCollapsed] = useState(false);
  const [selectedUseCase, setSelectedUseCase] = useState('');
  // const [selectedSubTypes, setSelectedSubTypes] = useState([]);
  const documentsRef = useRef(null); // For outside click


  // useEffect(() => {
  //   const handleClickOutside = (event) => {
  //     if (documentsRef.current && !documentsRef.current.contains(event.target)) {
  //       setCollapsed(true); // Collapse if clicking outside
  //     }
  //   };

  //   document.addEventListener('mousedown', handleClickOutside);
  //   return () => {
  //     document.removeEventListener('mousedown', handleClickOutside);
  //   };
  // }, []);


  const toggleDocument = (doc) => {
    setSelectedDocs((prevSelected) =>
      prevSelected.includes(doc)
        ? prevSelected.filter((d) => d !== doc)
        : [...prevSelected, doc]
    );
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

  return (
    <Box display="flex" flexDirection={{ xs: 'column', md: 'row' }} gap={6} mb={6} sx={{ padding: "0px 50px" }}>
      {/* Left Section */}
      <Box flex={1}>
        {/* Documents */}
        <Box
          ref={documentsRef}
          sx={{
            padding: "8px 16px",
            borderRadius: 3,
            mb: 5,
            border: '1px solid #EBEBEB'
          }}
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={0}
            sx={{ cursor: 'pointer' }}
            onClick={() => setCollapsed(!collapsed)}
          >
            <Typography fontWeight={600} fontSize={18}>Documents</Typography>
            <IconButton size="small" disableRipple disableFocusRipple sx={{ pointerEvents: 'none' }}>
              {collapsed ? <ExpandMoreIcon /> : <ExpandLessIcon />}
            </IconButton>
          </Box>

          {!collapsed && (
            <List sx={{ maxHeight: 300, overflow: 'auto', scrollbarWidth: "none", padding: '15px 25px' }}>
              {/* Select All Checkbox */}
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
                      setSelectedDocs(e.target.checked ? documentsData : []);
                    }}
                    sx={{
                      color: 'inherit',
                      '&.Mui-checked': { color: '#000080' },
                      '&.MuiCheckbox-indeterminate': { color: '#000080' },
                      '& .MuiSvgIcon-root': { borderRadius: '4px' },
                    }}
                  />

                </ListItemIcon>
                <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary="Select All" />
              </ListItem>

              {/* Individual Checkboxes */}
              {documentsData.map((doc, index) => (
                <ListItem key={index} disablePadding>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={selectedDocs.includes(doc)}
                      tabIndex={-1}
                      disableRipple
                      onChange={() => toggleDocument(doc)}
                      sx={{
                        color: selectedDocs.includes(doc) ? '#000080' : '#c4c4c4',
                        '&.Mui-checked': { color: '#000080' },
                        '& .MuiSvgIcon-root': { borderRadius: '4px' },
                      }}
                    />
                  </ListItemIcon>
                  <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary={doc} />
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Use Cases */}
        <Typography fontWeight={600} fontSize={18} mb={1} ml={2} sx={{ color: '#333' }}>
          Use Cases
        </Typography>
        <Paper elevation={0} sx={{ backgroundColor: '#F6F4FF', borderRadius: 3, p: 2 }}>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(3, 1fr)' },
              gap: 1.5,
            }}
          >
            {useCaseOptions.map((useCase) => {
              const isTestCases = useCase === 'Test Cases';
              const isSelected = selectedUseCase === useCase;

              return (
                <Button
                  key={useCase}
                  disableRipple
                  onClick={() => handleUseCaseSelect(useCase)}
                  disabled={!isTestCases}
                  sx={{
                    justifyContent: 'flex-start',
                    color: isSelected ? '#0A0080' : isTestCases ? '#000' : '#aaa',
                    fontSize: 14,
                    fontWeight: isSelected ? 600 : 400,
                    textTransform: 'none',
                    px: 1,
                    py: 1,
                    borderRadius: 2,
                    minWidth: 'unset',
                    boxShadow: 'none',
                    cursor: isTestCases ? 'pointer' : 'default',
                  }}
                >
                  <Box
                    sx={{
                      width: 16,
                      height: 16,
                      borderRadius: '50%',
                      border: '1.5px solid',
                      borderColor: isSelected ? '#0A0080' : isTestCases ? '#000' : '#aaa',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 1,
                    }}
                  >
                    {isSelected && (
                      <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#0A0080' }} />
                    )}
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
            <Typography fontWeight={600} fontSize={18} mt={4} ml={2} sx={{ color: '#333' }}>
              Sub-types
            </Typography>
            <Paper elevation={0} sx={{ borderRadius: 3, p: 2 }}>
              <Box display="flex" flexWrap="wrap" gap={2}>
                {subTypes.map((type) => (
                  <Box key={type} display="flex" alignItems="center" width={{ xs: '50%', sm: '25%' }}>
                    <Checkbox
                      size="small"
                      disableRipple
                      checked={selectedSubTypes.includes(type)}
                      onChange={() => toggleSubType(type)}
                      sx={{
                        color: selectedSubTypes.includes(type) ? '#000080' : '#c4c4c4',
                        '&:hover': { backgroundColor: 'transparent' },
                        '&.Mui-checked': { color: '#000080' },
                        '& .MuiSvgIcon-root': { borderRadius: '4px' },
                      }}
                    />
                    <Typography fontSize={13}>{type}</Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </>
        )}
      </Box>

      {/* Right Section */}
      <Box
        width={{ xs: '100%', md: '35%' }}
        sx={{
          position: { md: 'sticky' },
          top: { md: 80 }, // adjust as needed based on your header height
          alignSelf: 'flex-start', // ensures correct layout in flexbox
        }}
      >
        <Typography fontSize={18} fontWeight={700} mb={1.5}>Configure Summary</Typography>
        <Box sx={{ p: 2, borderRadius: 3, border: '1px solid #EBEBEB' }}>
          <Box mb={2}>
            <Typography fontSize={16} fontWeight={600} mb={2} sx={{ color: "#252525" }}>
              Documents
            </Typography>
            {selectedDocs.map((doc, idx) => (
              <Typography key={idx} fontSize={14} sx={{ color: '#000080', fontWeight: 400, mb: "3px", ml: "15px" }}>
                {doc}
              </Typography>
            ))}
          </Box>
          <Divider sx={{ my: 2 }} />
          <Box>
            <Typography fontSize={16} fontWeight={600} mb={1} sx={{ color: "#252525" }}>
              Use cases
            </Typography>
            <Box sx={{
              backgroundColor: '#FCFCFC', color: '#666', fontSize: 14, px: 1.5,
              py: 0.5, borderRadius: '12px', fontWeight: 500, width: "80px", ml: '15px'
            }}>
              <Typography fontSize={14} fontWeight={500}>{selectedUseCase}</Typography>
            </Box>
          </Box>

          {selectedUseCase && (
            <>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Typography fontSize={16} fontWeight={600} mb={1} sx={{ color: "#252525" }}>
                  Sub-types
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {selectedSubTypes.map((type, idx) => (
                    <Box key={idx} sx={{
                      backgroundColor: '#FCFCFC', color: '#666', fontSize: 14,
                      px: 1.5, py: 0.5, borderRadius: '12px', fontWeight: 500, ml: '15px'
                    }}>
                      {type}
                    </Box>
                  ))}
                </Box>
              </Box>
            </>
          )}
        </Box>

        {/* Generate Button */}
        <Box display="flex" justifyContent="flex-end" mt={3}>
          <Button
            variant="contained"
            disabled={selectedSubTypes.length === 0}
            onClick={onGenerate}
            sx={{
              backgroundColor: '#0A0080',
              borderRadius: '999px',
              fontSize: 14,
              textTransform: 'none',
              fontWeight: 500,
              px: 3,
              py: 1,
              boxShadow: 'none',
              '&:hover': { backgroundColor: '#07006B' },
            }}
          >
            Generate
          </Button>
        </Box>
      </Box>
    </Box>

  );
};

export default Configuration;
