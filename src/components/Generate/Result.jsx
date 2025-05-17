import React, { useState } from 'react';
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
import DownloadIcon from '@mui/icons-material/Download';
import CloudDownloadOutlinedIcon from '@mui/icons-material/CloudDownloadOutlined';

const tabLabels = [
  'All 20',
  'Functionality 05',
  'Non- Functionality 05',
  'Security 05',
  'Compliance 05',
];

const testData = [
  {
    id: 'FUNC_01',
    expected: 'Redirected to dashboard',
    steps: 'Enter valid credentials and login',
    scenario: 'User login',
    tags: '#FunctionalTest',
  },
  {
    id: 'FUNC_01',
    expected: 'Course added to “My Courses”',
    steps: 'Go to course list > Click Enroll',
    scenario: 'Enroll in a course',
    tags: '#APITest',
  },
  {
    id: 'FUNC_01',
    expected: 'Video plays without issue',
    steps: 'Click on video in module',
    scenario: 'Play course video',
    tags: '#InputValidation',
  },
  {
    id: 'FUNC_01',
    expected: 'Score calculated and stored',
    steps: 'Score calculated and stored',
    scenario: 'Submit quiz',
    tags: '#ResponseCheck',
  },
  {
    id: 'FUNC_01',
    expected: 'PDF generated and downloaded',
    steps: 'PDF generated and downloaded',
    scenario: 'Download certificate',
    tags: '#ScriptExecution',
  },
];

const TestCaseTable = () => {
  const [activeTab, setActiveTab] = useState(1); // Default to "Functionality 05"

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const exportCSV = () => {
    const headers = ['Test case ID', 'Expected results', 'Steps', 'Scenario', 'Tags'];
    const rows = testData.map((row) =>
      [row.id, row.expected, row.steps, row.scenario, row.tags].join(',')
    );
    const csvContent = [headers.join(','), ...rows].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'test_cases.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box padding={'0px 32px'}>
       {/* Export Button Row */}
  <Box display="flex" justifyContent="flex-end" mb={2}>
    <Button
      onClick={exportCSV}
      startIcon={<CloudDownloadOutlinedIcon />}
      sx={{
        textTransform: 'none',
        backgroundColor: '#000080',
        color: '#fff',
        fontWeight: 500,
        borderRadius: 5,
        px: 2.5,
        '&:hover': {
          backgroundColor: '#000060',
        },
      }}
    >
      Export as CSV
    </Button>
  </Box>

  {/* Tabs */}
  <Box display="flex" alignItems="center" justifyContent="space-between">
    <Tabs value={activeTab} onChange={handleTabChange} textColor="primary">
      {tabLabels.map((label, index) => (
        <Tab
          key={label}
          label={
            <Typography
              sx={{
                fontWeight: activeTab === index ? 600 : 400,
                textTransform: 'none',
                fontSize: 14,
              }}
            >
              {label}
            </Typography>
          }
        />
      ))}
    </Tabs>
  </Box>

      {/* Table */}
      <Paper elevation={0} sx={{ mt: 3, borderRadius: 3, overflowX: 'auto' }}>
        <Table>
          <TableHead>
            <TableRow>
              {['Test case ID', 'Expected results', 'Steps', 'Scenario', 'Tags'].map((header) => (
                <TableCell key={header} sx={{ fontWeight: 600 }}>
                  {header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {testData.map((row, index) => (
              <TableRow key={index}>
                <TableCell>{row.id}</TableCell>
                <TableCell>{row.expected}</TableCell>
                <TableCell>{row.steps}</TableCell>
                <TableCell>{row.scenario}</TableCell>
                <TableCell>{row.tags}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
};

export default TestCaseTable;
