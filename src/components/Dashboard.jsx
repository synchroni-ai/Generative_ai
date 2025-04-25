// import React, { useState } from "react";
// import { Button, Box, Typography, Container, Table, TableHead, TableBody, TableRow, TableCell, TableContainer, Paper } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import Header from "./Header"; // Import the Header component
// import UploadModal from "./UploadModal"; // Import the UploadModal component

// const Dashboard = () => {
//   const navigate = useNavigate();

//   const [modalOpen, setModalOpen] = useState(false); // State to control modal visibility

//   const handleUploadClick = () => {
//     setModalOpen(true); // Open the modal when the button is clicked
//   };

//   const handleModalClose = () => {
//     setModalOpen(false); // Close the modal
//   };

//   const handleLogout = () => {
//     // Perform any additional logout logic here if needed
//     console.log("Logging out...");
//     localStorage.removeItem("isLoggedIn"); // Clear login status if needed
//     navigate("/"); // Navigate to the login page
//   };

//   // Example document data
//   const documentData = [
//     { id: 1, name: "Document1.pdf", type: "PDF", size: "1.2MB", status: "Uploaded" },
//     { id: 2, name: "Document2.docx", type: "DOCX", size: "3.4MB", status: "Pending" },
//     { id: 3, name: "Document3.pdf", type: "PDF", size: "2.5MB", status: "Failed" },
//   ];

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
//       {/* Header component - visible only on the Dashboard */}
//       <Header onLogout={handleLogout} />

//       {/* Main content */}
//       <Box sx={{ mt: 12, px: 2 }}>
//         {/* Upload Button at the top-right corner */}
//         <Box
//           sx={{
//             position: "absolute",
//             top: 100,
//             right: 20,
//           }}
//         >
//           <Button
//             variant="contained"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//               color:"white",
//               backgroundColor:"#000080"
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         <Container maxWidth="lg" sx={{ mt: 15 }}>
//           {/* Table displaying document data */}
//           <TableContainer component={Paper} sx={{ width: "100%" }}>
//             <Table sx={{ width: "100%" }} aria-label="documents table">
//               <TableHead>
//                 <TableRow>
//                   <TableCell sx={{ fontWeight: 'bold' }}>Document ID</TableCell>
//                   <TableCell sx={{ fontWeight: 'bold' }}>File Name</TableCell>
//                   <TableCell sx={{ fontWeight: 'bold' }}>File Type</TableCell>
//                   <TableCell sx={{ fontWeight: 'bold' }}>Size</TableCell>
//                   <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
//                 </TableRow>
//               </TableHead>
//               <TableBody>
//                 {documentData.map((doc) => (
//                   <TableRow key={doc.id}>
//                     <TableCell>{doc.id}</TableCell>
//                     <TableCell>{doc.name}</TableCell>
//                     <TableCell>{doc.type}</TableCell>
//                     <TableCell>{doc.size}</TableCell>
//                     <TableCell>{doc.status}</TableCell>
//                   </TableRow>
//                 ))}
//               </TableBody>
//             </Table>
//           </TableContainer>
//         </Container>
//       </Box>

//       {/* UploadModal component */}
//       <UploadModal open={modalOpen} onClose={handleModalClose} />
//     </Box>
//   );
// };

// export default Dashboard;



// import React, { useState } from "react";
// import {
//   Button,
//   Box,
//   Typography,
//   Container,
//   Table,
//   TableHead,
//   TableBody,
//   TableRow,
//   TableCell,
//   TableContainer,
//   Paper,
//   Drawer, IconButton
// } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import CloseIcon from '@mui/icons-material/Close';
// import Header from "./Header"; // Import the Header component
// import UploadModal from "./UploadModal"; // Import the UploadModal component

// const Dashboard = () => {
//   const navigate = useNavigate();
//   const [modalOpen, setModalOpen] = useState(false); // State to control modal visibility
//   const [drawerOpen, setDrawerOpen] = useState(false);
//   const [testCaseData, setTestCaseData] = useState(""); // or use object if needed
  
//   const toggleDrawer = (open) => () => {
//     setDrawerOpen(open);
//   };
  
//   const handleUploadClick = () => {
//     setModalOpen(true); // Open the modal when the button is clicked
//   };

//   const handleModalClose = () => {
//     setModalOpen(false); // Close the modal
//   };

