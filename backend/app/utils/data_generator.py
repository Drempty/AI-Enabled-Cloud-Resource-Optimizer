"""
Data generator for creating sample metrics and resources
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Resource, Metric, CloudProvider, ResourceType


class DataGenerator:
    """Generate sample data for testing and demo purposes"""
    
    @staticmethod
    async def create_sample_resources(db: AsyncSession) -> List[Resource]:
        """Create sample cloud resources"""
        sample_resources = [
            {
                'name': 'prod-web-server-01',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.VM,
                'instance_type': 't3.medium',
                'region': 'us-east-1',
                'vcpus': 2,
                'memory_gb': 4,
                'cost_per_hour': 0.0416,
                'tags': {'environment': 'production', 'team': 'web'}
            },
            {
                'name': 'prod-api-server-01',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.VM,
                'instance_type': 'm5.large',
                'region': 'us-east-1',
                'vcpus': 2,
                'memory_gb': 8,
                'cost_per_hour': 0.096,
                'tags': {'environment': 'production', 'team': 'backend'}
            },
            {
                'name': 'dev-test-server-01',
                'provider': CloudProvider.AWS,
                'resource_type': ResourceType.VM,
                'instance_type': 't3.large',
                'region': 'us-west-2',
                'vcpus': 2,
                'memory_gb': 8,
                'cost_per_hour': 0.0832,
                'tags': {'environment': 'development', 'team': 'qa'}
            },
            {
                'name': 'azure-analytics-vm',
                'provider': CloudProvider.AZURE,
                'resource_type': ResourceType.VM,
                'instance_type': 'Standard_D4s_v3',
                'region': 'eastus',
                'vcpus': 4,
                'memory_gb': 16,
                'cost_per_hour': 0.192,
                'tags': {'environment': 'production', 'team': 'analytics'}
            },
        ]
        
        created_resources = []
        for resource_data in sample_resources:
            # Check if exists
            result = await db.execute(
                select(Resource).where(Resource.name == resource_data['name'])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                resource = Resource(**resource_data)
                db.add(resource)
                created_resources.append(resource)
        
        await db.commit()
        
        # Refresh all resources
        for resource in created_resources:
            await db.refresh(resource)
        
        return created_resources
    
    @staticmethod
    def generate_realistic_metrics(
        hours: int = 168,
        pattern: str = 'normal'
    ) -> List[Dict]:
        """
        Generate realistic metric patterns
        
        Args:
            hours: Number of hours of data to generate
            pattern: 'normal', 'overutilized', 'underutilized', 'bursty'
        """
        metrics = []
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for hour in range(hours):
            timestamp = base_time + timedelta(hours=hour)
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Generate patterns based on type
            if pattern == 'normal':
                # Normal business hours pattern
                if day_of_week < 5:  # Weekday
                    if 8 <= hour_of_day <= 18:  # Business hours
                        cpu = np.random.uniform(40, 70)
                        memory = np.random.uniform(50, 75)
                    else:
                        cpu = np.random.uniform(15, 35)
                        memory = np.random.uniform(30, 50)
                else:  # Weekend
                    cpu = np.random.uniform(10, 30)
                    memory = np.random.uniform(25, 45)
            
            elif pattern == 'overutilized':
                # Constantly high usage
                cpu = np.random.uniform(70, 95)
                memory = np.random.uniform(75, 90)
            
            elif pattern == 'underutilized':
                # Constantly low usage
                cpu = np.random.uniform(5, 20)
                memory = np.random.uniform(15, 30)
            
            elif pattern == 'bursty':
                # Random spikes
                if np.random.random() < 0.1:  # 10% chance of spike
                    cpu = np.random.uniform(80, 98)
                    memory = np.random.uniform(75, 90)
                else:
                    cpu = np.random.uniform(20, 40)
                    memory = np.random.uniform(30, 50)
            
            else:
                cpu = np.random.uniform(30, 60)
                memory = np.random.uniform(40, 65)
            
            # Network usage (correlated with CPU)
            network_in = cpu * np.random.uniform(0.5, 1.5)
            network_out = cpu * np.random.uniform(0.3, 1.0)
            
            # Disk operations
            disk_read = np.random.uniform(100, 1000)
            disk_write = np.random.uniform(50, 500)
            
            metric = {
                'timestamp': timestamp,
                'cpu_usage': round(cpu, 2),
                'memory_usage': round(memory, 2),
                'network_in_mb': round(network_in, 2),
                'network_out_mb': round(network_out, 2),
                'disk_read_ops': round(disk_read, 2),
                'disk_write_ops': round(disk_write, 2),
                'disk_usage': round(np.random.uniform(40, 75), 2),
                'request_count': int(cpu * 100),
                'error_rate': round(np.random.uniform(0, 2), 2),
                'response_time_ms': round(np.random.uniform(50, 200), 2)
            }
            
            metrics.append(metric)
        
        return metrics
    
    @staticmethod
    async def populate_sample_metrics(
        db: AsyncSession,
        resource_id: int,
        hours: int = 168,
        pattern: str = 'normal'
    ):
        """Populate database with sample metrics for a resource"""
        metrics_data = DataGenerator.generate_realistic_metrics(hours, pattern)
        
        for metric_data in metrics_data:
            metric = Metric(
                resource_id=resource_id,
                **metric_data
            )
            db.add(metric)
        
        await db.commit()
        
        return len(metrics_data)
