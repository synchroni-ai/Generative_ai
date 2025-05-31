import React, { useState,useEffect } from 'react';
import {
  Modal,
  Box,
  Typography,
  IconButton,
  Button,
  Paper,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import {
  ExpandLess,
  ExpandMore,
  InsertDriveFile,
} from '@mui/icons-material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import Cloudicon from "./../../asessts/images/cloudicon.png";
import Choosefileicon from "./../../asessts/images/choosefile.png";
import ImageIcon from '@mui/icons-material/Image';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

const fileIcons = {
  pdf: <PictureAsPdfIcon sx={{ color: '#f44336' }} />,
  png: <ImageIcon sx={{ color: '#2196f3' }} />,
  jpg: <ImageIcon sx={{ color: '#4caf50' }} />,
  default: <InsertDriveFile sx={{ color: '#757575' }} />,
};

const NewDocumentModal = ({ open, onClose }) => {
    const [file, setFile] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
const [uploadCompleted, setUploadCompleted] = useState(false);
const [progress, setProgress] = useState(0);
const [isDragging, setIsDragging] = useState(false);

  const handleClose = () => {
    setSelectedFiles([]);

    setFile(null);

    setUploadProgress([]);

    setProgress(0);

    setUploadCompleted(false);

    setCollapsed(true);


    if (onClose) onClose();
  };
  

const handleFileChange = (e) => {
  const newFiles = Array.from(e.target.files);
  if (newFiles.length) {
    const updatedFiles = [...selectedFiles, ...newFiles];
    const uniqueFiles = Array.from(new Map(updatedFiles.map(file => [file.name, file])).values());
    setSelectedFiles(uniqueFiles);

    // Expand progress section on file selection
    setCollapsed(false);

    newFiles.forEach(file => {
      if (!selectedFiles.some(f => f.name === file.name)) {
        triggerSimulatedProgress(file);
      }
    });
  }
  e.target.value = '';
};


  const triggerSimulatedProgress = (file) => {
    const progressItem = {
      name: file.name,
      type: file.type,
      size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
      uploaded: '0 MB',
      progress: 0,
    };

    setUploadProgress(prev => [...prev, progressItem]);

    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setUploadProgress(prev =>
        prev.map(f =>
          f.name === file.name
            ? {
                ...f,
                progress: Math.min(progress, 100),
                uploaded: `${((file.size * Math.min(progress, 100)) / 100 / 1024 / 1024).toFixed(1)} MB`
              }
            : f
        )
      );

      if (progress >= 100) {
        clearInterval(interval);
      }
    }, 300);
  };

 const getFileIcon = (type) => {
  const extension = type.split('/').pop(); // e.g., 'pdf' from 'application/pdf'
  return fileIcons[extension] || fileIcons.default;
};

useEffect(() => {
  if (uploadProgress.length === 0) {
    setCollapsed(true);
  }
}, [uploadProgress]);


  const handleUpload = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    //   setOpen(false);
    }, 1500);
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <Box
        onClick={(e) => e.stopPropagation()}
    onKeyDown={(e) => e.stopPropagation()}
        sx={{
          width: '70%',
          maxHeight: '90vh',
          overflowY: 'auto',
          bgcolor: 'background.paper',
          margin: '5% auto',
          borderRadius: 3,
          p: 4,
        }}
      >
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" fontWeight={700}>Add Document</Typography>
          <IconButton onClick={handleClose}><CloseIcon /></IconButton>
        </Box>

        {/* Upload Area */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'space-between',margin:"0px 30px" }}>
          <Paper
  onDragEnter={(e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }}
  onDragLeave={(e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }}
  onDragOver={(e) => {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'copy';
    setIsDragging(true);
  }}
  onDrop={(e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    const pdfFiles = droppedFiles.filter((file) => file.type === 'application/pdf');

    if (pdfFiles.length > 0) {
      const event = {
        target: {
          files: pdfFiles,
        },
      };
      handleFileChange(event);
    }
  }}
  sx={{
    border: isDragging ? '2px dashed var(--primary-blue)' : '2px dashed #D9D9D9',
    textAlign: 'center',
    borderRadius: '16px',
    minHeight: 280,
    minWidth: 220,
    flex: '1 1 0',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 2,
    boxShadow: 'none',
    backgroundColor: isDragging ? '#f0f6ff' : 'transparent',
    transition: 'background-color 0.3s ease',
  }}
