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
  Checkbox,
  Pagination,
  PaginationItem,
  TableContainer,
} from "@mui/material";
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import { useNavigate } from "react-router-dom";
import { Search } from 'react-feather'; // Add this at the top
import { Skeleton } from "@mui/material";
import {adminAxios} from '../../asessts/axios/index';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import IconButton from '@mui/material/IconButton';
import UploadModal from "../Upload/UploadModal";
import ImportIcon from "./../../asessts/images/importicon.png";
import RestartIcon from "./../../asessts/images/restarticon.png";
import DeleteIcon from "./../../asessts/images/deleteicon.png";
import GenerateDrawer from "../Generate/GenerateDrawer"; // adjust the path accordingly
import GenAIUploader from '../Upload/GenAi_Overview'; // import your component
import "./../../asessts/css/documentlist.css";

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
  const [selectedRows, setSelectedRows] = useState([]);
const [generateLoading, setGenerateLoading] = useState(false); // <-- ✅ Add this line


const FilteredDocs = documents.filter((doc) =>
  doc.name?.toLowerCase().includes(searchTerm?.toLowerCase())
);
 const totalItems = FilteredDocs.length;
const totalPages = Math.ceil(totalItems / rowsPerPage);
const start = page * rowsPerPage + 1;
const end = Math.min((page + 1) * rowsPerPage, totalItems);
const currentPage = page + 1; // 1-based

const getVisiblePages = () => {
  return Array.from({ length: totalPages }, (_, i) => i + 1);
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
  setLoading(true);
  try {
    const response = await adminAxios.get("/api/v1/data-spaces/");
    const mappedDocs = response.data.map((space, index) => ({
      _id: space.data_space_id,
      name: space.name,
      description: space.description,
      category: space.category,
      sub_category: space.sub_category,
      created_at: space.created_at,
      document_count: space.document_count,
    }));
    setDocuments(mappedDocs);
    // console.log("Fetched data spaces:", mappedDocs);
  } catch (error) {
    console.error("Error fetching data spaces:", error);
  } finally {
    setLoading(false);
  }
};


