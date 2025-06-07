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




// import React, { useState, useEffect } from 'react';
// import './../../asessts/css/History.css';
// import {
//   IconButton,
//   Box,
// } from '@mui/material';
// import CloseIcon from '@mui/icons-material/Close';
// import ExpandLessIcon from '@mui/icons-material/ExpandLess';
// import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
// import { adminAxios } from '../../asessts/axios';
// import dayjs from 'dayjs';

// const History = ({ onClose, onSelectDoc }) => {
//   const [showToday, setShowToday] = useState(true);
//   const [showYesterday, setShowYesterday] = useState(true);
//   const [showPrevious, setShowPrevious] = useState(true);
//   const [activeDoc, setActiveDoc] = useState('');
//   const [todayDocs, setTodayDocs] = useState([]);
//   const [yesterdayDocs, setYesterdayDocs] = useState([]);
//   const [previousWeekDocs, setPreviousWeekDocs] = useState([]);

// useEffect(() => {
//   const fetchHistoryDocs = async () => {
//     try {
//       const token = localStorage.getItem("token");

//       const res = await adminAxios.get('/api/v1/history/summary', {
//         headers: {
//           Authorization: `Bearer ${token}`
//         }
//       });

//       const allDocs = res.data.history || [];

//       const today = dayjs().startOf('day');
//       const yesterday = today.subtract(1, 'day');
//       const weekAgo = today.subtract(7, 'day');

//       const todayList = [];
//       const yesterdayList = [];
//       const last7DaysList = [];

//       allDocs.forEach(doc => {
//         const docDate = dayjs(doc.generated_at).startOf('day');
//         const docObj = {
//           id: doc.document_id,
//           name: doc.document_name,
//           date: docDate.format('YYYY-MM-DD')
//         };

//         if (docDate.isSame(today)) {
//           todayList.push(docObj);
//         } else if (docDate.isSame(yesterday)) {
//           yesterdayList.push(docObj);
//         } else if (docDate.isAfter(weekAgo)) {
//           last7DaysList.push(docObj);
//         }
//       });

//       setTodayDocs(todayList);
//       setYesterdayDocs(yesterdayList);
//       setPreviousWeekDocs(last7DaysList);
//     } catch (err) {
//       console.error("❌ Failed to fetch history:", err);
//     }
//   };

//   fetchHistoryDocs();
// }, []);



//   const renderDocs = (docs) =>
//     docs.map((doc) => (
//       <div
//         key={doc.id}
//         className={`history-document ${activeDoc === doc.id ? 'active' : ''}`}
//         onClick={() => {
//           setActiveDoc(doc.id);
//           onSelectDoc(doc);
//         }}
//       >
//         {doc.name}
//       </div>
//     ));

//   return (
//     <Box sx={{ width: "100%" }}>
//       {/* ❌ Close Button */}
//       <Box display="flex" justifyContent="flex-end" pr={2}>
//         <IconButton onClick={onClose}>
//           <CloseIcon />
//         </IconButton>
//       </Box>

//       {/* 📄 Document Sections */}
//       <div className="history-container">
//         <div className="history-section">
//           <div className="history-header" onClick={() => setShowToday(!showToday)}>
//             <span className="section-title">Today</span>
//             {showToday ? <ExpandLessIcon className="expand-icon" /> : <ExpandMoreIcon className="expand-icon" />}
//           </div>
//           {showToday && <div className="history-docs">{renderDocs(todayDocs)}</div>}
//         </div>

//         <div className="history-section">
//           <div className="history-header" onClick={() => setShowYesterday(!showYesterday)}>
//             <span className="section-title">Yesterday</span>
//             {showYesterday ? <ExpandLessIcon className="expand-icon" /> : <ExpandMoreIcon className="expand-icon" />}
//           </div>
//           {showYesterday && <div className="history-docs">{renderDocs(yesterdayDocs)}</div>}
//         </div>

//         <div className="history-section">
//           <div className="history-header" onClick={() => setShowPrevious(!showPrevious)}>
//             <span className="section-title">Previous 7 Days</span>
//             {showPrevious ? <ExpandLessIcon className="expand-icon" /> : <ExpandMoreIcon className="expand-icon" />}
//           </div>
//           {showPrevious && <div className="history-docs">{renderDocs(previousWeekDocs)}</div>}
//         </div>
//       </div>
//     </Box>
//   );
// };

