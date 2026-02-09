import React, { useState } from 'react';
import {
  Typography,
  Paper,
  Box,
  TextField,
  Button,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';

function Simulation() {
  const [results, setResults] = useState(null);

  const runSimulation = () => {
    // Mock simulation results
    setResults({
      avgCpu: 42.5,
      avgMemory: 55.3,
      totalCost: 487.20,
      savings: 62.50,
      recommendations: [
        'Peak usage occurs at 2 PM - consider auto-scaling',
        'Memory utilization is stable - current sizing is optimal'
      ]
    });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>What-If Simulation</Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Test different scaling scenarios before implementing changes
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Scenario Name"
              defaultValue="Production Scale-Down Test"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Duration (days)"
              defaultValue={30}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Instance Count"
              defaultValue={3}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={runSimulation}
              size="large"
            >
              Run Simulation
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {results && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>Avg CPU</Typography>
                <Typography variant="h4">{results.avgCpu}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>Avg Memory</Typography>
                <Typography variant="h4">{results.avgMemory}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>Total Cost</Typography>
                <Typography variant="h4">${results.totalCost}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: 'success.light' }}>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>Savings</Typography>
                <Typography variant="h4">${results.savings}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Recommendations</Typography>
              {results.recommendations.map((rec, idx) => (
                <Typography key={idx} variant="body2" sx={{ mb: 1 }}>
                  💡 {rec}
                </Typography>
              ))}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default Simulation;
