import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  TextField,
  MenuItem,
  IconButton,
  InputAdornment,
  LinearProgress,
  Paper,
  Grid,
  Avatar,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  CalendarToday,
  ExpandLess,
  ExpandMore,
  InsertDriveFile,
} from '@mui/icons-material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ImageIcon from '@mui/icons-material/Image';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

const fileIcons = {
  pdf: <PictureAsPdfIcon sx={{ color: '#f44336' }} />,
  png: <ImageIcon sx={{ color: '#2196f3' }} />,
  jpg: <ImageIcon sx={{ color: '#4caf50' }} />,
  default: <InsertDriveFile sx={{ color: '#757575' }} />,
};

const filesSample = [
  { name: 'GenAI_Request_Response_Examples', size: '3.6 MB', uploaded: '2.5 MB', type: 'pdf', progress: 72 },
  { name: 'GenAI_Audit_Records', size: '5 MB', uploaded: '3 MB', type: 'jpg', progress: 60 },
  { name: 'GenAI_API_Integration_Guide', size: '4.5 MB', uploaded: '3 MB', type: 'png', progress: 67 },
  { name: 'GenAI_Security_Test_Log', size: '6 MB', uploaded: '4 MB', type: 'pdf', progress: 75 },
  { name: 'GenAI_Compliance_Checklist', size: '2.6 MB', uploaded: '2 MB', type: 'pdf', progress: 77 },
  { name: 'GenAI_Datashare_Validation', size: '3.3 MB', uploaded: '2.2 MB', type: 'jpg', progress: 66 },
  { name: 'GenAI_Audit_Records', size: '2 MB', uploaded: '1.5 MB', type: 'png', progress: 80 },
];

