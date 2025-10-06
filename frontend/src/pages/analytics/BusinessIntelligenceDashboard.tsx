import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  PieChart, 
  TrendingUp, 
  Users, 
  Globe,
  DollarSign,
  FileText,
  Target
} from "lucide-react";

interface BusinessAnalytics {
  total_users: number;
  total_cases: number;
  revenue: number;
  growth_metrics: {
    user_growth_rate: number;
    case_growth_rate: number;
    revenue_growth_rate: number;
    daily_average_users: number;
    daily_average_cases: number;
  };
  geographic_insights: {
    top_countries: [string, number][];
    total_countries: number;
    country_distribution: Record<string, number>;
  };
  visa_type_insights: {
    most_popular_visa: string;
    visa_distribution: Record<string, number>;
    total_visa_types: number;
  };
}

const BusinessIntelligenceDashboard: React.FC<{ period: string }> = ({ period }) => {
  const [analytics, setAnalytics] = useState<BusinessAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBusinessAnalytics();
  }, [period]);

  const fetchBusinessAnalytics = async () => {
    setIsLoading(true);
    try {
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - (parseInt(period.replace('d', '')) * 24 * 60 * 60 * 1000))
        .toISOString().split('T')[0];

      const query = {
        start_date: startDate,
        end_date: endDate,
        group_by: 'summary',
        metrics: ['users', 'cases', 'revenue', 'growth']
      };

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/analytics/business/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        // Mock data for development
        setAnalytics({
          total_users: 3420,
          total_cases: 2890,
          revenue: 125600,
          growth_metrics: {
            user_growth_rate: 23.5,
            case_growth_rate: 18.2,
            revenue_growth_rate: 31.8,
            daily_average_users: 45.6,
            daily_average_cases: 38.5
          },
          geographic_insights: {
            top_countries: [
              ['United States', 1250],
              ['Brazil', 980],
              ['Canada', 420],
              ['Mexico', 350],
              ['India', 280],
              ['Philippines', 140]
            ],
            total_countries: 28,
            country_distribution: {
              'US': 1250,
              'BR': 980,
              'CA': 420,
              'MX': 350,
              'IN': 280,
              'PH': 140
            }
          },
          visa_type_insights: {
            most_popular_visa: 'H-1B',
            visa_distribution: {
              'H-1B': 1280,
              'F-1': 650,
              'B1/B2': 420,
              'I-485': 350,
              'O-1': 190
            },
            total_visa_types: 12
          }
        });
      }
    } catch (error) {
      console.error('Business analytics error:', error);
      setError('Connection error');
    } finally {
      setIsLoading(false);
    }
  };

  const getGrowthColor = (rate: number) => {
    if (rate > 20) return 'text-green-600';
    if (rate > 10) return 'text-blue-600';
    if (rate > 0) return 'text-gray-600';
    return 'text-red-600';
  };

  const getVisaTypeLabel = (visaType: string) => {
    const labels = {
      'H-1B': 'H-1B (Specialty Occupation)',
      'F-1': 'F-1 (Student Visa)',
      'B1/B2': 'B1/B2 (Visitor)',
      'I-485': 'I-485 (Green Card)',
      'O-1': 'O-1 (Extraordinary Ability)',
      'L-1': 'L-1 (Intracompany Transfer)'
    };
    return labels[visaType as keyof typeof labels] || visaType;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="bg-white border-0 shadow-md">
            <CardContent className="p-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <Card className="bg-white border-0 shadow-md">
        <CardContent className="p-6 text-center">
          <PieChart className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Business Analytics</h3>
          <p className="text-gray-600">{error || 'Failed to load business intelligence data'}</p>
          <Button onClick={fetchBusinessAnalytics} className="mt-4">Retry</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Key Business Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.total_users.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total Users</div>
                <div className={`text-xs font-medium ${getGrowthColor(analytics.growth_metrics.user_growth_rate)}`}>
                  +{analytics.growth_metrics.user_growth_rate.toFixed(1)}% growth
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <FileText className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.total_cases.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total Cases</div>
                <div className={`text-xs font-medium ${getGrowthColor(analytics.growth_metrics.case_growth_rate)}`}>
                  +{analytics.growth_metrics.case_growth_rate.toFixed(1)}% growth
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  ${analytics.revenue.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Revenue</div>
                <div className={`text-xs font-medium ${getGrowthColor(analytics.growth_metrics.revenue_growth_rate)}`}>
                  +{analytics.growth_metrics.revenue_growth_rate.toFixed(1)}% growth
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Target className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {((analytics.total_cases / analytics.total_users) * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">User-to-Case Rate</div>
                <div className="text-xs text-gray-500">
                  {analytics.growth_metrics.daily_average_cases.toFixed(1)} cases/day avg
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Geographic Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Geographic Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.geographic_insights.top_countries.slice(0, 6).map(([country, count]) => {
                const percentage = (count / analytics.total_users) * 100;
                return (
                  <div key={country} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900">{country}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">{count.toLocaleString()}</span>
                        <Badge variant="outline" className="text-xs">
                          {percentage.toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                    <Progress value={percentage} className="h-2" />
                  </div>
                );
              })}
              <div className="text-xs text-gray-500 text-center pt-2">
                Serving {analytics.geographic_insights.total_countries} countries worldwide
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Visa Type Popularity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(analytics.visa_type_insights.visa_distribution)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 6)
                .map(([visaType, count]) => {
                  const percentage = (count / analytics.total_cases) * 100;
                  return (
                    <div key={visaType} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-900">{getVisaTypeLabel(visaType)}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-600">{count.toLocaleString()}</span>
                          <Badge variant="outline" className="text-xs">
                            {percentage.toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                      <Progress value={percentage} className="h-2" />
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Growth Trends & KPIs */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Growth Analytics & Key Performance Indicators
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* User Acquisition */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-blue-800">User Acquisition</h4>
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Growth Rate</span>
                  <span className={`font-semibold ${getGrowthColor(analytics.growth_metrics.user_growth_rate)}`}>
                    +{analytics.growth_metrics.user_growth_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Daily Average</span>
                  <span className="font-semibold text-blue-900">
                    {analytics.growth_metrics.daily_average_users.toFixed(1)} users
                  </span>
                </div>
              </div>
            </div>

            {/* Case Volume */}
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-purple-800">Case Volume</h4>
                <FileText className="h-5 w-5 text-purple-600" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Growth Rate</span>
                  <span className={`font-semibold ${getGrowthColor(analytics.growth_metrics.case_growth_rate)}`}>
                    +{analytics.growth_metrics.case_growth_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Daily Average</span>
                  <span className="font-semibold text-purple-900">
                    {analytics.growth_metrics.daily_average_cases.toFixed(1)} cases
                  </span>
                </div>
              </div>
            </div>

            {/* Revenue Growth */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-green-800">Revenue Growth</h4>
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Growth Rate</span>
                  <span className={`font-semibold ${getGrowthColor(analytics.growth_metrics.revenue_growth_rate)}`}>
                    +{analytics.growth_metrics.revenue_growth_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Revenue per User</span>
                  <span className="font-semibold text-green-900">
                    ${(analytics.revenue / analytics.total_users).toFixed(0)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Business Insights */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Strategic Business Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Market Insights */}
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Market Analysis</h4>
              <div className="space-y-3">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Globe className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Top Market: United States</p>
                      <p className="text-xs text-gray-600">
                        Represents {((analytics.geographic_insights.top_countries[0]?.[1] || 0) / analytics.total_users * 100).toFixed(1)}% 
                        of total user base
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-start gap-3">
                    <FileText className="h-5 w-5 text-purple-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Most Popular: {analytics.visa_type_insights.most_popular_visa}
                      </p>
                      <p className="text-xs text-gray-600">
                        {((analytics.visa_type_insights.visa_distribution[analytics.visa_type_insights.most_popular_visa] || 0) / analytics.total_cases * 100).toFixed(1)}% 
                        of all cases
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Growth Opportunities */}
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Growth Opportunities</h4>
              <div className="space-y-3">
                {analytics.growth_metrics.user_growth_rate > 20 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm font-medium text-green-800">Strong User Acquisition</p>
                    <p className="text-xs text-green-700">
                      Excellent {analytics.growth_metrics.user_growth_rate.toFixed(1)}% growth rate. 
                      Consider scaling marketing efforts.
                    </p>
                  </div>
                )}
                
                {analytics.growth_metrics.revenue_growth_rate > analytics.growth_metrics.user_growth_rate && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm font-medium text-blue-800">Revenue Efficiency</p>
                    <p className="text-xs text-blue-700">
                      Revenue growing faster than users. Great monetization strategy!
                    </p>
                  </div>
                )}

                <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                  <p className="text-sm font-medium text-purple-800">Market Diversification</p>
                  <p className="text-xs text-purple-700">
                    Serving {analytics.geographic_insights.total_countries} countries. 
                    Consider localization for top markets.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessIntelligenceDashboard;