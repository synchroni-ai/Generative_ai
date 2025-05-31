import React, { useState } from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
  Button,
  LinearProgress,
  Box
} from "@mui/material";
import {adminAxios} from '../../asessts/axios/index';
import axios from "axios";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

const UploadModal = ({ open, onClose,fetchDocuments }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadCompleted, setUploadCompleted] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
    } else {
      setFile(null);
      alert("Please select a valid PDF file.");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }
  
    console.log("Starting upload for:", file.name);
  
    setUploading(true);
    setProgress(0);
    setUploadCompleted(false); // reset it before starting new upload

  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
           const response = await adminAxios.post("/upload_document/",
      // const response = await axios.post("http://192.168.0.173:8000/process_and_generate/",
        formData,
        {
          onUploadProgress: (progressEvent) => {
            // 🔥 Place it exactly here!
            let percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
  
            // 🔥 Cap the progress at 95% until server confirms
            if (percent >= 100) {
              percent = 95;
            }
  
            setProgress(percent);
            console.log(`Upload progress: ${percent}%`);
          }
      }
    );

      
  
      console.log("Upload complete. Server response:", response.data);
  
      // ✅ Call fetchDocuments after upload success
      if (response.status === 200) {
        // ✅ Force progress to 100%
        setProgress(100);
        // ✅ Mark upload as completed
        setUploadCompleted(true);
        // ✅ Fetch documents
        fetchDocuments();
      }
  
    } catch (error) {
      console.error("Upload failed:", error);
      alert("An error occurred during file upload.");
      setUploading(false);
      onClose();
    }
  };
  

  const handleClose = () => {
    setFile(null);
    setProgress(0);
    setUploading(false);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          p: 2
        }
      }}
    >
<DialogTitle sx={{ fontWeight: 'bold' }}>
  {uploading
    ? (progress === 100 ? "Uploaded Document" : "Uploading Document...")
    : "Upload Document"}
</DialogTitle>
      <DialogContent sx={{ pt: 1 }}>
        <Box sx={{ minHeight: 180, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          {!uploading ? (
            <>
              <Box
                sx={{
                  border: "2px dashed #ccc",
                  borderRadius: "12px",
                  padding: "40px 16px",
                  textAlign: "center",
                  cursor: "pointer",
                  mb: 2,
                  "&:hover": {
                    backgroundColor: "#f9f9f9"
                  }
                }}
                onClick={() => document.getElementById("fileInput").click()}
              >
                <CloudUploadIcon sx={{ fontSize: 40, color: "#888", mb: 1 }} />
                <Typography variant="body1" color="textSecondary">
                  Drop file
                </Typography>
                {file ? (
                  <Typography
                    variant="subtitle2"
                    sx={{ mt: 2, color: "#00008B", fontWeight: 500 }}
                  >
                    {file.name}
                  </Typography>
                ) : (
                  <Button
                    variant="contained"
                    sx={{
                      mt: 2,
                      backgroundColor: "#00008B",
                      textTransform:"none",
                      "&:hover": {
                        backgroundColor: "#000060"
                      }
                    }}
                  >
                    Choose file
                  </Button>
                )}
              </Box>
              <input
                type="file"
                id="fileInput"
                accept=".pdf"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
            </>
          ) : (
            <>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "black",fontWeight:"700" }}>
                {file?.name || "Uploading..."}
              </Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={progress}
                  sx={{
                    flex: 1,
                    height: 8,
                    borderRadius: 5,
                    backgroundColor: "#f0f0f0",
                    "& .MuiLinearProgress-bar": {
                      backgroundColor: "#00008B"
                    }
                  }}
                />
                <Typography
                  variant="body2"
                  sx={{ fontWeight: "bold", color: "#00008B" }}
                >
                  {progress}%
                </Typography>
              </Box>
            </>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        {!uploading && progress === 0 && (
          <>
            <Button onClick={handleClose} color="">
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={!file}
              sx={{backgroundColor:"var(--primary-blue)",color:"white"}}
            >
              Upload
            </Button>
          </>
        )}

        {uploading && (
          <Button
            variant="outlined"
            onClick={() => handleClose(true)}
            disabled={!uploadCompleted}  // ✅ Only enable if backend confirmed success
            sx={{backgroundColor:"var(--primary-blue)",color:"white",
              "&.Mui-disabled": {
        color: "white",
        backgroundColor: "var(--primary-blue)",
        opacity: 0.6, // optional: for a subtle disabled look
      },
            }}

          >
            OK
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default UploadModal;
