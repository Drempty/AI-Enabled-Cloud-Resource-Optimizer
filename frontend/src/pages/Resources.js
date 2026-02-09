import React, { useEffect, useState } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Typography,
  Box,
  Button
} from '@mui/material';
import { Delete, Edit, Add } from '@mui/icons-material';
import axios from 'axios';

function Resources() {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      const response = await axios.get('/api/v1/resources');
      setResources(response.data);
    } catch (error) {
      console.error('Error fetching resources:', error);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Cloud Resources</Typography>
        <Button variant="contained" startIcon={<Add />}>
          Add Resource
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Provider</TableCell>
              <TableCell>Instance Type</TableCell>
              <TableCell>Region</TableCell>
              <TableCell>vCPUs</TableCell>
              <TableCell>Memory (GB)</TableCell>
              <TableCell>Cost/Hour</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {resources.map((resource) => (
              <TableRow key={resource.id}>
                <TableCell>{resource.name}</TableCell>
                <TableCell>
                  <Chip label={resource.provider.toUpperCase()} size="small" />
                </TableCell>
                <TableCell>{resource.instance_type}</TableCell>
                <TableCell>{resource.region}</TableCell>
                <TableCell>{resource.vcpus}</TableCell>
                <TableCell>{resource.memory_gb}</TableCell>
                <TableCell>${resource.cost_per_hour}</TableCell>
                <TableCell>
                  <Chip 
                    label={resource.is_active ? 'Active' : 'Inactive'} 
                    color={resource.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton size="small"><Edit /></IconButton>
                  <IconButton size="small"><Delete /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Resources;
