// import React, { useState, useRef } from 'react';
// import {
//   Box,
//   Button,
//   Typography,
//   TextField,
//   MenuItem,
//   IconButton,
//   InputAdornment,
//   LinearProgress,
//   Paper,
//   Grid,
//   Avatar,
//   Divider,
// } from '@mui/material';
// import {
//   CloudUpload,
//   CalendarToday,
//   ExpandLess,
//   ExpandMore,
//   InsertDriveFile,
// } from '@mui/icons-material';
// import CloudUploadIcon from '@mui/icons-material/CloudUpload';
// import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
// import ImageIcon from '@mui/icons-material/Image';
// import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

// const fileIcons = {
//   pdf: <PictureAsPdfIcon sx={{ color: '#f44336' }} />,
//   png: <ImageIcon sx={{ color: '#2196f3' }} />,
//   jpg: <ImageIcon sx={{ color: '#4caf50' }} />,
//   default: <InsertDriveFile sx={{ color: '#757575' }} />,
// };

// const filesSample = [
//   { name: 'GenAI_Request_Response_Examples', size: '3.6 MB', uploaded: '2.5 MB', type: 'pdf', progress: 72 },
//   { name: 'GenAI_Audit_Records', size: '5 MB', uploaded: '3 MB', type: 'jpg', progress: 60 },
//   { name: 'GenAI_API_Integration_Guide', size: '4.5 MB', uploaded: '3 MB', type: 'png', progress: 67 },
//   { name: 'GenAI_Security_Test_Log', size: '6 MB', uploaded: '4 MB', type: 'pdf', progress: 75 },
//   { name: 'GenAI_Compliance_Checklist', size: '2.6 MB', uploaded: '2 MB', type: 'pdf', progress: 77 },
//   { name: 'GenAI_Datashare_Validation', size: '3.3 MB', uploaded: '2.2 MB', type: 'jpg', progress: 66 },
//   { name: 'GenAI_Audit_Records', size: '2 MB', uploaded: '1.5 MB', type: 'png', progress: 80 },
// ];

// export default function GenAIUploader() {
//   const [collapsed, setCollapsed] = useState(true);
//    const [uploading, setUploading] = useState(false);
// const [uploadProgress, setUploadProgress] = useState([]);
// const fileInputRef = useRef(null);

//   const getFileIcon = (type) => fileIcons[type] || fileIcons.default;

//   return (
//     <Box sx={{ p: 4, maxWidth: 900, mx: 'auto', fontFamily: 'sans-serif',width:'100%' }}>
//       <Typography variant="h5" fontWeight={700} mb={3}>
//         GenAI_Documentation_Overview
//       </Typography>

//       {/* Form with Starting Icon */}
//   <Box display="flex" alignItems="flex-start" gap={8} mb={4} >
//   {/* Avatar on the left */}
//   <Avatar
//     variant="rounded"
//     sx={{ bgcolor: '#f5f5f5', width: 56, height: 56, mt: 1,  marginTop:'30px',borderRadius:"12px" }}
//   >
//     <InsertDriveFile sx={{ fontSize: 32, color: '#777' }} />
//   </Avatar>

//   <Box flex={1}>
//   <Grid container spacing={2}>
//     {/* Row 1: full-width Data Space */}
//   <Grid item xs={12}>
//   <TextField
//     variant="outlined"
//     label="Data Space"
//     sx={{ width: 750 }}
//      InputProps={{
//       sx: {
//         borderRadius: '12px' // Apply border radius
//       }
//     }}
//   />
// </Grid>



//     {/* Row 2: three fields side-by-side */}
//    <Grid container spacing={2}>
//   <Grid item xs={12} md={3}>
//     <TextField fullWidth variant="outlined" label="Upload by"sx={{ width: 365 }}  InputProps={{
//       sx: {
//         borderRadius: '12px' // Apply border radius
//       }
//     }} />
//   </Grid>
//   <Grid item xs={12} md={6}>  {/* increased from 4 to 6 */}
//     <TextField fullWidth variant="outlined" label="Data space path" select     sx={{ width: 365 }}  InputProps={{
//       sx: {
//         borderRadius: '12px' // Apply border radius
//       }
//     }}>
//       <MenuItem value="/path1">/path1</MenuItem>
//       <MenuItem value="/path2">/path2</MenuItem>
//     </TextField>
//   </Grid>
// </Grid>

//   </Grid>
// </Box>



// </Box>



//       {/* Main Content: Upload Area + Progress */}
//       <Grid container spacing={3}>
//         {/* Upload Area */}
//         <Grid item xs={12} md={6}>
//   <Paper
//     sx={{
//       border: '2px dashed #ccc',
//       p: 4,
//       textAlign: 'center',
//       borderRadius: '12px',
//       minHeight: 280,
//       display: 'flex',
//       flexDirection: 'column',
//       justifyContent: 'center',
//       alignItems: 'center',
//       gap: 1,
//     }}
//   >
//     <CloudUploadIcon sx={{ fontSize: 40, color: '#333', mb: 1 }} />

//     <Typography fontWeight={600} sx={{ fontSize: '16px' }}>
//       Choose a file <Typography component="span" fontWeight={400}>(or) Drag & drop it here</Typography>
//     </Typography>

//     <Box display="flex" alignItems="center" gap={0.5} mb={2} mt={1}>
//       <InfoOutlinedIcon fontSize="small" color="disabled" />
//       <Typography variant="body2" color="text.secondary">
//         Supported files types: JPG, PNG, PDF, Max size is 10 MB
//       </Typography>
//     </Box>

