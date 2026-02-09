"""
Optimization service for cost and performance recommendations
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np


# Instance type pricing and specifications (AWS example)
INSTANCE_CATALOG = {
    'aws': {
        't3.nano': {'vcpus': 2, 'memory': 0.5, 'cost_hour': 0.0052},
        't3.micro': {'vcpus': 2, 'memory': 1, 'cost_hour': 0.0104},
        't3.small': {'vcpus': 2, 'memory': 2, 'cost_hour': 0.0208},
        't3.medium': {'vcpus': 2, 'memory': 4, 'cost_hour': 0.0416},
        't3.large': {'vcpus': 2, 'memory': 8, 'cost_hour': 0.0832},
        't3.xlarge': {'vcpus': 4, 'memory': 16, 'cost_hour': 0.1664},
        't3.2xlarge': {'vcpus': 8, 'memory': 32, 'cost_hour': 0.3328},
        'm5.large': {'vcpus': 2, 'memory': 8, 'cost_hour': 0.096},
        'm5.xlarge': {'vcpus': 4, 'memory': 16, 'cost_hour': 0.192},
        'm5.2xlarge': {'vcpus': 8, 'memory': 32, 'cost_hour': 0.384},
        'm5.4xlarge': {'vcpus': 16, 'memory': 64, 'cost_hour': 0.768},
        'c5.large': {'vcpus': 2, 'memory': 4, 'cost_hour': 0.085},
        'c5.xlarge': {'vcpus': 4, 'memory': 8, 'cost_hour': 0.170},
        'c5.2xlarge': {'vcpus': 8, 'memory': 16, 'cost_hour': 0.340},
        'r5.large': {'vcpus': 2, 'memory': 16, 'cost_hour': 0.126},
        'r5.xlarge': {'vcpus': 4, 'memory': 32, 'cost_hour': 0.252},
    },
    'azure': {
        'Standard_B1s': {'vcpus': 1, 'memory': 1, 'cost_hour': 0.0104},
        'Standard_B2s': {'vcpus': 2, 'memory': 4, 'cost_hour': 0.0416},
        'Standard_D2s_v3': {'vcpus': 2, 'memory': 8, 'cost_hour': 0.096},
        'Standard_D4s_v3': {'vcpus': 4, 'memory': 16, 'cost_hour': 0.192},
        'Standard_D8s_v3': {'vcpus': 8, 'memory': 32, 'cost_hour': 0.384},
        'Standard_E2s_v3': {'vcpus': 2, 'memory': 16, 'cost_hour': 0.126},
        'Standard_E4s_v3': {'vcpus': 4, 'memory': 32, 'cost_hour': 0.252},
    }
}


class OptimizationService:
    """Service for generating optimization recommendations"""
    
    def __init__(self):
        self.instance_catalog = INSTANCE_CATALOG
    
    async def generate_recommendations(
        self,
        resource: Dict,
        metrics: List[Dict],
        predictions: Optional[List[float]] = None,
        cost_weight: float = 0.6,
        performance_weight: float = 0.4
    ) -> List[Dict]:
        """
        Generate optimization recommendations for a resource
        
        Args:
            resource: Resource information
            metrics: Historical metrics
            predictions: Predicted future usage
            cost_weight: Weight for cost optimization (0-1)
            performance_weight: Weight for performance optimization (0-1)
            
        Returns:
            List of recommendation dictionaries
        """
        if not metrics:
            return []
        
        provider = resource.get('provider', 'aws')
        current_type = resource.get('instance_type', 't3.medium')
        
        # Calculate current utilization
        avg_cpu = np.mean([m.get('cpu_usage', 0) for m in metrics])
        avg_memory = np.mean([m.get('memory_usage', 0) for m in metrics])
        max_cpu = np.max([m.get('cpu_usage', 0) for m in metrics])
        max_memory = np.max([m.get('memory_usage', 0) for m in metrics])
        
        # Use predictions if available
        if predictions and len(predictions) > 0:
            predicted_cpu = np.mean(predictions)
            predicted_max_cpu = np.max(predictions)
        else:
            predicted_cpu = avg_cpu
            predicted_max_cpu = max_cpu
        
        recommendations = []
        
        # Get current instance specs
        current_specs = self.instance_catalog.get(provider, {}).get(
            current_type,
            {'vcpus': 2, 'memory': 4, 'cost_hour': 0.05}
        )
        
        # Rule 1: Over-provisioned (scale down)
        if avg_cpu < 20 and avg_memory < 30 and max_cpu < 40:
            smaller_instances = self._find_smaller_instances(
                provider, current_type, avg_cpu, avg_memory
            )
            
            for instance_type, specs in smaller_instances:
                recommendation = self._create_recommendation(
                    resource,
                    current_type,
                    current_specs,
                    instance_type,
                    specs,
                    'scale_down',
                    'low',
                    f"Resource is under-utilized (avg CPU: {avg_cpu:.1f}%, avg Memory: {avg_memory:.1f}%)"
                )
                recommendations.append(recommendation)
        
        # Rule 2: Under-provisioned (scale up)
        elif max_cpu > 80 or max_memory > 85 or predicted_max_cpu > 80:
            larger_instances = self._find_larger_instances(
                provider, current_type, max_cpu, max_memory
            )
            
            for instance_type, specs in larger_instances:
                recommendation = self._create_recommendation(
                    resource,
                    current_type,
                    current_specs,
                    instance_type,
                    specs,
                    'scale_up',
                    'high',
                    f"Resource approaching capacity limits (max CPU: {max_cpu:.1f}%, max Memory: {max_memory:.1f}%)"
                )
                recommendations.append(recommendation)
        
        # Rule 3: Right-sizing opportunities
        rightsize_options = self._find_rightsize_options(
            provider, current_type, avg_cpu, avg_memory, max_cpu, max_memory
        )
        
        for instance_type, specs in rightsize_options:
            recommendation = self._create_recommendation(
                resource,
                current_type,
                current_specs,
                instance_type,
                specs,
                'rightsize',
                'medium',
                f"Better fit for current usage pattern (avg CPU: {avg_cpu:.1f}%, avg Memory: {avg_memory:.1f}%)"
            )
            recommendations.append(recommendation)
        
        # Rule 4: Terminate idle resources
        if avg_cpu < 5 and avg_memory < 10:
            recommendation = {
                'recommendation_type': 'terminate',
                'priority': 'medium',
                'current_instance_type': current_type,
                'recommended_instance_type': None,
                'current_cost_per_hour': current_specs['cost_hour'],
                'recommended_cost_per_hour': 0,
                'cost_savings_per_month': current_specs['cost_hour'] * 730,
                'performance_impact': 'neutral',
                'confidence_score': 0.95,
                'reasoning': f"Resource is idle (avg CPU: {avg_cpu:.1f}%, avg Memory: {avg_memory:.1f}%). Consider terminating if not needed.",
                'implementation_steps': [
                    'Verify resource is not needed for production workloads',
                    'Check for any scheduled jobs or dependencies',
                    'Create backup/snapshot if needed',
                    'Terminate the instance'
                ]
            }
            recommendations.append(recommendation)
        
        # Sort recommendations by potential savings
        recommendations.sort(
            key=lambda x: x.get('cost_savings_per_month', 0),
            reverse=True
        )
        
        # Apply weights and re-rank
        for rec in recommendations:
            cost_score = rec.get('cost_savings_per_month', 0) / (current_specs['cost_hour'] * 730 + 1)
            perf_score = self._calculate_performance_score(rec)
            rec['weighted_score'] = cost_score * cost_weight + perf_score * performance_weight
        
        recommendations.sort(key=lambda x: x.get('weighted_score', 0), reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _find_smaller_instances(
        self,
        provider: str,
        current_type: str,
        avg_cpu: float,
        avg_memory: float
    ) -> List[Tuple[str, Dict]]:
        """Find suitable smaller instances"""
        catalog = self.instance_catalog.get(provider, {})
        current_specs = catalog.get(current_type, {'vcpus': 2, 'memory': 4})
        
        smaller = []
        for instance_type, specs in catalog.items():
            if (specs['memory'] < current_specs['memory'] and
                specs['vcpus'] <= current_specs['vcpus'] and
                specs['cost_hour'] < current_specs['cost_hour']):
                
                # Ensure it can handle current load with headroom
                if specs['memory'] >= (avg_memory / 100) * current_specs['memory'] * 1.5:
                    smaller.append((instance_type, specs))
        
        # Sort by cost savings
        smaller.sort(key=lambda x: current_specs['cost_hour'] - x[1]['cost_hour'], reverse=True)
        return smaller[:2]
    
    def _find_larger_instances(
        self,
        provider: str,
        current_type: str,
        max_cpu: float,
        max_memory: float
    ) -> List[Tuple[str, Dict]]:
        """Find suitable larger instances"""
        catalog = self.instance_catalog.get(provider, {})
        current_specs = catalog.get(current_type, {'vcpus': 2, 'memory': 4})
        
        larger = []
        for instance_type, specs in catalog.items():
            if (specs['memory'] > current_specs['memory'] or
                specs['vcpus'] > current_specs['vcpus']):
                
                # Ensure it provides adequate headroom
                if specs['memory'] >= current_specs['memory'] * 1.5:
                    larger.append((instance_type, specs))
        
        # Sort by cost (prefer cheaper upgrades)
        larger.sort(key=lambda x: x[1]['cost_hour'])
        return larger[:2]
    
    def _find_rightsize_options(
        self,
        provider: str,
        current_type: str,
        avg_cpu: float,
        avg_memory: float,
        max_cpu: float,
        max_memory: float
    ) -> List[Tuple[str, Dict]]:
        """Find right-sizing opportunities"""
        catalog = self.instance_catalog.get(provider, {})
        current_specs = catalog.get(current_type, {'vcpus': 2, 'memory': 4, 'cost_hour': 0.05})
        
        options = []
        for instance_type, specs in catalog.items():
            if instance_type == current_type:
                continue
            
            # Calculate efficiency score
            memory_efficiency = min(max_memory / 70, 1.0) if specs['memory'] >= current_specs['memory'] * (max_memory / 100) else 0
            cost_efficiency = (current_specs['cost_hour'] - specs['cost_hour']) / current_specs['cost_hour'] if specs['cost_hour'] < current_specs['cost_hour'] else 0
            
            if memory_efficiency > 0.7 and cost_efficiency > 0.1:
                options.append((instance_type, specs))
        
        # Sort by cost savings
        options.sort(
            key=lambda x: current_specs['cost_hour'] - x[1]['cost_hour'],
            reverse=True
        )
        return options[:2]
    
    def _create_recommendation(
        self,
        resource: Dict,
        current_type: str,
        current_specs: Dict,
        recommended_type: str,
        recommended_specs: Dict,
        rec_type: str,
        priority: str,
        reasoning: str
    ) -> Dict:
        """Create a recommendation dictionary"""
        cost_savings = (current_specs['cost_hour'] - recommended_specs['cost_hour']) * 730
        
        # Determine performance impact
        memory_change = (recommended_specs['memory'] - current_specs['memory']) / current_specs['memory']
        vcpu_change = (recommended_specs['vcpus'] - current_specs['vcpus']) / current_specs['vcpus']
        
        if memory_change > 0.2 or vcpu_change > 0.2:
            perf_impact = 'improved'
        elif memory_change < -0.2 or vcpu_change < -0.2:
            perf_impact = 'degraded'
        else:
            perf_impact = 'neutral'
        
        # Calculate confidence
        confidence = 0.85 if rec_type in ['scale_down', 'rightsize'] else 0.75
        
        return {
            'recommendation_type': rec_type,
            'priority': priority,
            'current_instance_type': current_type,
            'recommended_instance_type': recommended_type,
            'current_cost_per_hour': current_specs['cost_hour'],
            'recommended_cost_per_hour': recommended_specs['cost_hour'],
            'cost_savings_per_month': round(cost_savings, 2),
            'performance_impact': perf_impact,
            'confidence_score': confidence,
            'reasoning': reasoning,
            'implementation_steps': self._get_implementation_steps(rec_type),
            'details': {
                'current_vcpus': current_specs['vcpus'],
                'current_memory_gb': current_specs['memory'],
                'recommended_vcpus': recommended_specs['vcpus'],
                'recommended_memory_gb': recommended_specs['memory'],
                'vcpu_change_percent': round(vcpu_change * 100, 1),
                'memory_change_percent': round(memory_change * 100, 1)
            }
        }
    
    def _calculate_performance_score(self, recommendation: Dict) -> float:
        """Calculate performance score for a recommendation"""
        impact = recommendation.get('performance_impact', 'neutral')
        
        if impact == 'improved':
            return 1.0
        elif impact == 'neutral':
            return 0.7
        else:
            return 0.3
    
    def _get_implementation_steps(self, rec_type: str) -> List[str]:
        """Get implementation steps for recommendation type"""
        steps = {
            'scale_up': [
                'Create snapshot/backup of current instance',
                'Stop the instance during low-traffic period',
                'Change instance type in cloud console',
                'Start the instance and verify functionality',
                'Monitor performance for 24-48 hours'
            ],
            'scale_down': [
                'Monitor current load to confirm under-utilization',
                'Create snapshot/backup of current instance',
                'Schedule change during maintenance window',
                'Change instance type to recommended size',
                'Monitor performance and adjust if needed'
            ],
            'rightsize': [
                'Review current usage patterns',
                'Create snapshot/backup',
                'Apply instance type change during maintenance window',
                'Validate application performance',
                'Monitor metrics for optimization'
            ],
            'terminate': [
                'Verify resource is not needed',
                'Check for dependencies and scheduled jobs',
                'Create final backup/snapshot',
                'Terminate the instance',
                'Update infrastructure documentation'
            ]
        }
        
        return steps.get(rec_type, ['Review recommendation', 'Plan implementation', 'Execute change'])