//   const handleLogout = () => {
//     console.log("Logging out...");
//     localStorage.removeItem("isLoggedIn");
//     navigate("/"); // Navigate to the login page
//   };

//   const parseFormattedText = (text) => {
//     const lines = text.split("\n");
//     const elements = [];
 
//     let listItems = [];
 
//     const flushList = () => {
//       if (listItems.length > 0) {
//         elements.push(
//           <ul key={`list-${elements.length}`} style={{ paddingLeft: '1.5rem', marginTop: 4 }}>
//             {listItems.map((item, idx) => (
//               <li key={idx}>{renderBoldText(item)}</li>
//             ))}
//           </ul>
//         );
//         listItems = [];
//       }
//     };
 
//     const renderBoldText = (line) => {
//       return line.split(/(\*\*.*?\*\*)/g).map((part, index) => {
//         if (part.startsWith("**") && part.endsWith("**")) {
//           return <strong key={index}>{part.slice(2, -2)}</strong>;
//         }
//         return <React.Fragment key={index}>{part}</React.Fragment>;
//       });
//     };
 
//     lines.forEach((line, index) => {
//       const trimmed = line.trim();
//       if (trimmed.startsWith("* ")) {
//         listItems.push(trimmed.slice(2));
//       } else {
//         flushList();
//         if (trimmed !== "") {
//           elements.push(
//             <p key={index} style={{ marginBottom: "0.6rem" }}>
//               {renderBoldText(trimmed)}
//             </p>
//           );
//         }
//       }
//     });
 
//     flushList(); // Flush any remaining list items at the end
 
//     return elements;
//   };
  

//   // Updated document data
//   const documentData = [
//     {
//       doc_name: "Document1.pdf",
//       doc_path: "/documents/Document1.pdf",
//       llm_response_testcases: "Pass",
//       llm_response_latency: "120ms",
//     },
//     {
//       doc_name: "Document2.docx",
//       doc_path: "/documents/Document2.docx",
//       llm_response_testcases: "Fail",
//       llm_response_latency: "200ms",
//     },
//     {
//       doc_name: "Document3.pdf",
//       doc_path: "/documents/Document3.pdf",
//       llm_response_testcases: "Pass",
//       llm_response_latency: "180ms",
//     },
//   ];

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
//       <Header onLogout={handleLogout} />

//       <Box sx={{ mt: 12, px: 2 }}>
//         <Box
//           sx={{
//             position: "absolute",
//             top: 100,
//             right: 20,
//           }}
//         >
//           <Button
//             variant="contained"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//               color: "white",
//               backgroundColor: "#000080",
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         <Container maxWidth="lg" sx={{ mt: 15 }}>
//           <TableContainer component={Paper} sx={{ width: "100%" }}>
//             <Table sx={{ width: "100%" }} aria-label="documents table">
//               <TableHead>
//                 <TableRow>
//                   <TableCell sx={{ fontWeight: "bold" }}>Serial No</TableCell>
//                   <TableCell sx={{ fontWeight: "bold" }}>doc_name</TableCell>
//                   <TableCell sx={{ fontWeight: "bold" }}>doc_path</TableCell>
//                   <TableCell sx={{ fontWeight: "bold" }}>
//                     llm_response_latency
//                   </TableCell>
//                 </TableRow>
//               </TableHead>
//               <TableBody>
//                 {documentData.map((doc, index) => (
//                   <TableRow key={index}>
//                     <TableCell>{index + 1}</TableCell>
//                     <TableCell
//   sx={{ cursor: "pointer", color: "#1976d2", textDecoration: "underline" }}
//   onClick={() => {
//     setTestCaseData(doc.llm_response_testcases); // or doc if you want all data
//     setDrawerOpen(true);
//   }}
// >
//   {doc.doc_name}
// </TableCell>         
//            <TableCell>{doc.doc_path}</TableCell>
//                     <TableCell>{doc.llm_response_latency}</TableCell>
//                   </TableRow>
//                 ))}
//               </TableBody>
//             </Table>
//           </TableContainer>
//         </Container>
//       </Box>
//       <Drawer
//   anchor="right"
//   open={drawerOpen}
//   onClose={toggleDrawer(false)}
//   transitionDuration={{ enter: 1000, exit: 1000 }}
//   PaperProps={{
//     sx: {
//       width: "70%",
//       padding: 5,
//       height: "96%",
//       transition: "transform 2s ease-in-out",
//       transform: "translate(50%, 0%)",
//       borderRadius: '10px 0 0 10px',
//     },
//   }}
// >
//   <Box
//     sx={{
//       display: "flex",
//       justifyContent: "space-between",
//       alignItems: "center",
//       position: "sticky",
//       top: 30,
//       backgroundColor: "#fff",
//       zIndex: 1000,
//       paddingBottom: 2,
//     }}
//   >
//     <Typography variant="h6" fontWeight="bold">
//       Test Case Details
//     </Typography>
//     <IconButton onClick={toggleDrawer(false)}>
//       <CloseIcon />
//     </IconButton>
//   </Box>