// <Box sx={{  display: "flex", flexDirection: "column", justifyContent: "center" }}>
//   {!uploading ? (
//     <>
//       <Box
// onClick={() => {
//   if (!uploading) document.getElementById("fileInput").click();
// }}
//      >
//           <Button
//             variant="contained"
//             sx={{
//               mt: 2,
//               backgroundColor: "#00008B",
//               textTransform: "none",
//               "&:hover": {
//                 backgroundColor: "#000060"
//               }
//             }}
//           >
//             Choose file
//           </Button>
//       </Box>

//       {/* Hidden file input */}
//       <input
//         type="file"
//         id="fileInput"
//         style={{ display: "none" }}
//           accept=".jpg,.jpeg,.png,.pdf" // restrict file types
//      onChange={(e) => {
//   const selectedFile = e.target.files[0];
//   if (selectedFile) {
//     const type = selectedFile.name.split('.').pop().toLowerCase();
//     const newFile = {
//       name: selectedFile.name,
//       size: `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`,
//       uploaded: `0 MB`,
//       type: ['jpg', 'jpeg', 'png', 'pdf'].includes(type) ? type : 'default',
//       progress: 0,
//     };

//     // Expand the progress panel when upload starts
//     setCollapsed(false);

//     setUploading(true);
//     setUploadProgress(prev => [...prev, newFile]);

//     // Simulate progress
//     const interval = setInterval(() => {
//       setUploadProgress(prevFiles => {
//         return prevFiles.map(file => {
//           if (file.name === newFile.name && file.progress < 100) {
//             const updatedProgress = Math.min(file.progress + 10, 100);
//             const updatedUploaded = ((parseFloat(file.size) * updatedProgress) / 100).toFixed(1);
//             return {
//               ...file,
//               progress: updatedProgress,
//               uploaded: `${updatedUploaded} MB`
//             };
//           }
//           return file;
//         });
//       });
//     }, 500);

//     setTimeout(() => {
//       clearInterval(interval);
//       setUploading(false);
//     }, 5000);
//   }
// }}


//       />
//     </>
//   ) : null}
// </Box>

//   </Paper>
// </Grid>

//         {/* Upload Progress + Buttons */}
//         <Grid item xs={12} md={6}>
//           <Paper sx={{ p: 2, borderRadius: 3, maxHeight: 420,minWidth: 360, display: 'flex', flexDirection: 'column' }}>
//             <Box display="flex" justifyContent="space-between" alignItems="center">
//               <Typography fontWeight={600}>Uploading Progress</Typography>
//               <IconButton onClick={() => setCollapsed(!collapsed)} size="small">
//                 {collapsed ? <ExpandMore /> : <ExpandLess />}
//               </IconButton>
//             </Box>

//             {!collapsed && (
//               <Box mt={2} flex={1} overflow="auto">
//                 {uploadProgress.map((file, index) => (
//   <Box key={index} mb={2}>
//     <Box display="flex" alignItems="center" gap={1} mb={0.5}>
//       {getFileIcon(file.type)}
//       <Box flexGrow={1}>
//         <Typography
//           variant="body2"
//           fontWeight={600}
//           sx={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
//         >
//           {file.name}
//         </Typography>
//         <Typography variant="caption" color="text.secondary">
//           {file.uploaded} / {file.size}
//         </Typography>
//       </Box>
//       <Typography variant="body2" minWidth={35}>
//         {file.progress}%
//       </Typography>
//     </Box>
//     <LinearProgress variant="determinate" value={file.progress} />
//   </Box>
// ))}

//               </Box>
//             )}
//           </Paper>
//         </Grid>
//       </Grid>
//        {/* Buttons directly under upload list */}
//             <Box display="flex" justifyContent="flex-end" gap={2} mt={2} mr={3}>
//               <Button
//                 variant="outlined"
//                 sx={{ borderRadius: 5, textTransform: 'none' }}
//               >
//                 Cancel
//               </Button>
//               <Button
//                 variant="outlined"
//                 sx={{
//                   borderColor: '#000080',
//                   color: '#000080',
//                   borderRadius: 5,
//                   textTransform: 'none',
//                   fontWeight: 500,
//                 }}
//               >
//                 Create
//               </Button>
//             </Box>
//     </Box>
//   );
// }



// import React, { useState, useRef } from 'react';
// import {
//   Box,
//   Button,
//   Typography,
//   TextField,
//   MenuItem,
//   IconButton,
//   InputAdornment,
//   LinearProgress,
//   Paper,
//   Grid,
//   Drawer,
//   Avatar,
//   Divider,
//   CircularProgress
// } from '@mui/material';
// import {
//   CloudUpload,
//   CalendarToday,
//   ExpandLess,
//   ExpandMore,
//   InsertDriveFile,
// } from '@mui/icons-material';
// import CloseIcon from "@mui/icons-material/Close";
// import DocumentIcon from "./../../asessts/images/documenticon.png";
// import Cloudicon from "./../../asessts/images/cloudicon.png";
// import Choosefileicon from "./../../asessts/images/choosefile.png";
// import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
// import ImageIcon from '@mui/icons-material/Image';
// import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
// // import CircularProgress from '@mui/material';

// const fileIcons = {
//   pdf: <PictureAsPdfIcon sx={{ color: '#f44336' }} />,
//   png: <ImageIcon sx={{ color: '#2196f3' }} />,
//   jpg: <ImageIcon sx={{ color: '#4caf50' }} />,
//   default: <InsertDriveFile sx={{ color: '#757575' }} />,
// };

