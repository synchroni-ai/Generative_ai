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
  TableContainer,
} from "@mui/material";
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
import GenerateDrawer from "../Generate/GenerateDrawer"; // adjust the path accordingly
import "./../../asessts/css/documentlist.css";

const Documentlist = () => {
  const [activeTab, setActiveTab] = useState("testcase");
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
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

  const toggleDrawer = (open) => () => setDrawerOpen(open);
  const handleUploadClick = () => setModalOpen(true);
  const handleModalClose = () => setModalOpen(false);
  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/");
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
      setDocuments(response.data.reverse());
      console.log("Fetched data:", response.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };




  const handleGenerateClick = async (doc) => {
  try {
    setSelectedDocumentName(doc.file_name); // Set document name for drawer
    setGenerateDrawerOpen(true); // Open the drawer

    // Make the POST API call
    const formData = new FormData();
    formData.append("file_id", doc._id);

    const response = await adminAxios.post("/generate_test_cases/", formData);
    console.log("Generated Test Cases:", response.data);

    // Optionally: update state with the response if needed
    setGenerateData(response.data);
        setTaskId(response.data.task_id); // 👈 Add this line

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
      <Box sx={{ mt: 10, px: 5, overflowY: "auto", height: "89vh", scrollbarWidth: 'thin' }}>
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: 'end', marginRight: "20px" }}>
          <Box className="search-container" sx={{ position: "relative", mr: 2, width: "250px" }}>
            <input
              type="text"
              placeholder="Search topics..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search className="basic-header-search-icon" />
          </Box>

          <Button
            onClick={handleUploadClick}
            sx={{
              textTransform: "none",
              fontWeight: "bold",
              color: "white",
              backgroundColor: "#000080",
              borderRadius: "10px",
              padding: "6px 16px",
            }}
          >
            New Document
          </Button>
        </Box>
        <Container maxWidth="xl" sx={{ mt: 8 }}>
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
                    <TableCell sx={{ fontWeight: "bold" }}>SNo</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>Document Name</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>Document Path</TableCell>
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
                        <TableCell>{page * rowsPerPage + index + 1}</TableCell>
                        <TableCell
                          // sx={{ cursor: "pointer", color: "#1976d2", textDecoration: "underline" }}
                          onClick={() => {
                            setTestCaseData(doc.llm_response_testcases);
                            setDrawerOpen(true);
                          }}
                        >
                          {doc.file_name}
                        </TableCell>
                        <TableCell>{doc.file_path}</TableCell>
                        {/* <TableCell>{doc.llm_response_latency}</TableCell> */}
                        <TableCell sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <span
                            style={{ fontSize: '14px', textDecoration: 'underline', color: '#1976d2', cursor: 'pointer' }}
                            onClick={() => handleGenerateClick(doc)}
                          >
                            Generate
                          </span>
                          <IconButton
                            size="small"
                            disableRipple
                            disableFocusRipple
                            disableTouchRipple
                            sx={{
                              '&:hover': {
                                backgroundColor: 'transparent',
                              },
                              padding: 0,
                            }}
                          >
                            <MoreVertIcon sx={{ fontSize: 18 }} />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
count={
  documents.filter((doc) =>
    doc.file_name?.toLowerCase().includes(searchTerm?.toLowerCase())
  ).length
}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(event, newPage) => setPage(newPage)}
            onRowsPerPageChange={(event) => {
              setRowsPerPage(parseInt(event.target.value, 10));
              setPage(0);
            }}
          />
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