//   <Box sx={{ overflowY: "auto", mt: 3 }}>
//     {parseFormattedText(testCaseData)}
//   </Box>
// </Drawer>
//       <UploadModal open={modalOpen} onClose={handleModalClose} />
//     </Box>
//   );
// };

// export default Dashboard;



// import React, { useState } from "react";
// import {
//   Button,
//   Box,
//   Typography,
//   Container,
//   Table,
//   TableHead,
//   TableBody,
//   TableRow,
//   TableCell,
//   TableContainer,
//   Paper,
//   Drawer, IconButton
// } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import CloseIcon from '@mui/icons-material/Close';
// import Header from "./Header"; // Import the Header component
// import UploadModal from "./UploadModal"; // Import the UploadModal component

// const Dashboard = () => {
//   const navigate = useNavigate();
//   const [modalOpen, setModalOpen] = useState(false); // State to control modal visibility
//   const [drawerOpen, setDrawerOpen] = useState(false);
//   const [testCaseData, setTestCaseData] = useState(""); // or use object if needed
  
//   const toggleDrawer = (open) => () => {
//     setDrawerOpen(open);
//   };
  
//   const handleUploadClick = () => {
//     setModalOpen(true); // Open the modal when the button is clicked
//   };

//   const handleModalClose = () => {
//     setModalOpen(false); // Close the modal
//   };

//   const handleLogout = () => {
//     console.log("Logging out...");
//     localStorage.removeItem("isLoggedIn");
//     navigate("/"); // Navigate to the login page
//   };

//   const parseFormattedText = (text) => {
//     const lines = text.split("\n");
//     const elements = [];
 
//     let listItems = [];
 
//     const flushList = () => {
//       if (listItems.length > 0) {
//         elements.push(
//           <ul key={`list-${elements.length}`} style={{ paddingLeft: '1.5rem', marginTop: 4 }}>
//             {listItems.map((item, idx) => (
//               <li key={idx}>{renderBoldText(item)}</li>
//             ))}
//           </ul>
//         );
//         listItems = [];
//       }
//     };
 
//     const renderBoldText = (line) => {
//       return line.split(/(\*\*.*?\*\*)/g).map((part, index) => {
//         if (part.startsWith("**") && part.endsWith("**")) {
//           return <strong key={index}>{part.slice(2, -2)}</strong>;
//         }
//         return <React.Fragment key={index}>{part}</React.Fragment>;
//       });
//     };
 
//     lines.forEach((line, index) => {
//       const trimmed = line.trim();
//       if (trimmed.startsWith("* ")) {
//         listItems.push(trimmed.slice(2));
//       } else {
//         flushList();
//         if (trimmed !== "") {
//           elements.push(
//             <p key={index} style={{ marginBottom: "0.6rem" }}>
//               {renderBoldText(trimmed)}
//             </p>
//           );
//         }
//       }
//     });
 
//     flushList(); // Flush any remaining list items at the end
 
//     return elements;
//   };
  

//   // Updated document data
//   const documentData = [
//     {
//       doc_name: "Document1.pdf",
//       doc_path: "/documents/Document1.pdf",
//       llm_response_testcases: "Pass",
//       llm_response_latency: "120ms",
//     },
//     {
//       doc_name: "Document2.docx",
//       doc_path: "/documents/Document2.docx",
//       llm_response_testcases: "Fail",
//       llm_response_latency: "200ms",
//     },
//     {
//       doc_name: "Document3.pdf",
//       doc_path: "/documents/Document3.pdf",
//       llm_response_testcases: "Pass",
//       llm_response_latency: "180ms",
//     },
//   ];

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
//       <Header onLogout={handleLogout} />