const handleGenerateClick = async (doc) => {
  if (generateLoading) return;

  try {
    setGenerateLoading(true);
    setSelectedDocumentName(doc.file_name);

    const formData = new FormData();
    formData.append("data_space_id", doc._id);
    formData.append("model_name", "Openai");

    // Step 1: POST to trigger test case generation
    const response = await adminAxios.post(
      "/api/v1/documents/batch-generate-test-cases/",
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    const generationId = response.data.generation_id;
    const taskId = response.data.task_id;

    // Step 2: GET generation status
    const statusRes = await adminAxios.get(
      `/api/v1/documents/generation-status/?data_space_id=${doc._id}`
    );

    console.log("✅ Generation status:", statusRes.data);

    // Step 3: Navigate to configurator
    navigate("/uiux-configurator", {
      state: {
        doc,
        task_id: taskId,
        data_space_id: doc._id,
        generation_id: generationId,
        status: statusRes.data, // optional: pass the generation status
      },
    });

  } catch (error) {
    console.error("❌ Error:", error);
  } finally {
    setGenerateLoading(false);
  }
};

  useEffect(() => {
    fetchDocuments();
  }, []);



  return (
   <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* <Header onLogout={handleLogout} /> */}
      <Box sx={{ mt: 8, px: 5, flex: 1,mb:7 }}>
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
            color: 'var(--primary-blue)',
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
          Dataspace
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
    <TableCell padding="checkbox">
      {/* Optional: master checkbox for selecting all */}
      {/* <Checkbox
        indeterminate={selectedRows.length > 0 && selectedRows.length < totalItems}
        checked={selectedRows.length === totalItems}
        onChange={(e) => {
          const checked = e.target.checked;
          setSelectedRows(checked ? FilteredDocs.map(doc => doc._id) : []);
        }}
      /> */}
    </TableCell>
    <TableCell sx={{ fontWeight: "bold" }}>Data Space Name</TableCell>
    <TableCell sx={{ fontWeight: "bold" }}>Category</TableCell>
    <TableCell sx={{ fontWeight: "bold" }}>Subcategory</TableCell>
    <TableCell sx={{ fontWeight: "bold" }}>Documents</TableCell>
    <TableCell sx={{ fontWeight: "bold" }}>Created At</TableCell>
    <TableCell sx={{ fontWeight: "bold" }}>Actions</TableCell>
  </TableRow>
</TableHead>


       <TableBody>
  {[...Array(rowsPerPage)].map((_, index) => (
    <TableRow key={index}>
      <TableCell padding="checkbox">
        <Skeleton variant="rectangular" width={18} height={18} />
      </TableCell>
      <TableCell><Skeleton variant="rectangular" width="80%" height={20} /></TableCell>
      <TableCell><Skeleton variant="rectangular" width="60%" height={20} /></TableCell>
      <TableCell><Skeleton variant="rectangular" width="60%" height={20} /></TableCell>
      <TableCell><Skeleton variant="text" width={30} /></TableCell>
      <TableCell><Skeleton variant="rectangular" width="60%" height={20} /></TableCell>
      <TableCell><Skeleton variant="rectangular" width={30} height={20} /></TableCell>
    </TableRow>
  ))}
</TableBody>
              </Table>
            </TableContainer>
          ) : (
            <TableContainer className="documentlist_tableContainer">
      <Table aria-label="documents table">
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                disableRipple
                indeterminate={selectedRows.length > 0 && selectedRows.length < totalItems}
                checked={selectedRows.length === totalItems}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setSelectedRows(checked ? FilteredDocs.map(doc => doc._id) : []);
                }}
                className="documentlist_checkbox"
              />
            </TableCell>
            <TableCell className="documentlist_header">Data Space Name</TableCell>
            <TableCell className="documentlist_header">Category</TableCell>
            <TableCell className="documentlist_header">Subcategory</TableCell>
            <TableCell className="documentlist_header">Documents</TableCell>
            <TableCell className="documentlist_header">Created At</TableCell>
            <TableCell className="documentlist_header">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {documents
            .filter(doc =>
              doc.name?.toLowerCase().includes(searchTerm?.toLowerCase())
            )
            .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
            .map((doc) => (
              <TableRow key={doc._id}>
                <TableCell padding="checkbox">
                  <Checkbox
                    disableRipple
                    checked={selectedRows.includes(doc._id)}
                    onChange={(e) => {
                      const checked = e.target.checked;
                      setSelectedRows((prev) =>
                        checked ? [...prev, doc._id] : prev.filter(id => id !== doc._id)
                      );
                    }}
                    className="documentlist_checkbox"
                  />
                </TableCell>
                <TableCell
                  onClick={() => handleGenerateClick(doc)}
                  className="documentlist_clickableCell"
                >
                  {doc.name}
                </TableCell>

                <TableCell className="documentlist_dimmedText">{doc.category}</TableCell>
                <TableCell className="documentlist_dimmedText">{doc.sub_category}</TableCell>
                <TableCell className="documentlist_dimmedText">{doc.document_count}</TableCell>
                <TableCell className="documentlist_dimmedText">{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton
                  disableRipple
                    size="small"
                    onClick={handleClick}
                    className="documentlist_actionIcon"
                  >
                    <MoreVertIcon className="documentlist_moreIcon" />
                  </IconButton>
                  <Menu
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                    disabled
                    disableRipple
                    PaperProps={{
                      elevation: 0,
                      className: 'documentlist_menuPaper',
                    }}
                    anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                    transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                  >
                    <MenuItem onClick={handleClose} disabled >
                      <ListItemIcon>
                        <img src={DeleteIcon} width={18} height={18} alt="Delete" />
                      </ListItemIcon>
                      <ListItemText
                        primaryTypographyProps={{ className: 'documentlist_deleteText' }}
                      >
                        Delete
                      </ListItemText>
                    </MenuItem>
                  </Menu>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </TableContainer>
          )}

           <Box className="documentlist_footerContainer">
      <Box className="documentlist_footerRow">
        {/* Left Controls */}
        <Box className="documentlist_leftControls">
          <Box className="documentlist_dropdownContainer">
            <Typography variant="body2" className="documentlist_dropdownLabel">
              Show
            </Typography>
            <Select
              size="small"
              value={rowsPerPage}
              onChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              className="documentlist_rowsPerPageSelect"
            >
              {[5, 10, 25].map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            <Typography variant="body2" className="documentlist_dropdownLabel">Entries</Typography>
          </Box>

          <Typography variant="body2" className="documentlist_entriesInfo">
            Showing {start} to {end} of {totalItems} entries
          </Typography>
        </Box>

        {/* Right Controls */}
        <div className="documentlist_paginationControls">
          <PaginationItem
            disableRipple
            type="previous"
            disabled={currentPage === 1}
            onClick={() => setPage((prev) => Math.max(prev - 1, 0))}
            slots={{ previous: () => <span>Previous</span> }}
            className="documentlist_paginationItem"
          />

          {getVisiblePages().map((pg) => (
            <PaginationItem
              disableRipple
              key={pg}
              page={pg}
              selected={pg === currentPage}
              onClick={() => setPage(pg - 1)}
              className={`documentlist_paginationItem ${pg === currentPage ? 'Mui-selected' : ''}`}
            />
          ))}

          <PaginationItem
            disableRipple
            type="next"
            disabled={currentPage === totalPages}
            onClick={() => setPage((prev) => Math.min(prev + 1, totalPages - 1))}
            slots={{ next: () => <span>Next</span> }}
            className="documentlist_paginationItem"
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

