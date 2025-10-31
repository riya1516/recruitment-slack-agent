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
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function JobPostingCreate() {
  const navigate = useNavigate();
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
    }
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

        <Paper sx={{ p: 3, mt: 3 }}>
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
                  >
                    作成
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
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
