// import React, { useState } from "react";
// import {
//   Drawer,
//   Box,
//   Button,
//   IconButton,
//   Checkbox,
//   FormControlLabel,
//   Grid
// } from "@mui/material";
// import CloseIcon from "@mui/icons-material/Close";
// import FileDownloadIcon from "@mui/icons-material/FileDownload";

// const GenerateDrawer = ({ open, onClose, data, parseFormattedText }) => {
//   const [checkedItems, setCheckedItems] = useState({
//     boundary: false,
//     security: false,
//     performance: false,
//     functional: false,
//     "non-functional": false,
//     compliance: false,
//   });

//   const [isGenerateDisabled, setGenerateDisabled] = useState(true);

//   const handleChange = (event) => {
//     const newCheckedItems = {
//       ...checkedItems,
//       [event.target.name]: event.target.checked,
//     };
//     setCheckedItems(newCheckedItems);

//     // Enable Generate button if at least one checkbox is selected
//     setGenerateDisabled(Object.values(newCheckedItems).every((val) => !val));
//   };

//   const handleGenerate = () => {
//     // Implement the logic for generating test cases
//     console.log("Generating test cases...");
//   };

//   return (
//     <Drawer
//       anchor="right"
//       open={open}
//       onClose={onClose}
//       transitionDuration={{ enter: 1000, exit: 1000 }}
//       PaperProps={{
//         sx: {
//           width: "70%",
//           padding: "0px 23px",
//           height: "92%",
//           top: "64px",
//           transition: "transform 2s ease-in-out",
//           transform: "translate(50%, 0%)",
//           borderRadius: "20px 0px 0px 20px",
//           scrollbarWidth: "thin"
//         },
//       }}
//     >
//       <Box
//         sx={{
//           display: "flex",
//           flexDirection: "column",
//           position: "sticky",
//           top: 0,
//           backgroundColor: "#fff",
//           zIndex: 1000,
//           paddingY: 2,
//           paddingX: 2,
//         }}
//       >
//         <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
//           <Box sx={{ fontSize: "18px", fontWeight: 600, ml: 1 }}>
//             Generate Test Cases
//           </Box>
//           <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
//             <IconButton
//               onClick={() => {
//                 // Export logic here
//               }}
//             >
//               <FileDownloadIcon />
//             </IconButton>
//             <IconButton onClick={onClose}>
//               <CloseIcon />
//             </IconButton>
//           </Box>
//         </Box>
//       </Box>

//       {/* Checkboxes */}
//       {/* <Box sx={{ mt: 0, ml: 3, p: 2, borderRadius: "15px" }}>
//         <Grid container spacing={2}>
//           {Object.keys(checkedItems).map((key) => (
//             <Grid item xs={4} key={key}>
//               <FormControlLabel
//                 control={
//                   <Checkbox
//                     checked={checkedItems[key]}
//                     onChange={handleChange}
//                     name={key}
//                   />
//                 }
//                 label={key.charAt(0).toUpperCase() + key.slice(1)}
//               />
//             </Grid>
//           ))}
//         </Grid>
//       </Box>

//       <Box sx={{ position: "absolute", bottom: 16, right: 16, width: "auto" }}>
//         <Button
//           variant="contained"
//           color="primary"
//           disabled={isGenerateDisabled} // Disable button when no checkbox is selected
//           onClick={handleGenerate}
//         >
//           Generate
//         </Button>
//       </Box> */}
//     </Drawer>
//   );
// };

// export default GenerateDrawer;



// import React from "react";
// import {
//   Drawer,
//   Box,
//   IconButton,
//   Table,
//   TableBody,
//   TableCell,
//   TableContainer,
//   TableHead,
//   TableRow,
//   Paper
// } from "@mui/material";
// import CloseIcon from "@mui/icons-material/Close";
// import FileDownloadIcon from "@mui/icons-material/FileDownload";

