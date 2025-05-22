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
  Drawer,
  Avatar,
  Divider,
  CircularProgress,Dialog,DialogTitle,DialogContent,DialogActions
} from '@mui/material';
import {
  CloudUpload,
  CalendarToday,
  ExpandLess,
  ExpandMore,
  InsertDriveFile,
} from '@mui/icons-material';
import CloseIcon from "@mui/icons-material/Close";
import CheckIcon from "@mui/icons-material/Check"
import {adminAxios} from '../../asessts/axios/index';
import DocumentIcon from "./../../asessts/images/documenticon.png";
import Cloudicon from "./../../asessts/images/cloudicon.png";
import Choosefileicon from "./../../asessts/images/choosefile.png";
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ImageIcon from '@mui/icons-material/Image';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
// import CircularProgress from '@mui/material';

const fileIcons = {
  pdf: <PictureAsPdfIcon sx={{ color: '#f44336' }} />,
  png: <ImageIcon sx={{ color: '#2196f3' }} />,
  jpg: <ImageIcon sx={{ color: '#4caf50' }} />,
  default: <InsertDriveFile sx={{ color: '#757575' }} />,
};

const filesSample = [
  { name: 'GenAI_Request_Response_Examples', size: '3.6 MB', uploaded: '2.5 MB', type: 'pdf', progress: 72,date:'2 Apr,2025',time:'11:25' },
  { name: 'GenAI_Audit_Records', size: '5 MB', uploaded: '3 MB', type: 'jpg', progress: 60,date:'2 Apr,2025',time:'11:25' },
  { name: 'GenAI_API_Integration_Guide', size: '4.5 MB', uploaded: '3 MB', type: 'png', progress: 67,date:'2 Apr,2025',time:'11:25' },
  { name: 'GenAI_Security_Test_Log', size: '6 MB', uploaded: '4 MB', type: 'pdf', progress: 75,date:'2 Apr,2025',time:'11:25' },
  { name: 'GenAI_Compliance_Checklist', size: '2.6 MB', uploaded: '2 MB', type: 'pdf', progress: 77,date:'2 Apr,2025',time:'11:25' },
  { name: 'GenAI_Datashare_Validation', size: '3.3 MB', uploaded: '2.2 MB', type: 'jpg', progress: 66,date:'2 Apr,2025',time:'11:25' },
  { name: 'GenAI_Audit_Records', size: '2 MB', uploaded: '1.5 MB', type: 'png', progress: 80,date:'2 Apr,2025',time:'11:25' },
];
const GenAIUploader = ({open, onClose,fetchDocuments}) => {
  const [dataSpace, setDataSpace] = useState('');
const [uploadBy, setUploadBy] = useState('');
const [dataSpacePath, setDataSpacePath] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
const [modalOpen, setModalOpen] = useState(false);
const [responseData, setResponseData] = useState(null);
  const [collapsed, setCollapsed] = useState(true);
   const [uploading, setUploading] = useState(false);
   const [progress, setProgress] = useState(0);
     const [uploadCompleted, setUploadCompleted] = useState(false);
const [uploadProgress, setUploadProgress] = useState([]);
const fileInputRef = useRef(null);
const StyledMenuProps = {
  PaperProps: {
    sx: {
      borderRadius: '16px', // Rounded corners for the dropdown card
    },
  },
};

  const getFileIcon = (type) => fileIcons[type] || fileIcons.default;
const handleUpload = async (selectedFile) => {
  if (!selectedFile) {
    alert("Please select a file to upload.");
    return;
  }

  setLoading(true); // Show loader on Create button

  const formData = new FormData();
  formData.append("file", selectedFile);
 formData.append("data_space", dataSpace);
  formData.append("upload_by", uploadBy);
  formData.append("data_space_path", dataSpacePath);

  try {
    const response = await adminAxios.post("/upload_document/", formData, {
      onUploadProgress: (progressEvent) => {
        let percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (percent >= 100) percent = 95;
        setProgress(percent); // You can optionally show this
      },
    });

    if (response.status === 200) {
      setProgress(100);
      setUploadCompleted(true);
      setResponseData(response.data); // store response
      setModalOpen(true);             // show modal
    }
  } catch (error) {
    console.error("Upload failed:", error);
    alert("An error occurred during file upload.");
  } finally {
    setLoading(false);
  }
};


const triggerSimulatedProgress = (selectedFile) => {
  const type = selectedFile.name.split('.').pop().toLowerCase();
  const newFile = {
    name: selectedFile.name,
    size: `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`,
    uploaded: `0 MB`,
    type: ['jpg', 'jpeg', 'png', 'pdf'].includes(type) ? type : 'default',
    progress: 0,
  };

  setCollapsed(false);
  setUploadProgress(prev => [...prev, newFile]);

  const interval = setInterval(() => {
    setUploadProgress(prevFiles =>
      prevFiles.map(file => {
        if (file.name === newFile.name && file.progress < 100) {
          const updatedProgress = Math.min(file.progress + 10, 100);
          const updatedUploaded = ((parseFloat(file.size) * updatedProgress) / 100).toFixed(1);
          return {
            ...file,
            progress: updatedProgress,
            uploaded: `${updatedUploaded} MB`,
          };
        }
        return file;
      })
    );
  }, 500);

  setTimeout(() => clearInterval(interval), 5000);
};

  return (
     <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
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
          scrollbarWidth:"thin",
        overflowX:"hidden"        },
      }}
    >
    <Box sx={{  fontFamily: 'sans-serif',width:'100%',maxWidth:'900px',p:4 }}>
     <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
  <Typography variant="h5" fontWeight={700}>
    GenAI_Documentation_Overview
  </Typography>
  <IconButton onClick={onClose} >
    <CloseIcon />
  </IconButton>