//       <Box sx={{ mt: 12, px: 2 }}>
//         <Box
//           sx={{
//             position: "absolute",
//             top: 100,
//             right: 20,
//           }}
//         >
//           <Button
//             variant="contained"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//               color: "white",
//               backgroundColor: "#000080",
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         <Container maxWidth="lg" sx={{ mt: 15 }}>
//           <TableContainer component={Paper} sx={{ width: "100%" }}>
//             <Table sx={{ width: "100%" }} aria-label="documents table">
//               <TableHead>
//                 <TableRow>
//                   <TableCell sx={{ fontWeight: "bold" }}>Serial No</TableCell>
//                   <TableCell sx={{ fontWeight: "bold" }}>doc_name</TableCell>
//                   <TableCell sx={{ fontWeight: "bold" }}>doc_path</TableCell>
//                   <TableCell sx={{ fontWeight: "bold" }}>
//                     llm_response_latency
//                   </TableCell>
//                 </TableRow>
//               </TableHead>
//               <TableBody>
//                 {documentData.map((doc, index) => (
//                   <TableRow key={index}>
//                     <TableCell>{index + 1}</TableCell>
//                     <TableCell
//   sx={{ cursor: "pointer", color: "#1976d2", textDecoration: "underline" }}
//   onClick={() => {
//     setTestCaseData(doc.llm_response_testcases); // or doc if you want all data
//     setDrawerOpen(true);
//   }}
// >
//   {doc.doc_name}
// </TableCell>         
//            <TableCell>{doc.doc_path}</TableCell>
//                     <TableCell>{doc.llm_response_latency}</TableCell>
//                   </TableRow>
//                 ))}
//               </TableBody>
//             </Table>
//           </TableContainer>
//         </Container>
//       </Box>
//       <Drawer
//   anchor="right"
//   open={drawerOpen}
//   onClose={toggleDrawer(false)}
//   transitionDuration={{ enter: 1000, exit: 1000 }}
//   PaperProps={{
//     sx: {
//       width: "70%",
//       padding: 5,
//       height: "96%",
//       transition: "transform 2s ease-in-out",
//       transform: "translate(50%, 0%)",
//       borderRadius: '10px 0 0 10px',
//     },
//   }}
// >
//   <Box
//     sx={{
//       display: "flex",
//       justifyContent: "space-between",
//       alignItems: "center",
//       position: "sticky",
//       top: 30,
//       backgroundColor: "#fff",
//       zIndex: 1000,
//       paddingBottom: 2,
//     }}
//   >
//     <Typography variant="h6" fontWeight="bold">
//       Test Case Details
//     </Typography>
//     <IconButton onClick={toggleDrawer(false)}>
//       <CloseIcon />
//     </IconButton>
//   </Box>

//   <Box sx={{ overflowY: "auto", mt: 3 }}>
//     {parseFormattedText(testCaseData)}
//   </Box>
// </Drawer>
//       <UploadModal open={modalOpen} onClose={handleModalClose} />
//     </Box>
//   );
// };

// export default Dashboard;