// // Sample test case data
// const testCaseData = [
//   {
//     TCID: "BTC_001",
//     "Test type": "Boundary",
//     Title: "Validate Minimum Password Length",
//     Description: "Test the system with the minimum acceptable password length.",
//     Precondition: "None",
//     Steps:
//       "1. Navigate to the login page. 2. Enter a username. 3. Enter a password with the minimum length (assuming the minimum length is 8 characters, e.g., \"Password\"). 4. Click on the login button.",
//     Action: "Entering a password with the minimum length.",
//     Data: 'Username: testuser, Password: "Password"',
//     Result: "The system should accept the password and allow login.",
//     "Type (P / N / in)": "P",
//     "Test priority": "High"
//   },
//   {
//     TCID: "BTC_002",
//     "Test type": "Boundary",
//     Title: "Validate Maximum Password Length",
//     Description: "Test the system with the maximum acceptable password length.",
//     Precondition: "None",
//     Steps:
//       "1. Navigate to the login page. 2. Enter a username. 3. Enter a password with the maximum length (assuming the maximum length is 20 characters, e.g., \"Password123456789012345\"). 4. Click on the login button.",
//     Action: "Entering a password with the maximum length.",
//     Data: 'Username: testuser, Password: "Password123456789012345"',
//     Result: "The system should accept the password and allow login.",
//     "Type (P / N / in)": "P",
//     "Test priority": "High"
//   }
// ];

// const GenerateDrawer = ({ open, onClose }) => {
//   return (
//     <Drawer
//       anchor="right"
//       open={open}
//       onClose={onClose}
//       transitionDuration={{ enter: 1000, exit: 1000 }}
//       PaperProps={{
//         sx: {
//           width: "70%",
//           padding: "0px 23px",
//           height: "92%",
//           top: "64px",
//           transition: "transform 2s ease-in-out",
//           transform: "translate(50%, 0%)",
//           borderRadius: "20px 0px 0px 20px",
//           overflow: "auto"
//         },
//       }}
//     >
//       {/* Header */}
//       <Box
//         sx={{
//           display: "flex",
//           justifyContent: "space-between",
//           alignItems: "center",
//           p: 2,
//           borderBottom: "1px solid #ddd",
//           backgroundColor: "#fff",
//           position: "sticky",
//           top: 0,
//           zIndex: 10,
//         }}
//       >
//         <Box sx={{ fontSize: "18px", fontWeight: 600 }}>Generate Test Cases</Box>
//         <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
//           <IconButton onClick={() => {/* export logic here */}}>
//             <FileDownloadIcon />
//           </IconButton>
//           <IconButton onClick={onClose}>
//             <CloseIcon />
//           </IconButton>
//         </Box>
//       </Box>

//       {/* Table */}
//       <Box sx={{ p: 2 }}>
//         <TableContainer component={Paper}>
//           <Table sx={{ minWidth: 650 }} size="small">
//             <TableHead>
//               <TableRow>
//                 {Object.keys(testCaseData[0]).map((key) => (
//                   <TableCell key={key} sx={{ fontWeight: 600 }}>
//                     {key}
//                   </TableCell>
//                 ))}
//               </TableRow>
//             </TableHead>
//             <TableBody>
//               {testCaseData.map((row, index) => (
//                 <TableRow key={index}>
//                   {Object.values(row).map((value, i) => (
//                     <TableCell key={i}>{value}</TableCell>
//                   ))}
//                 </TableRow>
//               ))}
//             </TableBody>
//           </Table>
//         </TableContainer>
//       </Box>
//     </Drawer>
//   );
// };

// export default GenerateDrawer;



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
        console.log("Documensst ID received:", documentId);

 useEffect(() => {
  if (!taskId) return;

  setLoading(true);
  setError(false);
  setDocumentId(null);
  setParsedData([]);
  setHeaders([]);

  const socketUrl = `wss://gen-backend.synchroni.xyz/ws/task_status?task_id=${taskId}`;
  socketRef.current = new WebSocket(socketUrl);

  socketRef.current.onopen = () => {
    console.log("✅ WebSocket connected");
    setError(false);
  };

  socketRef.current.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("📨 WebSocket message received:", data);

    if (data.status === "SUCCESS" && data.result?.results) {
      const allRows = data.result.results.map((item) => {
        const lines = item.test_cases.split("\n").filter((line) => line.includes(":"));
        const row = {};
        lines.forEach((line) => {
          const [key, ...rest] = line.split(":");
          row[key.trim()] = rest.join(":").trim();
        });
        return row;
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
    const response = await axios.get(`https://gen-backend.synchroni.xyz/download-csv/${documentId}`, {
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