// export default History;
import React, { useState, useEffect } from 'react';
import './../../asessts/css/History.css';
import {
  IconButton,
  Box,
  InputBase,
  Divider,Typography
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { Search } from 'react-feather'; // Add this at the top
import { adminAxios } from '../../asessts/axios';
import dayjs from 'dayjs';

const History = ({ onClose, onSelectDoc }) => {
  const [activeDocKey, setActiveDocKey] = useState('');
  const [todayDocs, setTodayDocs] = useState([]);
  const [yesterdayDocs, setYesterdayDocs] = useState([]);
  const [previousWeekDocs, setPreviousWeekDocs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchHistoryDocs = async () => {
      try {
        const token = localStorage.getItem("token");

        const res = await adminAxios.get('/api/v1/history/summary', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        const allDocs = res.data.history || [];

        const today = dayjs().startOf('day');
        const yesterday = today.subtract(1, 'day');
        const weekAgo = today.subtract(7, 'day');

        const todayList = [];
        const yesterdayList = [];
        const last7DaysList = [];

        allDocs.forEach(doc => {
          const docDate = dayjs(doc.generated_at).startOf('day');
          const docTime = dayjs(doc.generated_at).format('hh:mm A');
          const docKey = `${doc.document_id}-${doc.generated_at}`;

          const docObj = {
            id: doc.document_id,
            name: doc.document_name,
            date: docDate.format('YYYY-MM-DD'),
            time: docTime,
            key: docKey
          };

          if (docDate.isSame(today)) {
            todayList.push(docObj);
          } else if (docDate.isSame(yesterday)) {
            yesterdayList.push(docObj);
          } else if (docDate.isAfter(weekAgo)) {
            last7DaysList.push(docObj);
          }
        });

        setTodayDocs(todayList);
        setYesterdayDocs(yesterdayList);
        setPreviousWeekDocs(last7DaysList);
      } catch (err) {
        console.error("❌ Failed to fetch history:", err);
      }
    };

    fetchHistoryDocs();
  }, []);

  const renderDocs = (docs) =>
    docs
      .filter(doc => doc.name.toLowerCase().includes(searchTerm.toLowerCase()))
      .map((doc) => (
        <div
          key={doc.key}
          className={`history-document ${activeDocKey === doc.key ? 'active' : ''}`}
          onClick={() => {
            setActiveDocKey(doc.key);
            onSelectDoc(doc); // ✅ passing the full doc object with id, name, time etc.
          }}
        >
          <div className="history-doc-name">{doc.name}</div>
          <div className="history-doc-time">{doc.time}</div>
        </div>
      ));

  return (
    <Box sx={{ width: "100%",padding:2 }}>
      {/* ❌ Close Button */}
    {/* <Box display="flex" justifyContent="space-between" alignItems="center" px={2} py={1}>
  <Box display="flex" alignItems="center" gap={2}>
    <Typography fontWeight={600} fontSize={16}>History</Typography>
    <Box className="search-container" sx={{ position: "relative", width: "250px" }}>
      <input
        type="text"
        placeholder="Search topics..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <Search className="basic-header-search-icon" />
    </Box>
  </Box>

  <IconButton onClick={onClose}>
    <CloseIcon />
  </IconButton>
</Box> */}

<Box px={2} py={1}>
  {/* Top Right: Close Button */}
  <Box display="flex" justifyContent="flex-end">
    <IconButton onClick={onClose}>
      <CloseIcon />
    </IconButton>
  </Box>

  {/* Bottom Row: History + Search */}
  <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}marginRight={'20px'}>
    <Typography fontWeight={600} fontSize={16}>History</Typography>

    <Box className="search-container" sx={{ position: "relative", width: "250px" }}>
      <input
        type="text"
        placeholder="Search topics..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <Search className="basic-header-search-icon" />
    </Box>
  </Box>
</Box>


      {/* <Divider /> */}

      {/* 📄 Document Sections */}
      <div className="history-doc-section">
        {todayDocs.length > 0 && <div className="history-label">Today</div>}
        {renderDocs(todayDocs)}

        {yesterdayDocs.length > 0 && <div className="history-label">Yesterday</div>}
        {renderDocs(yesterdayDocs)}

        {previousWeekDocs.length > 0 && <div className="history-label">Previous 7 Days</div>}
        {renderDocs(previousWeekDocs)}
      </div>
    </Box>
  );
};

export default History;




// import React from 'react';
// import { Box, Typography, IconButton } from '@mui/material';
// import CloseIcon from '@mui/icons-material/Close';

// const History = ({ onClose }) => {
//   return (
//     <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
//       {/* ❌ Close Button */}
//       <Box position="absolute" top={8} right={8}>
//         <IconButton onClick={onClose}>
//           <CloseIcon />
//         </IconButton>
//       </Box>

//       {/* 📭 Centered Message */}
//       <Box
//         height="100%"
//         display="flex"
//         justifyContent="center"
//         alignItems="center"
//         textAlign="center"
//       >
//         <Typography variant="h6" fontWeight={600} color="text.secondary">
//           No history available
//         </Typography>
//       </Box>
//     </Box>
//   );
// };

// export default History;