import React, { useState, useEffect } from "react";
import {
  Button,
  Box,
  Typography,
  Container,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  Paper,
  Drawer,
  IconButton,
  CircularProgress
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import CloseIcon from "@mui/icons-material/Close";
import axios from "axios";
import Header from "./Header";
import UploadModal from "./UploadModal";

const Dashboard = () => {
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [testCaseData, setTestCaseData] = useState("");
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const toggleDrawer = (open) => () => setDrawerOpen(open);
  const handleUploadClick = () => setModalOpen(true);
  const handleModalClose = () => setModalOpen(false);
  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/");
  };

  const parseFormattedText = (text) => {
    const lines = text.split("\n");
    const elements = [];
    let listItems = [];
    const flushList = () => {
      if (listItems.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} style={{ paddingLeft: "1.5rem", marginTop: 4 }}>
            {listItems.map((item, idx) => (
              <li key={idx}>{renderBoldText(item)}</li>
            ))}
          </ul>
        );
        listItems = [];
      }
    };
    const renderBoldText = (line) =>
      line.split(/(\*\*.*?\*\*)/g).map((part, index) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={index}>{part.slice(2, -2)}</strong>
        ) : (
          <React.Fragment key={index}>{part}</React.Fragment>
        )
      );

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      if (trimmed.startsWith("* ")) {
        listItems.push(trimmed.slice(2));
      } else {
        flushList();
        if (trimmed !== "") {
          elements.push(
            <p key={index} style={{ marginBottom: "0.6rem" }}>
              {renderBoldText(trimmed)}
            </p>
          );
        }
      }
    });
    flushList();
    return elements;
  };

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await axios.get("http://98.81.68.180:8000/documents/");
        setDocuments(response.data); // Assuming response.data is an array
        console.log("Fetched data:", response.data);
      } catch (error) {
        console.error("Error fetching documents:", error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchDocuments();
  }, []);
  
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Header onLogout={handleLogout} />
      <Box sx={{ mt: 12, px: 2 }}>
        <Box sx={{ position: "absolute", top: 100, right: 20 }}>
          <Button
            variant="contained"
            onClick={handleUploadClick}
            sx={{ textTransform: "none", fontWeight: "bold", color: "white", backgroundColor: "#000080" }}
          >
            Upload Document
          </Button>
        </Box>

        <Container maxWidth="lg" sx={{ mt: 15 }}>
          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 10 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{ width: "100%" }}>
              <Table aria-label="documents table">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: "bold" }}>Serial No</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>doc_name</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>doc_path</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>llm_response_latency</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {documents.map((doc, index) => (
                    <TableRow key={doc._id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell
                        sx={{ cursor: "pointer", color: "#1976d2", textDecoration: "underline" }}
                        onClick={() => {
                          setTestCaseData(doc.llm_response_testcases);
                          setDrawerOpen(true);
                        }}
                      >
                        {doc.doc_name}
                      </TableCell>
                      <TableCell>{doc.doc_path}</TableCell>
                      <TableCell>{doc.llm_response_latency}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Container>
      </Box>

      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        transitionDuration={{ enter: 1000, exit: 1000 }}
        PaperProps={{
          sx: {
            width: "70%",
            padding: 5,
            height: "96%",
            transition: "transform 2s ease-in-out",
            transform: "translate(50%, 0%)",
            borderRadius: "10px 0 0 10px",
          },
        }}
      >
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 22, backgroundColor: "#fff", zIndex: 1000, paddingBottom: 2,paddingTop:2 }}>
          <Typography variant="h6" sx={{fontWeight:700}}>Test Case Details</Typography>
          <IconButton onClick={toggleDrawer(false)}><CloseIcon /></IconButton>
        </Box>
        <Box sx={{ mt: 3,ml:3 }}>{parseFormattedText(testCaseData)}</Box>
      </Drawer>

      <UploadModal open={modalOpen} onClose={handleModalClose} />
    </Box>
  );
};

export default Dashboard;



// import React, { useState } from "react";
// import { Button, Box, Typography,  Drawer, IconButton, Paper } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import CloseIcon from '@mui/icons-material/Close';
// import Header from "./Header"; // Import the Header component
// import UploadModal from "./UploadModal"; // Import the UploadModal component

// const Dashboard = () => {
//   const navigate = useNavigate();

//   const [modalOpen, setModalOpen] = useState(false); // State to control modal visibility

//   const handleUploadClick = () => {
//     setModalOpen(true); // Open the modal when the button is clicked
//   };

//   const handleModalClose = () => {
//     setModalOpen(false); // Close the modal
//   };

//   const handleLogout = () => {
//     // Perform any additional logout logic here if needed
//     console.log("Logging out...");
//     localStorage.removeItem("isLoggedIn"); // Clear login status if needed
//     navigate("/"); // Navigate to the login page
//   };

//   const [drawerOpen, setDrawerOpen] = useState(false);

// const toggleDrawer = (open) => () => {
//   setDrawerOpen(open);
// };

// const testCaseData = "Based on the BRD, I've identified the key functionalities and requirements."
//   const parseFormattedText = (text) => {
//     const lines = text.split("\n");
//     const elements = [];
  
//     let listItems = [];
  
