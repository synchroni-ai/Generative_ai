import React, { useState } from 'react';
import './../../asessts/css/History.css'; // CSS must be created separately
import arrowUp from './../../asessts/images/arrowupicon.png';
import arrowDown from './../../asessts/images/arrowupicon.png';

const History = ({ onClose }) => {
  const [showToday, setShowToday] = useState(true);
  const [showYesterday, setShowYesterday] = useState(true);
  const [activeDoc, setActiveDoc] = useState('GenAI_Documentation');

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
        onClick={() => setActiveDoc(doc)}
      >
        {doc}
      </div>
    ));

  return (
     <div>
      <button onClick={onClose}>Close</button>
    <div className="history-container">
      {/* Today Section */}
      <div className="history-section">
        <div className="history-header" onClick={() => setShowToday(!showToday)}>
          <span className="section-title">Today</span>
<img
            src={showToday ? arrowUp : arrowDown}
            alt="toggle arrow"
            className="arrow-icon"
          />        </div>
        {showToday && <div className="history-docs">{renderDocs(todayDocs)}</div>}
      </div>

      {/* Yesterday Section */}
      <div className="history-section">
        <div className="history-header" onClick={() => setShowYesterday(!showYesterday)}>
          <span className="section-title">Yesterday</span>
 <img
            src={showYesterday ? arrowUp : arrowDown}
            alt="toggle arrow"
            className="arrow-icon"
          />        </div>
        {showYesterday && <div className="history-docs">{renderDocs(yesterdayDocs)}</div>}
      </div>
    </div>
        </div>
  );
};

export default History;