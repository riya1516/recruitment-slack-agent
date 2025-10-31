import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function JobPostingsList() {
  const [jobPostings, setJobPostings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobPostings();
  }, []);

  const fetchJobPostings = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/job-postings/`);
      setJobPostings(response.data);
    } catch (error) {
      console.error('Failed to fetch job postings:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            募集要項一覧
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            component={RouterLink}
            to="/job-postings/new"
          >
            新規作成
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>職種</TableCell>
                <TableCell>部署</TableCell>
                <TableCell>雇用形態</TableCell>
                <TableCell>ステータス</TableCell>
                <TableCell align="right">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {jobPostings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    募集要項がありません。新規作成してください。
                  </TableCell>
                </TableRow>
              ) : (
                jobPostings.map((job) => (
                  <TableRow key={job.id} hover>
                    <TableCell>{job.title}</TableCell>
                    <TableCell>{job.department || '-'}</TableCell>
                    <TableCell>{job.employment_type || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={job.is_active ? 'アクティブ' : '非アクティブ'}
                        color={job.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Button size="small">詳細</Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
}

export default JobPostingsList;