//     const flushList = () => {
//       if (listItems.length > 0) {
//         elements.push(
//           <ul key={`list-${elements.length}`} style={{ paddingLeft: '1.5rem', marginTop: 4 }}>
//             {listItems.map((item, idx) => (
//               <li key={idx}>{renderBoldText(item)}</li>
//             ))}
//           </ul>
//         );
//         listItems = [];
//       }
//     };
  
//     const renderBoldText = (line) => {
//       return line.split(/(\*\*.*?\*\*)/g).map((part, index) => {
//         if (part.startsWith("**") && part.endsWith("**")) {
//           return <strong key={index}>{part.slice(2, -2)}</strong>;
//         }
//         return <React.Fragment key={index}>{part}</React.Fragment>;
//       });
//     };
  
//     lines.forEach((line, index) => {
//       const trimmed = line.trim();
//       if (trimmed.startsWith("* ")) {
//         listItems.push(trimmed.slice(2));
//       } else {
//         flushList();
//         if (trimmed !== "") {
//           elements.push(
//             <p key={index} style={{ marginBottom: "0.6rem" }}>
//               {renderBoldText(trimmed)}
//             </p>
//           );
//         }
//       }
//     });
  
//     flushList(); // Flush any remaining list items at the end
  
//     return elements;
//   };
  

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
//       {/* Header component - visible only on the Dashboard */}
//       <Header onLogout={handleLogout} />

//       {/* Main content */}
//       <Box sx={{ mt: 12, px: 2 }}>
//         {/* Upload Button at the top-right corner */}
//         <Box
//           sx={{
//             position: "absolute",
//             top: 100,
//             right: 20,
//           }}
//         >
//           <Button
//             variant="contained"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//               color:"white",
//               backgroundColor:"#000080"
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>
//         {/* Centered Fullscreen Container for the Button */}
// <Box
//   sx={{
//     flex: 1,
//     display: "flex",
//     alignItems: "center",
//     justifyContent: "center",
//     minHeight: "calc(90vh - 64px)", // Adjust for header height if needed
//   }}
// >
//   <Button
//     variant="outlined"
//     onClick={toggleDrawer(true)}
//     sx={{
//       textTransform: "none",
//       fontWeight: "bold",
//       color: "#000080",
//       borderColor: "#000080",
//       padding: "12px 24px",
//       fontSize: "1rem",
//     }}
//   >
//     View Test Cases
//   </Button>
// </Box>

//       </Box>
      
//       <Drawer
//   anchor="right"
//   open={drawerOpen}
//   onClose={toggleDrawer(false)}
//   transitionDuration={{ enter: 1500, exit: 800 }} // Optional: controls speed of built-in transition (ms)
//   PaperProps={{
//     sx: {
//       width: "70%",
//       padding: 5,
//       height: "96%",
//       transition: "transform 2s ease-in-out", // Custom transition style
//       transform: drawerOpen ? "translateX(0)" : "translateX(100%)", // Handle the transition for opening/closing
//     },
//   }}
// >
//   {/* Top Bar with Title and Close Icon */}
//   <Box
//     sx={{
//       display: "flex",
//       justifyContent: "space-between",
//       alignItems: "center",
//       position: "sticky",
//       top: 30,
//       backgroundColor: "#fff",
//       zIndex: 1000,
//       paddingBottom: 2,
//     }}
//   >
//     <Typography variant="h6" fontWeight="bold">
//       Test Case Details
//     </Typography>
//     <IconButton onClick={toggleDrawer(false)}>
//       <CloseIcon />
//     </IconButton>
//   </Box>

//   {/* Content */}
//   <Box sx={{ overflowY: "auto", mt: 3 }}>
//     {parseFormattedText(testCaseData)}
//   </Box>
// </Drawer>


//       {/* UploadModal component */}
//       <UploadModal open={modalOpen} onClose={handleModalClose} />
//     </Box>
//   );
// };

// export default Dashboard;



// import React, { useState } from "react";
// import { Button, Box, Typography, Drawer, IconButton, Paper } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import CloseIcon from '@mui/icons-material/Close';
// import CheckCircleIcon from '@mui/icons-material/CheckCircle'; // Import success icon
// import Header from "./Header"; // Import the Header component
// import UploadModal from "./UploadModal"; // Import the UploadModal component

// const Dashboard = () => {
//   const navigate = useNavigate();

