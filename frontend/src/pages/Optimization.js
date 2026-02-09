import React from 'react';
import {
  Typography,
  Paper,
  Box,
  Card,
  CardContent,
  Chip,
  Button,
  Grid
} from '@mui/material';
import { TrendingDown, TrendingUp, SwapHoriz } from '@mui/icons-material';

const recommendations = [
  {
    id: 1,
    resource: 'prod-web-server-01',
    type: 'scale_down',
    current: 't3.medium',
    recommended: 't3.small',
    savings: 15.20,
    priority: 'high',
    impact: 'neutral'
  },
  {
    id: 2,
    resource: 'dev-test-server-01',
    type: 'terminate',
    current: 't3.large',
    recommended: 'N/A',
    savings: 60.74,
    priority: 'medium',
    impact: 'neutral'
  },
  {
    id: 3,
    resource: 'prod-api-server-01',
    type: 'rightsize',
    current: 'm5.large',
    recommended: 'm5.xlarge',
    savings: -20.00,
    priority: 'high',
    impact: 'improved'
  }
];

function Optimization() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Cost Optimization</Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        AI-driven recommendations to optimize your cloud spending
      </Typography>

      <Paper sx={{ p: 3, mb: 3, bgcolor: 'success.light' }}>
        <Typography variant="h5" gutterBottom>
          💰 Total Potential Savings: $55.94/month
        </Typography>
        <Typography variant="body2">
          Based on current usage patterns and AI analysis
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {recommendations.map((rec) => (
          <Grid item xs={12} key={rec.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6">{rec.resource}</Typography>
                    <Chip 
                      label={rec.priority.toUpperCase()} 
                      color={rec.priority === 'high' ? 'error' : 'warning'}
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="h5" color={rec.savings > 0 ? 'success.main' : 'error.main'}>
                      {rec.savings > 0 ? '+' : ''} ${Math.abs(rec.savings).toFixed(2)}/mo
                    </Typography>
                    <Typography variant="caption">
                      {rec.savings > 0 ? 'Savings' : 'Investment'}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {rec.type === 'scale_down' && <TrendingDown sx={{ mr: 1 }} />}
                  {rec.type === 'scale_up' && <TrendingUp sx={{ mr: 1 }} />}
                  {rec.type === 'rightsize' && <SwapHoriz sx={{ mr: 1 }} />}
                  <Typography variant="body1">
                    <strong>{rec.current}</strong> → <strong>{rec.recommended}</strong>
                  </Typography>
                </Box>

                <Typography variant="body2" color="textSecondary" paragraph>
                  {rec.type === 'scale_down' && 'Resource is under-utilized. Safe to downsize.'}
                  {rec.type === 'terminate' && 'Resource has minimal activity. Consider terminating.'}
                  {rec.type === 'rightsize' && 'Upgrade recommended for better performance.'}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button variant="contained" size="small">Apply</Button>
                  <Button variant="outlined" size="small">Details</Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Optimization;
