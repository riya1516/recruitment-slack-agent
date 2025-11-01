import { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  Grid,
  Snackbar,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function JobPostingCreate() {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    employment_type: '',
    description: '',
    requirements: [],
    preferred_skills: [],
    company_values: [],
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleArrayChange = (e, field) => {
    const value = e.target.value;
    const array = value.split('\n').filter(item => item.trim() !== '');
    setFormData(prev => ({
      ...prev,
      [field]: array
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API_BASE_URL}/job-postings/`, formData);
      setSnackbar({
        open: true,
        message: '募集要項を作成しました',
        severity: 'success'
      });
      setTimeout(() => {
        navigate('/job-postings');
      }, 1500);
    } catch (error) {
      console.error('Failed to create job posting:', error);
      setSnackbar({
        open: true,
        message: '募集要項の作成に失敗しました',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setImportResult(null);
    }
  };

  const handleFileImport = async () => {
    if (!selectedFile) {
      setSnackbar({
        open: true,
        message: 'CSVファイルを選択してください',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    setImportResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${API_BASE_URL}/job-postings/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setImportResult(response.data);
      setSelectedFile(null);

      if (response.data.success && response.data.success_count > 0) {
        setSnackbar({
          open: true,
          message: `${response.data.success_count}件の募集要項をインポートしました`,
          severity: 'success'
        });
        setTimeout(() => {
          navigate('/job-postings');
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to import job postings:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'CSVのインポートに失敗しました',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setImportResult(null);
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          募集要項の新規作成
        </Typography>

        {importResult && (
          <Alert severity={importResult.error_count > 0 ? 'warning' : 'success'} sx={{ mt: 2 }}>
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

        <Paper sx={{ p: 3, mt: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab label="手動入力" />
            <Tab label="CSVインポート" />
          </Tabs>

          {tabValue === 0 && (
            <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  label="職種名"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="例: ソフトウェアエンジニア"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="部署"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  placeholder="例: エンジニアリング部"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="雇用形態"
                  name="employment_type"
                  value={formData.employment_type}
                  onChange={handleChange}
                  placeholder="例: 正社員"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="職務内容"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="職務内容の詳細を記入してください"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="必須スキル・条件"
                  value={formData.requirements.join('\n')}
                  onChange={(e) => handleArrayChange(e, 'requirements')}
                  placeholder="1行に1つずつ記入してください&#10;例:&#10;Python, Java等のプログラミング言語の実務経験（2年以上）&#10;Webアプリケーション開発経験"
                  helperText="1行に1つずつ記入してください"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="優遇スキル"
                  value={formData.preferred_skills.join('\n')}
                  onChange={(e) => handleArrayChange(e, 'preferred_skills')}
                  placeholder="1行に1つずつ記入してください&#10;例:&#10;クラウドサービス（AWS, GCP）の利用経験&#10;アジャイル開発の経験"
                  helperText="1行に1つずつ記入してください"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="企業価値観"
                  value={formData.company_values.join('\n')}
                  onChange={(e) => handleArrayChange(e, 'company_values')}
                  placeholder="1行に1つずつ記入してください&#10;例:&#10;顧客志向&#10;チームワーク"
                  helperText="1行に1つずつ記入してください"
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/job-postings')}
                  >
                    キャンセル
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : '作成'}
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
                  ヘッダー行: 職種名, 部署, 雇用形態, 職務内容, 必須要件, 優遇要件
                </Typography>
                <br />
                <Typography variant="caption">
                  ※必須要件と優遇要件は「|」で区切ってください
                </Typography>
                <br />
                <Typography variant="caption">
                  例: ソフトウェアエンジニア, エンジニアリング部, 正社員, Webアプリ開発, Python経験|AWS経験, 機械学習知識|Docker経験
                </Typography>
              </Alert>

              <Box sx={{ mb: 3 }}>
                <input
                  accept=".csv"
                  style={{ display: 'none' }}
                  id="csv-file-input"
                  type="file"
                  onChange={handleFileChange}
                />
                <label htmlFor="csv-file-input">
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
                  onClick={() => navigate('/job-postings')}
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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default JobPostingCreate;
