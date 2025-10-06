import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Zap, 
  BarChart3, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Database,
  Trash2,
  RefreshCw
} from 'lucide-react';

interface PerformanceStats {
  operation_name: string;
  total_calls: number;
  successful_calls: number;
  success_rate_percent: number;
  avg_duration_seconds: number;
  min_duration_seconds: number;
  max_duration_seconds: number;
  percentile_95_seconds: number;
}

interface SystemHealth {
  health_status: string;
  overall_success_rate_percent: number;
  overall_avg_response_time_seconds: number;
  total_operations: number;
  critical_alerts: number;
  warning_alerts: number;
  monitored_operations_count: number;
}

interface CacheStats {
  cache_size: number;
  max_size: number;
  hit_rate_percentage: number;
  total_hits: number;
  total_misses: number;
  total_time_saved_seconds: number;
  average_processing_time_saved: number;
}

interface Alert {
  type: string;
  operation: string;
  severity: string;
  current_value: number;
  threshold: number;
  timestamp: string;
  description?: string;
}

const PerformanceDashboard: React.FC = () => {
  const [performanceStats, setPerformanceStats] = useState<Record<string, PerformanceStats>>({});
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const backendUrl = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  const fetchPerformanceData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Fetch all performance data
      const [statsRes, healthRes, cacheRes, alertsRes] = await Promise.all([
        fetch(`${backendUrl}/api/performance/stats`, { headers }),
        fetch(`${backendUrl}/api/performance/health`, { headers }),
        fetch(`${backendUrl}/api/performance/cache-stats`, { headers }),
        fetch(`${backendUrl}/api/performance/alerts?limit=10`, { headers })
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setPerformanceStats(statsData.performance_stats || {});
      }

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setSystemHealth(healthData.system_health);
      }

      if (cacheRes.ok) {
        const cacheData = await cacheRes.json();
        setCacheStats(cacheData.cache_stats);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearCache = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/performance/clear-cache`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await fetchPerformanceData(); // Refresh data
        alert('Cache cleared successfully!');
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
      alert('Error clearing cache');
    }
  };

  useEffect(() => {
    fetchPerformanceData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchPerformanceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'HEALTHY': return 'text-green-500';
      case 'WARNING': return 'text-yellow-500';
      case 'CRITICAL': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'HEALTHY': return <CheckCircle className="w-5 h-5" />;
      case 'WARNING': return <AlertCircle className="w-5 h-5" />;
      case 'CRITICAL': return <AlertCircle className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading performance data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Performance Dashboard</h1>
              <p className="text-gray-600 mt-2">Real-time system performance monitoring and analytics</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={fetchPerformanceData}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
              <button
                onClick={clearCache}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear Cache</span>
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Last updated: {lastUpdated.toLocaleString()}
          </p>
        </div>

        {/* System Health Overview */}
        {systemHealth && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center">
                <div className={`${getHealthStatusColor(systemHealth.health_status)} mr-3`}>
                  {getHealthStatusIcon(systemHealth.health_status)}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">System Health</p>
                  <p className={`text-lg font-bold ${getHealthStatusColor(systemHealth.health_status)}`}>
                    {systemHealth.health_status}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center">
                <TrendingUp className="w-5 h-5 text-green-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-lg font-bold text-gray-900">
                    {systemHealth.overall_success_rate_percent.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-blue-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Response</p>
                  <p className="text-lg font-bold text-gray-900">
                    {systemHealth.overall_avg_response_time_seconds.toFixed(3)}s
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center">
                <BarChart3 className="w-5 h-5 text-purple-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Operations</p>
                  <p className="text-lg font-bold text-gray-900">
                    {systemHealth.total_operations.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Cache Statistics */}
        {cacheStats && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <Database className="w-5 h-5 mr-2" />
              OCR Cache Performance
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div>
                <p className="text-sm font-medium text-gray-600">Hit Rate</p>
                <p className="text-2xl font-bold text-green-600">{cacheStats.hit_rate_percentage.toFixed(1)}%</p>
                <p className="text-xs text-gray-500">{cacheStats.total_hits} hits / {cacheStats.total_misses} misses</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Cache Usage</p>
                <p className="text-2xl font-bold text-blue-600">
                  {cacheStats.cache_size} / {cacheStats.max_size}
                </p>
                <p className="text-xs text-gray-500">
                  {((cacheStats.cache_size / cacheStats.max_size) * 100).toFixed(1)}% full
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Time Saved</p>
                <p className="text-2xl font-bold text-purple-600">
                  {cacheStats.total_time_saved_seconds.toFixed(1)}s
                </p>
                <p className="text-xs text-gray-500">Total processing time saved</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Speedup</p>
                <p className="text-2xl font-bold text-orange-600">
                  {cacheStats.average_processing_time_saved.toFixed(1)}s
                </p>
                <p className="text-xs text-gray-500">Per cache hit</p>
              </div>
            </div>
          </div>
        )}

        {/* Performance Statistics */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Operation Performance Statistics
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Operation
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Calls
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    95th Percentile
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.values(performanceStats).map((stat) => (
                  <tr key={stat.operation_name}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {stat.operation_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {stat.total_calls.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        stat.success_rate_percent >= 95 
                          ? 'bg-green-100 text-green-800' 
                          : stat.success_rate_percent >= 90
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {stat.success_rate_percent.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {stat.avg_duration_seconds.toFixed(3)}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {stat.percentile_95_seconds.toFixed(3)}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              Recent Alerts
            </h2>
            <div className="space-y-4">
              {alerts.map((alert, index) => (
                <div key={index} className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'CRITICAL' 
                    ? 'bg-red-50 border-red-400' 
                    : 'bg-yellow-50 border-yellow-400'
                }`}>
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className={`text-sm font-medium ${
                        alert.severity === 'CRITICAL' ? 'text-red-800' : 'text-yellow-800'
                      }`}>
                        {alert.type.replace(/_/g, ' ')} - {alert.operation}
                      </h3>
                      <p className={`mt-1 text-sm ${
                        alert.severity === 'CRITICAL' ? 'text-red-700' : 'text-yellow-700'
                      }`}>
                        Current: {alert.current_value} | Threshold: {alert.threshold}
                      </p>
                      <p className="mt-1 text-xs text-gray-500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceDashboard;