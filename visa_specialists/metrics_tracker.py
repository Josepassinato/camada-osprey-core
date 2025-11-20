"""
Metrics Tracker
Sistema de tracking de performance e analytics
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import json
from collections import defaultdict


class MetricsTracker:
    """Sistema de métricas e analytics"""
    
    def __init__(self):
        self.metrics_dir = Path(__file__).parent / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.metrics_dir / 'metrics.json'
        
        # Carregar métricas existentes
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Carrega métricas do arquivo"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            'total_requests': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'by_visa_type': {},
            'validation_results': [],
            'qa_scores': [],
            'processing_times': [],
            'start_date': datetime.now().isoformat()
        }
    
    def _save_metrics(self):
        """Salva métricas no arquivo"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def track_request(self, visa_type: str, success: bool, processing_time: float, 
                     validation_result: Dict[str, Any] = None, qa_score: float = None):
        """Registra uma requisição"""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_generations'] += 1
        else:
            self.metrics['failed_generations'] += 1
        
        # Por tipo de visto
        if visa_type not in self.metrics['by_visa_type']:
            self.metrics['by_visa_type'][visa_type] = {
                'count': 0,
                'success': 0,
                'failed': 0,
                'avg_processing_time': 0
            }
        
        visa_metrics = self.metrics['by_visa_type'][visa_type]
        visa_metrics['count'] += 1
        if success:
            visa_metrics['success'] += 1
        else:
            visa_metrics['failed'] += 1
        
        # Processing time
        self.metrics['processing_times'].append({
            'visa_type': visa_type,
            'time': processing_time,
            'timestamp': datetime.now().isoformat()
        })
        
        # Validation result
        if validation_result:
            self.metrics['validation_results'].append({
                'visa_type': visa_type,
                'is_valid': validation_result.get('is_valid', False),
                'missing_items_count': len(validation_result.get('missing_items', [])),
                'forbidden_items_count': len(validation_result.get('forbidden_items_found', [])),
                'timestamp': datetime.now().isoformat()
            })
        
        # QA score
        if qa_score is not None:
            self.metrics['qa_scores'].append({
                'visa_type': visa_type,
                'score': qa_score,
                'timestamp': datetime.now().isoformat()
            })
        
        # Salvar
        self._save_metrics()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard"""
        return {
            'overview': self._get_overview(),
            'by_visa_type': self._get_visa_type_stats(),
            'quality_trends': self._get_quality_trends(),
            'performance': self._get_performance_stats()
        }
    
    def _get_overview(self) -> Dict[str, Any]:
        """Estatísticas gerais"""
        total = self.metrics['total_requests']
        success = self.metrics['successful_generations']
        
        return {
            'total_requests': total,
            'successful_generations': success,
            'failed_generations': self.metrics['failed_generations'],
            'success_rate': (success / total * 100) if total > 0 else 0,
            'avg_qa_score': self._calculate_avg_qa_score()
        }
    
    def _get_visa_type_stats(self) -> Dict[str, Dict[str, Any]]:
        """Estatísticas por tipo de visto"""
        stats = {}
        
        for visa_type, data in self.metrics['by_visa_type'].items():
            stats[visa_type] = {
                'total': data['count'],
                'success': data['success'],
                'failed': data['failed'],
                'success_rate': (data['success'] / data['count'] * 100) if data['count'] > 0 else 0
            }
        
        return stats
    
    def _get_quality_trends(self) -> Dict[str, Any]:
        """Tendências de qualidade"""
        qa_scores = self.metrics['qa_scores']
        
        if not qa_scores:
            return {'average': 0, 'trend': 'no_data'}
        
        recent_scores = [s['score'] for s in qa_scores[-10:]]  # Últimos 10
        avg_score = sum(recent_scores) / len(recent_scores)
        
        return {
            'average': avg_score,
            'count': len(qa_scores),
            'recent_scores': recent_scores
        }
    
    def _get_performance_stats(self) -> Dict[str, Any]:
        """Estatísticas de performance"""
        times = self.metrics['processing_times']
        
        if not times:
            return {'avg_time': 0, 'fastest': 0, 'slowest': 0}
        
        time_values = [t['time'] for t in times]
        
        return {
            'avg_time': sum(time_values) / len(time_values),
            'fastest': min(time_values),
            'slowest': max(time_values),
            'total_processed': len(times)
        }
    
    def _calculate_avg_qa_score(self) -> float:
        """Calcula score médio de QA"""
        qa_scores = self.metrics['qa_scores']
        if not qa_scores:
            return 0.0
        
        scores = [s['score'] for s in qa_scores]
        return sum(scores) / len(scores)
    
    def print_dashboard(self):
        """Imprime dashboard de métricas"""
        data = self.get_dashboard_data()
        
        print(f"\n{'='*80}")
        print(f"📊 METRICS DASHBOARD")
        print(f"{'='*80}\n")
        
        # Overview
        overview = data['overview']
        print("📈 OVERVIEW:")
        print(f"  Total Requests: {overview['total_requests']}")
        print(f"  Success Rate: {overview['success_rate']:.1f}%")
        print(f"  Average QA Score: {overview['avg_qa_score']:.1%}\n")
        
        # By visa type
        print("📋 BY VISA TYPE:")
        for visa_type, stats in data['by_visa_type'].items():
            print(f"  {visa_type}:")
            print(f"    Total: {stats['total']}")
            print(f"    Success Rate: {stats['success_rate']:.1f}%")
        
        # Performance
        perf = data['performance']
        print(f"\n⚡ PERFORMANCE:")
        print(f"  Average Processing Time: {perf['avg_time']:.2f}s")
        print(f"  Fastest: {perf['fastest']:.2f}s")
        print(f"  Slowest: {perf['slowest']:.2f}s")
        
        # Quality
        quality = data['quality_trends']
        print(f"\n✨ QUALITY:")
        print(f"  Average QA Score: {quality['average']:.1%}")
        print(f"  Total QA Reviews: {quality['count']}")
        
        print(f"\n{'='*80}\n")