//   const [modalOpen, setModalOpen] = useState(false); // State to control modal visibility
//   const [drawerOpen, setDrawerOpen] = useState(false); // State to control drawer visibility
//   const [uploadSuccess, setUploadSuccess] = useState(false);

//   const handleUploadClick = () => {
//     setModalOpen(true); // Open the modal when the button is clicked
//   };

//   const handleModalClose = (success = false) => {
//     setModalOpen(false);
//     if (success) {
//       setUploadSuccess(true);
//     }
//   };


//   const handleLogout = () => {
//     // Perform any additional logout logic here if needed
//     console.log("Logging out...");
//     localStorage.removeItem("isLoggedIn"); // Clear login status if needed
//     navigate("/"); // Navigate to the login page
//   };

//   const toggleDrawer = (open) => () => {
//     setDrawerOpen(open);
//   };

//   const testCaseData = "Based on the BRD, I've identified the key functionalities and requirements. Here are two test cases for each functionality:\n\n**Functionality: Store Owner/Admin**\n\n**Test Case 1:**\n\n*   **Test Case ID:** TC_STO_001\n*";


//   const parseFormattedText = (text) => {
//     const lines = text.split("\n");
//     const elements = [];

//     let listItems = [];

//     const flushList = () => {
//       if (listItems.length > 0) {
//         elements.push(
//           <ul key={`list-${elements.length}`} style={{ paddingLeft: '1.5rem', marginTop: 4 }}>
//             {listItems.map((item, idx) => (
//               <li key={idx}>{renderBoldText(item)}</li>
//             ))}
//           </ul>
//         );
//         listItems = [];
//       }
//     };

//     const renderBoldText = (line) => {
//       return line.split(/(\*\*.*?\*\*)/g).map((part, index) => {
//         if (part.startsWith("**") && part.endsWith("**")) {
//           return <strong key={index}>{part.slice(2, -2)}</strong>;
//         }
//         return <React.Fragment key={index}>{part}</React.Fragment>;
//       });
//     };

//     lines.forEach((line, index) => {
//       const trimmed = line.trim();
//       if (trimmed.startsWith("* ")) {
//         listItems.push(trimmed.slice(2));
//       } else {
//         flushList();
//         if (trimmed !== "") {
//           elements.push(
//             <p key={index} style={{ marginBottom: "0.6rem" }}>
//               {renderBoldText(trimmed)}
//             </p>
//           );
//         }
//       }
//     });

//     flushList(); // Flush any remaining list items at the end

//     return elements;
//   };

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
//       {/* Header component - visible only on the Dashboard */}
//       <Header onLogout={handleLogout} />

//       {/* Main content */}
//       <Box sx={{ mt: 12, px: 2 }}>
//         {/* Upload Button at the top-right corner */}
//         <Box sx={{ position: "absolute", top: 100, right: 20 }}>
//           <Button
//             variant="contained"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//               color: "white",
//               backgroundColor: "#000080"
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         {/* Centered Fullscreen Container for the Button */}
// <Box
//   sx={{
//     flex: 1,
//     display: "flex",
//     alignItems: "center",
//     justifyContent: "center",
//     minHeight: "calc(90vh - 64px)", // Adjust for header height
//   }}
// >
//   {uploadSuccess ? (
//     <Paper
//       elevation={4}
//       sx={{
//         padding: 4,
//         borderRadius: 4,
//         display: "flex",
//         flexDirection: "column",
//         alignItems: "center",
//         textAlign: "center",
//       }}
//     >
//       <Typography variant="h5" fontWeight="bold" color="green" gutterBottom>
//         Document Uploaded Successful!
//       </Typography>
//       <Typography variant="body1" mb={3}>
//         You can check the uploaded Document.
//       </Typography>
//       <Box
//         sx={{
//           width: 100,
//           height: 100,
//           borderRadius: "50%",
//           backgroundColor: "rgba(0, 128, 0, 0.1)",
//           display: "flex",
//           alignItems: "center",
//           justifyContent: "center",
//           mb: 6,
//         }}
//       >
//         <CheckCircleIcon sx={{ fontSize: 60, color: "green" }} />
//       </Box>
//       <Button
//         variant="outlined"
//         onClick={toggleDrawer(true)}
//         sx={{
//           textTransform: "none",
//           fontWeight: "bold",
//           backgroundColor: "#000080",
//           borderColor: "#000080",
//           padding: "6px 16px",
//           fontSize: "14px",
//           color: "white"
//         }}
//       >
//         View Document
//       </Button>
//     </Paper>
//   ) : (
//     <Typography variant="h6" fontWeight="medium" color="gray">
//       No Document is available.
//     </Typography>
//   )}
// </Box>
//       </Box>