>
            <img src={Cloudicon} alt="Upload" style={{ width: 50, height: 50, marginBottom: '8px' }} />
            <Typography fontWeight={500} fontSize="16px" color="#494949">
              Choose a file{' '}
              <Typography component="span" fontWeight={500} color="#494949">
                (or) Drag & drop it here
              </Typography>
            </Typography>
            <Box display="flex" alignItems="center" gap={0.5} mb={2} mt={0}>
              <InfoOutlinedIcon fontSize="small" color="disabled" />
              <Typography variant="body2" color="#666">Supported file type: PDF Max size is 10 MB</Typography>
            </Box>
            <Box>
              <Button
                onClick={() => !uploading && document.getElementById('fileInput').click()}
                disabled={uploading}
                sx={{
                  mt: 2,
                  backgroundColor: uploading ? '#ccc' : 'var(--primary-blue)',
                  color: '#fff',
                  padding: '6px 16px',
                  fontSize: '14px',
                  borderRadius: '30px',
                  textTransform: 'none',
                  boxShadow: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  '&:hover': { backgroundColor: uploading ? '#ccc' : 'var(--primary-blue)' },
                }}
              >
                <img src={Choosefileicon} alt="icon" style={{ width: 20, height: 20 }} />
                Choose file
              </Button>
              <input
                type="file"
                multiple
                id="fileInput"
                style={{ display: 'none' }}
                accept=".pdf"
                onChange={handleFileChange}
              />
            </Box>
          </Paper>

          {/* Upload Progress Section */}
          <Box
            sx={{
              padding: '10px 0px 10px 10px',
              borderRadius: 3,
                            maxHeight: collapsed ? 40 : 'auto', // Collapsed = small height
              minWidth: 220,
              flex: '1 1 0',
              display: 'flex',
              flexDirection: 'column',
              bgcolor: '#fff',
              border: '1px solid #EBEBEB'
            }}
          >
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography fontWeight={600} fontSize="16px">Uploading Progress</Typography>
           <IconButton
  onClick={() => {
    if (uploadProgress.length > 0) setCollapsed(!collapsed);
  }}
  disabled={uploadProgress.length === 0}
  size="small"
  sx={{ color: uploadProgress.length === 0 ? '#ccc' : 'inherit' }}
>
  {collapsed ? <ExpandMore /> : <ExpandLess />}
</IconButton>


            </Box>

            {!collapsed && (
              <Box mt={2} px={3} maxHeight={200} overflow="auto" sx={{scrollbarWidth:"thin"}}>
                {uploadProgress.map((file, index) => (
                  <Box
                    key={index}
                    mb={2}
                    sx={{
                      position: 'relative',
                      border: '1px solid #eee',
                      borderRadius: 2,
                      padding: '8px 16px',
                    //   backgroundColor: '#fafafa'
                    }}
                  >
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedFiles(prev => prev.filter(f => f.name !== file.name));
                        setUploadProgress(prev => prev.filter(f => f.name !== file.name));
                      }}
                      sx={{ position: 'absolute', top: 4, right: 4, padding: 0.5 }}
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getFileIcon(file.type)}
                      <Box flexGrow={1}>
                        <Typography fontWeight={500} fontSize="12px" noWrap>{file.name}</Typography>
                        <Typography variant="caption" color="text.secondary">{file.uploaded} / {file.size}</Typography>
                      </Box>
                      <Box position="relative" display="inline-flex" mr={6}>
                        <CircularProgress variant="determinate" value={file.progress} size={30} thickness={3} sx={{ color: 'var(--primary-blue)' }} />
                        <Box
                          top={0}
                          left={0}
                          bottom={0}
                          right={0}
                          position="absolute"
                          display="flex"
                          alignItems="center"
                          justifyContent="center"
                        >
                          <Typography variant="caption" fontWeight={500} sx={{ fontSize: '0.65rem' }}>
                            {file.progress}%
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                    <Box mt={1.5} width="90%">
                      <LinearProgress
                        variant="determinate"
                        value={file.progress}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#e0e0e0',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 3,
                            backgroundColor: 'var(--primary-blue)'
                          }
                        }}
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </Box>

        {/* Footer */}
        <Box display="flex" justifyContent="flex-end" gap={2} mt={5} mr={3}>
          <Button
            disableRipple
            onClick={handleClose}
            sx={{ borderRadius: '20px', textTransform: 'none', padding: '6px 16px', color: "grey" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={loading || selectedFiles.length === 0 || uploadProgress.some(f => f.progress < 100)}
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
                backgroundColor: '#f5f5f5',
              },
            }}
          >
            {loading ? (
              <Box display="flex" alignItems="center" gap={1}>
                <span>Create</span>
                <CircularProgress size={18} sx={{ color: 'var(--primary-blue)' }} />
              </Box>
            ) : 'Create'}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default NewDocumentModal;
