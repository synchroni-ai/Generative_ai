import React, { useEffect, useState, useRef  } from "react";
import {
  Drawer,
  Box,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
} from "@mui/material";
import {adminAxios} from '../../asessts/axios/index';
import {WebsocketAxios} from '../../asessts/axios/index';
import axios from "axios";
import CloseIcon from "@mui/icons-material/Close";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import Papa from "papaparse";


const GenerateDrawer = ({ open, onClose, documentName, taskId   }) => {
  const [parsedData, setParsedData] = useState([]);
  const [headers, setHeaders] = useState([]);
 const [loading, setLoading] = useState(true);
  const socketRef = useRef(null);
const [error, setError] = useState(false);
const [documentId, setDocumentId] = useState(null);
        // console.log("Documensst ID received:", documentId);

 useEffect(() => {
  if (!taskId) return;

  setLoading(true);
  setError(false);
  setDocumentId(null);
  setParsedData([]);
  setHeaders([]);

  const socketUrl = `${WebsocketAxios}/task_status?task_id=${taskId}`;
  socketRef.current = new WebSocket(socketUrl);

  socketRef.current.onopen = () => {
    console.log("✅ WebSocket connected");
    setError(false);
  };

 socketRef.current.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("📨 WebSocket message received:", data);

  if (data.status === "SUCCESS" && data.result?.results) {
    const allRows = [];

    data.result.results.forEach((item) => {
      const testCaseBlocks = (item.test_cases || "").split('---').map(block => block.trim()).filter(Boolean);

      testCaseBlocks.forEach((block) => {
        const lines = block.split("\n").filter((line) => line.includes(":"));
        const row = {};

        lines.forEach((line) => {
          const [key, ...rest] = line.split(":");
          row[key.trim()] = rest.join(":").trim();
        });

        row["Test Case Type"] = item.test_case_type; // Optional: add context
        allRows.push(row);
      });
    });

    if (allRows.length > 0) {
      const filteredHeaders = Object.keys(allRows[0]).filter(
        (key) => key.toLowerCase() !== "test cases" && key.toLowerCase() !== "test_cases"
      );

      setHeaders(filteredHeaders);
      setParsedData(
        allRows.map((row) => {
          const filteredRow = { ...row };
          delete filteredRow["Test Cases"];
          delete filteredRow["test_cases"];
          return filteredRow;
        })
      );
    }

    if (data.result?.combined_test_case_document?._id) {
      console.log("Document ID received:", data.result._id);
      setDocumentId(data.result.combined_test_case_document._id);
    }

    setLoading(false);
  } else if (data.status === "FAILURE") {
    console.error("❌ Task failed:", data.result?.message);
    setError(true);
    setLoading(false);
  }
};


  socketRef.current.onerror = (event) => {
    console.error("🛑 WebSocket error:", event);
    setError(true);
    setLoading(false);
  };

  socketRef.current.onclose = () => {
    console.log("🔌 WebSocket connection closed");
  };

  return () => {
    socketRef.current?.close();
  };
}, [taskId]);


  const handleDownloadCSV = async () => {
  if (!documentId) return;
  console.log("Downloading CSV for documentId:", documentId);  // <-- added log here

  try {
    const response = await adminAxios.get(`/download-csv/${documentId}`, {
      responseType: 'blob', // Important for file download
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${documentName || "test-cases"}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error("Error downloading CSV:", error);
  }
};



  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      transitionDuration={{ enter: 1000, exit: 1000 }}
      PaperProps={{
        sx: {
          width: "70%",
          padding: "0px 23px",
          height: "92%",
          top: "64px",
          transition: "transform 2s ease-in-out",
          transform: "translate(50%, 0%)",
          borderRadius: "20px 0px 0px 20px",
          overflow: "auto",
          overflowY:"hidden"
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          p: 2,
          borderBottom: "1px solid #ddd",
          backgroundColor: "#fff",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <Box sx={{ fontSize: "18px", fontWeight: 600 }}>Generate Test Cases</Box>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Document Name */}
      {documentName && (
  <Box
    sx={{
      display: "flex",
      alignItems: "center",
      p: 2,
    }}
  >
    <Box sx={{ fontWeight: 600, fontSize: "16px", color: "#333",marginRight:"20px" }}>
      Document: <span>{documentName}</span>
    </Box>
    <IconButton onClick={handleDownloadCSV}  disabled={!documentId} sx={{ mt: "2px" }} // 👈 moves the icon 2px down
>
      <FileDownloadIcon />
    </IconButton>
  </Box>
)}


      {/* Table Section */}
      <Box sx={{ p: 2  ,height: '500px', // same height as your scrollable area for consistency
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  }}>
        {parsedData.length === 0 ? (
          <CircularProgress />
        ) : (
          <TableContainer component={Paper}
           sx={{
    maxHeight: '500px', // Set a height to enable scrolling
    overflow: 'auto',
    '&::-webkit-scrollbar': {
      width: '6px', // Thin width
      height: '6px',
    },
    '&::-webkit-scrollbar-thumb': {
      backgroundColor: '#c1c1c1',
      borderRadius: '10px',
    },
    '&::-webkit-scrollbar-track': {
      backgroundColor: '#f1f1f1',
    },
    scrollbarWidth: 'thin', // Firefox
    scrollbarColor: '#c1c1c1 #f1f1f1', // Firefox
  }}>
            <Table sx={{ minWidth: 650 }} size="small" >
              <TableHead>
                <TableRow>
                  {headers.map((header) => (
                    <TableCell key={header} sx={{ fontWeight: 600 }}>
                      {header}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {parsedData.map((row, index) => (
                  <TableRow key={index}>
                    {headers.map((key) => (
                      <TableCell key={key}>{row[key]}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Drawer>
  );
};

export default GenerateDrawer;