//       {/* Drawer with Test Case Details */}
//       <Drawer
//         anchor="right"
//         open={drawerOpen}
//         onClose={toggleDrawer(false)}
//         transitionDuration={{ enter: 1000, exit: 1000 }} // Optional: controls speed of built-in transition (ms)
//         PaperProps={{
//           sx: {
//             width: "70%",
//             padding: 5,
//             height: "96%",
//             transition: "transform 2s ease-in-out", // Custom transition style
//             // transform: drawerOpen ? "translateX(0)" : "translateX(100%)", // Handle the transition for opening/closing
//             transform: "translate(50%, 0%)",
//             borderRadius: '10px 0 0 10px',
//           },
//         }}
//       >
//         {/* Top Bar with Title and Close Icon */}
//         <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 30, backgroundColor: "#fff", zIndex: 1000, paddingBottom: 2 }}>
//           <Typography variant="h6" fontWeight="bold">
//             Test Case Details
//           </Typography>
//           <IconButton onClick={toggleDrawer(false)}>
//             <CloseIcon />
//           </IconButton>
//         </Box>

//         {/* Content */}
//         <Box sx={{ overflowY: "auto", mt: 3 }}>
//           {parseFormattedText(testCaseData)}
//         </Box>
//       </Drawer>

//       {/* UploadModal component */}
//       <UploadModal open={modalOpen} onClose={handleModalClose} />
//     </Box>
//   );
// };

// export default Dashboard;



// import React, { useState } from "react";
// import {
//   Button,
//   Box,
//   Container,
//   Paper,
//   Table,
//   TableHead,
//   TableBody,
//   TableRow,
//   TableCell,
//   TableContainer,
// } from "@mui/material";
// import { useNavigate } from "react-router-dom";
// import Header from "./Header";
// import UploadModal from "./UploadModal";

// const Dashboard = () => {
//   const navigate = useNavigate();
//   const [modalOpen, setModalOpen] = useState(false);
//   const [csvData, setCsvData] = useState([]);

//   const handleUploadClick = () => {
//     setModalOpen(true);
//   };

//   const handleModalClose = () => {
//     setModalOpen(false);
//   };

//   const handleUploadComplete = (data) => {
//     setCsvData(data); // Set extracted CSV data
//     setModalOpen(false);
//   };

//   const handleLogout = () => {
//     localStorage.removeItem("isLoggedIn");
//     navigate("/");
//   };

//   return (
//     <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
//       <Header onLogout={handleLogout} />

//       <Box sx={{ mt: 12, px: 2 }}>
//         <Box sx={{ position: "absolute", top: 100, right: 20 }}>
//           <Button
//             variant="contained"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//               color: "white",
//               backgroundColor: "#000080",
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         <Container maxWidth="lg" sx={{ mt: 15 }}>
//           <TableContainer component={Paper}>
//             <Table aria-label="extracted content table">
//             <TableHead>
//   <TableRow>
//     {csvData.length > 0 &&
//       Object.keys(csvData[0]).map((key) => (
//         <TableCell key={key}>{key}</TableCell>
//       ))}
//   </TableRow>
// </TableHead>
// <TableBody>
//   {csvData.map((row, index) => (
//     <TableRow key={index}>
//       {Object.keys(row).map((key) => (
//         <TableCell key={key}>{row[key]}</TableCell>
//       ))}
//     </TableRow>
//   ))}
// </TableBody>

//               <TableBody>
//                 {csvData.map((row) => (
//                   <TableRow key={row.id}>
//                     <TableCell>{row.id}</TableCell>
//                     <TableCell>{row.content}</TableCell>
//                   </TableRow>
//                 ))}
//               </TableBody>
//             </Table>
//           </TableContainer>
//         </Container>
//       </Box>

//       <UploadModal open={modalOpen} onClose={handleModalClose} onUploadComplete={handleUploadComplete} />
//     </Box>
//   );
// };

// export default Dashboard;