// const filesSample = [
//   { name: 'GenAI_Request_Response_Examples', size: '3.6 MB', uploaded: '2.5 MB', type: 'pdf', progress: 72,date:'2 Apr,2025',time:'11:25' },
//   { name: 'GenAI_Audit_Records', size: '5 MB', uploaded: '3 MB', type: 'jpg', progress: 60,date:'2 Apr,2025',time:'11:25' },
//   { name: 'GenAI_API_Integration_Guide', size: '4.5 MB', uploaded: '3 MB', type: 'png', progress: 67,date:'2 Apr,2025',time:'11:25' },
//   { name: 'GenAI_Security_Test_Log', size: '6 MB', uploaded: '4 MB', type: 'pdf', progress: 75,date:'2 Apr,2025',time:'11:25' },
//   { name: 'GenAI_Compliance_Checklist', size: '2.6 MB', uploaded: '2 MB', type: 'pdf', progress: 77,date:'2 Apr,2025',time:'11:25' },
//   { name: 'GenAI_Datashare_Validation', size: '3.3 MB', uploaded: '2.2 MB', type: 'jpg', progress: 66,date:'2 Apr,2025',time:'11:25' },
//   { name: 'GenAI_Audit_Records', size: '2 MB', uploaded: '1.5 MB', type: 'png', progress: 80,date:'2 Apr,2025',time:'11:25' },
// ];
// const GenAIUploader = ({open, onClose}) => {
//   const [collapsed, setCollapsed] = useState(true);
//    const [uploading, setUploading] = useState(false);
// const [uploadProgress, setUploadProgress] = useState([]);
// const fileInputRef = useRef(null);
// const StyledMenuProps = {
//   PaperProps: {
//     sx: {
//       borderRadius: '16px', // Rounded corners for the dropdown card
//     },
//   },
// };

//   const getFileIcon = (type) => fileIcons[type] || fileIcons.default;

//   return (
//      <Drawer
//       anchor="right"
//       open={open}
//       onClose={onClose}
//       transitionDuration={{ enter: 1000, exit: 1000 }}
//       PaperProps={{
//         sx: {
//           width: '60%',
//                     height: "92%",
//           borderRadius: '20px 0px 0px 20px',
//                     transition: "transform 2s ease-in-out",
//                               transform: "translate(50%, 0%)",
//           padding: "0px 32px",
//           mt: '64px',
// overflow: "auto",
//           overflowY:"hidden",
//         overflowX:"hidden"        },
//       }}
//     >
//     <Box sx={{  fontFamily: 'sans-serif',width:'100%',maxWidth:'900px',p:4 }}>
//      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
//   <Typography variant="h5" fontWeight={700}>
//     GenAI_Documentation_Overview
//   </Typography>
//   <IconButton onClick={onClose} >
//     <CloseIcon />
//   </IconButton>
// </Box>

//       {/* Form with Starting Icon */}
//   <Box display="flex" alignItems="flex-start" gap={4} mb={4} >
//   {/* Avatar on the left */}
//   <Avatar
//   variant="rounded"
//   src={DocumentIcon}
//   alt="Document Thumbnail"
//   sx={{
//     bgcolor: '#f5f5f5',
//     width: 56,
//     height: 56,
//     borderRadius: "12px",
//     mt: { xs: 0, md: '10px' },
//     objectFit: 'cover',
//     padding:"10px",
//   }}
// />

//   <Box flex={1}>
//   <Grid container spacing={2}>
//     {/* Row 1: full-width Data Space */}
//   <Grid item xs={12}>
//   <TextField
//     variant="outlined"
//     label="Data Space"
//     sx={{ width: 750 }}
//     InputProps={{
//       sx: {
//         borderRadius: '20px',
//         height: 45, // Optional: Sets total height
//         fontSize: 14, // Optional: Controls font size
//         padding: '0 10px',
//         '& .MuiOutlinedInput-input': {
//           padding: '8px 12px', // Reduces inner padding
//         }
//       }
//     }}
//     InputLabelProps={{
//       sx: {
//         fontSize: 14, // Optional: Smaller label
//       }
//     }}
//   />
// </Grid>




//     {/* Row 2: three fields side-by-side */}
//    <Grid container spacing={2}>
//   <Grid item xs={12} md={3}>
//   <TextField
//     fullWidth
//     variant="outlined"
//     label="Upload by"
//     sx={{ width: 365 }}
//     InputProps={{
//       sx: {
//         borderRadius: '20px',
//         height: 45, // Optional: total field height
//         '& .MuiOutlinedInput-input': {
//           padding: '8px 12px', // Reduce internal padding
//           fontSize: 14,
//         },
//       },
//     }}
//     InputLabelProps={{
//       sx: {
//         fontSize: 14,
//       },
//     }}
//   />
// </Grid>

// <Grid item xs={12} md={6}>
//   <TextField
//     fullWidth
//     variant="outlined"
//     label="Data space path"
//     select
//     sx={{ width: 365 }}
//     SelectProps={{
//       MenuProps: StyledMenuProps,
//     }}
//     InputProps={{
//       sx: {
//         borderRadius: '20px',
//         height: 45,
//         '& .MuiSelect-select': {
//           padding: '8px 12px',
//           fontSize: 14,
//         },
//       },
//     }}
//     InputLabelProps={{
//       sx: {
//         fontSize: 14,
//       },
//     }}
//   >
//     <MenuItem value="/path1">/path1</MenuItem>
//     <MenuItem value="/path2">/path2</MenuItem>
//   </TextField>
// </Grid>

// </Grid>

//   </Grid>
// </Box>



// </Box>



//       {/* Main Content: Upload Area + Progress */}
//       <Grid container spacing={3}>
//         {/* Upload Area */}
//         <Grid item xs={12} md={6}>
//   <Paper
//   sx={{
//     border: '2px dashed #D9D9D9',
//     p: 4,
//     textAlign: 'center',
//     borderRadius: '16px',
//     minHeight: 280,
//     minWidth:300,
//     display: 'flex',
//     flexDirection: 'column',
//     justifyContent: 'center',
//     alignItems: 'center',
//     gap: 2,
//     boxShadow: 'none'
//   }}
// >

