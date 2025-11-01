import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function CandidateEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [jobPostings, setJobPostings] = useState([]);
  const [formData, setFormData] = useState({
    job_posting_id: '',
    name: '',
    email: '',
    phone: '',
    notes: '',
  });

  useEffect(() => {
    fetchJobPostings();
    fetchCandidate();
  }, [id]);

  const fetchJobPostings = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/job-postings/`);
      setJobPostings(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch job postings:', error);
      setJobPostings([]);
    }
  };

  const fetchCandidate = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/candidates/${id}`);
      const candidate = response.data;

      setFormData({
        job_posting_id: candidate.job_posting_id || '',
        name: candidate.name || '',
        email: candidate.email || '',
        phone: candidate.phone || '',
        notes: candidate.notes || '',
      });
    } catch (error) {
      console.error('Failed to fetch candidate:', error);
      setError('候補者情報の取得に失敗しました');
    } finally {
      setLoading(false);
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
    setSaving(true);
    setError(null);

    try {
      await axios.put(`${API_BASE_URL}/candidates/${id}`, {
        ...formData,
        job_posting_id: parseInt(formData.job_posting_id),
      });

      navigate(`/candidates/${id}`);
    } catch (error) {
      console.error('Failed to update candidate:', error);
      setError('候補者情報の更新に失敗しました');
    } finally {
      setSaving(false);
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
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/candidates/${id}`)}
          sx={{ mb: 2 }}
        >
          戻る
        </Button>

        <Typography variant="h4" component="h1" gutterBottom>
          候補者情報の編集
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ p: 3 }}>
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
                    onClick={() => navigate(`/candidates/${id}`)}
                  >
                    キャンセル
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={saving || !formData.name || !formData.job_posting_id}
                  >
                    {saving ? <CircularProgress size={24} /> : '更新'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
    </Container>
  );
}

export default CandidateEdit;
