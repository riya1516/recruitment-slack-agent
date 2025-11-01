import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function CandidateCreate() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jobPostings, setJobPostings] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [formData, setFormData] = useState({
    job_posting_id: '',
    name: '',
    email: '',
    phone: '',
    notes: '',
  });

  useEffect(() => {
    fetchJobPostings();
  }, []);

  const fetchJobPostings = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/job-postings/`);
      const data = Array.isArray(response.data) ? response.data : [];
      setJobPostings(data);
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, job_posting_id: data[0].id }));
      }
    } catch (error) {
      console.error('Failed to fetch job postings:', error);
      setError('募集要項の取得に失敗しました');
      setJobPostings([]);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/candidates/`, {
        ...formData,
        job_posting_id: parseInt(formData.job_posting_id),
      });

      navigate(`/candidates/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create candidate:', error);
      setError('候補者の作成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setImportResult(null);
      setError(null);
    }
  };

  const handleFileImport = async () => {
    if (!selectedFile) {
      setError('CSVファイルを選択してください');
      return;
    }

    setLoading(true);
    setError(null);
    setImportResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${API_BASE_URL}/candidates/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setImportResult(response.data);
      setSelectedFile(null);

      // 成功した場合、少し待ってから一覧ページに戻る
      if (response.data.success && response.data.success_count > 0) {
        setTimeout(() => {
          navigate('/candidates');
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to import candidates:', error);
      setError(error.response?.data?.detail || 'CSVのインポートに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError(null);
    setImportResult(null);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/candidates')}
          sx={{ mb: 2 }}
        >
          一覧に戻る
        </Button>

        <Typography variant="h4" component="h1" gutterBottom>
          候補者の新規登録
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {importResult && (
          <Alert severity={importResult.error_count > 0 ? 'warning' : 'success'} sx={{ mb: 2 }}>
            <Typography variant="subtitle2">
              インポート完了: {importResult.success_count}件成功, {importResult.error_count}件失敗
            </Typography>
            {importResult.errors && importResult.errors.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption">エラー詳細:</Typography>
                <List dense>
                  {importResult.errors.map((err, idx) => (
                    <ListItem key={idx}>
                      <ListItemText primary={err} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Alert>
        )}

        <Paper sx={{ p: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab label="手動入力" />
            <Tab label="CSVインポート" />
          </Tabs>

          {tabValue === 0 && (
            <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  select
                  required
                  fullWidth
                  label="募集要項"
                  name="job_posting_id"
                  value={formData.job_posting_id}
                  onChange={handleChange}
                >
                  {jobPostings.map((job) => (
                    <MenuItem key={job.id} value={job.id}>
                      {job.job_title}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  label="氏名"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="メールアドレス"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="電話番号"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="備考"
                  name="notes"
                  multiline
                  rows={4}
                  value={formData.notes}
                  onChange={handleChange}
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/candidates')}
                  >
                    キャンセル
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading || !formData.name || !formData.job_posting_id}
                  >
                    {loading ? <CircularProgress size={24} /> : '登録'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
          )}

          {tabValue === 1 && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  CSVフォーマット
                </Typography>
                <Typography variant="caption">
                  ヘッダー行: 名前, メールアドレス, 電話番号, 応募職種ID, 備考
                </Typography>
                <br />
                <Typography variant="caption">
                  例: 山田太郎, yamada@example.com, 090-1234-5678, 1, 備考内容
                </Typography>
              </Alert>

              <Box sx={{ mb: 3 }}>
                <input
                  accept=".csv"
                  style={{ display: 'none' }}
                  id="candidate-csv-file-input"
                  type="file"
                  onChange={handleFileChange}
                />
                <label htmlFor="candidate-csv-file-input">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadFileIcon />}
                    fullWidth
                  >
                    CSVファイルを選択
                  </Button>
                </label>
                {selectedFile && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    選択されたファイル: {selectedFile.name}
                  </Typography>
                )}
              </Box>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/candidates')}
                >
                  キャンセル
                </Button>
                <Button
                  variant="contained"
                  onClick={handleFileImport}
                  disabled={loading || !selectedFile}
                >
                  {loading ? <CircularProgress size={24} /> : 'インポート'}
                </Button>
              </Box>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
}

export default CandidateCreate;
