import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
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
  TextField,
  MenuItem,
  Button,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function CandidatesList() {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchCandidates();
  }, [search, statusFilter]);

  const fetchCandidates = async () => {
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;

      const response = await axios.get(`${API_BASE_URL}/candidates/`, { params });
      setCandidates(response.data);
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;

      const response = await axios.get(`${API_BASE_URL}/candidates/export`, {
        params,
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `candidates_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export CSV:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case '選考中':
        return 'primary';
      case '合格':
        return 'success';
      case '不合格':
        return 'error';
      case '保留':
        return 'warning';
      default:
        return 'default';
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
            選考者一覧
          </Typography>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExportCSV}
          >
            CSVエクスポート
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <TextField
            label="検索"
            placeholder="名前またはメールアドレス"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flexGrow: 1 }}
          />
          <TextField
            select
            label="ステータス"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">すべて</MenuItem>
            <MenuItem value="選考中">選考中</MenuItem>
            <MenuItem value="合格">合格</MenuItem>
            <MenuItem value="不合格">不合格</MenuItem>
            <MenuItem value="保留">保留</MenuItem>
          </TextField>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>候補者番号</TableCell>
                <TableCell>名前</TableCell>
                <TableCell>メールアドレス</TableCell>
                <TableCell>ステータス</TableCell>
                <TableCell>登録日時</TableCell>
                <TableCell align="right">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {candidates.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    選考者がいません
                  </TableCell>
                </TableRow>
              ) : (
                candidates.map((candidate) => (
                  <TableRow key={candidate.id} hover>
                    <TableCell>{candidate.candidate_number}</TableCell>
                    <TableCell>{candidate.name}</TableCell>
                    <TableCell>{candidate.email || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={candidate.overall_status}
                        color={getStatusColor(candidate.overall_status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(candidate.created_at).toLocaleDateString('ja-JP')}
                    </TableCell>
                    <TableCell align="right">
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => navigate(`/candidates/${candidate.id}`)}
                      >
                        詳細
                      </Button>
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

export default CandidatesList;
