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
  Tabs,
  Tab,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { WebsocketAxios } from '../../asessts/axios/index';
import { adminAxios } from '../../asessts/axios/index';
import CloudDownloadOutlinedIcon from '@mui/icons-material/CloudDownloadOutlined';
import ExportIcon from "./../../asessts/images/exporticon.png";
import { Skeleton } from '@mui/material';
import "./Tabs.css";
// const parseTestCasesFromContent = (content, testType, fileName) => {
//   const parsed = [];
//   const entries = content.split(/\n(?=TCID:)/g); // Split at each TCID

//   entries.forEach(raw => {
//     const fields = {
//       file_name: fileName,
//       "TCID": "",
//       "Test type": testType,
//       "Title": "",
//       "Description": "",
//       "Precondition": "",
//       "Steps": "",
//       "Action": "",
//       "Data": "",
//       "Result": "",
//       "Test Nature": "",
//       "Test priority": ""
//     };

//     Object.keys(fields).forEach(key => {
//       if (key === "file_name") return;
//       const regex = new RegExp(`${key}:\\s*([\\s\\S]*?)(?=\\n[A-Z][^:]*?:|\\n*$)`, 'i');
//       const match = raw.match(regex);
//       if (match) {
//         fields[key] = match[1].trim();
//       }
//     });

//     // Skip if it's just a heading or doesn't have a valid TCID
//     if (!fields["TCID"]) return;

//     fields["Type (P / N / in)"] = fields["Test Nature"];
//     delete fields["Test Nature"];

//     parsed.push(fields);
//   });

//   return parsed;
// };


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

