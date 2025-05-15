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
//   // const [testCaseData, setTestCaseData] = useState(""); // or use object if needed
  
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
  
//      const testCaseData = "Based on the BRD, I've identified the key functionalities and requirements. Here are two test cases for each functionality:\n\n**Functionality: Store Owner/Admin**\n\n**Test Case 1:**\n\n*   **Test Case ID:** TC_STO_001\n*   **Description:** Verify that the store owner/admin can create a new product with valid details.\n*   **Steps:**\n    1. Log in as a store owner/admin.\n    2. Click on the \"Add Product\" button.\n    3. Fill in the product details (name, description, price, etc.) with valid values.\n    4. Click the \"Save\" button.\n*   **Expected Result:** The new product is successfully created and displayed in the product list.\n\n**Test Case 2:**\n\n*   **Test Case ID:** TC_STO_002\n*   **Description:** Verify that the store owner/admin cannot create a new product with invalid details.\n*   **Steps:**\n    1. Log in as a store owner/admin.\n    2. Click on the \"Add Product\" button.\n    3. Fill in the product details (name, description, price, etc.) with invalid values (e.g., empty fields, special characters, etc.).\n    4. Click the \"Save\" button.\n*   **Expected Result:** An error message is displayed indicating that the product details are invalid.\n\n**Functionality: Fashion Designers**\n\n**Test Case 1:**\n\n*   **Test Case ID:** TC_FD_001\n*   **Description:** Verify that fashion designers can upload their designs with valid files.\n*   **Steps:**\n    1. Log in as a fashion designer.\n    2. Click on the \"Upload Design\" button.\n    3. Select a valid design file (e.g., PDF, JPEG, etc.).\n    4. Click the \"Upload\" button.\n*   **Expected Result:** The design is successfully uploaded and displayed in the designer's portfolio.\n\n**Test Case 2:**\n\n*   **Test Case ID:** TC_FD_002\n*   **Description:** Verify that fashion designers cannot upload designs with invalid files.\n*   **Steps:**\n    1. Log in as a fashion designer.\n    2. Click on the \"Upload Design\" button.\n    3. Select an invalid design file (e.g., a video file, a text file, etc.).\n    4. Click the \"Upload\" button.\n*   **Expected Result:** An error message is displayed indicating that the file is not a valid design file.\n\n**Functionality: Customers (Fashion Designers)**\n\n**Test Case 1:**\n\n*   **Test Case ID:** TC_FD_C_001\n*   **Description:** Verify that customers (fashion designers) can view and purchase products with valid payment information.\n*   **Steps:**\n    1. Log in as a customer (fashion designer).\n    2. Browse and select a product to purchase.\n    3. Enter valid payment information (e.g., credit card details, etc.).\n    4. Click the \"Purchase\" button.\n*   **Expected Result:** The product is successfully purchased, and the customer receives a confirmation email.\n\n**Test Case 2:**\n\n*   **Test Case ID:** TC_FD_C_002\n*   **Description:** Verify that customers (fashion designers) cannot purchase products with invalid payment information.\n*   **Steps:**\n    1. Log in as a customer (fashion designer).\n    2. Browse and select a product to purchase.\n    3. Enter invalid payment information (e.g., expired credit card, etc.).\n    4. Click the \"Purchase\" button.\n*   **Expected Result:** An error message is displayed indicating that the payment information is invalid.\n\nThese test cases cover a range\nBased on the provided Business Requirements Document (BRD), I've identified the key functionalities and requirements. Here are two test cases for each functionality:\n\n**Test Cases:**\n\n**1. Agile Development Methodology**\n\n**Test Case ID:** TC_AGILE_001\n\n**Description:** Verify that the system implements agile development methodology correctly.\n\n**Steps:**\n\n1. Log in to the system as a developer.\n2. Navigate to the project management dashboard.\n3. Verify that the dashboard displays the agile development methodology framework (e.g., Scrum, Kanban).\n4. Check that the system allows for iterative development, continuous integration, and continuous testing.\n\n**Expected Result:** The system correctly implements agile development methodology, displaying the framework and allowing for iterative development, continuous integration, and continuous testing.\n\n**Test Case ID:** TC_AGILE_002\n\n**Description:** Verify that the system handles changes in market trends and user adoption.\n\n**Steps:**\n\n1. Simulate a change in market trends (e.g., new competitor enters the market).\n2. Log in to the system as a developer.\n3. Navigate to the project management dashboard.\n4. Verify that the system adapts to the change in market trends by adjusting the development methodology and prioritizing features accordingly.\n5. Check that the system provides insights on user adoption and feedback.\n\n**Expected Result:** The system correctly adapts to changes in market trends and user adoption, adjusting the development methodology and prioritizing features accordingly, and providing insights on user adoption and feedback.\n\n**2. Financial Feasibility**\n\n**Test Case ID:** TC_FINANCE_001\n\n**Description:** Verify that the system calculates financial feasibility correctly.\n\n**Steps:**\n\n1. Log in to the system as a financial analyst.\n2. Enter valid financial data (e.g., revenue, expenses, ROI).\n3. Verify that the system calculates financial feasibility (e.g., break-even analysis, return on investment).\n4. Check that the system provides accurate financial projections.\n\n**Expected Result:** The system correctly calculates financial feasibility, providing accurate financial projections and insights.\n\n**Test Case ID:** TC_FINANCE_002\n\n**Description:** Verify that the system handles invalid financial data.\n\n**Steps:**\n\n1. Log in to the system as a financial analyst.\n2. Enter invalid financial data (e.g., negative revenue, invalid expense category).\n3. Verify that the system detects and handles the error, preventing incorrect financial calculations.\n\n**Expected Result:** The system detects and handles invalid financial data, preventing incorrect financial calculations and providing an error message.\n\nPlease note that these are just two examples of test cases, and you may need to generate more test cases to cover all the requirements and edge cases.\nBased on the provided Business Requirements Document (BRD), I have identified the key functionalities and requirements. Here are two test cases for the Alphaura e-commerce website:\n\n**Test Cases:**\n\n**TC_001: Valid User Registration**\n\n* **Description:** Verify that a user can successfully register on the Alphaura e-commerce website with valid input.\n* **Steps:**\n    1. Launch the Alphaura e-commerce website.\n    2. Click on the \"Register\" button.\n    3. Enter valid registration information (e.g., name, email address, password, and confirm password).\n    4. Click on the \"Register\" button.\n* **Expected Result:** The user is successfully registered, and a confirmation message is displayed.\n\n**TC_002: Invalid User Registration (Invalid Email Address)**\n\n* **Description:** Verify that the system handles invalid email addresses during user registration.\n* **Steps:**\n    1. Launch the Alphaura e-commerce website.\n    2. Click on the \"Register\" button.\n    3. Enter invalid registration information (e.g., email address with special characters or without the @ symbol).\n    4. Click on the \"Register\" button.\n* **Expected Result:** An error message is displayed indicating that the email address is invalid, and the registration process is not completed.\n\nAdditional test cases can be generated for other functionalities, such as:\n\n* Valid and invalid login credentials\n* Product search and filtering\n* Product details and reviews\n* Cart and checkout processes\n* Payment and order management\n* User profile and account management\n* Search and filtering of products by category, price, and brand\n\nPlease let me know if you would like me to generate more test cases or if you have any specific requirements.\nHere are the test cases for the Similar Site Comparison web app:\n\n**Test Cases:**\n\n**TC_001: User Experience and Interface Design - Stockroom.lk**\n\n* **Description:** Verify that the Stockroom.lk website has a sleek and minimalist interface with intuitive navigation and a visually appealing layout.\n* **Steps:**\n\t1. Open the Stockroom.lk website in a web browser.\n\t2. Observe the website's layout, navigation, and visual design.\n\t3. Click on different sections of the website (e.g., product categories, search bar) to verify that the navigation is intuitive.\n\t4. Check that the website's design prioritizes simplicity and elegance.\n* **Expected Result:** The website should have a clean and minimalist design with easy-to-use navigation and a visually appealing layout.\n\n**TC_002: Functionality and Feature Integration - Adidas.com/lk**\n\n* **Description:** Verify that Adidas.com/lk offers advanced product customization tools, size guides, and interactive product showcases.\n* **Steps:**\n\t1. Open the Adidas.com/lk website in a web browser.\n\t2. Search for a specific product and click on it to view its details.\n\t3. Verify that the product is displayed with interactive features (e.g., 360-degree views, zoom functionality).\n\t4. Check that the website provides size guides and product customization options.\n\t5. Attempt to customize a product and verify that the changes are reflected in the product details.\n* **Expected Result:** The website should display the product with interactive features, provide size guides, and allow for product customization.\n\n**TC_003: Error Handling - Incarnage.com**\n\n* **Description:** Verify that Incarnage.com handles error conditions gracefully when a user attempts to access a non-existent product or page.\n* **Steps:**\n\t1. Open the Incarnage.com website in a web browser.\n\t2. Search for a non-existent product and click on the search result.\n\t3. Verify that the website displays an error message indicating that the product is not found.\n\t4. Attempt to access a non-existent page (e.g., a fictional product category) and verify that the website displays an error message.\n* **Expected Result:** The website should display an error message when a user attempts to access a non-existent product or page.\n\n**TC_004: Boundary Value Test Case - Scalability and Performance Optimization - Stockroom.lk**\n\n* **Description:** Verify that Stockroom.lk's scalability and performance optimization features work correctly when handling a large number of concurrent users.\n* **Steps:**\n\t1. Simulate a large number of concurrent users accessing the Stockroom.lk website using a load testing tool.\n\t2. Verify that the website's loading times remain fast and responsive.\n\t3. Check that the website's caching mechanisms and CDNs are effective in optimizing performance.\n* **Expected Result:** The website should handle a large number of concurrent users without significant performance degradation.\n\n**TC_005: Edge Case Test Case - Incarnage.com**\n\n* **Description:** Verify that Incarnage.com's community forums and live chat support features work correctly when handling a large number of concurrent users.\n* **Steps:**\n\t1. Simulate a large number of concurrent users accessing the Incarnage.com website's community forums and live chat support features using a load testing tool.\n\t2. Verify that the features remain responsive and functional.\n\t3. Check that the website's server infrastructure can handle the increased load without significant performance degradation.\n* **Expected Result:** The website's community forums and live chat support features should remain functional and responsive when handling a large number of concurrent users.\n\nNote: These test cases are just a starting point, and you may need to modify or add to them based on your specific testing requirements and the web app's functionality.\nHere are the test cases for the given Business Requirements Document (BRD):\n\n**Test Cases:**\n\n**TC_001: Extensive Product Catalog - Valid Search**\n\n*   **Description:** Verify that the website's product catalog can be searched successfully with valid inputs.\n*   **Steps:**\n    1. Open the website and navigate to the product catalog page.\n    2. Enter a valid search term in the search bar (e.g., \"gaming mouse\").\n    3. Click the search button.\n    4. Verify that the search results display relevant products.\n*   **Expected Result:** The search results should display a list of products matching the search term, with accurate product information and images.\n\n**TC_002: Secure Payment Options - Invalid Payment Method**\n\n*   **Description:** Verify that the website handles invalid payment methods gracefully.\n*   **Steps:**\n    1. Open the website and navigate to the checkout page.\n    2. Select an invalid payment method (e.g., \"Bitcoin\").\n    3. Click the \"Proceed to Payment\" button.\n    4. Verify that an error message is displayed, indicating that the payment method is not supported.\n*   **Expected Result:** The website should display an error message, and the payment process should not proceed.\n\n**TC_003: Account Management - Valid Login**\n\n*   **Description:** Verify that the website's account management system can be used successfully with valid login credentials.\n*   **Steps:**\n    1. Open the website and navigate to the login page.\n    2. Enter valid login credentials (e.g., username and password).\n    3. Click the login button.\n    4. Verify that the user is successfully logged in and can access their account information.\n*   **Expected Result:** The user should be logged in successfully, and their account information should be displayed.\n\n**TC_004: Customer Reviews and Ratings - Edge Case: No Reviews**\n\n*   **Description:** Verify that the website handles the absence of customer reviews and ratings correctly.\n*   **Steps:**\n    1. Open the website and navigate to a product page with no customer reviews.\n    2. Verify that the product page displays a message indicating that there are no reviews available.\n*   **Expected Result:** The website should display a message indicating that there are no reviews available, and the product page should not display any reviews or ratings.\n\nThese test cases cover a range of scenarios, including valid inputs, invalid inputs, boundary conditions, and error handling. They focus on key functionalities such as the product catalog, secure payment options, account management, and customer reviews and ratings.\nBased on the BRD, I've generated a comprehensive set of functional test cases and edge case test cases for each website. Here are the test cases for Stockroom.lk, Incarnage.com, and Adidas.com/lk:\n\n**Stockroom.lk**\n\n**Test Cases:**\n\n*   **TC_001: Pre-Order System - Valid Input**\n    *   **Description:** Verify that the pre-order system works correctly with valid inputs.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the pre-order section.\n        3. Select a product to pre-order.\n        4. Enter valid payment information.\n        5. Confirm the pre-order.\n    *   **Expected Result:** The product is successfully pre-ordered, and the user receives a confirmation email.\n*   **TC_002: Pre-Order System - Invalid Input**\n    *   **Description:** Verify that the pre-order system handles invalid inputs correctly.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the pre-order section.\n        3. Select a product to pre-order.\n        4. Enter invalid payment information (e.g., incorrect credit card number).\n        5. Confirm the pre-order.\n    *   **Expected Result:** The pre-order is not processed, and an error message is displayed.\n\n**Incarnage.com**\n\n**Test Cases:**\n\n*   **TC_003: Limited Edition Releases - Valid Input**\n    *   **Description:** Verify that the limited edition releases feature works correctly with valid inputs.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the limited edition releases section.\n        3. Select a product to purchase.\n        4. Enter valid payment information.\n        5. Confirm the purchase.\n    *   **Expected Result:** The product is successfully purchased, and the user receives a confirmation email.\n*   **TC_004: Community Forums - Edge Case**\n    *   **Description:** Verify that the community forums handle unusual or unexpected scenarios.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the community forums.\n        3. Post a topic with a very long title (e.g., 500 characters).\n        4. Post a reply with a very long message (e.g., 1000 characters).\n    *   **Expected Result:** The topic and reply are successfully posted, and the system handles the long input data correctly.\n\n**Adidas.com/lk**\n\n**Test Cases:**\n\n*   **TC_005: Product Customization - Valid Input**\n    *   **Description:** Verify that the product customization feature works correctly with valid inputs.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the product customization section.\n        3. Select a product to customize.\n        4. Enter valid customization options (e.g., color, design).\n        5. Confirm the customization.\n    *   **Expected Result:** The customized product is successfully created, and the user receives a confirmation email.\n*   **TC_006: Size Guides - Boundary Value**\n    *   **Description:** Verify that the size guides handle boundary values correctly.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the product details page.\n        3. Select a product with a size guide.\n        4. Enter a size value at the minimum or maximum boundary (e.g., size 1 or size 12).\n        5. Confirm the size selection.\n    *   **Expected Result:** The size guide correctly\nHere are the test cases for the given Business Requirements Document (BRD):\n\n**Test Cases:**\n\n**Test Case ID:** TC_001\n**Description:** Account Creation for Store Owner/Admin\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter valid store owner/admin credentials (username, email, password).\n3. Fill in the required information (store name, address, etc.).\n4. Click the \"Create Account\" button.\n\n**Expected Result:** The account is successfully created, and the store owner/admin is logged in.\n\n**Test Case ID:** TC_002\n**Description:** Account Creation for Fashion Designer\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter valid fashion designer credentials (username, email, password).\n3. Fill in the required information (designer name, bio, etc.).\n4. Click the \"Create Account\" button.\n\n**Expected Result:** The account is successfully created, and the fashion designer is logged in.\n\n**Test Case ID:** TC_003\n**Description:** Invalid Account Creation\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter invalid credentials (username, email, password).\n3. Fill in the required information (store name, address, etc.).\n4. Click the \"Create Account\" button.\n\n**Expected Result:** An error message is displayed, indicating that the account creation failed due to invalid credentials.\n\n**Test Case ID:** TC_004\n**Description:** Account Creation with Existing Email\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter an email address that already exists in the system.\n3. Fill in the required information (store name, address, etc.).\n4. Click the \"Create Account\" button.\n\n**Expected Result:** An error message is displayed, indicating that the email address is already in use.\n\n**Test Case ID:** TC_005\n**Description:** Account Creation with Weak Password\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter valid store owner/admin credentials (username, email, password).\n3. Fill in the required information (store name, address, etc.).\n4. Enter a weak password (e.g., \"password123\").\n5. Click the \"Create Account\" button.\n\n**Expected Result:** An error message is displayed, indicating that the password is too weak.\n\n**Test Case ID:** TC_006\n**Description:** Account Creation with Missing Information\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter valid store owner/admin credentials (username, email, password).\n3. Leave some required information (store name, address, etc.) blank.\n4. Click the \"Create Account\" button.\n\n**Expected Result:** An error message is displayed, indicating that some required information is missing.\n\n**Test Case ID:** TC_007\n**Description:** Account Creation with Invalid Store Name\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter valid store owner/admin credentials (username, email, password).\n3. Enter an invalid store name (e.g., containing special characters).\n4. Fill in the required information (address, etc.).\n5. Click the \"Create Account\" button.\n\n**Expected Result:** An error message is displayed, indicating that the store name is invalid.\n\n**Test Case ID:** TC_008\n**Description:** Account Creation with Invalid Address\n**Steps:**\n\n1. Navigate to the account creation page.\n2. Enter valid store owner/admin credentials (username, email, password).\n3. Enter an invalid address (e.g., containing special characters).\n4. Fill in the required information (store name, etc.).\n5. Click the \"Create Account\" button.\n\n**Expected Result:** An error message is displayed, indicating that the address is invalid.\n\n**Test Case ID:** TC_009\n**Description:** Account Creation with Valid Information\n**Steps:**\n\n\nHere are the test cases for the Customization Options, Fashion Quiz, Style Guides, Size Recommender, Fashion Events Calendar, and Fast Selling Products and New Arrivals functionalities:\n\n**Test Cases:**\n\n**Customization Options:**\n\n*   **Test Case ID:** TC_001\n    *   **Description:** Verify that the customization options are displayed correctly for a select product.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the product page for a select product that offers customization options.\n        3. Verify that the customization options (e.g., colors, designs, features) are displayed correctly.\n        4. Select a product customization option and verify that the updated product information is displayed correctly.\n    *   **Expected Result:** The customization options are displayed correctly, and selecting a customization option updates the product information accordingly.\n\n*   **Test Case ID:** TC_002\n    *   **Description:** Verify that the customization options are not displayed for products that do not offer customization.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the product page for a product that does not offer customization options.\n        3. Verify that the customization options are not displayed.\n    *   **Expected Result:** The customization options are not displayed for products that do not offer customization.\n\n**Fashion Quiz:**\n\n*   **Test Case ID:** TC_003\n    *   **Description:** Verify that the fashion quiz is displayed correctly and allows users to submit their answers.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the fashion quiz page.\n        3. Verify that the quiz questions are displayed correctly and allow users to submit their answers.\n        4. Submit answers to the quiz questions and verify that the results are displayed correctly.\n    *   **Expected Result:** The fashion quiz is displayed correctly, and submitting answers updates the results accordingly.\n\n*   **Test Case ID:** TC_004\n    *   **Description:** Verify that the fashion quiz handles invalid input (e.g., skipping questions, submitting incomplete answers).\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the fashion quiz page.\n        3. Skip one or more quiz questions and submit incomplete answers.\n        4. Verify that the quiz handles the invalid input correctly and displays an error message.\n    *   **Expected Result:** The quiz handles invalid input correctly and displays an error message.\n\n**Style Guides:**\n\n*   **Test Case ID:** TC_005\n    *   **Description:** Verify that the style guides are displayed correctly and allow users to browse through the content.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the style guides page.\n        3. Verify that the style guides are displayed correctly and allow users to browse through the content.\n        4. Verify that the style guides include relevant information, such as trend forecasts and styling tips.\n    *   **Expected Result:** The style guides are displayed correctly, and users can browse through the content.\n\n**Size Recommender:**\n\n*   **Test Case ID:** TC_006\n    *   **Description:** Verify that the size recommender is displayed correctly and provides accurate size recommendations.\n    *   **Steps:**\n        1. Log in to the website as a registered user.\n        2. Navigate to the product page for a clothing or accessory item.\n        3. Verify that the size recommender is displayed correctly and provides size recommendations based on body measurements, past purchases, and brand-specific size charts.\n        4. Verify that the size recommendations are accurate and relevant to the user's\nBased on the provided Business Requirements Document (BRD), I've generated a comprehensive set of functional test cases and edge case test cases. Here are the first two test cases:\n\n**Test Cases:**\n\n**TC_001: Agile Methodology Selection**\n\n*   **Description:** Verify that the system allows for the selection of the Agile methodology for the Alphaura website development.\n*   **Steps:**\n    1. Log in to the system as a project manager.\n    2. Navigate to the project settings page.\n    3. Click on the \"Methodology\" dropdown menu.\n    4. Select \"Agile\" from the dropdown menu.\n    5. Verify that the system displays a confirmation message indicating that the Agile methodology has been selected.\n*   **Expected Result:** The system successfully selects the Agile methodology for the Alphaura website development, and the confirmation message is displayed.\n\n**TC_002: Domain Registration**\n\n*   **Description:** Verify that the system allows for the registration of a domain name for the Alphaura website.\n*   **Steps:**\n    1. Log in to the system as a project manager.\n    2. Navigate to the domain registration page.\n    3. Enter a valid domain name (e.g., \"alphaura.com\") in the input field.\n    4. Click on the \"Register Domain\" button.\n    5. Verify that the system displays a confirmation message indicating that the domain name has been successfully registered.\n*   **Expected Result:** The system successfully registers the domain name, and the confirmation message is displayed.\n\n**Edge Case Test Cases:**\n\n**EC_TC_001: Invalid Domain Name**\n\n*   **Description:** Verify that the system handles an invalid domain name during registration.\n*   **Steps:**\n    1. Log in to the system as a project manager.\n    2. Navigate to the domain registration page.\n    3. Enter an invalid domain name (e.g., \"alphaura.\") in the input field.\n    4. Click on the \"Register Domain\" button.\n    5. Verify that the system displays an error message indicating that the domain name is invalid.\n*   **Expected Result:** The system displays an error message indicating that the domain name is invalid, and the registration process is aborted.\n\n**EC_TC_002: Duplicate Domain Name**\n\n*   **Description:** Verify that the system handles a duplicate domain name during registration.\n*   **Steps:**\n    1. Log in to the system as a project manager.\n    2. Navigate to the domain registration page.\n    3. Enter a domain name that is already registered (e.g., \"alphaura.com\") in the input field.\n    4. Click on the \"Register Domain\" button.\n    5. Verify that the system displays an error message indicating that the domain name is already registered.\n*   **Expected Result:** The system displays an error message indicating that the domain name is already registered, and the registration process is aborted.\n\nPlease note that these are just the first two test cases, and I will continue to generate more test cases based on the BRD.\nBased on the BRD, I've identified the key functionalities and requirements. Here are two test cases for each functionality:\n\n**Test Cases:**\n\n**Functionalities:**\n\n1. **Inventory Management**\n2. **Order Fulfillment**\n3. **Customer Relationship Management (CRM)**\n4. **Point of Sale (POS) Integration**\n5. **Order Processing**\n6. **Customer Service**\n7. **Workflow Adjustments**\n8. **Training and Skill Requirements for Staff**\n9. **Team Collaboration and Communication**\n\n**Test Cases:**\n\n**Inventory Management**\n\n*   **Test Case ID:** TC_INV_001\n    *   **Description:** Verify that the online application synchronizes with the current inventory management system in real-time.\n    *   **Steps:**\n        1. Log in to the online application as an administrator.\n        2. Update the inventory levels in the online application.\n        3. Verify that the changes are reflected in the current inventory management system.\n    *   **Expected Result:** The inventory levels in the online application and the current inventory management system should match.\n*   **Test Case ID:** TC_INV_002\n    *   **Description:** Verify that the online application handles inventory inconsistencies.\n    *   **Steps:**\n        1. Log in to the online application as an administrator.\n        2. Manually update the inventory levels in the current inventory management system.\n        3. Verify that the online application detects the inconsistency and updates the inventory levels accordingly.\n    *   **Expected Result:** The online application should detect the inconsistency and update the inventory levels to match the current inventory management system.\n\n**Order Fulfillment**\n\n*   **Test Case ID:** TC_OF_001\n    *   **Description:** Verify that the online application processes orders efficiently.\n    *   **Steps:**\n        1. Log in to the online application as a customer.\n        2. Place an order through the online application.\n        3. Verify that the order is processed and the customer receives a confirmation email.\n    *   **Expected Result:** The order should be processed and the customer should receive a confirmation email.\n*   **Test Case ID:** TC_OF_002\n    *   **Description:** Verify that the online application handles order processing errors.\n    *   **Steps:**\n        1. Log in to the online application as a customer.\n        2. Attempt to place an order with invalid payment information.\n        3. Verify that the online application detects the error and provides an error message.\n    *   **Expected Result:** The online application should detect the error and provide an error message.\n\n**Customer Relationship Management (CRM)**\n\n*   **Test Case ID:** TC_CRM_001\n    *   **Description:** Verify that the online application integrates with the existing CRM system.\n    *   **Steps:**\n        1. Log in to the online application as an administrator.\n        2. Update a customer's information in the online application.\n        3. Verify that the changes are reflected in the existing CRM system.\n    *   **Expected Result:** The changes should be reflected in the existing CRM system.\n*   **Test Case ID:** TC_CRM_002\n    *   **Description:** Verify that the online application handles CRM system errors.\n    *   **Steps:**\n        1. Log in to the online application as an administrator.\n        2. Attempt to update a customer's information in the online application, but the CRM system is down.\n        3. Verify that the online application detects the error and provides an error message.\n    *   **Expected Result:** The online application should detect the error and provide an error message.\n\n**Point of Sale (POS) Integration**\n\n*   **Test Case ID:** TC_POS_001\n    *   **Description:** Verify that the online application integrates with the current POS system.\n   \nBased on the provided Business Requirements Document (BRD), I've generated a comprehensive set of functional test cases and edge case test cases for the Alphaura Fashion Accessories Web Application. Here are the first two test cases:\n\n**Test Cases:**\n\n**TC_001: User Registration**\n\n*   **Description:** Verify that a user can successfully register with valid information.\n*   **Steps:**\n    1. Navigate to the registration page.\n    2. Enter a valid name, contact number, and email address.\n    3. Click the \"Register\" button.\n*   **Expected Result:** The system should create a new user account with the provided information, and the user should be logged in successfully.\n\n**TC_002: Invalid User Registration**\n\n*   **Description:** Verify that the system handles invalid user registration attempts.\n*   **Steps:**\n    1. Navigate to the registration page.\n    2. Enter an invalid name (e.g., only numbers or special characters).\n    3. Enter a valid contact number and email address.\n    4. Click the \"Register\" button.\n*   **Expected Result:** The system should display an error message indicating that the name is invalid, and the registration process should not be completed.\n\nAdditional test cases will be generated based on the BRD, covering various functionalities, such as:\n\n*   User Management: Valid and invalid login attempts, password reset, and profile management.\n*   Product Management: Adding, deleting, and editing product listings, as well as updating stock levels.\n*   Blog Management: Creating, editing, and deleting blog posts, as well as viewing and leaving feedback.\n*   Order Management: Managing orders, including accepting, deleting, and updating order details.\n*   Feedback Management: Viewing and responding to feedback on blog posts and purchased products.\n*   Discount Management: Setting up discounts and promotions, and displaying them to signed-up customers.\n*   Shopping Cart and Checkout: Adding products to the cart, editing quantities, and proceeding to checkout.\n*   Search and Filtering: Searching for products using keywords and filtering results by category, price, and discounts.\n*   Communication Features: Responding to user inquiries and feedback.\n\nPlease let me know if you'd like me to generate more test cases or if you have any specific requirements.\nBased on the provided Business Requirements Document (BRD), I've generated a comprehensive set of functional test cases and edge case test cases. Here are the first two test cases:\n\n**Test Cases:**\n\n**TC_001: Define Project Plan**\n\n*   **Description:** Verify that the project plan is successfully created with all required deliverables, schedule, resource allocation, and risk mitigation strategies.\n*   **Steps:**\n    1. Log in to the project management tool.\n    2. Click on the \"Create Project Plan\" button.\n    3. Fill in the required fields for project deliverables, schedule, resource allocation, and risk mitigation strategies.\n    4. Click on the \"Save\" button.\n*   **Expected Result:** The project plan is successfully created with all required information.\n\n**TC_002: Implement Project Deliverables**\n\n*   **Description:** Verify that the project deliverables are correctly implemented with valid inputs.\n*   **Steps:**\n    1. Log in to the project management tool.\n    2. Click on the \"Define Project Deliverables\" button.\n    3. Enter valid project deliverables (e.g., project scope, timelines, budget).\n    4. Click on the \"Save\" button.\n*   **Expected Result:** The project deliverables are correctly implemented with valid inputs.\n\n**Edge Case Test Cases:**\n\n**TC_003: Invalid Project Deliverables**\n\n*   **Description:** Verify that the system handles invalid project deliverables (e.g., empty fields, invalid data types).\n*   **Steps:**\n    1. Log in to the project management tool.\n    2. Click on the \"Define Project Deliverables\" button.\n    3. Enter invalid project deliverables (e.g., empty fields, invalid data types).\n    4. Click on the \"Save\" button.\n*   **Expected Result:** The system displays an error message indicating that the input is invalid.\n\n**Test Case ID:** TC_004: **Boundary Value Test Case - Project Deliverables**\n\n*   **Description:** Verify that the system handles project deliverables at the boundary values (e.g., minimum and maximum values).\n*   **Steps:**\n    1. Log in to the project management tool.\n    2. Click on the \"Define Project Deliverables\" button.\n    3. Enter project deliverables at the boundary values (e.g., minimum and maximum values).\n    4. Click on the \"Save\" button.\n*   **Expected Result:** The system correctly handles project deliverables at the boundary values.\n\nPlease note that these are just the first two test cases, and there are many more functionalities and requirements to cover. I'll be happy to generate more test cases based on the BRD.\nBased on the BRD, I've identified the key functionalities and requirements. Here are two test cases, covering positive, negative, boundary value, and edge cases:\n\n**Test Cases:**\n\n**TC_001: Risk Response Plan Development**\n\n*   **Description:** Verify that the system allows for the development of a risk response plan and assesses the impact of external factors.\n*   **Steps:**\n    1. Log in to the system as a user with the necessary permissions.\n    2. Navigate to the \"Risk Response Plan\" section.\n    3. Fill in the required fields for the risk response plan, including the risk description, impact assessment, and mitigation strategies.\n    4. Click \"Save\" to save the risk response plan.\n    5. Verify that the risk response plan is saved successfully and can be viewed in the system.\n*   **Expected Result:** The system successfully saves the risk response plan and displays it in the system.\n\n**TC_002: Contingency Plan for Major Disruptions**\n\n*   **Description:** Verify that the system allows for the creation of contingency plans for major disruptions and handles invalid inputs.\n*   **Steps:**\n    1. Log in to the system as a user with the necessary permissions.\n    2. Navigate to the \"Contingency Plans\" section.\n    3. Fill in the required fields for the contingency plan, including the disruption type, impact assessment, and mitigation strategies.\n    4. Enter an invalid input, such as an empty field or an invalid date, in one of the required fields.\n    5. Click \"Save\" to save the contingency plan.\n    6. Verify that the system displays an error message indicating the invalid input and does not save the contingency plan.\n    7. Repeat steps 3-6 with valid inputs to verify that the system saves the contingency plan successfully.\n*   **Expected Result:** The system displays an error message for invalid inputs and does not save the contingency plan. With valid inputs, the system saves the contingency plan successfully.\n\nAdditional test cases can be generated to cover more scenarios, such as:\n\n*   TC_003: Review and Update Legal Compliance\n*   TC_004: Assessment of Impact of External Factors\n*   TC_005: Error Handling for Unforeseen Events\n*   TC_006: Contingency Plan for Natural Disasters\n*   TC_007: Risk Response Plan for Economic Downturns\n\nThese test cases cover a range of scenarios, including valid inputs, invalid inputs, boundary conditions, and error handling. They can be used to ensure that the system meets the requirements outlined in the BRD.";

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
//     // setTestCaseData(doc.llm_response_testcases); // or doc if you want all data
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


