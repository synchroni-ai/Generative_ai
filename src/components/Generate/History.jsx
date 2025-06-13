import React, { useState, useEffect } from 'react';
import './../../asessts/css/History.css';
import {
  IconButton,
  Box,
  InputBase,
  Divider,Typography,Tooltip
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { Search } from 'react-feather'; // Add this at the top
import { adminAxios } from '../../asessts/axios';
import { Skeleton } from '@mui/material';
import dayjs from 'dayjs';

const History = ({ onClose, onSelectDoc }) => {
  const [activeDocKey, setActiveDocKey] = useState('');
  const [todayDocs, setTodayDocs] = useState([]);
  const [yesterdayDocs, setYesterdayDocs] = useState([]);
  const [previousWeekDocs, setPreviousWeekDocs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
const [loading, setLoading] = useState(true);


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
    } finally {
      setLoading(false);
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
    <Box sx={{ width: "100%",padding:"10px 16px", overflowX:"hidden" }}>
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
 <Tooltip title="Hide History" placement="bottom-end" arrow>
  <IconButton onClick={onClose} disableRipple>
    <img
      src={require('./../../asessts/images/Closesidebar.png')} // adjust path if needed
      alt="Close"
      width={22}
      height={22}
      style={{ objectFit: 'contain',marginRight:"10px" }}
    />
  </IconButton>
</Tooltip>
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
  {loading ? (
    <>
      <div className="history-label">Today</div>
      {[...Array(2)].map((_, idx) => (
        <Box key={`today-skeleton-${idx}`} className="history-document">
          <Skeleton variant="text" width="80%" height={24} />
          <Skeleton variant="text" width="40%" height={20} />
        </Box>
      ))}

      <div className="history-label">Yesterday</div>
      {[...Array(2)].map((_, idx) => (
        <Box key={`yesterday-skeleton-${idx}`} className="history-document">
          <Skeleton variant="text" width="80%" height={24} />
          <Skeleton variant="text" width="40%" height={20} />
        </Box>
      ))}

      <div className="history-label">Previous 7 Days</div>
      {[...Array(2)].map((_, idx) => (
        <Box key={`week-skeleton-${idx}`} className="history-document">
          <Skeleton variant="text" width="80%" height={24} />
          <Skeleton variant="text" width="40%" height={20} />
        </Box>
      ))}
    </>
  ) : (
    <>
      {todayDocs.length > 0 && <div className="history-label">Today</div>}
      {renderDocs([...todayDocs].reverse())}

      {yesterdayDocs.length > 0 && <div className="history-label">Yesterday</div>}
      {renderDocs([...yesterdayDocs].reverse())}

      {previousWeekDocs.length > 0 && <div className="history-label">Previous 7 Days</div>}
      {renderDocs([...previousWeekDocs].reverse())}
    </>
  )}
</div>

    </Box>
  );
};

export default History;