// <img 
//   src={Cloudicon} 
//   alt="Upload" 
//   style={{ width: 50, height: 50, marginBottom: '8px' }} 
// />

//    <Typography fontWeight={500} fontSize="16px" color="#494949">
//   Choose a file <Typography component="span" fontWeight={500} color='#494949'>(or) Drag & drop it here</Typography>
// </Typography>

//     <Box display="flex" alignItems="center" gap={0.5} mb={2} mt={0}>
//       <InfoOutlinedIcon fontSize="small" color="disabled" />
//       <Typography variant="body2" color="#666">
//   Supported file types: JPG, PNG, PDF, Max size is 10 MB
// </Typography>
//     </Box>

// <Box sx={{  display: "flex", flexDirection: "column", justifyContent: "center" }}>
//   {!uploading ? (
//     <>
//       <Box
// onClick={() => {
//   if (!uploading) document.getElementById("fileInput").click();
// }}
//      >
//   <Button
//   // variant="contained"
//   sx={{
//     mt: 2,
//     backgroundColor: "#000080",
//     color: "#fff",
//     padding: "6px 16px",
//     fontSize: "14px",
//     borderRadius: "30px",
//     textTransform: "none",
//     boxShadow: "none",
//     display: "flex",
//     alignItems: "center",
//     gap: "8px", // space between image and text
//     '&:hover': {
//       backgroundColor: "#000080"
//     }
//   }}
// >
//   <img
//     src={Choosefileicon}
//     alt="icon"
//     style={{ width: 20, height: 20 }}
//   />
//   Choose file
// </Button>


//       </Box>

//       {/* Hidden file input */}
//       <input
//         type="file"
//         id="fileInput"
//         style={{ display: "none" }}
//           accept=".jpg,.jpeg,.png,.pdf" // restrict file types
//      onChange={(e) => {
//   const selectedFile = e.target.files[0];
//   if (selectedFile) {
//     const type = selectedFile.name.split('.').pop().toLowerCase();
//     const newFile = {
//       name: selectedFile.name,
//       size: `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`,
//       uploaded: `0 MB`,
//       type: ['jpg', 'jpeg', 'png', 'pdf'].includes(type) ? type : 'default',
//       progress: 0,
//     };

//     // Expand the progress panel when upload starts
//     setCollapsed(false);

//     setUploading(true);
//     setUploadProgress(prev => [...prev, newFile]);

//     // Simulate progress
//     const interval = setInterval(() => {
//       setUploadProgress(prevFiles => {
//         return prevFiles.map(file => {
//           if (file.name === newFile.name && file.progress < 100) {
//             const updatedProgress = Math.min(file.progress + 10, 100);
//             const updatedUploaded = ((parseFloat(file.size) * updatedProgress) / 100).toFixed(1);
//             return {
//               ...file,
//               progress: updatedProgress,
//               uploaded: `${updatedUploaded} MB`
//             };
//           }
//           return file;
//         });
//       });
//     }, 500);

//     setTimeout(() => {
//       clearInterval(interval);
//       setUploading(false);
//     }, 5000);
//   }
// }}


//       />
//     </>
//   ) : null}
// </Box>

//   </Paper>
// </Grid>

//         {/* Upload Progress + Buttons */}
// <Grid item xs={12} md={6}>
//   <Paper
//     sx={{
//       padding:'5px 15px',
//       borderRadius: 3,
//       maxHeight: 335,
//       minWidth: 360,
//       display: 'flex',
//       flexDirection: 'column',
//       bgcolor: '#fff',
//     }}
//   >
//     {/* Header */}
//     <Box display="flex" justifyContent="space-between" alignItems="center">
//       <Typography fontWeight={600} fontSize="16px">
//         Uploading Progress
//       </Typography>
//       <IconButton onClick={() => setCollapsed(!collapsed)} size="small">
//         {collapsed ? <ExpandMore /> : <ExpandLess />}
//       </IconButton>
//     </Box>

//     {/* Top Progress */}
//     <Box mt={0} display="flex" alignItems="center" gap={1} width={'200px'}>
//       <Box flexGrow={1}>
//   <LinearProgress
//     variant="determinate"
//     value={16}
//     sx={{
//       height: 6,
//       borderRadius: 5,
//       backgroundColor: '#eee',
//       '& .MuiLinearProgress-bar': {
//         borderRadius: 5,
//         backgroundColor: '#000080', // Dark blue progress color
//       },
//     }}
//   />
// </Box>

//       <Typography variant="caption" color="text.secondary">
//         16%
//       </Typography>
//     </Box>

//     {/* File List */}
//     {!collapsed && (
//       <Box mt={2} flex={1} overflow="auto" pr={1} sx={{scrollbarWidth:"none"}}>
//         {filesSample.map((file, index) => (
//           <Box key={index} mb={2}>
//             <Box display="flex" alignItems="center" gap={1}>
//               {getFileIcon(file.type)}
//               <Box flexGrow={1}>
//                 <Typography
//                   variant="body2"
//                   fontWeight={500}
//                   sx={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
//                 >
//                   {file.name}
//                 </Typography>
//                 <Typography variant="caption" color="text.secondary">
//                   {file.date} - {file.time} &nbsp; {file.uploaded} / {file.size}
//                 </Typography>
//               </Box>

