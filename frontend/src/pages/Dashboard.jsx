import { Container, Typography, Grid, Card, CardContent, CardActions, Button, Box, Paper, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import PersonIcon from '@mui/icons-material/Person';
import WorkIcon from '@mui/icons-material/Work';
import AssessmentIcon from '@mui/icons-material/Assessment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import DownloadIcon from '@mui/icons-material/Download';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

function Dashboard() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          ダッシュボード
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          採用選考支援システムへようこそ
        </Typography>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <WorkIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6">
                    募集要項管理
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  募集要項の作成・編集・管理を行います。複数の募集要項を保持し、それぞれに評価基準や選考段階を設定できます。
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" component={RouterLink} to="/job-postings">
                  募集要項を見る
                </Button>
                <Button size="small" component={RouterLink} to="/job-postings/new">
                  新規作成
                </Button>
              </CardActions>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6">
                    選考者管理
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  選考者の登録・検索・評価を行います。選考段階ごとの評価や要点サマリーを確認できます。
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" component={RouterLink} to="/candidates">
                  選考者を見る
                </Button>
              </CardActions>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AssessmentIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6">
                    AI評価・質問生成
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  AI自動評価、選考段階別の質問生成、評価履歴のCSVエクスポートなど、AIを活用した採用支援機能。
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" component={RouterLink} to="/candidates">
                  選考者で確認
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>

        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            実装済み機能
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Slack連携"
                    secondary="PDFアップロードで自動評価・DB保存"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SmartToyIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="AI質問生成"
                    secondary="選考段階別に30問の面接質問を自動生成"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="評価履歴管理"
                    secondary="段階別の評価履歴と詳細スコア表示"
                  />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={6}>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <TrendingUpIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="選考段階管理"
                    secondary="ステータス更新・次段階への遷移"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <DownloadIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="CSV出力"
                    secondary="候補者一覧・評価履歴・面接質問"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="募集要項管理"
                    secondary="複数の募集要項と評価基準の設定"
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </Paper>

        <Paper sx={{ p: 3, mt: 3, bgcolor: 'primary.light', color: 'white' }}>
          <Typography variant="h6" gutterBottom>
            使い方
          </Typography>
          <Typography variant="body2" paragraph>
            1. 募集要項を作成（職種、必須スキル、評価基準を設定）
          </Typography>
          <Typography variant="body2" paragraph>
            2. Slackで候補者のPDFをアップロード → AIが自動評価
          </Typography>
          <Typography variant="body2" paragraph>
            3. Web管理画面で候補者を確認 → 詳細ページでAI質問生成
          </Typography>
          <Typography variant="body2" paragraph>
            4. 面接実施 → 評価入力 → 次段階へ進める
          </Typography>
          <Typography variant="body2">
            5. 必要に応じてCSVエクスポート（候補者一覧・評価履歴・質問）
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}

export default Dashboard;