const TestCaseTable = ({ selectedHistoryDoc, fromHistory, taskId, token, fileId, selectedSubTypes, results = [],selectedDocs }) => {
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
    console.log("Selected SubTypes:", selectedSubTypes);
  }, [selectedSubTypes]);

  useEffect(() => {
    const groupedByFile = {}; // { file_name: [testcases] }

    results.forEach(fileResult => {
      const fileName = fileResult.file_name;
      const testCaseTypes = fileResult.test_cases || {};

      Object.entries(testCaseTypes).forEach(([type, tc]) => {
        if (tc.content) {
          const parsedRows = parseTestCasesFromContent(tc.content, type, fileName);
          if (!groupedByFile[fileName]) groupedByFile[fileName] = [];
          groupedByFile[fileName].push(...parsedRows);
        }
      });
    });

    setAllTestCases(groupedByFile); // store grouped format
    setParsedData(groupedByFile); // same as above if no additional filtering needed

    const firstGroup = Object.values(groupedByFile)[0] || [];
    const headers = firstGroup.length ? Object.keys(firstGroup[0]) : [];

    setHeaders(headers);
    setLoading(false);
  }, [results]);



  useEffect(() => {
    let pollingTimeout = null;

    const fetchTestCasesFromAPI = async () => {
      try {
        const response = await adminAxios.get(`/get-test-cases/${fileId}`);
        const resultData = response.data;

        // ⏳ Keep polling until status_code is 1
        if (resultData.status_code === 0) {
          console.log("⏳ Status code 0: Retrying in 5 seconds...");
          pollingTimeout = setTimeout(fetchTestCasesFromAPI, 5000);
          return;
        }

        // ✅ Only process when status_code is 1
        console.log("✅ Status code 1: Final result received");

        setLoading(true);
        setError(false);
        setDocumentId(null);
        setParsedData([]);
        setHeaders([]);

        if (resultData.test_cases?.length > 0) {
          const rows = resultData.test_cases;
          const headers = Object.keys(rows[0]);
          setAllTestCases(rows);
          setParsedData(filterByTab(rows, activeTab));
          setHeaders(headers);
        }

        if (resultData.document_id) {
          setDocumentId(resultData.document_id);
        }

        if (resultData.combined_test_case_document?._id) {
          setDocumentId(resultData.combined_test_case_document._id);
        }

        setLoading(false);
      } catch (err) {
        console.error("❌ Error fetching test cases from REST API:", err);
        setError(true);
        setLoading(false);
      }
    };

    if (taskId) {
      // 🔁 WebSocket logic
      setLoading(true);
      setError(false);
      setDocumentId(null);
      setParsedData([]);
      setHeaders([]);

      const socketUrl = `${WebsocketAxios}/task_status/${taskId}?token=${token}`;
      socketRef.current = new WebSocket(socketUrl);

      socketRef.current.onopen = () => {
        console.log("✅ WebSocket connected");
        setError(false);
      };

      socketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("📨 WebSocket message received:", data);

        if (data.status === "SUCCESS" && data.result?.test_cases?.length > 0) {
          const rows = data.result.test_cases;
          const headers = Object.keys(rows[0]);

          setAllTestCases(rows);
          setParsedData(filterByTab(rows, activeTab));
          setHeaders(headers);

          if (data.result?.document_id) {
            setDocumentId(data.result.document_id);
          }

          setLoading(false);
        }
      };

      socketRef.current.onerror = (event) => {
        console.error("🛑 WebSocket error:", event);
        setError(true);
        setLoading(false);
      };

      socketRef.current.onclose = () => {
        console.log("🔌 WebSocket connection closed");
      };

      return () => {
        socketRef.current?.close();
      };
    } else if (fileId) {
      // ✅ Start polling if fileId is available
      fetchTestCasesFromAPI();
    }

    return () => {
      // Cleanup any scheduled polling
      if (pollingTimeout) {
        clearTimeout(pollingTimeout);
      }
    };
  }, [taskId, fileId]);


  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setParsedData(filterByTab(allTestCases, newValue));
  };
  const handleTabClick = (label) => {
    setActiveTab(label);
    setParsedData(filterByTab(allTestCases, label));
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




  useEffect(() => {
    const fetchTestCaseSummary = async () => {
      try {
        const res = await adminAxios.get(`/test-case-summary/${fileId}`);
        const summary = res.data;

        setTestCaseCounts({
          All: summary.total_test_cases,
          ...summary.counts_by_type
        });
      } catch (err) {
        console.error("❌ Error fetching test case summary:", err);
      }
    };

    if (fileId) {
      fetchTestCaseSummary();
    }
  }, [fileId]);


const exportCSV = async () => {
  try {
    // Join selectedDocs for file_ids
    const fileIdsParam = selectedDocs.join(',');
    // Join selectedSubTypes for types (make sure to lowercase them)
    const typesParam = selectedSubTypes.map(type => type.toLowerCase()).join(',');

    const url = `/api/v1/documents/download-testcases?file_ids=${fileIdsParam}&types=${typesParam}&mode=zip`;

    const response = await adminAxios.get(url, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const blob = new Blob([response.data], { type: 'application/zip' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', 'test_cases_bundle.zip');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error("❌ Error downloading test cases ZIP:", error);
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
      {/* Export Button Row */}
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          onClick={exportCSV}
          sx={{
            textTransform: 'none',
            backgroundColor: '#000080',
            color: '#fff',
            fontWeight: 500,
            borderRadius: 5,
            px: 2,
            '&:hover': {
              backgroundColor: '#000080',
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

      {/* Tabs */}
      {/* <Box display="flex" alignItems="center" justifyContent="space-between" ml={3}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          textColor="inherit"
          TabIndicatorProps={{
            style: {
              backgroundColor: '#000080',
              height: '2px',
            },
          }}
        >
          {tabLabels.map((label, index) => (
            <Tab
              key={label}
              disableRipple
              label={
                <Typography
                  sx={{
                    fontWeight: 400,
                    textTransform: 'none',
                    fontSize: 14,
                    color: activeTab === index ? '#000080' : '',
                  }}
                >
                  {label}
                </Typography>
              }
            />
          ))}
        </Tabs>
      </Box> */}
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



      {/* Conditional Heading */}
      {selectedHistoryDoc && (
        <Typography fontWeight={600} fontSize={16} mb={2} mt={3} ml={2.5}>
          TestScripts_Execution_Report_Doc
        </Typography>
      )}

      {/* Table */}
      {/* <Paper elevation={0} sx={{ mt: 3, borderRadius: 3, overflowX: 'auto', ml: 2.5, border: "1px solid #e6e6e6" }}>
        <Table>
          <TableHead>
            <TableRow>
              {fromHistory ? (
                <>
                  <TableCell sx={{ fontWeight: 600 }}>Test case ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Test case</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Tags</TableCell>
                </>
              ) : (
                headers.map((header) => (
                  <TableCell key={header} sx={{ fontWeight: 600 }}>
                    {header}
                  </TableCell>
                ))
              )}
            </TableRow>
          </TableHead>

          <TableBody>
           {!selectedHistoryDoc && Object.entries(parsedData).map(([fileName, testCases], docIndex) => (
  <Box key={docIndex} mb={4}>
    <Typography fontWeight={600} fontSize={18} mt={3} mb={2} ml={1}>
      {fileName}
    </Typography>
    <Paper elevation={0} sx={{ borderRadius: 3, overflowX: 'auto', border: "1px solid #e6e6e6" }}>
      <Table>
        <TableHead>
          <TableRow>
            {headers.map((header) => (
              <TableCell key={header} sx={{ fontWeight: 600 }}>{header}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {testCases.map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {headers.map((header) => (
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


          </TableBody>
        </Table>
      </Paper> */}


      {!selectedHistoryDoc && Object.entries(parsedData).map(([fileName, testCases], docIndex) => (
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

    </Box>
  );
};

export default TestCaseTable;
