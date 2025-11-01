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
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function StageManagement({ candidateId, currentStatus, currentStage, onStatusUpdate }) {
  const [newStatus, setNewStatus] = useState(currentStatus);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: null });

  const statusOptions = [
    { value: '選考中', label: '選考中', color: 'primary' },
    { value: '合格', label: '合格', color: 'success' },
    { value: '不合格', label: '不合格', color: 'error' },
    { value: '保留', label: '保留', color: 'warning' },
  ];

  const handleStatusUpdate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await axios.put(`${API_BASE_URL}/candidates/${candidateId}/status`, {
        status: newStatus
      });

      setSuccess(`ステータスを「${newStatus}」に更新しました`);
      if (onStatusUpdate) {
        onStatusUpdate();
      }
    } catch (err) {
      console.error('Failed to update status:', err);
      setError('ステータスの更新に失敗しました');
    } finally {
      setLoading(false);
      setConfirmDialog({ open: false, action: null });
    }
  };

  const handleAdvanceStage = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/candidates/${candidateId}/advance-stage`);

      setSuccess(`${response.data.previous_stage} → ${response.data.current_stage} に進めました`);
      if (onStatusUpdate) {
        onStatusUpdate();
      }
    } catch (err) {
      console.error('Failed to advance stage:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('段階の遷移に失敗しました');
      }
    } finally {
      setLoading(false);
      setConfirmDialog({ open: false, action: null });
    }
  };

  const openConfirmDialog = (action) => {
    setConfirmDialog({ open: true, action });
  };

  const closeConfirmDialog = () => {
    setConfirmDialog({ open: false, action: null });
  };

  const executeConfirmedAction = () => {
    if (confirmDialog.action === 'status') {
      handleStatusUpdate();
    } else if (confirmDialog.action === 'advance') {
      handleAdvanceStage();
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        選考段階管理
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          現在のステータス
        </Typography>
        <Chip
          label={currentStatus}
          color={statusOptions.find(opt => opt.value === currentStatus)?.color || 'default'}
          sx={{ mb: 2 }}
        />

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>新しいステータス</InputLabel>
          <Select
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            label="新しいステータス"
          >
            {statusOptions.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="contained"
          onClick={() => openConfirmDialog('status')}
          disabled={loading || newStatus === currentStatus}
          fullWidth
        >
          ステータスを更新
        </Button>
      </Box>

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          選考段階の遷移
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {currentStage ? `現在: ${currentStage}` : '段階情報なし'}
        </Typography>

        <Button
          variant="outlined"
          startIcon={<ArrowForwardIcon />}
          onClick={() => openConfirmDialog('advance')}
          disabled={loading}
          fullWidth
        >
          次の段階に進める
        </Button>
      </Box>

      {/* 確認ダイアログ */}
      <Dialog open={confirmDialog.open} onClose={closeConfirmDialog}>
        <DialogTitle>確認</DialogTitle>
        <DialogContent>
          <Typography>
            {confirmDialog.action === 'status' && `ステータスを「${newStatus}」に更新しますか？`}
            {confirmDialog.action === 'advance' && '候補者を次の選考段階に進めますか？'}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeConfirmDialog}>キャンセル</Button>
          <Button onClick={executeConfirmedAction} variant="contained" autoFocus>
            実行
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

export default StageManagement;