export default function GenAIUploader() {
  const [collapsed, setCollapsed] = useState(true);
   const [uploading, setUploading] = useState(false);
const [uploadProgress, setUploadProgress] = useState([]);
const fileInputRef = useRef(null);

  const getFileIcon = (type) => fileIcons[type] || fileIcons.default;

  return (
    <Box sx={{ p: 4, maxWidth: 900, mx: 'auto', fontFamily: 'sans-serif',width:'100%' }}>
      <Typography variant="h5" fontWeight={700} mb={3}>
        GenAI_Documentation_Overview
      </Typography>

      {/* Form with Starting Icon */}
  <Box display="flex" alignItems="flex-start" gap={8} mb={4} >
  {/* Avatar on the left */}
  <Avatar
    variant="rounded"
    sx={{ bgcolor: '#f5f5f5', width: 56, height: 56, mt: 1,  marginTop:'30px',borderRadius:"12px" }}
  >
    <InsertDriveFile sx={{ fontSize: 32, color: '#777' }} />
  </Avatar>

  <Box flex={1}>
  <Grid container spacing={2}>
    {/* Row 1: full-width Data Space */}
  <Grid item xs={12}>
  <TextField
    variant="outlined"
    label="Data Space"
    sx={{ width: 750 }}
     InputProps={{
      sx: {
        borderRadius: '12px' // Apply border radius
      }
    }}
  />
</Grid>



    {/* Row 2: three fields side-by-side */}
   <Grid container spacing={2}>
  <Grid item xs={12} md={3}>
    <TextField fullWidth variant="outlined" label="Upload by"sx={{ width: 365 }}  InputProps={{
      sx: {
        borderRadius: '12px' // Apply border radius
      }
    }} />
  </Grid>
  <Grid item xs={12} md={6}>  {/* increased from 4 to 6 */}
    <TextField fullWidth variant="outlined" label="Data space path" select     sx={{ width: 365 }}  InputProps={{
      sx: {
        borderRadius: '12px' // Apply border radius
      }
    }}>
      <MenuItem value="/path1">/path1</MenuItem>
      <MenuItem value="/path2">/path2</MenuItem>
    </TextField>
  </Grid>
</Grid>

  </Grid>
</Box>



</Box>



      {/* Main Content: Upload Area + Progress */}
      <Grid container spacing={3}>
        {/* Upload Area */}
        <Grid item xs={12} md={6}>
  <Paper
    sx={{
      border: '2px dashed #ccc',
      p: 4,
      textAlign: 'center',
      borderRadius: '12px',
      minHeight: 280,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      gap: 1,
    }}
  >
    <CloudUploadIcon sx={{ fontSize: 40, color: '#333', mb: 1 }} />

    <Typography fontWeight={600} sx={{ fontSize: '16px' }}>
      Choose a file <Typography component="span" fontWeight={400}>(or) Drag & drop it here</Typography>
    </Typography>

    <Box display="flex" alignItems="center" gap={0.5} mb={2} mt={1}>
      <InfoOutlinedIcon fontSize="small" color="disabled" />
      <Typography variant="body2" color="text.secondary">
        Supported files types: JPG, PNG, PDF, Max size is 10 MB
      </Typography>
    </Box>

<Box sx={{  display: "flex", flexDirection: "column", justifyContent: "center" }}>
  {!uploading ? (
    <>
      <Box
onClick={() => {
  if (!uploading) document.getElementById("fileInput").click();
}}
     >
          <Button
            variant="contained"
            sx={{
              mt: 2,
              backgroundColor: "#00008B",
              textTransform: "none",
              "&:hover": {
                backgroundColor: "#000060"
              }
            }}
          >
            Choose file
          </Button>
      </Box>

      {/* Hidden file input */}
      <input
        type="file"
        id="fileInput"
        style={{ display: "none" }}
          accept=".jpg,.jpeg,.png,.pdf" // restrict file types
     onChange={(e) => {
  const selectedFile = e.target.files[0];
  if (selectedFile) {
    const type = selectedFile.name.split('.').pop().toLowerCase();
    const newFile = {
      name: selectedFile.name,
      size: `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`,
      uploaded: `0 MB`,
      type: ['jpg', 'jpeg', 'png', 'pdf'].includes(type) ? type : 'default',
      progress: 0,
    };

    // Expand the progress panel when upload starts
    setCollapsed(false);

    setUploading(true);
    setUploadProgress(prev => [...prev, newFile]);

    // Simulate progress
    const interval = setInterval(() => {
      setUploadProgress(prevFiles => {
        return prevFiles.map(file => {
          if (file.name === newFile.name && file.progress < 100) {
            const updatedProgress = Math.min(file.progress + 10, 100);
            const updatedUploaded = ((parseFloat(file.size) * updatedProgress) / 100).toFixed(1);
            return {
              ...file,
              progress: updatedProgress,
              uploaded: `${updatedUploaded} MB`
            };
          }
          return file;
        });
      });
    }, 500);

    setTimeout(() => {
      clearInterval(interval);
      setUploading(false);
    }, 5000);
  }
}}


      />
    </>
  ) : null}
</Box>

  </Paper>
</Grid>

        {/* Upload Progress + Buttons */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3, maxHeight: 420,minWidth: 360, display: 'flex', flexDirection: 'column' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography fontWeight={600}>Uploading Progress</Typography>
              <IconButton onClick={() => setCollapsed(!collapsed)} size="small">
                {collapsed ? <ExpandMore /> : <ExpandLess />}
              </IconButton>
            </Box>

            {!collapsed && (
              <Box mt={2} flex={1} overflow="auto">
                {uploadProgress.map((file, index) => (
  <Box key={index} mb={2}>
    <Box display="flex" alignItems="center" gap={1} mb={0.5}>
      {getFileIcon(file.type)}
      <Box flexGrow={1}>
        <Typography
          variant="body2"
          fontWeight={600}
          sx={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
        >
          {file.name}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {file.uploaded} / {file.size}
        </Typography>
      </Box>
      <Typography variant="body2" minWidth={35}>
        {file.progress}%
      </Typography>
    </Box>
    <LinearProgress variant="determinate" value={file.progress} />
  </Box>
))}

              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
       {/* Buttons directly under upload list */}
            <Box display="flex" justifyContent="flex-end" gap={2} mt={2} mr={3}>
              <Button
                variant="outlined"
                sx={{ borderRadius: 5, textTransform: 'none' }}
              >
                Cancel
              </Button>
              <Button
                variant="outlined"
                sx={{
                  borderColor: '#000080',
                  color: '#000080',
                  borderRadius: 5,
                  textTransform: 'none',
                  fontWeight: 500,
                }}
              >
                Create
              </Button>
            </Box>
    </Box>
  );
}
