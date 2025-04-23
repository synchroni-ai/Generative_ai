// import React, { useState } from "react";
// import { Button, Box, Typography, Container } from "@mui/material";
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
//             color="primary"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         <Container maxWidth="lg" sx={{ mt: 8 }}>
//           <Typography variant="body1" color="textSecondary">
//             Welcome to your dashboard. You can upload documents, view reports, and manage your content.
//           </Typography>
//         </Container>
//       </Box>

//       {/* UploadModal component */}
//       <UploadModal open={modalOpen} onClose={handleModalClose} />
//     </Box>
//   );
// };

// export default Dashboard;



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
//             color="primary"
//             onClick={handleUploadClick}
//             sx={{
//               textTransform: "none",
//               fontWeight: "bold",
//             }}
//           >
//             Upload Document
//           </Button>
//         </Box>

//         <Container maxWidth="lg" sx={{ mt: 15 }}>

//           {/* Table displaying document data */}
//           <TableContainer  component={Paper}>
//             <Table  aria-label="documents table">
//               <TableHead>
//                 <TableRow>
//                   <TableCell>Document ID</TableCell>
//                   <TableCell>File Name</TableCell>
//                   <TableCell>File Type</TableCell>
//                   <TableCell>Size</TableCell>
//                   <TableCell>Status</TableCell>
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


import React, { useState } from "react";
import { Button, Box, Typography, Container, Table, TableHead, TableBody, TableRow, TableCell, TableContainer, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Header from "./Header"; // Import the Header component
import UploadModal from "./UploadModal"; // Import the UploadModal component

const Dashboard = () => {
  const navigate = useNavigate();

  const [modalOpen, setModalOpen] = useState(false); // State to control modal visibility

  const handleUploadClick = () => {
    setModalOpen(true); // Open the modal when the button is clicked
  };

  const handleModalClose = () => {
    setModalOpen(false); // Close the modal
  };

  const handleLogout = () => {
    // Perform any additional logout logic here if needed
    console.log("Logging out...");
    localStorage.removeItem("isLoggedIn"); // Clear login status if needed
    navigate("/"); // Navigate to the login page
  };

  // Example document data
  const documentData = [
    { id: 1, name: "Document1.pdf", type: "PDF", size: "1.2MB", status: "Uploaded" },
    { id: 2, name: "Document2.docx", type: "DOCX", size: "3.4MB", status: "Pending" },
    { id: 3, name: "Document3.pdf", type: "PDF", size: "2.5MB", status: "Failed" },
  ];

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header component - visible only on the Dashboard */}
      <Header onLogout={handleLogout} />

      {/* Main content */}
      <Box sx={{ mt: 12, px: 2 }}>
        {/* Upload Button at the top-right corner */}
        <Box
          sx={{
            position: "absolute",
            top: 100,
            right: 20,
          }}
        >
          <Button
            variant="contained"
            color="primary"
            onClick={handleUploadClick}
            sx={{
              textTransform: "none",
              fontWeight: "bold",
            }}
          >
            Upload Document
          </Button>
        </Box>

        <Container maxWidth="lg" sx={{ mt: 15 }}>
          {/* Table displaying document data */}
          <TableContainer component={Paper} sx={{ width: "100%" }}>
            <Table sx={{ width: "100%" }} aria-label="documents table">
              <TableHead>
                <TableRow>
                  <TableCell>Document ID</TableCell>
                  <TableCell>File Name</TableCell>
                  <TableCell>File Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {documentData.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>{doc.id}</TableCell>
                    <TableCell>{doc.name}</TableCell>
                    <TableCell>{doc.type}</TableCell>
                    <TableCell>{doc.size}</TableCell>
                    <TableCell>{doc.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Container>
      </Box>

      {/* UploadModal component */}
      <UploadModal open={modalOpen} onClose={handleModalClose} />
    </Box>
  );
};

export default Dashboard;