//Api code
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
import { TablePagination } from "@mui/material";
import "./../asessts/css/dashboard.css";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("testcase");
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [testCaseData, setTestCaseData] = useState("");
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(5); // or 10 or anything else


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
          <strong key={index} >{part.slice(2, -2)}</strong>
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

//  useEffect(() => {
//   const fetchDocuments = async () => {
//     try {
//       const response = await axios.get("http://gen-ai.synchroni.xyz:8000/documents/");
//       const sortedDocs = [...response.data].sort((a, b) => {
//         // 🔄 Option 1: If your API has `created_at` field (ISO format)
//         return new Date(b.created_at) - new Date(a.created_at);

//         // 🔄 Option 2: If you're using MongoDB and no created_at field is available
//         // return b._id.localeCompare(a._id); // or just b._id - a._id if numeric
//       });

//       setDocuments(sortedDocs);
//       console.log("Fetched and sorted data:", sortedDocs);
//     } catch (error) {
//       console.error("Error fetching documents:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   fetchDocuments();
// }, []);

useEffect(() => {
  const fetchDocuments = async () => {
    try {
      const response = await axios.get("http://gen-ai.synchroni.xyz:8000/documents/");
      
      // ⬇️ Sort newest documents first using _id (default in MongoDB)
      const sortedDocs = [...response.data].sort((a, b) => (b._id > a._id ? 1 : -1));
      
      setDocuments(sortedDocs);
      console.log("Sorted documents:", sortedDocs);
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
      <Box sx={{ mt: 10, px: 2}}>
        <Box sx={{ position: "absolute", top: 80, right: 20}}>
          <Button
            // variant="contained"
            onClick={handleUploadClick}
            sx={{ textTransform: "none", fontWeight: "bold", color: "white", backgroundColor: "#000080",borderRadius:"10px",padding:"6px 16px",marginRight:"20px" }}
          >
            New Document
          </Button>
        </Box>

        <Container maxWidth="xl" sx={{ mt: 8 }}>
          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 10 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer  sx={{ width: "100%",border:"1px solid #e6e6e6",borderRadius:"10px" }}>
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
                {documents.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((doc, index) => (
                    <TableRow key={doc._id}>
<TableCell>{page * rowsPerPage + index + 1}</TableCell>
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
          <TablePagination
  rowsPerPageOptions={[5, 10, 25]}
  component="div"
  count={documents.length}
  rowsPerPage={rowsPerPage}
  page={page}
  onPageChange={(event, newPage) => setPage(newPage)}
  onRowsPerPageChange={(event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  }}
/>
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
            padding: "0px 23px",
            height: "93%",
            top:"64px",
            transition: "transform 2s ease-in-out",
            transform: "translate(50%, 0%)",
            borderRadius: "20px",
          },
        }}
      >
        <Box
  sx={{
    display: "flex",
    flexDirection: "column",
    position: "sticky",
    top: 0,
    backgroundColor: "#fff",
    zIndex: 1000,
    paddingY: 2,
    paddingX: 2,
  }}
>
  {/* Title and Close */}
  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
  <Box className="header-tabs-flex-wrapper" sx={{ display: "flex", gap: 2 }}>
  <Box className="header-dashboard-wrapper" ml={1}>
    <Box
      className={`header-dashboard ${activeTab === "testcase" ? "active" : ""}`}
      onClick={() => setActiveTab("testcase")}
    >
      Test Case
    </Box>
  </Box>
  <Box className="header-courses-wrapper">
    <Box
      className={`header-dashboard ${activeTab === "userstory" ? "active" : ""}`}
      onClick={() => setActiveTab("userstory")}
    >
      User Story
    </Box>
  </Box>
</Box>
    <IconButton onClick={toggleDrawer(false)}>
      <CloseIcon />
    </IconButton>
  </Box>
</Box>

        <Box sx={{ mt: 0,ml:3,backgroundColor:"#f5f5f5",p:2,borderRadius:"15px"}}>{parseFormattedText(testCaseData)}</Box>
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
