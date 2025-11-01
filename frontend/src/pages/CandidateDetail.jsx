import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Chip,
  CircularProgress,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Button,
  Stepper,
  Step,
  StepLabel,
  IconButton,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import axios from 'axios';
import QuestionGenerator from '../components/QuestionGenerator';
import StageManagement from '../components/StageManagement';
import { API_BASE_URL } from '../config';

function CandidateDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCandidateDetail();
  }, [id]);

  const fetchCandidateDetail = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/candidates/${id}`);
      setCandidate(response.data);
    } catch (error) {
      console.error('Failed to fetch candidate detail:', error);
    } finally {
      setLoading(false);
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

  const handleExportEvaluations = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/candidates/${id}/evaluations/export`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `evaluations_${candidate.candidate_number}_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export evaluations:', error);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!candidate) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography variant="h6">候補者が見つかりませんでした</Typography>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/candidates')}
          sx={{ mt: 2 }}
        >
          一覧に戻る
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/candidates')}
          >
            一覧に戻る
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate(`/candidates/${id}/edit`)}
          >
            編集
          </Button>
        </Box>

        {/* 基本情報 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h4" component="h1">
                  {candidate.name}
                </Typography>
                <Chip
                  label={candidate.overall_status}
                  color={getStatusColor(candidate.overall_status)}
                />
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                候補者番号
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                {candidate.candidate_number}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                応募職種
              </Typography>
              <Typography variant="body1">
                {candidate.job_posting_title || '未設定'}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                メールアドレス
              </Typography>
              <Typography variant="body1">
                {candidate.email || '-'}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                電話番号
              </Typography>
              <Typography variant="body1">
                {candidate.phone || '-'}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                登録日時
              </Typography>
              <Typography variant="body1">
                {new Date(candidate.created_at).toLocaleString('ja-JP')}
              </Typography>
            </Grid>

            {candidate.tags && candidate.tags.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  タグ
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {candidate.tags.map((tag, index) => (
                    <Chip key={index} label={tag} size="small" />
                  ))}
                </Box>
              </Grid>
            )}

            {candidate.notes && (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  備考
                </Typography>
                <Typography variant="body1">
                  {candidate.notes}
                </Typography>
              </Grid>
            )}
          </Grid>
        </Paper>

        {/* 選考段階の進捗 */}
        {candidate.stage_progress && candidate.stage_progress.length > 0 && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              選考段階の進捗
            </Typography>
            <Stepper activeStep={candidate.stage_progress.length - 1} sx={{ mt: 2 }}>
              {candidate.stage_progress.map((stage) => (
                <Step key={stage.stage_id}>
                  <StepLabel>
                    <Typography variant="body2">{stage.stage_name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {stage.status}
                    </Typography>
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </Paper>
        )}

        {/* 選考段階管理 */}
        <StageManagement
          candidateId={parseInt(id)}
          currentStatus={candidate.overall_status}
          currentStage={
            candidate.stage_progress && candidate.stage_progress.length > 0
              ? candidate.stage_progress[candidate.stage_progress.length - 1].stage_name
              : null
          }
          onStatusUpdate={fetchCandidateDetail}
        />

        {/* 評価履歴 */}
        {candidate.evaluations && candidate.evaluations.length > 0 && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                評価履歴
              </Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={<DownloadIcon />}
                onClick={handleExportEvaluations}
              >
                CSVエクスポート
              </Button>
            </Box>

            {candidate.evaluations.map((evaluation, index) => (
              <Card key={evaluation.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">
                      {evaluation.stage_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(evaluation.created_at).toLocaleString('ja-JP')}
                    </Typography>
                  </Box>

                  <Divider sx={{ mb: 2 }} />

                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        評価者: {evaluation.evaluator_name}
                      </Typography>
                    </Grid>

                    {/* 評価スコア */}
                    {evaluation.scores && Object.keys(evaluation.scores).length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom>
                          評価項目
                        </Typography>
                        <List dense>
                          {Object.entries(evaluation.scores).map(([key, value]) => (
                            <ListItem key={key}>
                              <ListItemText
                                primary={key}
                                secondary={typeof value === 'object' ? JSON.stringify(value) : value}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}

                    {/* 強み */}
                    {evaluation.strengths && evaluation.strengths.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom color="success.main">
                          強み
                        </Typography>
                        <List dense>
                          {evaluation.strengths.map((strength, idx) => (
                            <ListItem key={idx}>
                              <ListItemText primary={`• ${strength}`} />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}

                    {/* 懸念点 */}
                    {evaluation.concerns && evaluation.concerns.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom color="warning.main">
                          懸念点
                        </Typography>
                        <List dense>
                          {evaluation.concerns.map((concern, idx) => (
                            <ListItem key={idx}>
                              <ListItemText primary={`• ${concern}`} />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}

                    {/* コメント */}
                    {evaluation.comments && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom>
                          総合コメント
                        </Typography>
                        <Typography variant="body2">
                          {evaluation.comments}
                        </Typography>
                      </Grid>
                    )}

                    {/* 推薦 */}
                    {evaluation.recommendation && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom>
                          推薦
                        </Typography>
                        <Typography variant="body2">
                          {evaluation.recommendation}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </Paper>
        )}

        {/* AI質問生成 */}
        <QuestionGenerator
          candidateId={parseInt(id)}
          stages={candidate.stage_progress || []}
        />
      </Box>
    </Container>
  );
}

export default CandidateDetail;