//               {/* Circular Progress */}
//               <Box position="relative" display="inline-flex">
//                 <CircularProgress
//                   variant="determinate"
//                   value={file.progress}
//                   size={30}
//                   thickness={3}
//                   sx={{ color: '#000080' }}
//                 />
//                 <Box
//                   top={0}
//                   left={0}
//                   bottom={0}
//                   right={0}
//                   position="absolute"
//                   display="flex"
//                   alignItems="center"
//                   justifyContent="center"
//                 >
//                  <Typography
//   variant="caption"
//   fontWeight={500}
//   color="text.primary"
//   sx={{ fontSize: '0.65rem' }} // or try '10px', '0.6rem', etc.
// >
//   {file.progress}%
// </Typography>

//                 </Box>
//               </Box>
//             </Box>
//           </Box>
//         ))}
//       </Box>
//     )}
//   </Paper>
// </Grid>



//       </Grid>
//        {/* Buttons directly under upload list */}
//             <Box display="flex" justifyContent="flex-end" gap={2} mt={5} mr={3}>
//               <Button disableRipple
//                 sx={{ borderRadius: '20px', textTransform: 'none',padding:'6px 16px',color:"grey" }}
//               >
//                 Cancel
//               </Button>
//               <Button
//               disableRipple
//                 // sx={{
//                 //   backgroundColor: '#000080',
//                 //   color: 'white',
//                 //   borderRadius: '20px',
//                 //   textTransform: 'none',
//                 //   fontWeight: 500,
//                 //   padding:"6px 16px"
//                 // }}
//                  sx={{
//                   border: '1px solid #000080',
//                   color: '#000080',
//                   borderRadius: '20px',
//                   textTransform: 'none',
//                   // fontWeight: 500,
//                   padding:"1px 28px",
//                    '&:hover': {
//       borderColor: '#000080',
//       color: '#000080',
//       backgroundColor: 'transparent', // Prevent background color change
//     },
//                 }}
//               >
//                 Create
//               </Button>
//             </Box>
//     </Box>
//     </Drawer>
//   );
// };

// export default GenAIUploader;




// import React, { useState, useRef } from 'react';
// import {
//   Box,
//   Button,
//   Typography,
//   TextField,
//   MenuItem,
//   IconButton,
//   InputAdornment,
//   LinearProgress,
//   Paper,
//   Grid,
//   Drawer,
//   Avatar,
//   Divider,
//   CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions
// } from '@mui/material';
// import {
//   CloudUpload,
//   CalendarToday,
//   ExpandLess,
//   ExpandMore,
//   InsertDriveFile,
// } from '@mui/icons-material';
// import CloseIcon from "@mui/icons-material/Close";
// import CheckIcon from "@mui/icons-material/Check"
// import { adminAxios } from '../../asessts/axios/index';
// import DocumentIcon from "./../../asessts/images/documenticon.png";
// import Cloudicon from "./../../asessts/images/cloudicon.png";
// import Choosefileicon from "./../../asessts/images/choosefile.png";
// import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
// import ImageIcon from '@mui/icons-material/Image';
// import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
// // import CircularProgress from '@mui/material';

// const fileIcons = {
//   pdf: <PictureAsPdfIcon sx={{ color: '#f44336' }} />,
//   png: <ImageIcon sx={{ color: '#2196f3' }} />,
//   jpg: <ImageIcon sx={{ color: '#4caf50' }} />,
//   default: <InsertDriveFile sx={{ color: '#757575' }} />,
// };

// const filesSample = [
//   { name: 'GenAI_Request_Response_Examples', size: '3.6 MB', uploaded: '2.5 MB', type: 'pdf', progress: 72, date: '2 Apr,2025', time: '11:25' },
//   { name: 'GenAI_Audit_Records', size: '5 MB', uploaded: '3 MB', type: 'jpg', progress: 60, date: '2 Apr,2025', time: '11:25' },
//   { name: 'GenAI_API_Integration_Guide', size: '4.5 MB', uploaded: '3 MB', type: 'png', progress: 67, date: '2 Apr,2025', time: '11:25' },
//   { name: 'GenAI_Security_Test_Log', size: '6 MB', uploaded: '4 MB', type: 'pdf', progress: 75, date: '2 Apr,2025', time: '11:25' },
//   { name: 'GenAI_Compliance_Checklist', size: '2.6 MB', uploaded: '2 MB', type: 'pdf', progress: 77, date: '2 Apr,2025', time: '11:25' },
//   { name: 'GenAI_Datashare_Validation', size: '3.3 MB', uploaded: '2.2 MB', type: 'jpg', progress: 66, date: '2 Apr,2025', time: '11:25' },
//   { name: 'GenAI_Audit_Records', size: '2 MB', uploaded: '1.5 MB', type: 'png', progress: 80, date: '2 Apr,2025', time: '11:25' },
// ];
// const GenAIUploader = ({ open, onClose, fetchDocuments }) => {
//   const [dataSpace, setDataSpace] = useState('');
//   const [uploadBy, setUploadBy] = useState('');
//   const [dataSpacePath, setDataSpacePath] = useState('');
//   const [file, setFile] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [modalOpen, setModalOpen] = useState(false);
//   const [responseData, setResponseData] = useState(null);
//   const [collapsed, setCollapsed] = useState(true);
//   const [uploading, setUploading] = useState(false);
//   const [progress, setProgress] = useState(0);
//   const [dataSpaceName, setDataSpaceName] = useState("");
//   const [dataSpaceDescription, setDataSpaceDescription] = useState("");
//   const [category, setCategory] = useState("");
//   const [subCategory, setSubCategory] = useState("");
//   const [uploadCompleted, setUploadCompleted] = useState(false);
//   const [uploadProgress, setUploadProgress] = useState([]);
//   const [errorMessage, setErrorMessage] = useState('');
//   const fileInputRef = useRef(null);
//   const StyledMenuProps = {
//     PaperProps: {
//       sx: {
//         borderRadius: '16px', // Rounded corners for the dropdown card
//       },
//     },
//   };

