// import React, { useState } from 'react';
// import './../../asessts/css/History.css'; // CSS must be created separately
// import { IconButton } from '@mui/material';
// import arrowUp from './../../asessts/images/arrowupicon.png';
// import arrowDown from './../../asessts/images/arrowupicon.png';
// import CloseIcon from '@mui/icons-material/Close';
// import ExpandLessIcon from '@mui/icons-material/ExpandLess';
// import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

// const History = ({ onClose, onSelectDoc }) => {
//   const [showToday, setShowToday] = useState(true);
//   const [showYesterday, setShowYesterday] = useState(true);
//   const [activeDoc, setActiveDoc] = useState('');

//   const todayDocs = [
//     'GenAI_Documentation',
//     'GenAI_Application_Guide',
//     'GenAI_Platform_Docs',
//     'GenAI_DeveloperDocs',
//     'GenAI_Functional_Test_Plan',
//     'GenAI_Script_Validation_Sheet',
//   ];

//   const yesterdayDocs = [
//     'GenAI_Documentation',
//     'GenAI_Application_Guide',
//     'GenAI_Platform_Docs',
//     'GenAI_DeveloperDocs',
//     'GenAI_Functional_Test_Plan',
//   ];

//   const renderDocs = (docs) =>
//     docs.map((doc) => (
//       <div
//   key={doc}
//   className={`history-document ${activeDoc === doc ? 'active' : ''}`}
//   onClick={() => {
//     setActiveDoc(doc);
//     onSelectDoc(doc); // Notify parent
//   }}
// >
//         {doc}
//       </div>
//     ));

//   return (
//     <div>
//      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
//         <IconButton onClick={onClose}>
//             <CloseIcon />
//           </IconButton>
//       </div>
//     <div className="history-container">
//       {/* Today Section */}
//       <div className="history-section">
//         <div className="history-header" onClick={() => setShowToday(!showToday)}>
//           <span className="section-title">Today</span>
// {showToday ? (
//   <ExpandLessIcon sx={{ fontSize: 20, color: '#555' }} />
// ) : (
//   <ExpandMoreIcon sx={{ fontSize: 20, color: '#555' }} />
// )}
//        </div>
//         {showToday && <div className="history-docs">{renderDocs(todayDocs)}</div>}
//       </div>

//       {/* Yesterday Section */}
//       <div className="history-section">
//         <div className="history-header" onClick={() => setShowYesterday(!showYesterday)}>
//           <span className="section-title">Yesterday</span>
//  {showYesterday ? (
//   <ExpandLessIcon sx={{ fontSize: 20, color: '#555' }} />
// ) : (
//   <ExpandMoreIcon sx={{ fontSize: 20, color: '#555' }} />
// )}       </div>
//         {showYesterday && <div className="history-docs">{renderDocs(yesterdayDocs)}</div>}
//       </div>
//     </div>
//        </div> 
//   );
// };

// export default History;





// import React, { useState } from 'react';
// import './../../asessts/css/History.css';
// import {
//   IconButton,
//   Box,
//   Button,
//   TextField,
// } from '@mui/material';
// import CloseIcon from '@mui/icons-material/Close';
// import ExpandLessIcon from '@mui/icons-material/ExpandLess';
// import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
// import { DatePicker } from '@mui/x-date-pickers/DatePicker';
// import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
// import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
// import dayjs from 'dayjs';


// const History = ({ onClose, onSelectDoc }) => {
//   const [showToday, setShowToday] = useState(true);
//   const [showYesterday, setShowYesterday] = useState(true);
//   const [activeDoc, setActiveDoc] = useState('');
//   const [fromDate, setFromDate] = useState(dayjs().subtract(7, 'day'));
//   const [toDate, setToDate] = useState(dayjs());

//   const todayDocs = [
//     'GenAI_Documentation',
//     'GenAI_Application_Guide',
//     'GenAI_Platform_Docs',
//     'GenAI_DeveloperDocs',
//     'GenAI_Functional_Test_Plan',
//     'GenAI_Script_Validation_Sheet',
//   ];

