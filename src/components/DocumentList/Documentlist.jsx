import React, { useState, useEffect } from "react";
import {
  Button,
  Box,
  Container,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
   MenuItem, Menu, ListItemIcon, ListItemText,
  Select,
  Typography,
  Pagination,
  PaginationItem,
  TableContainer,
} from "@mui/material";
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ReplayIcon from '@mui/icons-material/Replay';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import TuneIcon from '@mui/icons-material/Tune';
import { useNavigate } from "react-router-dom";
import { Search } from 'react-feather'; // Add this at the top
import { Skeleton } from "@mui/material";
import {adminAxios} from '../../asessts/axios/index';
import axios from "axios";
import Header from "../../Layout/Header";
import MoreVertIcon from '@mui/icons-material/MoreVert';
import IconButton from '@mui/material/IconButton';
import UploadModal from "../Upload/UploadModal";
import { TablePagination } from "@mui/material";
import TestCaseDrawer from "../TestCaseDrawer";
import Coursecreatesearchcourselistplus from "./../../asessts/images/DocumentlistPlusicon.png";
import Coursecreatesearchsearch from "./../../asessts/images/DocumentlistSearchicon.png";
import ImportIcon from "./../../asessts/images/importicon.png";
import RestartIcon from "./../../asessts/images/restarticon.png";
import DeleteIcon from "./../../asessts/images/deleteicon.png";
import GenerateDrawer from "../Generate/GenerateDrawer"; // adjust the path accordingly
import GenAIUploader from '../Upload/GenAi_Overview'; // import your component
import "./../../asessts/css/documentlist.css";
import "./header.css";

const Documentlist = () => {
  const [activeTab, setActiveTab] = useState("testcase");
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [testCaseData, setTestCaseData] = useState("");
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5); // or 10 or anything else
  const [generateDrawerOpen, setGenerateDrawerOpen] = React.useState(false);
  const [generateData, setGenerateData] = React.useState(null);
  const [selectedDocumentName, setSelectedDocumentName] = useState('');
const [taskId, setTaskId] = useState('');
const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

const FilteredDocs = documents.filter((doc) =>
  doc.file_name?.toLowerCase().includes(searchTerm?.toLowerCase())
);
 const totalItems = FilteredDocs.length;
const totalPages = Math.ceil(totalItems / rowsPerPage);
const start = page * rowsPerPage + 1;
const end = Math.min((page + 1) * rowsPerPage, totalItems);
const currentPage = page + 1; // 1-based