//   const getFileIcon = (type) => fileIcons[type] || fileIcons.default;
//   const handleUpload = async (selectedFile) => {
//     if (!selectedFile) {
//       alert("Please select a file to upload.");
//       return;
//     }

//     setLoading(true); // Show loader on Create button

//     const formData = new FormData();
//     formData.append("data_space_name", dataSpaceName);
//     formData.append("data_space_description", dataSpaceDescription);
//     formData.append("category", category);
//     formData.append("sub_category", subCategory);
//     formData.append("files", selectedFile);

//     try {
//       const response = await adminAxios.post("/api/v1/data-spaces/create-and-upload/", formData, {
//         onUploadProgress: (progressEvent) => {
//           let percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
//           if (percent >= 100) percent = 95;
//           setProgress(percent); // You can optionally show this
//         },
//       });

//       if (response.status === 200 || response.status === 201) {
//         setProgress(100);
//         setUploadCompleted(true);
//         setResponseData(response.data); // store response
//         setModalOpen(true);             // show modal
//       }
//     } catch (error) {
//       console.error("Upload failed:", error);
//       const serverMessage = error?.response?.data?.detail || "An error occurred during file upload.";
//       setErrorMessage(serverMessage);       // Set the error message
//       setModalOpen(true);                   // Still show the dialog
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleModalClose = () => {
//     onClose();
//     setDataSpaceName('');
//     setDataSpaceDescription('');
//     setCategory('');
//     setSubCategory('');
//     setFile(null);
//     setProgress(0);
//     setUploadProgress([]);
//     setModalOpen(false);
//   };

//   const handleModalExited = () => {
//     setErrorMessage('');
//     onClose();
//     setFile(null);
//     setProgress(0);
//     setUploadProgress([]);
//     setUploadCompleted(false);
//     if (!errorMessage && fetchDocuments) {
//       fetchDocuments();
//     }
//   };


//   const triggerSimulatedProgress = (selectedFile) => {
//     const type = selectedFile.name.split('.').pop().toLowerCase();
//     const newFile = {
//       name: selectedFile.name,
//       size: `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`,
//       uploaded: `0 MB`,
//       type: ['jpg', 'jpeg', 'png', 'pdf'].includes(type) ? type : 'default',
//       progress: 0,
//     };

//     setCollapsed(false);
//     setUploadProgress(prev => [...prev, newFile]);

//     const interval = setInterval(() => {
//       setUploadProgress(prevFiles =>
//         prevFiles.map(file => {
//           if (file.name === newFile.name && file.progress < 100) {
//             const updatedProgress = Math.min(file.progress + 10, 100);
//             const updatedUploaded = ((parseFloat(file.size) * updatedProgress) / 100).toFixed(1);
//             return {
//               ...file,
//               progress: updatedProgress,
//               uploaded: `${updatedUploaded} MB`,
//             };
//           }
//           return file;
//         })
//       );
//     }, 500);

//     setTimeout(() => clearInterval(interval), 5000);
//   };
//   const handleCancel = () => {

//     // Reset all state variables

//     setDataSpaceName('');

//     setDataSpaceDescription('');

//     setCategory('');

//     setSubCategory('');


//     setFile(null);

//     setUploadProgress([]);

//     setProgress(0);

//     setUploadCompleted(false);

//     setCollapsed(true);

//     // Close the drawer

//     onClose();

//   };

//   const inputStyle = {
//     '& .MuiOutlinedInput-root': {
//       borderRadius: '12px',
//       minHeight: '36px',
//       fontSize: '13px', // input text size
//     },
//     '& .MuiInputBase-input': {
//       padding: '12px 12px',
//       fontSize: '13px', // input text size
//     },
//     '& .MuiInputLabel-root': {
//       fontSize: '14px', // label size
//     },
//   };

//   return (
//     <Drawer
//       anchor="right"
//       open={open}
//       onClose={onClose}
//       transitionDuration={{ enter: 1000, exit: 1000 }}
//       PaperProps={{
//         sx: {
//           width: '60%',
//           height: "92%",
//           borderRadius: '20px 0px 0px 20px',
//           transition: "transform 2s ease-in-out",
//           transform: "translate(50%, 0%)",
//           padding: "0px 32px",
//           mt: '64px',
//           overflow: "auto",
//           scrollbarWidth: "thin",
//           overflowX: "hidden"
//         },
//       }}
//     >
//       <Box sx={{ fontFamily: 'sans-serif', width: '100%', maxWidth: '900px', p: 2 }}>
//         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
//           <Typography variant="h5" fontWeight={700}>
//             New DataSpace
//           </Typography>
//           <IconButton onClick={handleCancel}  >
//             <CloseIcon />
//           </IconButton>
//         </Box>

//         <Box display="flex" gap={3} mb={3}>
//           {/* Left side - 3 fields */}
//           <Box flex={1} display="flex" flexDirection="column" gap={2}>
//             <TextField
//               label="Dataspace Name"
//               variant="outlined"
//               fullWidth
//               size="small"
//               value={dataSpaceName}
//               onChange={(e) => setDataSpaceName(e.target.value)}
//               sx={inputStyle}
//             />
//             <TextField
//               label="Category"
//               variant="outlined"
//               fullWidth
//               size="small"
//               value={category}
//               onChange={(e) => setCategory(e.target.value)}
//               sx={inputStyle}
//             /><TextField
//               label="Subcategory"
//               variant="outlined"
//               fullWidth
//               size="small"
//               value={subCategory}
//               onChange={(e) => setSubCategory(e.target.value)}
//               sx={inputStyle}
//             />
//           </Box>

//           {/* Right side - Description input field */}
//           <Box flex={1}>
//             <TextField
//               label="Description"
//               variant="outlined"
//               fullWidth
//               multiline
//               minRows={8} // sets initial visible rows
//               maxRows={9} // optional: limits expansion
//               value={dataSpaceDescription}
//               onChange={(e) => setDataSpaceDescription(e.target.value)}
//               sx={{
//                 '& .MuiOutlinedInput-root': {
//                   borderRadius: '12px',
//                   fontSize: '13px',
//                   padding: '8px 12px',
//                 },
//                 '& textarea': {
//                   fontSize: '13px',
//                   maxHeight: '125px',
//                   overflowY: 'auto',
//                   scrollbarWidth: 'thin',
//                 },
//                 '& .MuiInputLabel-root': {
//                   fontSize: '14px',
//                 },
//                 // Optional Webkit scrollbar styles for better appearance
//                 '& textarea::-webkit-scrollbar': {
//                   width: '6px',
//                 },
//                 '& textarea::-webkit-scrollbar-thumb': {
//                   backgroundColor: '#ccc',
//                   borderRadius: '4px',
//                 },
//               }}
//             />
//           </Box>

//         </Box>


//         {/* Main Content: Upload Area + Progress */}
//         <Box sx={{
//           display: 'flex',
//           flexWrap: 'wrap',  // allow wrapping if absolutely necessary
//           gap: 2,
//           justifyContent: 'space-between'
//         }}>  {/* Upload Area */}
//           <Paper
//             sx={{
//               border: '2px dashed #D9D9D9',
//               p: 2,
//               textAlign: 'center',
//               borderRadius: '16px',
//               minHeight: 280,
//               minWidth: 220, // minimum width allowed
//               flex: '1 1 0',  // shrink and grow equally
//               display: 'flex',
//               flexDirection: 'column',
//               justifyContent: 'center',
//               alignItems: 'center',
//               gap: 2,
//               boxShadow: 'none'
//             }}
//           >
//             <img
//               src={Cloudicon}
//               alt="Upload"
//               style={{ width: 50, height: 50, marginBottom: '8px' }}
//             />

//             <Typography fontWeight={500} fontSize="16px" color="#494949">
//               Choose a file{' '}
//               {/* <Typography component="span" fontWeight={500} color="#494949">
//         (or) Drag & drop it here
//       </Typography> */}
//             </Typography>

//             <Box display="flex" alignItems="center" gap={0.5} mb={2} mt={0}>
//               <InfoOutlinedIcon fontSize="small" color="disabled" />
//               <Typography variant="body2" color="#666">
//                 Supported file types:  PDF  Max size is 10 MB
//               </Typography>
//             </Box>

//             {/* Upload Button */}
//             <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
//               {!uploading && !file && (
//                 <>
//                   <Box onClick={() => document.getElementById('fileInput').click()}>
//                     <Button
//                       sx={{
//                         mt: 2,
//                         backgroundColor: '#000080',
//                         color: '#fff',
//                         padding: '6px 16px',
//                         fontSize: '14px',
//                         borderRadius: '30px',
//                         textTransform: 'none',
//                         boxShadow: 'none',
//                         display: 'flex',
//                         alignItems: 'center',
//                         gap: '8px',
//                         '&:hover': {
//                           backgroundColor: '#000080'
//                         }
//                       }}
//                     >
//                       <img
//                         src={Choosefileicon}
//                         alt="icon"
//                         style={{ width: 20, height: 20 }}
//                       />
//                       Choose file
//                     </Button>
//                   </Box>

//                   {/* Hidden File Input */}
//                   <input
//                     type="file"
//                     id="fileInput"
//                     style={{ display: 'none' }}
//                     accept=".jpg,.jpeg,.png,.pdf"
//                     onChange={(e) => {
//                       const selectedFile = e.target.files[0];
//                       if (selectedFile) {
//                         setFile(selectedFile);
//                         triggerSimulatedProgress(selectedFile);
//                       }
//                     }}
//                   />
//                 </>
//               )}
//             </Box>
//           </Paper>

//           {/* Upload Progress Section */}
//           <Box
//             sx={{
//               padding: '10px 15px',
//               borderRadius: 3,
//               maxHeight: collapsed ? 40 : 'auto', // Collapsed = small height
//               minWidth: 220,  // match upload box
//               flex: '1 1 0',  // shrink and grow equally
//               display: 'flex',
//               flexDirection: 'column',
//               bgcolor: '#fff',
//               border: '1px solid #EBEBEB'
//             }}
//           >
//             <Box display="flex" justifyContent="space-between" alignItems="center">
//               <Typography fontWeight={600} fontSize="16px">
//                 Uploading Progress
//               </Typography>
//               <IconButton
//                 onClick={() => {
//                   if (file) setCollapsed(!collapsed);
//                 }}
//                 disabled={!file}
//                 size="small"
//                 sx={{ color: file ? 'inherit' : '#ccc' }}
//               >
//                 {collapsed ? <ExpandMore /> : <ExpandLess />}
//               </IconButton>
//             </Box>

//             {!collapsed && (
//               <Box mt={2} flex={1} overflow="auto" sx={{ padding: '0 10px' }}>
//                 {uploadProgress.map((file, index) => (
//                   <Box key={index} mb={1.5}>
//                     <Box display="flex" alignItems="center" gap={1} mb={0.5}>
//                       {getFileIcon(file.type)}
//                       <Box flexGrow={1}>
//                         <Typography
//                           variant="body2"
//                           fontWeight={600}
//                           sx={{
//                             whiteSpace: 'nowrap',
//                             overflow: 'hidden',
//                             textOverflow: 'ellipsis'
//                           }}
//                         >
//                           {file.name}
//                         </Typography>
//                         <Typography variant="caption" color="text.secondary">
//                           {file.uploaded} / {file.size}
//                         </Typography>
//                       </Box>
//                       {/* Circular Progress */}
//                       <Box position="relative" display="inline-flex">
//                         <CircularProgress
//                           variant="determinate"
//                           value={file.progress}
//                           size={30}
//                           thickness={3}
//                           sx={{ color: '#000080' }}
//                         />
//                         <Box
//                           top={0}
//                           left={0}
//                           bottom={0}
//                           right={0}
//                           position="absolute"
//                           display="flex"
//                           alignItems="center"
//                           justifyContent="center"
//                         >
//                           <Typography
//                             variant="caption"
//                             fontWeight={500}
//                             color="text.primary"
//                             sx={{ fontSize: '0.65rem' }} // or try '10px', '0.6rem', etc.
//                           >
//                             {file.progress}%
//                           </Typography>

//                         </Box>
//                       </Box>
//                     </Box>
//                     <LinearProgress
//                       variant="determinate"
//                       value={file.progress}
//                       sx={{
//                         height: 5,
//                         borderRadius: 5,
//                         backgroundColor: '#eee',
//                         '& .MuiLinearProgress-bar': {
//                           borderRadius: 5,
//                           backgroundColor: '#000080'
//                         }
//                       }}
//                     />
//                   </Box>
//                 ))}
//               </Box>
//             )}
//           </Box>
//         </Box>

//         {/* Buttons directly under upload list */}
//         <Box display="flex" justifyContent="flex-end" gap={2} mt={5} mr={3}>
//           <Button disableRipple
//             onClick={handleCancel}
//             sx={{ borderRadius: '20px', textTransform: 'none', padding: '6px 16px', color: "grey" }}
//           >
//             Cancel
//           </Button>
//           <Button
//             onClick={() => handleUpload(file)}
//             disabled={
//               loading ||
//               !file ||
//               uploadProgress.some((file) => file.progress < 100)
//             }                // sx={{
//             //   backgroundColor: '#000080',
//             //   color: 'white',
//             //   borderRadius: '20px',
//             //   textTransform: 'none',
//             //   fontWeight: 500,
//             //   padding:"6px 16px"
//             // }}
//             sx={{
//               border: '1px solid #000080',
//               color: '#000080',
//               borderRadius: '20px',
//               textTransform: 'none',
//               padding: '1px 28px',
//               '&:hover': {
//                 borderColor: '#000080',
//                 color: '#000080',
//                 backgroundColor: 'transparent',
//               },
//               '&.Mui-disabled': {
//                 border: 'none',
//                 color: 'grey',
//                 backgroundColor: '#f5f5f5', // optional: light background to show it's disabled
//               },
//             }}
//           >
//             Create
//             {loading && (
//               <CircularProgress size={16} sx={{ color: "#000080" }} />
//             )}              </Button>
//         </Box>
//       </Box>
//       <Dialog
//         open={modalOpen}
//         onClose={handleModalClose}
//         onExited={handleModalExited} // cleanup AFTER animation
//         PaperProps={{
//           sx: {
//             width: '400px',        // Adjust width as needed (e.g. 400px, 500px)
//             maxWidth: '90vw',      // Optional: responsive on smaller screens
//             borderRadius: 2,       // Optional: rounded corners
//             padding: 2             // Optional: inner padding
//           }
//         }}
//       >
//         <DialogTitle sx={{ fontWeight: 'bold' }}>
//           <Box display="flex" alignItems="center" gap={1} mb={2}>
//             <Box
//               sx={{
//                 width: 32,
//                 height: 32,
//                 backgroundColor: errorMessage ? "#f44336" : "#4caf50", // red for error, green for success
//                 borderRadius: "50%",
//                 display: "flex",
//                 alignItems: "center",
//                 justifyContent: "center",
//               }}
//             >
//               <CheckIcon sx={{ color: "white", fontSize: 20 }} />
//             </Box>
//             <Typography variant="h5" fontWeight={600} color={errorMessage ? "#f44336" : "#4caf50"}>
//               {errorMessage ? "Upload Failed" : "Upload Successful"}
//             </Typography>
//           </Box>
//         </DialogTitle>
//         <DialogContent sx={{ ml: "20px", mt: 1 }}>
//           {errorMessage ? (
//             <Typography mt={0} fontSize="15px" color="text.secondary">
//               {errorMessage}
//             </Typography>
//           ) : (
//             file?.name && (
//               <Typography mt={0} fontSize="16px" color="text.secondary">
//                 <strong>File:</strong> {file.name}
//               </Typography>
//             )
//           )}
//         </DialogContent>
//         <DialogActions>
//           <Button
//             variant="outlined"
//             onClick={handleModalClose}
//             sx={{
//               backgroundColor: "#000080",
//               color: "white",
//               "&.Mui-disabled": {
//                 color: "white",
//                 backgroundColor: "#000080",
//                 opacity: 0.6,
//               },
//             }}
//           >
//             OK
//           </Button>
//         </DialogActions>

//       </Dialog>

//     </Drawer>
//   );
// };

// export default GenAIUploader;



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
            // sx={{
            //   backgroundColor: '#000080',
            //   color: 'white',
            //   borderRadius: '20px',
            //   textTransform: 'none',
            //   fontWeight: 500,
            //   padding:"6px 16px"
            // }}
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
