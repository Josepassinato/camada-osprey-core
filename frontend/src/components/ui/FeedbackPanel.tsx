import React from 'react';
import { CheckCircle, AlertTriangle, Lock, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

export interface FeedbackItem {
  type: 'success' | 'warning' | 'info' | 'locked';
  message: string;
  details?: string[];
}

interface FeedbackPanelProps {
  title?: string;
  items: FeedbackItem[];
  className?: string;
}

const FeedbackPanel: React.FC<FeedbackPanelProps> = ({ 
  title = "Status do Sistema",
  items,
  className = ""
}) => {
  const getIcon = (type: FeedbackItem['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-600" />;
      case 'locked':
        return <Lock className="h-5 w-5 text-gray-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };

  const getAlertVariant = (type: FeedbackItem['type']) => {
    switch (type) {
      case 'success':
        return 'default';
      case 'warning':
        return 'destructive';
      default:
        return 'default';
    }
  };

  const getBgColor = (type: FeedbackItem['type']) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      case 'locked':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getTextColor = (type: FeedbackItem['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-900';
      case 'warning':
        return 'text-yellow-900';
      case 'info':
        return 'text-blue-900';
      case 'locked':
        return 'text-gray-900';
      default:
        return 'text-gray-900';
    }
  };

  if (items.length === 0) return null;

  return (
    <Card className={`border-2 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => (
          <div
            key={index}
            className={`border rounded-lg p-3 ${getBgColor(item.type)}`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                {getIcon(item.type)}
              </div>
              <div className="flex-1 space-y-2">
                <p className={`font-medium ${getTextColor(item.type)}`}>
                  {item.message}
                </p>
                {item.details && item.details.length > 0 && (
                  <ul className={`text-sm space-y-1 ${getTextColor(item.type)} opacity-90`}>
                    {item.details.map((detail, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-xs mt-1">•</span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

export default FeedbackPanel;