</Box>

      {/* Form with Starting Icon */}
  <Box display="flex" alignItems="flex-start" gap={4} mb={4} >
  {/* Avatar on the left */}
  <Avatar
  variant="rounded"
  src={DocumentIcon}
  alt="Document Thumbnail"
  sx={{
    bgcolor: '#f5f5f5',
    width: 56,
    height: 56,
    borderRadius: "12px",
    mt: { xs: 0, md: '10px' },
    objectFit: 'cover',
    padding:"10px",
  }}
/>

  <Box flex={1}>
  <Grid container spacing={2}>
    {/* Row 1: full-width Data Space */}
  <Grid item xs={12}>
  <TextField
  value={dataSpace}
  onChange={(e) => setDataSpace(e.target.value)}
  variant="outlined"
  label="Data Space"
  sx={{ width: 750 }}
  InputProps={{
    sx: {
      borderRadius: '20px',
      height: 45,
      fontSize: 14,
      padding: '0 10px',
      '& .MuiOutlinedInput-input': {
        padding: '8px 12px',
      }
    }
  }}
  InputLabelProps={{ sx: { fontSize: 14 } }}
/>
</Grid>




    {/* Row 2: three fields side-by-side */}
   <Grid container spacing={2}>
  <Grid item xs={12} md={3}>
  <TextField
  value={uploadBy}
  onChange={(e) => setUploadBy(e.target.value)}
  fullWidth
  variant="outlined"
  label="Upload by"
  sx={{ width: 365 }}
  InputProps={{
    sx: {
      borderRadius: '20px',
      height: 45,
      '& .MuiOutlinedInput-input': {
        padding: '8px 12px',
        fontSize: 14,
      },
    },
  }}
  InputLabelProps={{ sx: { fontSize: 14 } }}
/>
</Grid>

<Grid item xs={12} md={6}>
  <TextField
  select
  label="Data space path"
  value={dataSpacePath}
  onChange={(e) => setDataSpacePath(e.target.value)} // <-- Important!
  sx={{ width: 365 }}
  SelectProps={{ MenuProps: StyledMenuProps }}
  InputProps={{
    sx: {
      borderRadius: '20px',
      height: 45,
      '& .MuiSelect-select': {
        padding: '8px 12px',
        fontSize: 14,
      },
    },
  }}
  InputLabelProps={{ sx: { fontSize: 14 } }}