//   const yesterdayDocs = [
//     'GenAI_Documentation',
//     'GenAI_Application_Guide',
//     'GenAI_Platform_Docs',
//     'GenAI_DeveloperDocs',
//     'GenAI_Functional_Test_Plan',
//   ];

//   const renderDocs = (docs) =>
//     docs.map((doc) => (
//       <div
//         key={doc}
//         className={`history-document ${activeDoc === doc ? 'active' : ''}`}
//         onClick={() => {
//           setActiveDoc(doc);
//           onSelectDoc(doc);
//         }}
//       >
//         {doc}
//       </div>
//     ));

//   const handleApply = () => {
//     console.log("Filtering from:", fromDate.format('YYYY-MM-DD'), "to:", toDate.format('YYYY-MM-DD'));
//     // Add your actual filtering logic or API call here
//   };

//   return (
//     <Box sx={{width:"100%"}}>
//       {/* ❌ Close Button */}
//       <Box display="flex" justifyContent="flex-end" pr={2}>
//         <IconButton onClick={onClose}>
//           <CloseIcon />
//         </IconButton>
//       </Box>
//   {/* 📅 Date Range Section - Moved to Top */}
// <LocalizationProvider dateAdapter={AdapterDayjs}>
//   <Box
//     display="flex"
//     justifyContent="space-between"
//     alignItems="center"
//     p={2}
//   >
//     {/* Left Side: From and To Pickers */}
//     <Box display="flex" gap={2}>
//       <DatePicker
//   label="From"
//   value={fromDate}
//   onChange={(newValue) => setFromDate(newValue)}
//   slotProps={{
//     textField: {
//       size: 'small',
//       sx: {
//         '& .MuiInputBase-root': {
//           height: 36, // ⬅️ Set desired height
//           fontSize: 13
//         },
//       },
//     },
//   }}
// />

// <DatePicker
//   label="To"
//   value={toDate}
//   onChange={(newValue) => setToDate(newValue)}
//   slotProps={{
//     textField: {
//       size: 'small',
//       sx: {
//         '& .MuiInputBase-root': {
//           height: 36, // ⬅️ Match the height
//           fontSize: 13
//         },
//       },
//     },
//   }}
// />

//     </Box>

//     {/* Right Side: Apply Button */}
//     <Button
//       variant="contained"
//       size="small"
//       sx={{ backgroundColor: '#000080', textTransform: 'none' }}
//       onClick={handleApply}
//     >
//       Apply
//     </Button>
//   </Box>
// </LocalizationProvider>
//       {/* 📄 Document Sections */}
//       <div className="history-container">
//         <div className="history-section">
//           <div className="history-header" onClick={() => setShowToday(!showToday)}>
//             <span className="section-title">Today</span>
//             {showToday ? (
//               <ExpandLessIcon sx={{ fontSize: 20, color: '#555' }} />
//             ) : (
//               <ExpandMoreIcon sx={{ fontSize: 20, color: '#555' }} />
//             )}
//           </div>
//           {showToday && <div className="history-docs">{renderDocs(todayDocs)}</div>}
//         </div>

//         <div className="history-section">
//           <div className="history-header" onClick={() => setShowYesterday(!showYesterday)}>
//             <span className="section-title">Yesterday</span>
//             {showYesterday ? (
//               <ExpandLessIcon sx={{ fontSize: 20, color: '#555' }} />
//             ) : (
//               <ExpandMoreIcon sx={{ fontSize: 20, color: '#555' }} />
//             )}
//           </div>
//           {showYesterday && <div className="history-docs">{renderDocs(yesterdayDocs)}</div>}
//         </div>
//       </div>
//     </Box>
//   );
// };

// export default History;



import React from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const History = ({ onClose }) => {
  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* ❌ Close Button */}
      <Box position="absolute" top={8} right={8}>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* 📭 Centered Message */}
      <Box
        height="100%"
        display="flex"
        justifyContent="center"
        alignItems="center"
        textAlign="center"
      >
        <Typography variant="h6" fontWeight={600} color="text.secondary">
          No history available
        </Typography>
      </Box>
    </Box>
  );
};

export default History;