const getVisiblePages = () => {
  const pages = [];

  // Start with max(1, currentPage - 1)
  const start = Math.max(1, currentPage - 1);
  // End at min(totalPages, currentPage + 1)
  const end = Math.min(totalPages, start + 2);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  return pages;
};
  const toggleDrawer = (open) => () => setDrawerOpen(open);
  // const handleUploadClick = () => setModalOpen(true);
  const handleModalClose = () => setModalOpen(false);
  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/");
  };
  
  const handleUploadClick = () => {
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
  };
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const parseFormattedText = (text) => {
      if (!text || typeof text !== 'string') return null; // <-- Prevent error if undefined/null
    const lines = text.split("\n");
    const elements = [];
    let listItems = [];
    const flushList = () => {
      if (listItems.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} style={{ paddingLeft: "1.5rem", marginTop: 4 }}>
            {listItems.map((item, idx) => (
              <li key={idx}>{renderBoldText(item)}</li>
            ))}
          </ul>
        );
        listItems = [];
      }
    };
    const renderBoldText = (line) =>
      line.split(/(\*\*.*?\*\*)/g).map((part, index) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={index} >{part.slice(2, -2)}</strong>
        ) : (
          <React.Fragment key={index}>{part}</React.Fragment>
        )
      );

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      if (trimmed.startsWith("* ")) {
        listItems.push(trimmed.slice(2));
      } else {
        flushList();
        if (trimmed !== "") {
          elements.push(
            <p key={index} style={{ marginBottom: "0.6rem" }}>
              {renderBoldText(trimmed)}
            </p>
          );
        }
      }
    });
    flushList();
    return elements;
  };
  const fetchDocuments = async () => {
    try {
      const response = await adminAxios.get("/documents/");
      // const response = await axios.get("http://192.168.0.173:8000/documents/");
      setDocuments(response.data);
      console.log("Fetched data:", response.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };




const handleGenerateClick = async (doc) => {
  try {
    setSelectedDocumentName(doc.file_name); 

    if (doc.status === -1) {
      // 🔁 Generate test cases first
      const formData = new FormData();
      formData.append("file_id", doc.file_id);

      const response = await adminAxios.post("/generate_test_cases/", formData);
      console.log("Generated Test Cases:", response.data);

      setGenerateData(response.data);
      setTaskId(response.data.task_id);

      navigate('/uiux-configurator', {
        state: {
          doc,
          task_id: response.data.task_id,
        },
      });
    } else {
      // ✅ Already processed, skip generation
      navigate('/uiux-configurator', {
        state: {
          doc,
          file_id: doc.file_id,
        },
      });
    }
  } catch (error) {
    console.error("Error generating test cases:", error);
  }
};


  useEffect(() => {
    fetchDocuments();
  }, []);



  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column", overflowY: "hidden" }}>
      {/* <Header onLogout={handleLogout} /> */}
      <Box sx={{ mt: 8, px: 5, overflowY: "auto", height: "89vh", scrollbarWidth: 'thin' }}>
        <Box
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      px={2}
      py={1}
      mt={3}
      bgcolor="white"
    >
      {/* Left Section */}
      <Box display="flex" alignItems="center" gap={2}>
        <Typography variant="h6" fontWeight="bold">
          Dataspace
        </Typography>

        <Button
                    onClick={handleUploadClick}
          variant="outlined"
          sx={{
            borderRadius: '30px',
            textTransform: 'none',
            color: '#000080',
            borderColor: 'transparent',
            bgcolor: '#f9f9f9',
            '&:hover': {
              bgcolor: '#f0f0f0',
            },
             '& .MuiButton-startIcon': {
      marginRight: '6px',
      '& svg': {
        fontSize: '18px', // 👈 reduce icon size here
      },
    },
          }}
          startIcon={<AddCircleOutlineIcon />}
          // endIcon={<ArrowDropDownIcon />}
        >
          Data Space
        </Button>
      </Box>

      {/* Right Section */}
      {/* <Button
        variant="outlined"
        sx={{
          borderRadius: '30px',
          textTransform: 'none',
          color: 'text.primary',
          borderColor: '#bdbdbd',
        }}
        startIcon={<TuneIcon />}
      >
        Filter
      </Button> */}
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
        <Container maxWidth="xl" sx={{ mt: 4 }}>
          {loading ? (
            <TableContainer sx={{ width: "100%", border: "1px solid #e6e6e6", borderRadius: "10px", borderBottom: "none" }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: "bold" }}>SNo.</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>Document Name</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>Document Path</TableCell>
                    {/* <TableCell sx={{ fontWeight: "bold" }}>Completion Latency</TableCell> */}
                    <TableCell sx={{ fontWeight: "bold" }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {[...Array(rowsPerPage)].map((_, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Skeleton variant="text" width={30} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width="80%" height={20} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width="90%" height={20} />
                      </TableCell>
                      {/* <TableCell>
                        <Skeleton variant="rectangular" width="60%" height={20} />
                      </TableCell> */}
                      <TableCell>
                        <Skeleton variant="rectangular" width="60%" height={20} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <TableContainer sx={{ width: "100%", border: "1px solid #e6e6e6", borderRadius: "10px", borderBottom: "none" }}>
              <Table aria-label="documents table">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: "bold" }}>SI no</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>Data space</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>Data space path</TableCell>
                    {/* <TableCell sx={{ fontWeight: "bold" }}>Completion Latency</TableCell> */}
                    <TableCell sx={{ fontWeight: "bold" }}>Actions</TableCell> {/* New Column */}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {documents
                    .filter((doc) =>
                      doc.file_name?.toLowerCase().includes(searchTerm?.toLowerCase())
                    )
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((doc, index) => (
                      <TableRow key={doc._id}>
                        <TableCell sx={{color:"#8e8e8e"}}>{page * rowsPerPage + index + 1}</TableCell>
                       <TableCell
  onClick={async () => {
    await handleGenerateClick(doc); // Generate first
    // navigate('/uiux-configurator', { state: { doc } }); // Then navigate
  }}
  sx={{ cursor: "pointer", color: "#8e8e8e", textDecoration: "underline" }}
>
  {doc.file_name}
</TableCell>
                        <TableCell sx={{color:"#8e8e8e"}}>{doc.file_path}</TableCell>
                        {/* <TableCell>{doc.llm_response_latency}</TableCell> */}
                        <TableCell sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {/* <span
                            style={{ fontSize: '14px', textDecoration: 'underline', color: '#1976d2', cursor: 'pointer' }}
                            onClick={() => handleGenerateClick(doc)}
                          >
                            Generate
                          </span> */}
                           <IconButton
        size="small"
        disableRipple
        disableFocusRipple
        disableTouchRipple
        onClick={handleClick}
        sx={{
          '&:hover': { backgroundColor: 'transparent' },
          padding: 0,
          marginLeft: '10px'
        }}
      >
        <MoreVertIcon sx={{ fontSize: 22, color: "#8e8e8e" }} />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          elevation: 0,
          sx: {
            backgroundColor:"#FBFBFB",
            borderRadius: 5,
            paddingY: 0,
            minWidth: 150,
          },
        }}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleClose}>
          <ListItemIcon>
            {/* Use image or icon */}
            {/* <CloudUploadIcon fontSize="small" /> */}
         <img src={ImportIcon} width={18} height={18} alt="import" />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ sx: { color: '#666666' } }}>Import</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleClose}>
          <ListItemIcon>
          <img src={RestartIcon} width={18} height={18} alt="Restart" />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ sx: { color: '#666666' } }}>Restart</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleClose}>
          <ListItemIcon>
            <img src={DeleteIcon} width={18} height={18} alt="Delete" />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ sx: { color: '#666666' } }}>Delete</ListItemText>
        </MenuItem>
      </Menu>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

           <Box mt={3}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        flexWrap="wrap"
        gap={2}
      >
        {/* Left side: Show dropdown + Showing info */}
        <Box display="flex" alignItems="center" gap={5} flexWrap="wrap">
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="body2" sx={{color:"#8e8e8e"}}>Show</Typography>
            <Select
              size="small"
              value={rowsPerPage}
              onChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              sx={{
                minWidth: 50,
                height: 30,
                color:"#8e8e8e",
                fontSize: '0.875rem',
                '& .MuiSelect-select': {
                  // paddingTop: '4px',
                  // paddingBottom: '4px',
                },
              }}
            >
              {[5, 10, 25].map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            <Typography variant="body2" sx={{color:"#8e8e8e"}}>Entries</Typography>
          </Box>

          <Typography variant="body2" sx={{color:"#8e8e8e"}}>
            Showing {start} to {end} of {totalItems} entries
          </Typography>
        </Box>
          {/* Right Side - Pagination with "Previous" and "Next" text */}
   
  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
  {/* Previous */}
  <PaginationItem
  disableRipple
    type="previous"
    disabled={currentPage === 1}
    onClick={() => setPage((prev) => Math.max(prev - 1, 0))}
    slots={{ previous: () => <span>Previous</span> }}
    sx={{
      padding: '6px 16px',
      borderRadius: '50%',
      minWidth: 'auto',
      height: 'auto',
      color:"#666666",
      '&:hover': { backgroundColor: 'transparent' },
    }}
  />

  {/* Dynamic page buttons */}
  {getVisiblePages().map((pg) => (
    <PaginationItem
    disableRipple
      key={pg}
      page={pg}
      selected={pg === currentPage}
      onClick={() => setPage(pg - 1)}
      sx={{
        borderRadius: '50%',
        minWidth: 32,
        height: 32,
        // backgroundColor: pg === currentPage ? '#000080' : 'transparent',
        color: pg === currentPage ? '#fff' : '#666666',
         '&:hover': {
              backgroundColor: '',
            },
             '&.Mui-selected': {
              backgroundColor: '#000080',
              color: '#fff',
              '&:hover': {
                backgroundColor: '#000080',
              },
            },
      }}
    />
  ))}

  {/* Next */}
  <PaginationItem
  disableRipple
    type="next"
    disabled={currentPage === totalPages}
    onClick={() => setPage((prev) => Math.min(prev + 1, totalPages - 1))}
    slots={{ next: () => <span>Next</span> }}
    sx={{
      padding: '6px 16px',
      borderRadius: '50%',
      minWidth: 'auto',
      height: 'auto',
      color:"#666666",
      '&:hover': { backgroundColor: 'transparent' },
    }}
  />
</div>



      </Box>
    </Box>
        </Container>
      </Box>

      {/* <TestCaseDrawer
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        data={testCaseData}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        parseFormattedText={parseFormattedText}
      /> */}
      <GenAIUploader open={drawerOpen}  onClose={() => setDrawerOpen(false)} fetchDocuments={fetchDocuments} />

      <GenerateDrawer
        open={generateDrawerOpen}
        onClose={() => setGenerateDrawerOpen(false)}
        documentName={selectedDocumentName} // ✅ Correctly scoped and passed
          taskId={taskId} // 👈 Pass task_id here
      />
      <UploadModal open={modalOpen} onClose={handleModalClose} fetchDocuments={fetchDocuments} />
    </Box>
  );
};

export default Documentlist;

