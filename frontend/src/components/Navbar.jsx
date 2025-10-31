import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import WorkIcon from '@mui/icons-material/Work';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <WorkIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          採用管理システム
        </Typography>
        <Box>
          <Button color="inherit" component={RouterLink} to="/">
            ダッシュボード
          </Button>
          <Button color="inherit" component={RouterLink} to="/job-postings">
            募集要項
          </Button>
          <Button color="inherit" component={RouterLink} to="/candidates">
            選考者
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
