// import React, { useState } from 'react';
// import {
//   Box,
//   Tabs,
//   Tab,
//   Typography,
//   Button,
//   Table,
//   TableBody,
//   TableCell,
//   TableHead,
//   TableRow,
//   Paper,
// } from '@mui/material';
// import DownloadIcon from '@mui/icons-material/Download';
// import CloudDownloadOutlinedIcon from '@mui/icons-material/CloudDownloadOutlined';

// const tabLabels = [
//   'All 20',
//   'Functionality 05',
//   'Non- Functionality 05',
//   'Security 05',
//   'Compliance 05',
// ];

// const testData = [
//   {
//     id: 'FUNC_01',
//     expected: 'Redirected to dashboard',
//     steps: 'Enter valid credentials and login',
//     scenario: 'User login',
//     tags: '#FunctionalTest',
//   },
//   {
//     id: 'FUNC_01',
//     expected: 'Course added to “My Courses”',
//     steps: 'Go to course list > Click Enroll',
//     scenario: 'Enroll in a course',
//     tags: '#APITest',
//   },
//   {
//     id: 'FUNC_01',
//     expected: 'Video plays without issue',
//     steps: 'Click on video in module',
//     scenario: 'Play course video',
//     tags: '#InputValidation',
//   },
//   {
//     id: 'FUNC_01',
//     expected: 'Score calculated and stored',
//     steps: 'Score calculated and stored',
//     scenario: 'Submit quiz',
//     tags: '#ResponseCheck',
//   },
//   {
//     id: 'FUNC_01',
//     expected: 'PDF generated and downloaded',
//     steps: 'PDF generated and downloaded',
//     scenario: 'Download certificate',
//     tags: '#ScriptExecution',
//   },
// ];

// const TestCaseTable = ({ selectedHistoryDoc, fromHistory }) => {
//   const [activeTab, setActiveTab] = useState(1); // Default to "Functionality 05"

//   const handleTabChange = (event, newValue) => {
//     setActiveTab(newValue);
//   };

//   const exportCSV = () => {
//     const headers = ['Test case ID', 'Expected results', 'Steps', 'Scenario', 'Tags'];
//     const rows = testData.map((row) =>
//       [row.id, row.expected, row.steps, row.scenario, row.tags].join(',')
//     );
//     const csvContent = [headers.join(','), ...rows].join('\n');

//     const blob = new Blob([csvContent], { type: 'text/csv' });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = 'test_cases.csv';
//     a.click();
//     URL.revokeObjectURL(url);
//   };


//   return (
//     <Box padding={'0px 32px'}>
//        {/* Export Button Row */}
//   <Box display="flex" justifyContent="flex-end" mb={2}>
//     <Button
//       onClick={exportCSV}
//       startIcon={<CloudDownloadOutlinedIcon />}
//       sx={{
//         textTransform: 'none',
//         backgroundColor: '#000080',
//         color: '#fff',
//         fontWeight: 500,
//         borderRadius: 5,
//         px: 2.5,
//         '&:hover': {
//           backgroundColor: '#000060',
//         },
//       }}
//     >
//       Export as CSV
//     </Button>
//   </Box>

//   {/* Tabs */}
//   <Box display="flex" alignItems="center" justifyContent="space-between">
//     <Tabs value={activeTab} onChange={handleTabChange} textColor="inherit"
//   TabIndicatorProps={{
//     style: {
//       backgroundColor: '#000080', // Underline color
//       height: '2px',
//     },
//   }}>
//       {tabLabels.map((label, index) => (
//         <Tab
//           key={label}
//                   disableRipple
//           label={
//             <Typography
//               sx={{
//                 fontWeight: activeTab === index ? 400 : 400,
//                 textTransform: 'none',
//                 fontSize: 14,
//                 color:activeTab===index ? '#000080':''
//               }}
//             >
//               {label}
//             </Typography>
//           }
//         />
//       ))}
//     </Tabs>
//   </Box>

