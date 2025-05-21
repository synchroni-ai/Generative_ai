import React, { useState } from 'react';
import './../../asessts/css/History.css'; // CSS must be created separately
import { IconButton } from '@mui/material';
import arrowUp from './../../asessts/images/arrowupicon.png';
import arrowDown from './../../asessts/images/arrowupicon.png';
import CloseIcon from '@mui/icons-material/Close';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const History = ({ onClose, onSelectDoc }) => {
  const [showToday, setShowToday] = useState(true);
  const [showYesterday, setShowYesterday] = useState(true);
  const [activeDoc, setActiveDoc] = useState('');

  const todayDocs = [
    'GenAI_Documentation',
    'GenAI_Application_Guide',
    'GenAI_Platform_Docs',
    'GenAI_DeveloperDocs',
    'GenAI_Functional_Test_Plan',
    'GenAI_Script_Validation_Sheet',
  ];

  const yesterdayDocs = [
    'GenAI_Documentation',
    'GenAI_Application_Guide',
    'GenAI_Platform_Docs',
    'GenAI_DeveloperDocs',
    'GenAI_Functional_Test_Plan',
  ];

  const renderDocs = (docs) =>
    docs.map((doc) => (
      <div
  key={doc}
  className={`history-document ${activeDoc === doc ? 'active' : ''}`}
  onClick={() => {
    setActiveDoc(doc);
    onSelectDoc(doc); // Notify parent
  }}
>
        {doc}
      </div>
    ));

  return (
    <div>
     <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
      </div>
    <div className="history-container">
      {/* Today Section */}
      <div className="history-section">
        <div className="history-header" onClick={() => setShowToday(!showToday)}>
          <span className="section-title">Today</span>
{showToday ? (
  <ExpandLessIcon sx={{ fontSize: 20, color: '#555' }} />
) : (
  <ExpandMoreIcon sx={{ fontSize: 20, color: '#555' }} />
)}
       </div>
        {showToday && <div className="history-docs">{renderDocs(todayDocs)}</div>}
      </div>

      {/* Yesterday Section */}
      <div className="history-section">
        <div className="history-header" onClick={() => setShowYesterday(!showYesterday)}>
          <span className="section-title">Yesterday</span>
 {showYesterday ? (
  <ExpandLessIcon sx={{ fontSize: 20, color: '#555' }} />
) : (
  <ExpandMoreIcon sx={{ fontSize: 20, color: '#555' }} />
)}       </div>
        {showYesterday && <div className="history-docs">{renderDocs(yesterdayDocs)}</div>}
      </div>
    </div>
       </div> 
  );
};

export default History;