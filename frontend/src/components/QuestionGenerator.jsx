import { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function QuestionGenerator({ candidateId, stages }) {
  const [selectedStageId, setSelectedStageId] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateQuestions = async () => {
    if (!selectedStageId) {
      setError('選考段階を選択してください');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/questions/generate`, {
        candidate_id: candidateId,
        stage_id: selectedStageId,
        num_questions: 30
      });

      setQuestions(response.data);
    } catch (err) {
      console.error('Failed to generate questions:', err);
      setError('質問の生成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadQuestions = async () => {
    if (!selectedStageId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${API_BASE_URL}/questions/candidate/${candidateId}/stage/${selectedStageId}`
      );

      setQuestions(response.data);
    } catch (err) {
      console.error('Failed to load questions:', err);
      setError('質問の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    if (!selectedStageId) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/questions/candidate/${candidateId}/stage/${selectedStageId}/export`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `questions_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to export CSV:', err);
      setError('CSVエクスポートに失敗しました');
    }
  };

  const groupedQuestions = questions.reduce((acc, q) => {
    const category = q.category || 'その他';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(q);
    return acc;
  }, {});

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        AI質問生成
      </Typography>

      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>選考段階</InputLabel>
          <Select
            value={selectedStageId}
            onChange={(e) => {
              setSelectedStageId(e.target.value);
              handleLoadQuestions();
            }}
            label="選考段階"
          >
            {stages && stages.map((stage) => (
              <MenuItem key={stage.stage_id} value={stage.stage_id}>
                {stage.stage_name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleGenerateQuestions}
            disabled={loading || !selectedStageId}
            startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          >
            {questions.length > 0 ? '質問を追加生成' : '質問を生成'}
          </Button>

          {questions.length > 0 && (
            <Button
              variant="outlined"
              onClick={handleExportCSV}
              startIcon={<DownloadIcon />}
            >
              CSVダウンロード
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {questions.length > 0 && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            生成された質問（{questions.length}問）
          </Typography>

          {Object.entries(groupedQuestions).map(([category, categoryQuestions]) => (
            <Accordion key={category} defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2">{category}</Typography>
                  <Chip label={`${categoryQuestions.length}問`} size="small" />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {categoryQuestions.map((question, index) => (
                    <ListItem key={question.id} sx={{ flexDirection: 'column', alignItems: 'flex-start', borderBottom: '1px solid #eee' }}>
                      <ListItemText
                        primary={
                          <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                            Q{index + 1}. {question.question_text}
                          </Typography>
                        }
                        secondary={
                          question.purpose && (
                            <Typography variant="caption" color="text.secondary">
                              目的: {question.purpose}
                            </Typography>
                          )
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}

      {!loading && questions.length === 0 && selectedStageId && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
          <Typography variant="body2">
            「質問を生成」ボタンをクリックして、面接質問を生成してください
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

export default QuestionGenerator;