//   {/* Conditional Heading */}
//   {selectedHistoryDoc && (
//     <Typography fontWeight={600} fontSize={16} mb={2} mt={3} ml={2.5}>
//       TestScripts_Execution_Report_Doc
//     </Typography>
//   )}
//       {/* Table */}
//      <Paper elevation={0} sx={{ mt: 3, borderRadius: 3, overflowX: 'auto', ml:2.5 }}>
//   <Table>
//     <TableHead>
//       <TableRow>
// {fromHistory ? (
//           <>
//             <TableCell sx={{ fontWeight: 600 }}>Test case ID</TableCell>
//             <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
//             <TableCell sx={{ fontWeight: 600 }}>Test case</TableCell>
//             <TableCell sx={{ fontWeight: 600 }}>Tags</TableCell>
//           </>
//         ) : (
//           ['Test case ID', 'Expected results', 'Steps', 'Scenario', 'Tags'].map((header) => (
//             <TableCell key={header} sx={{ fontWeight: 600 }}>
//               {header}
//             </TableCell>
//           ))
//         )}
//       </TableRow>
//     </TableHead>

//     <TableBody>
//       {selectedHistoryDoc ? (
//         [
//           {
//             id: 'FUNC_01',
//             date: '15 May,2025',
//             name: 'AIPlatform_Testing_Reference',
//             tag: '#FunctionalTest',
//           },
//           {
//             id: 'FUNC_01',
//             date: '10 May,2025',
//             name: 'GenAI_Functional_Testing_Document',
//             tag: '#APITest',
//           },
//           {
//             id: 'FUNC_01',
//             date: '02 May,2025',
//             name: 'GenAI_TestCase_Suite',
//             tag: '#InputValidations',
//           },
//         ].map((row, index) => (
//           <TableRow key={index}>
//             <TableCell>{row.id}</TableCell>
//             <TableCell>{row.date}</TableCell>
//             <TableCell>
//               <a href="#" style={{ color: '#0000EE', textDecoration: 'underline' }}>
//                 {row.name}
//               </a>
//             </TableCell>
//             <TableCell>{row.tag}</TableCell>
//           </TableRow>
//         ))
//       ) : (
//         testData.map((row, index) => (
//           <TableRow key={index}>
//             <TableCell>{row.id}</TableCell>
//             <TableCell>{row.expected}</TableCell>
//             <TableCell>{row.steps}</TableCell>
//             <TableCell>{row.scenario}</TableCell>
//             <TableCell>{row.tags}</TableCell>
//           </TableRow>
//         ))
//       )}
//     </TableBody>
//   </Table>
// </Paper>

//     </Box>
//   );
// };

// export default TestCaseTable;


import React, { useEffect, useState, useRef, useMemo } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import ExportIcon from "./../../asessts/images/exporticon.png";
import LinearProgress from '@mui/material/LinearProgress';
import { saveAs } from 'file-saver';
import "./Tabs.css";



const parseTestCasesFromContent = (content, testType, fileName) => {
  const parsed = [];

  // Normalize **label:** to label: (strip Markdown bolds)
  const cleanedContent = content.replace(/\*\*(.*?)\*\*/g, '$1');

  // Split entries based on TCID start
  const entries = cleanedContent
    .split(/\n\s*TCID:/g)
    .filter(Boolean)
    .map((e) => `TCID:${e.trim()}`)  // Reattach "TCID:" label
    .filter(e => e.toLowerCase().includes('title:'));  // ✅ Ensure it's an actual test case

  entries.forEach(raw => {
    const fields = {
      file_name: fileName,
      "TCID": "",
      "Test type": testType,
      "Title": "",
      "Description": "",
      "Precondition": "",
      "Steps": "",
      "Action": "",
      "Data": "",
      "Result": "",
      "Test Nature": "",
      "Test priority": ""
    };

    Object.keys(fields).forEach(key => {
      if (key === "file_name") return;
      const regex = new RegExp(`${key}:\\s*([\\s\\S]*?)(?=\\n[A-Z][^:]*?:|\\n*$)`, 'i');
      const match = raw.match(regex);
      if (match) {
        fields[key] = match[1].trim();
      }
    });

    // Skip if no TCID or improperly formatted block
    if (!fields["TCID"] || fields["TCID"].toLowerCase().includes("test cases")) return;

    fields["Type (P / N / in)"] = fields["Test Nature"];
    delete fields["Test Nature"];

    parsed.push(fields);
  });

  return parsed;
};



const selectedHistoryDocData = [
  {
    id: 'FUNC_01',
    date: '15 May,2025',
    name: 'AIPlatform_Testing_Reference',
    tag: '#FunctionalTest',
  },
  {
    id: 'FUNC_01',
    date: '10 May,2025',
    name: 'GenAI_Functional_Testing_Document',
    tag: '#APITest',
  },
  {
    id: 'FUNC_01',
    date: '02 May,2025',
    name: 'GenAI_TestCase_Suite',
    tag: '#InputValidations',
  },
];