>
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
    border: '2px dashed #D9D9D9',
    p: 4,
    textAlign: 'center',
    borderRadius: '16px',
    minHeight: 280,
    minWidth:300,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 2,
    boxShadow: 'none'
  }}
>

<img 
  src={Cloudicon} 
  alt="Upload" 
  style={{ width: 50, height: 50, marginBottom: '8px' }} 
/>

   <Typography fontWeight={500} fontSize="16px" color="#494949">
  Choose a file <Typography component="span" fontWeight={500} color='#494949'>(or) Drag & drop it here</Typography>
</Typography>

    <Box display="flex" alignItems="center" gap={0.5} mb={2} mt={0}>
      <InfoOutlinedIcon fontSize="small" color="disabled" />
      <Typography variant="body2" color="#666">
  Supported file types: JPG, PNG, PDF, Max size is 10 MB
</Typography>
    </Box>

<Box sx={{  display: "flex", flexDirection: "column", justifyContent: "center" }}>
 {!uploading && !file ? (  // ⬅️ hide button if uploading OR file is selected
 <>
  <Box
    onClick={() => document.getElementById("fileInput").click()}
  >

  <Button
  // variant="contained"
  sx={{
    mt: 2,
    backgroundColor: "#000080",
    color: "#fff",
    padding: "6px 16px",
    fontSize: "14px",
    borderRadius: "30px",
    textTransform: "none",
    boxShadow: "none",
    display: "flex",
    alignItems: "center",
    gap: "8px", // space between image and text
    '&:hover': {
      backgroundColor: "#000080"
    }
  }}
>
  <img
    src={Choosefileicon}
    alt="icon"
    style={{ width: 20, height: 20 }}
  />
  Choose file
</Button>


      </Box>

      {/* Hidden file input */}
     <input
  type="file"
  id="fileInput"
  style={{ display: "none" }}
  accept=".jpg,.jpeg,.png,.pdf"
  onChange={(e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile); // Store selected file
      triggerSimulatedProgress(selectedFile); // (Optional) Simulate progress UI
      // handleUpload(selectedFile); // 🔥 Call upload
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
  <Box
    sx={{
      padding:'10px 15px',
      borderRadius: 3,
      maxHeight: 335,
      minWidth: 360,
      display: 'flex',
      flexDirection: 'column',
      bgcolor: '#fff',
      border:"1px solid #EBEBEB"
    }}
  >
    {/* Header */}
    <Box display="flex" justifyContent="space-between" alignItems="center">
      <Typography fontWeight={600} fontSize="16px">
        Uploading Progress
      </Typography>
     <IconButton
  onClick={() => {
    if (file) setCollapsed(!collapsed); // only allow toggle if file is selected
  }}
  disabled={!file} // visually disables the button until a file is chosen
  size="small"
  sx={{
    color: file ? 'inherit' : '#ccc', // optional: change icon color when disabled
  }}
>
  {collapsed ? <ExpandMore /> : <ExpandLess />}
</IconButton>

    </Box>
 
    {/* Top Progress */}
    {/* <Box mt={0} display="flex" alignItems="center" gap={1} width={'200px'}>
      <Box flexGrow={1}>
  <LinearProgress
    variant="determinate"
    value={16}
    sx={{
      height: 6,
      borderRadius: 5,
      backgroundColor: '#eee',
      '& .MuiLinearProgress-bar': {
        borderRadius: 5,
        backgroundColor: '#000080', // Dark blue progress color
      },
    }}
  />
</Box>
 
      <Typography variant="caption" color="text.secondary">
        16%
      </Typography>
    </Box> */}
 
    {/* File List */}
    {!collapsed && (
              <Box mt={3} flex={1} overflow="auto" sx={{padding:"0px 15px"}}>
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
    <LinearProgress variant="determinate" value={file.progress} sx={{
      height: 6,
      borderRadius: 5,
      backgroundColor: '#eee',
      '& .MuiLinearProgress-bar': {
        borderRadius: 5,
        backgroundColor: '#000080', // Dark blue progress color
      },
    }}/>
  </Box>
))}

              </Box>
            )}
  </Box>
