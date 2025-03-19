import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Snackbar,
  Alert,
  TextField,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import axios from "axios";

const VisuallyHiddenInput = styled("input")`
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  height: 1px;
  overflow: hidden;
  position: absolute;
  bottom: 0;
  left: 0;
  white-space: nowrap;
  width: 1px;
`;

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [movieName, setMovieName] = useState("");
  const [recognizedName, setRecognizedName] = useState("");

  const handleFileSelect = (event) => {
    setSelectedFiles(Array.from(event.target.files));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError("Please select files to process");
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("extract_hardcoded", "false");

        const response = await axios.post(
          "http://localhost:8001/api/videos/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        setResults((prev) => [...prev, response.data]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Error processing videos");
    } finally {
      setProcessing(false);
    }
  };

  const handleRecognizeName = async () => {
    if (!movieName) {
      setError("Please enter a movie name");
      return;
    }

    try {
      const response = await axios.post(
        "http://localhost:8001/api/recognize/name",
        {
          name: movieName,
        }
      );
      setRecognizedName(response.data.official_name);
    } catch (err) {
      setError(err.response?.data?.detail || "Error recognizing movie name");
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Video Analysis and Metadata Management
        </Typography>

        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Process Videos
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Button
              component="label"
              variant="contained"
              startIcon={<CloudUploadIcon />}
            >
              Select Videos
              <VisuallyHiddenInput
                type="file"
                multiple
                onChange={handleFileSelect}
              />
            </Button>
          </Box>
          {selectedFiles.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1">
                Selected files: {selectedFiles.map((f) => f.name).join(", ")}
              </Typography>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={processing}
                sx={{ mt: 1 }}
              >
                {processing ? <CircularProgress size={24} /> : "Process Videos"}
              </Button>
            </Box>
          )}
        </Paper>

        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recognize Movie Name
          </Typography>
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <TextField
              label="Movie Name or Filename"
              value={movieName}
              onChange={(e) => setMovieName(e.target.value)}
              fullWidth
            />
            <Button
              variant="contained"
              onClick={handleRecognizeName}
              disabled={!movieName}
            >
              Recognize
            </Button>
          </Box>
          {recognizedName && (
            <Typography sx={{ mt: 2 }}>
              Recognized Name: {recognizedName}
            </Typography>
          )}
        </Paper>

        {results.length > 0 && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Results
            </Typography>
            <List>
              {results.map((result, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={result.official_name || result.original_name}
                    secondary={`Subtitles: ${result.subtitles.length}, DB ID: ${result.db_id}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
}

export default App;
