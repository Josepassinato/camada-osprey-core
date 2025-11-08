import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Plane, Home } from 'lucide-react';

interface ProcessTypeBadgeProps {
  processType: 'consular' | 'change_of_status' | null;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const ProcessTypeBadge: React.FC<ProcessTypeBadgeProps> = ({ 
  processType, 
  className = '',
  size = 'md'
}) => {
  if (!processType) return null;

  const isConsular = processType === 'consular';
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  return (
    <div 
      className={`inline-flex items-center gap-2 rounded-full font-medium shadow-sm ${
        isConsular 
          ? 'bg-blue-100 text-blue-800 border-2 border-blue-500' 
          : 'bg-orange-100 text-orange-800 border-2 border-orange-500'
      } ${sizeClasses[size]} ${className}`}
    >
      {isConsular ? (
        <Plane className={iconSizes[size]} />
      ) : (
        <Home className={iconSizes[size]} />
      )}
      <span className="font-semibold">
        {isConsular ? 'Processo Consular' : 'Mudança de Status'}
      </span>
    </div>
  );
};

export default ProcessTypeBadge;