const TestCaseTable = ({ selectedHistoryDoc, fromHistory, taskId, token, fileId, selectedSubTypes, results = {},selectedDocs, generationLoading = false, progress = 0 }) => {
  const [activeTab, setActiveTab] = useState('All'); // not index 0
  const [parsedData, setParsedData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [documentId, setDocumentId] = useState(null);
  const socketRef = useRef(null);
  const [allTestCases, setAllTestCases] = useState([]);
  const [testCaseCounts, setTestCaseCounts] = useState({});

  const tabLabels = useMemo(() => {
    const defaultTabs = selectedSubTypes || [];
    return ['All', ...defaultTabs];
  }, [selectedSubTypes]);

  useEffect(() => {
  }, [selectedSubTypes]);

useEffect(() => {
 if (
  !results ||
  typeof results !== "object"
) {
  console.warn("⚠️ Invalid results structure:", results);
  return;
}

const finalSubtypeMap =
  results.all_documents?.Final_subtypes ||  // normal API format
  results.results?.all_documents?.Final_subtypes || // history API format
  null;

if (!finalSubtypeMap || typeof finalSubtypeMap !== 'object') {
  console.warn("⚠️ Final_subtypes not found in results:", results);
  return;
}

  const groupedByFile = {};
  
  Object.entries(finalSubtypeMap).forEach(([fileId, fileData]) => {
    if (!fileData || typeof fileData !== "object") return;

    const fileName =
      fileData.document_name ||
      selectedDocs?.find(doc => doc._id === fileId)?.name ||
      `File-${fileId}`;

    const contentArray = fileData.content || [];
    const seenTCIDs = new Set(); // Per file

    contentArray.forEach(content => {
      if (!content || typeof content !== "string") return;

      const parsedRows = parseTestCasesFromContent(content, "functional", fileName);

      const uniqueRows = parsedRows.filter(row => {
        const tcid = row.TCID?.trim();
        if (!tcid || seenTCIDs.has(tcid)) return false;
        seenTCIDs.add(tcid);
        return true;
      });

      if (!groupedByFile[fileName]) groupedByFile[fileName] = [];
      groupedByFile[fileName].push(...uniqueRows);
    });
  });

  setAllTestCases(groupedByFile);
  setParsedData(groupedByFile);

  const firstGroup = Object.values(groupedByFile)[0] || [];
  const dynamicHeaders = firstGroup.length ? Object.keys(firstGroup[0]) : [];
  setHeaders(dynamicHeaders);
  setLoading(false);
}, [results, selectedDocs]);





const handleTabClick = (label) => {
  setActiveTab(label);
};
const handleTabChange = (event, newValue) => {
  setActiveTab(newValue);
};




 const filterByTab = (data, label) => {
  if (label === 'All') return data;

  const filtered = {};

  Object.entries(data).forEach(([fileName, testCases]) => {
    const match = testCases.filter(tc => tc["Test type"]?.toLowerCase() === label.toLowerCase());
    if (match.length > 0) {
      filtered[fileName] = match;
    }
  });

  return filtered;
};


const exportCSV = () => {
  try {
    const allRows = [];
    const headersSet = new Set();

    const visibleData = filterByTab(allTestCases, activeTab);

    Object.values(visibleData).forEach(testCases => {
      testCases.forEach(row => {
        allRows.push(row);
        Object.keys(row).forEach(h => {
          if (h !== 'file_name') headersSet.add(h);
        });
      });
    });

    const headers = Array.from(headersSet);

    const csvRows = allRows.map(row =>
      headers.map(h => {
        let cell = row[h] || '';
        if (typeof cell === 'string') {
          cell = cell.replace(/"/g, '""'); // Escape quotes
          cell = `"${cell.replace(/\r?\n/g, '\r\n')}"`; // Wrap and normalize line breaks
        }
        return cell;
      }).join(',')
    );

    const csvContent = [headers.join(','), ...csvRows].join('\r\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

    const fileName = activeTab === 'All'
      ? 'All_Test_Cases.csv'
      : `${activeTab}_Test_Cases.csv`;

    saveAs(blob, fileName);
  } catch (error) {
    console.error("❌ Error generating CSV:", error);
  }
};



useEffect(() => {
  const counts = {};
  let total = 0;

  Object.values(allTestCases).forEach(testCases => {
    testCases.forEach(tc => {
      const type = tc["Test type"]?.toLowerCase();
      if (type) {
        counts[type] = (counts[type] || 0) + 1;
        total += 1;
      }
    });
  });

  counts["all"] = total;
  setTestCaseCounts(counts);
}, [allTestCases]);


  return (
    <Box padding={'0px 32px'} mb={5}>
{generationLoading ? (
<Box
    width="100%"
    height="calc(100vh - 100px)" // Adjust based on your header height
    display="flex"
    justifyContent="center"
    alignItems="center"
  >
    <Box
      width="30%"
      height="35%"
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      textAlign="center"
      p={4}
      sx={{
        background: 'linear-gradient(to bottom right, #f3f6fd, #ffffff)',
        borderRadius: 4,
        // boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Typography variant="h5" fontWeight={700} color="#0A0080" mb={3}>
        Test Case Generation in Progress...
      </Typography>

      <Box display="flex" alignItems="center" gap={2} width="100%" maxWidth={500}>
        <Box flex={1}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: '#e0e0e0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: progress >= 95 ? '#ffa726' : '#0A0080',
              },
            }}
          />
        </Box>
        <Typography variant="body1" fontWeight={600} width={50}>
          {progress}%
        </Typography>
      </Box>

      {progress >= 95 && (
        <Typography mt={3} fontSize={14} color="text.secondary">
          We are Almost Reaching there...
        </Typography>
      )}

      <Typography mt={2} fontSize={12} color="text.disabled">
        You will see results once all test cases are ready.
      </Typography>
    </Box>
  </Box>

) : (
  <>
    {/* 👉 Everything below only renders when not generating */}
      {/* Export Button Row */}
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          onClick={exportCSV}
          sx={{
            textTransform: 'none',
            backgroundColor: 'var(--primary-blue)',
            color: '#fff',
            fontWeight: 500,
            borderRadius: 5,
            px: 2,
            '&:hover': {
              backgroundColor: 'var(--primary-blue)',
            },
            display: 'flex',
            alignItems: 'center',
            gap: 1.2, // space between text and image
          }}
        >
          Export as CSV
          <img
            src={ExportIcon}
            alt="Export icon"
            style={{ width: 20, height: 20 }}
          />
        </Button>
      </Box>

    
    {!selectedHistoryDoc && (
  <Box className="custom-tab-container" ml={3}>
    {tabLabels.map((label) => {
      const key = label.toLowerCase();
      const count = testCaseCounts[key] || 0;
      const isActive = activeTab === label;

      return (
        <div
          key={label}
          className={`custom-tab-item ${isActive ? 'active' : ''}`}
          onClick={() => handleTabClick(label)}
        >
          <div className="custom-tab-label">{label}</div>
          <div className={`custom-tab-badge-wrapper ${isActive ? 'active' : ''}`}>
            <div className="custom-tab-badge">{String(count).padStart(2, '0')}</div>
          </div>
        </div>
      );
    })}
  </Box>
)}



      {/* Conditional Heading */}
     {/* {selectedHistoryDoc && (
  <Box ml={2.5} mb={2} mt={3}>
    <Typography fontWeight={600} fontSize={16}>{selectedHistoryDoc.name}</Typography>
    {selectedHistoryDoc.time && (
      <Typography fontSize={12} color="text.secondary">
        Generated at {selectedHistoryDoc.time}
      </Typography>
    )}
  </Box>
)} */}



{Object.entries(filterByTab(allTestCases, activeTab)).map(([fileName, testCases], docIndex) => (
        <Box key={docIndex} mb={4} ml={3}>
          <Typography fontWeight={600} fontSize={18} mt={3} mb={2} ml={1}>
            {fileName}
          </Typography>
          <Paper elevation={0} sx={{ borderRadius: 3, overflowX: 'auto', border: "1px solid #e6e6e6" }}>
            <Table>
              <TableHead>
                <TableRow>
                  {headers.filter(h => h !== 'file_name').map((header) => (
                    <TableCell key={header} sx={{ fontWeight: 600 }}>{header}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {testCases.map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    {headers.filter(h => h !== 'file_name').map((header) => (
                      <TableCell key={header}>
                        {typeof row[header] === 'string' && row[header].includes('\n')
                          ? row[header].split('\n').map((line, i) => <div key={i}>{line}</div>)
                          : row[header]}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Box>
      ))}
</>
)}
    </Box>
  );
};

export default TestCaseTable;
