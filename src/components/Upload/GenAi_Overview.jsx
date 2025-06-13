import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  TextField,
  IconButton,
  Drawer,
  CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import CloseIcon from "@mui/icons-material/Close";
import CheckIcon from "@mui/icons-material/Check"
import { adminAxios } from '../../asessts/axios/index';

const GenAIUploader = ({ open, onClose, fetchDocuments }) => {
  const [dataSpaceName, setDataSpaceName] = useState("");
  const [dataSpaceDescription, setDataSpaceDescription] = useState("");
  const [category, setCategory] = useState("");
  const [subCategory, setSubCategory] = useState("");
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [responseData, setResponseData] = useState(null);

  const [touchedFields, setTouchedFields] = useState({
    name: false,
    description: false,
    category: false,
    subCategory: false,
  });

  const handleUpload = async () => {
    if (!dataSpaceName || !dataSpaceDescription || !category || !subCategory) {
      // Mark all fields as touched to trigger red borders
      setTouchedFields({
        name: true,
        description: true,
        category: true,
        subCategory: true,
      });
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      const response = await adminAxios.post("/api/v1/dataspaces",
        {
          name: dataSpaceName,
          description: dataSpaceDescription,
          category,
          sub_category: subCategory,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 200 || response.status === 201) {
        setModalOpen(true);
        setResponseData(response.data);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      alert("An error occurred during submission.");
    } finally {
      setLoading(false);
    }
  };


  const handleDrawerClose = () => {
    // Clear form values
    setDataSpaceName('');
    setDataSpaceDescription('');
    setCategory('');
    setSubCategory('');

    // Clear form values and touched field state
    setTouchedFields({
      name: false,
      description: false,
      category: false,
      subCategory: false,
    });
    onClose(); // Call parent handler to close drawer
  };



  const inputStyle = (isError) => ({
    '& .MuiOutlinedInput-root': {
      borderRadius: '12px',
      minHeight: '36px',
      fontSize: '13px',
      ...(isError && {
        '&:hover .MuiOutlinedInput-notchedOutline': {
          // borderColor: 'red',
          borderColor: 'none',
        },
      }),
    },
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: isError ? 'red' : '',
    },
    '&:hover .MuiOutlinedInput-notchedOutline': {
      borderColor: isError ? 'red' : '',  // keeps red on hover if error
    },
    '& .MuiInputBase-input': {
      padding: '12px 12px',
      fontSize: '13px',
    },
    '& .MuiInputLabel-root': {
      fontSize: '14px',
      color: isError ? 'red' : '',
    },
  });


  const handleCancel = () => {
    setDataSpaceName('');
    setDataSpaceDescription('');
    setCategory('');
    setSubCategory('');
    setTouchedFields({
      name: false,
      description: false,
      category: false,
      subCategory: false,
    });
    onClose();
  };




  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={handleDrawerClose}  // <-- use the new handler here
      transitionDuration={{ enter: 1000, exit: 1000 }}
      PaperProps={{
        sx: {
          width: '60%',
          height: "92%",
          borderRadius: '20px 0px 0px 20px',
          transition: "transform 2s ease-in-out",
          transform: "translate(50%, 0%)",
          padding: "0px 32px",
          mt: '64px',
          overflow: "auto",
          scrollbarWidth: "thin",
          overflowX: "hidden"
        },
      }}
    >
      <Box sx={{ fontFamily: 'sans-serif', width: '100%', maxWidth: '900px', p: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" fontWeight={700}>
            New Dataspace
          </Typography>
          <IconButton onClick={handleCancel} >
            <CloseIcon />
          </IconButton>
        </Box>

        <Box display="flex" gap={3} mb={3}>
          {/* Left side - 3 fields */}
          <Box flex={1} display="flex" flexDirection="column" gap={2}>
            <TextField
              label="Dataspace Name"
              variant="outlined"
              fullWidth
              size="small"
              value={dataSpaceName}
              onChange={(e) => setDataSpaceName(e.target.value)}
              onBlur={() => setTouchedFields(prev => ({ ...prev, name: true }))}
              onFocus={() => setTouchedFields(prev => ({ ...prev, name: false }))}
              sx={inputStyle(touchedFields.name && !dataSpaceName)}
            />

            <TextField
              label="Category"
              variant="outlined"
              fullWidth
              size="small"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              onBlur={() => setTouchedFields(prev => ({ ...prev, category: true }))}
              onFocus={() => setTouchedFields(prev => ({ ...prev, category: false }))}
              sx={inputStyle(touchedFields.category && !category)}
            />

            <TextField
              label="Subcategory"
              variant="outlined"
              fullWidth
              size="small"
              value={subCategory}
              onChange={(e) => setSubCategory(e.target.value)}
              onBlur={() => setTouchedFields(prev => ({ ...prev, subCategory: true }))}
              onFocus={() => setTouchedFields(prev => ({ ...prev, subCategory: false }))}
              sx={inputStyle(touchedFields.subCategory && !subCategory)}
            />
          </Box>

          {/* Right side - Description input field */}
          <Box flex={1}>
            <TextField
              label="Description"
              variant="outlined"
              fullWidth
              multiline
              minRows={7}
              maxRows={8}
              value={dataSpaceDescription}
              onChange={(e) => setDataSpaceDescription(e.target.value)}
              onBlur={() => setTouchedFields(prev => ({ ...prev, description: true }))}
              onFocus={() => setTouchedFields(prev => ({ ...prev, description: false }))}
              sx={{
                ...inputStyle(touchedFields.description && !dataSpaceDescription),
                '& textarea': {
                  fontSize: '13px',
                  maxHeight: '105px',
                  overflowY: 'auto',
                  scrollbarWidth: 'thin',
                },
                '& textarea::-webkit-scrollbar': {
                  width: '6px',
                },
                '& textarea::-webkit-scrollbar-thumb': {
                  backgroundColor: '#ccc',
                  borderRadius: '4px',
                },
              }}
            />
          </Box>
        </Box>

        {/* Buttons directly under upload list */}
        <Box display="flex" justifyContent="flex-end" gap={2} mt={5} mr={3}>
          <Button
            disableRipple
            onClick={handleCancel}
            sx={{ borderRadius: '20px', textTransform: 'none', padding: '6px 16px', color: "grey" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={
              loading}
            sx={{
              border: '1px solid var(--primary-blue)',
              color: 'var(--primary-blue)',
              borderRadius: '20px',
              textTransform: 'none',
              padding: '1px 28px',
              '&:hover': {
                borderColor: 'var(--primary-blue)',
                color: 'var(--primary-blue)',
                backgroundColor: 'transparent',
              },
              '&.Mui-disabled': {
                border: 'none',
                color: 'grey',
                backgroundColor: '#f5f5f5', // optional: light background to show it's disabled
              },
            }}
          >
            {loading ? (
              <Box display="flex" alignItems="center" gap={1}>
                <span>Create</span>
                <CircularProgress size={18} sx={{ color: '#fff' }} />
              </Box>) : (
              'Create')}              </Button>
        </Box>
      </Box>
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        PaperProps={{
          sx: {
            width: '400px',
            maxWidth: '90vw',
            borderRadius: 2,
            padding: 2,
          }
        }}
      >
        <DialogTitle sx={{ fontWeight: 'bold' }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Box
              sx={{
                width: 32,
                height: 32,
                backgroundColor: "#4caf50", // green
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CheckIcon sx={{ color: "white", fontSize: 20 }} />
            </Box>
            <Typography variant="h5" fontWeight={600} color="#4caf50">
              Dataspace Created
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ ml: "20px", mt: 1 }}>
          <Typography fontSize="14px" fontWeight={500}>
            Successfully new dataspace is created.
          </Typography>
        </DialogContent>

        <DialogActions>
          <Button
            variant="outlined"
            onClick={() => {
              setModalOpen(false);
              onClose();             // Close the drawer
              if (fetchDocuments) fetchDocuments(); // refresh list if provided
            }}
            sx={{
              backgroundColor: "var(--primary-blue)",
              color: "white",
              "&.Mui-disabled": {
                color: "white",
                backgroundColor: "var(--primary-blue)",
                opacity: 0.6,
              },
            }}
          >
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </Drawer>
  );
};

export default GenAIUploader;
