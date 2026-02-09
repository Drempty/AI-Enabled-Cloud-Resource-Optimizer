import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Warning,
  Cloud,
  Speed
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import axios from 'axios';

const StatCard = ({ title, value, icon: Icon, color, trend }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
          {trend && (
            <Typography variant="body2" sx={{ color: trend > 0 ? 'success.main' : 'error.main', display: 'flex', alignItems: 'center', mt: 1 }}>
              {trend > 0 ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
              {Math.abs(trend)}% vs last month
            </Typography>
          )}
        </Box>
        <Icon sx={{ fontSize: 48, color: color, opacity: 0.3 }} />
      </Box>
    </CardContent>
  </Card>
);

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [resources, setResources] = useState([]);
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [resourcesRes] = await Promise.all([
        axios.get('/api/v1/resources')
      ]);
      
      setResources(resourcesRes.data);
      
      // Generate sample metrics for demo
      const sampleMetrics = Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        cpu: Math.random() * 40 + 30,
        memory: Math.random() * 30 + 40,
        cost: Math.random() * 20 + 10
      }));
      setMetrics(sampleMetrics);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const totalMonthlyCost = resources.reduce((sum, r) => sum + (r.cost_per_hour * 730), 0);
  const potentialSavings = totalMonthlyCost * 0.25; // Estimated 25% savings

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Overview of your cloud resources and optimization opportunities
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Resources"
            value={resources.length}
            icon={Cloud}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Monthly Cost"
            value={`$${totalMonthlyCost.toFixed(2)}`}
            icon={AttachMoney}
            color="#f57c00"
            trend={-8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Potential Savings"
            value={`$${potentialSavings.toFixed(2)}`}
            icon={TrendingDown}
            color="#388e3c"
            trend={15}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Utilization"
            value="54%"
            icon={Speed}
            color="#7b1fa2"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Resource Utilization (24h)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cpu" stroke="#1976d2" name="CPU %" />
                <Line type="monotone" dataKey="memory" stroke="#dc004e" name="Memory %" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Cost by Provider
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                { provider: 'AWS', cost: totalMonthlyCost * 0.6 },
                { provider: 'Azure', cost: totalMonthlyCost * 0.3 },
                { provider: 'GCP', cost: totalMonthlyCost * 0.1 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="provider" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="cost" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Warning sx={{ mr: 1, color: 'warning.main' }} />
              Recent Recommendations
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                💡 <strong>prod-web-server-01</strong>: Scale down to t3.small to save $15.20/month
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                💡 <strong>dev-test-server-01</strong>: Under-utilized (8% avg CPU), consider terminating
              </Typography>
              <Typography variant="body2">
                💡 <strong>azure-analytics-vm</strong>: Upgrade to Standard_D8s_v3 for better performance
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