</Grid>
 


      </Grid>
       {/* Buttons directly under upload list */}
            <Box display="flex" justifyContent="flex-end" gap={2} mt={5} mr={3}>
              <Button disableRipple
                sx={{ borderRadius: '20px', textTransform: 'none',padding:'6px 16px',color:"grey" }}
              >
                Cancel
              </Button>
              <Button
onClick={() => handleUpload(file)}
disabled={
    loading || 
    !file || 
    uploadProgress.some((file) => file.progress < 100)
  }                // sx={{
                //   backgroundColor: '#000080',
                //   color: 'white',
                //   borderRadius: '20px',
                //   textTransform: 'none',
                //   fontWeight: 500,
                //   padding:"6px 16px"
                // }}
                 sx={{
    border: '1px solid #000080',
    color: '#000080',
    borderRadius: '20px',
    textTransform: 'none',
    padding: '1px 28px',
    '&:hover': {
      borderColor: '#000080',
      color: '#000080',
      backgroundColor: 'transparent',
    },
    '&.Mui-disabled': {
      border: 'none',
      color: 'grey',
      backgroundColor: '#f5f5f5', // optional: light background to show it's disabled
    },
  }}
              >
 Create
  {loading && (
    <CircularProgress size={16} sx={{ color: "#000080" }} />
  )}              </Button>
            </Box>
    </Box>
    <Dialog
  open={modalOpen}
  onClose={() => setModalOpen(false)}
  PaperProps={{
    sx: {
      width: '400px',        // Adjust width as needed (e.g. 400px, 500px)
      maxWidth: '90vw',      // Optional: responsive on smaller screens
      borderRadius: 2,       // Optional: rounded corners
      padding: 2             // Optional: inner padding
    }
  }}
>
  <DialogTitle sx={{ fontWeight: 'bold' }}><Box display="flex" alignItems="center" gap={1} mb={2}>
    <Box
      sx={{
        width: 32,
        height: 32,
        backgroundColor: "#4caf50", // green background
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <CheckIcon sx={{ color: "white", fontSize: 20 }} />
    </Box>
    <Typography variant="h5" fontWeight={600} color="#4caf50">
      Upload Successful
    </Typography>
  </Box></DialogTitle>
<DialogContent sx={{ ml: "20px", mt: 1 }}>
  {/* Success Row with Green Tick */}
  {/* <Box display="flex" alignItems="center" gap={1} mb={2}>
    <Box
      sx={{
        width: 32,
        height: 32,
        backgroundColor: "#4caf50", // green background
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <CheckIcon sx={{ color: "white", fontSize: 20 }} />
    </Box>
    <Typography variant="h6" fontWeight={600} color="#4caf50">
      Upload Successful
    </Typography>
  </Box> */}
  {/* Uploaded File Name */}
  {file?.name && (
    <Typography mt={0} fontSize="16px" color="text.secondary">
      <strong>File:</strong> {file.name}
    </Typography>
  )}
</DialogContent>
  <DialogActions>
    <Button
      variant="outlined"
 onClick={() => {
      setModalOpen(false);
          onClose();             // Close the drawer
      setFile(null);
      setProgress(0);
      setUploadProgress([]);
      setUploadCompleted(false);
      if (fetchDocuments) fetchDocuments(); // refresh document list
    }}     disabled={!uploadCompleted}
      sx={{
        backgroundColor: "#000080",
        color: "white",
        "&.Mui-disabled": {
          color: "white",
          backgroundColor: "#000080",
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
