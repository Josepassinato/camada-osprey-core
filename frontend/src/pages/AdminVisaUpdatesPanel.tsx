import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Clock, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Bell, 
  AlertTriangle,
  TrendingUp,
  Calendar,
  DollarSign,
  FileText,
  Globe
} from 'lucide-react';

interface VisaUpdate {
  id: string;
  form_code: string;
  update_type: string;
  source: string;
  title: string;
  description: string;
  old_value: any;
  new_value: any;
  confidence_score: number;
  status: 'pending' | 'approved' | 'rejected';
  detected_date: string;
  admin_notes?: string;
}

interface AdminNotification {
  id: string;
  type: string;
  title: string;
  message: string;
  created_at: string;
  priority: 'high' | 'medium' | 'low';
}

const AdminVisaUpdatesPanel = () => {
  const [pendingUpdates, setPendingUpdates] = useState<VisaUpdate[]>([]);
  const [updateHistory, setUpdateHistory] = useState<VisaUpdate[]>([]);
  const [notifications, setNotifications] = useState<AdminNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanLoading, setScanLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load pending updates
      const pendingResponse = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/admin/visa-updates/pending`);
      const pendingData = await pendingResponse.json();
      if (pendingData.success) {
        setPendingUpdates(pendingData.updates);
      }

      // Load update history
      const historyResponse = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/admin/visa-updates/history?limit=20`);
      const historyData = await historyResponse.json();
      if (historyData.success) {
        setUpdateHistory(historyData.updates);
      }

      // Load notifications
      const notificationResponse = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/admin/notifications`);
      const notificationData = await notificationResponse.json();
      if (notificationData.success) {
        setNotifications(notificationData.notifications);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const runManualScan = async () => {
    setScanLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/admin/visa-updates/run-manual-scan`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        alert(`Manual scan completed! ${data.changes_detected} changes detected.`);
        loadData(); // Reload data
      } else {
        alert('Manual scan failed. Please check logs.');
      }
    } catch (error) {
      console.error('Error running manual scan:', error);
      alert('Manual scan failed. Please try again.');
    }
    setScanLoading(false);
  };

  const approveUpdate = async (updateId: string, adminNotes: string = '') => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/admin/visa-updates/${updateId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          admin_notes: adminNotes,
          admin_user: 'admin' // In real app, get from auth context
        })
      });

      const data = await response.json();
      if (data.success) {
        alert('Update approved and applied!');
        loadData(); // Reload data
      } else {
        alert('Failed to approve update.');
      }
    } catch (error) {
      console.error('Error approving update:', error);
      alert('Failed to approve update.');
    }
  };

  const rejectUpdate = async (updateId: string, adminNotes: string = '') => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/admin/visa-updates/${updateId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          admin_notes: adminNotes,
          admin_user: 'admin' // In real app, get from auth context
        })
      });

      const data = await response.json();
      if (data.success) {
        alert('Update rejected.');
        loadData(); // Reload data
      } else {
        alert('Failed to reject update.');
      }
    } catch (error) {
      console.error('Error rejecting update:', error);
      alert('Failed to reject update.');
    }
  };

  const getUpdateTypeIcon = (type: string) => {
    switch (type) {
      case 'processing_time': return <Clock className="w-4 h-4" />;
      case 'filing_fee': return <DollarSign className="w-4 h-4" />;
      case 'form_requirement': return <FileText className="w-4 h-4" />;
      case 'visa_bulletin': return <Calendar className="w-4 h-4" />;
      case 'regulation_change': return <Globe className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  const getSourceBadgeColor = (source: string) => {
    switch (source) {
      case 'uscis': return 'bg-blue-100 text-blue-800';
      case 'state_department': return 'bg-green-100 text-green-800';
      case 'federal_register': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 animate-spin" />
        <span className="ml-2">Loading visa updates...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Visa Information Management</h1>
          <p className="text-gray-600">Monitor and approve automatic visa information updates</p>
        </div>
        <Button 
          onClick={runManualScan} 
          disabled={scanLoading}
          className="flex items-center gap-2"
        >
          {scanLoading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Run Manual Scan
        </Button>
      </div>

      {/* Notifications */}
      {notifications.length > 0 && (
        <Alert className="border-orange-200 bg-orange-50">
          <Bell className="h-4 w-4" />
          <AlertDescription>
            <strong>{notifications.length} notifications:</strong>{' '}
            {notifications[0]?.message}
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Updates</p>
                <p className="text-2xl font-bold text-orange-600">{pendingUpdates.length}</p>
              </div>
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Approved Today</p>
                <p className="text-2xl font-bold text-green-600">
                  {updateHistory.filter(u => 
                    u.status === 'approved' && 
                    new Date(u.detected_date).toDateString() === new Date().toDateString()
                  ).length}
                </p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Confidence</p>
                <p className="text-2xl font-bold text-blue-600">
                  {pendingUpdates.filter(u => u.confidence_score >= 0.8).length}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Notifications</p>
                <p className="text-2xl font-bold text-purple-600">{notifications.length}</p>
              </div>
              <Bell className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="pending" className="space-y-4">
        <TabsList>
          <TabsTrigger value="pending">
            Pending Updates ({pendingUpdates.length})
          </TabsTrigger>
          <TabsTrigger value="history">
            Update History
          </TabsTrigger>
        </TabsList>

        {/* Pending Updates */}
        <TabsContent value="pending" className="space-y-4">
          {pendingUpdates.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold">All Up to Date!</h3>
                <p className="text-gray-600">No pending visa updates at this time.</p>
              </CardContent>
            </Card>
          ) : (
            pendingUpdates.map((update) => (
              <Card key={update.id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getUpdateTypeIcon(update.update_type)}
                      <CardTitle className="text-lg">{update.title}</CardTitle>
                      <Badge className={getSourceBadgeColor(update.source)}>
                        {update.source.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="mb-2">
                        {update.form_code}
                      </Badge>
                      <p className={`text-sm font-medium ${getConfidenceColor(update.confidence_score)}`}>
                        Confidence: {Math.round(update.confidence_score * 100)}%
                      </p>
                    </div>
                  </div>
                  <CardDescription>{update.description}</CardDescription>
                </CardHeader>

                <CardContent>
                  <div className="space-y-4">
                    {/* Show changes comparison */}
                    {update.old_value && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded">
                        <div>
                          <h4 className="font-medium text-red-600 mb-2">Current Value:</h4>
                          <pre className="text-xs bg-white p-2 rounded border max-h-32 overflow-auto">
                            {JSON.stringify(update.old_value, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <h4 className="font-medium text-green-600 mb-2">New Value:</h4>
                          <pre className="text-xs bg-white p-2 rounded border max-h-32 overflow-auto">
                            {JSON.stringify(update.new_value, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}

                    {/* Action buttons */}
                    <div className="flex gap-2 pt-4 border-t">
                      <Button
                        onClick={() => approveUpdate(update.id)}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        Approve & Apply
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => rejectUpdate(update.id)}
                        className="flex items-center gap-2 text-red-600 border-red-600 hover:bg-red-50"
                      >
                        <XCircle className="w-4 h-4" />
                        Reject
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* History */}
        <TabsContent value="history" className="space-y-4">
          {updateHistory.map((update) => (
            <Card key={update.id} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {getUpdateTypeIcon(update.update_type)}
                    <CardTitle className="text-lg">{update.title}</CardTitle>
                    <Badge className={getSourceBadgeColor(update.source)}>
                      {update.source.toUpperCase()}
                    </Badge>
                    <Badge 
                      className={
                        update.status === 'approved' 
                          ? 'bg-green-100 text-green-800'
                          : update.status === 'rejected'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }
                    >
                      {update.status.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="mb-2">
                      {update.form_code}
                    </Badge>
                    <p className="text-xs text-gray-500">
                      {new Date(update.detected_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <CardDescription>{update.description}</CardDescription>
                {update.admin_notes && (
                  <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded mt-2">
                    <strong>Admin Notes:</strong> {update.admin_notes}
                  </div>
                )}
              </CardHeader>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminVisaUpdatesPanel;