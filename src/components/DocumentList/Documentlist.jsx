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
import "./header.css";
import Footer from "../../Layout/Footer";

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
    console.log("Fetched data spaces:", mappedDocs);
  } catch (error) {
    console.error("Error fetching data spaces:", error);
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
            data_space_id: doc._id, // 👈 Add this line to pass the data_space_id
        },
      });
    } else {
      // ✅ Already processed, skip generation
      navigate('/uiux-configurator', {
        state: {
          doc,
          file_id: doc.file_id,
              data_space_id: doc._id, // 👈 Add this line to pass the data_space_id
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
            <TableContainer sx={{ width: "100%", border: "1px solid #e6e6e6", borderRadius: "10px", borderBottom: "none" }}>
              <Table aria-label="documents table">
               <TableHead>
  <TableRow>
    <TableCell padding="checkbox">
      {/* Optional: master checkbox for selecting all */}
      <Checkbox
      disableRipple
        indeterminate={selectedRows.length > 0 && selectedRows.length < totalItems}
        checked={selectedRows.length === totalItems}
        onChange={(e) => {
          const checked = e.target.checked;
          setSelectedRows(checked ? FilteredDocs.map(doc => doc._id) : []);
        }}
          sx={{
    color: '#c4c4c4',
    '&.Mui-checked': {
      color: '#000080', // your desired checked color
    },
    '&.MuiCheckbox-indeterminate': {
      color: '#000080', // minus icon color
    },
    '& .MuiSvgIcon-root': {
      borderRadius: '4px',
    },
  }}
      />
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
              sx={{
    color: '#c4c4c4',
    '&.Mui-checked': {
      color: '#000080', // your desired checked color
    },
    '& .MuiSvgIcon-root': {
      borderRadius: '4px',
    },
  }}
          />
        </TableCell>
        <TableCell 
          onClick={async () => await handleGenerateClick(doc)}
          sx={{ cursor: "pointer", color: "navy" }}
        >
          {doc.name}
        </TableCell>
        <TableCell sx={{ color: "#8e8e8e" }}>{doc.category}</TableCell>
        <TableCell sx={{ color: "#8e8e8e" }}>{doc.sub_category}</TableCell>
        <TableCell sx={{ color: "#8e8e8e" }}>{doc.document_count}</TableCell>
        <TableCell sx={{ color: "#8e8e8e" }}>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
         <TableCell>
          <IconButton
            size="small"
            onClick={handleClick}
            sx={{ '&:hover': { backgroundColor: 'transparent' }, padding: 0 }}
          >
            <MoreVertIcon sx={{ fontSize: 22, color: "#8e8e8e" }} />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            disabled={true}
            disableRipple
            PaperProps={{
              elevation: 0,
              sx: {
                backgroundColor: "#FBFBFB",
                borderRadius: 5,
                paddingY: 0,
                minWidth: 100,
              },
            }}
            anchorOrigin={{
    vertical: "top",     // Align top of menu with anchor
    horizontal: "right", // Anchor from the right edge of the icon
  }}
  transformOrigin={{
    vertical: "top",      // Transform from top of the menu
    horizontal: "left",   // Menu grows to the right
  }}
          >
            <MenuItem onClick={handleClose} disabled={true}>
              <ListItemIcon>
                <img src={DeleteIcon} width={18} height={18} alt="Delete" />
              </ListItemIcon>
              <ListItemText primaryTypographyProps={{ sx: { color: "#666666" } }}>Delete</ListItemText>
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
<Typography variant="body2" sx={{ color: "#8e8e8e" }}>
  Show
</Typography>
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

