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
import CloseIcon from '@mui/icons-material/Close';
import { adminAxios } from '../../asessts/axios/index';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import DeleteIcon from "./../../asessts/images/deleteicon.png";
import NewDocumentModal from './AddDocumentModal';
import './configuration.css';


const Configuration = ({ selectedDocs, setSelectedDocs, selectedUseCase, setSelectedUseCase, selectedSubTypes, setSelectedSubTypes, onGenerate, dataSpaceId, generationId, selectedLLM, setSelectedLLM, temperature, setTemperature, onClose }) => {
  const [documentsData, setDocumentsData] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

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

  const handleCloseAndReset = () => {
    setSelectedDocs([]);
    setSelectedUseCase('');
    setSelectedSubTypes([]);
    setIsGenerating(false);
    onClose();
  };

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

    const payload = {
      documents: selectedDocs.map(doc => doc.file_id),
      config: {
        llm_model: selectedLLM === 'mistral' ? 'Mistral' : 'GPT-4',
        temperature: temperature,
        use_case: ['test case generation'],
        subtypes: selectedSubTypes.map(type =>
          type.toLowerCase().replace(/\s|-/g, '_')
        ),
      },
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
        onClose();              // 👈 Close the drawer
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
    <>
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          left: 25,
          right: 16,
          zIndex: 1301,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        {/* Left Heading */}
        <Typography variant="h6" fontWeight="bold">
          Configuration
        </Typography>

        {/* Right Close Button */}
        <IconButton onClick={handleCloseAndReset}>
          <CloseIcon />
        </IconButton>
      </Box>


      <Box display="flex" flexDirection={{ xs: 'column', md: 'row' }} gap={6} mb={6} sx={{ padding: "0px 10px", marginTop: "68px" }}>

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
                      checked={selectedLLM === 'gpt4'}
                      onChange={() => setSelectedLLM('gpt4')}
                      value="gpt4"
                      name="llm-model"
                      sx={{
                        p: 0.5,
                        '&.Mui-checked': { color: '#000080' },
                        '& svg': { fontSize: 20 }
                      }}
                    />
                  }
                  label={<Typography fontSize={15}>GPT-4</Typography>}
                />
              </Box>

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
                  }}
                  min={0}
                  max={1}
                  step={0.1}
                  sx={{
                    width: 160,
                    color: '#000080', // default MUI blue, or you can use '#000080'
                    '& .MuiSlider-thumb': {
                      width: 20,
                      height: 20,
                    },
                    '&:hover': {
                      boxShadow: 'none',
                      background: 'transparent', // removes glow
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
                  </Box>
                </Box>
              )}

              {/* Temperature Summary - show only if user interacted */}
              <Box display="flex" alignItems="center" mt={1} ml={2}>
                <Typography className="configuration_summaryLabel">Temperature:</Typography>
                <Box className="configuration_chip">
                  {temperature}
                </Box>
              </Box>
            </Box>
          </Box>

          {/* Generate Button */}
          <Box className="configuration_generateButtonWrapper">
            <Button
              variant="contained"
              disabled={
                selectedDocs.length === 0 ||
                selectedSubTypes.length === 0 ||
                !selectedLLM ||
                temperature === null || temperature === undefined
              }
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
    </>
  );
};
export default Configuration;
