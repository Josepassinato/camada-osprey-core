import React, { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';

interface HelpTooltipProps {
  title?: string;
  content: string | string[];
  examples?: string[];
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const HelpTooltip: React.FC<HelpTooltipProps> = ({
  title,
  content,
  examples,
  size = 'md',
  className = ''
}) => {
  const [open, setOpen] = useState(false);

  const iconSize = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  }[size];

  const contentArray = Array.isArray(content) ? content : [content];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          className={`inline-flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 text-blue-600 transition-colors ${className}`}
          style={{ width: size === 'sm' ? '20px' : size === 'md' ? '24px' : '28px', height: size === 'sm' ? '20px' : size === 'md' ? '24px' : '28px' }}
          onClick={(e) => {
            e.preventDefault();
            setOpen(!open);
          }}
        >
          <HelpCircle className={iconSize} />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-80 sm:w-96 p-0 shadow-lg" align="start">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 px-4 py-3 border-b border-blue-200">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-blue-600 flex-shrink-0" />
              {title && (
                <h3 className="font-semibold text-blue-900 text-sm">
                  {title}
                </h3>
              )}
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-blue-600 hover:text-blue-800 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <div className="p-4 space-y-3">
          <div className="space-y-2">
            {contentArray.map((text, idx) => (
              <p key={idx} className="text-sm text-gray-700 leading-relaxed">
                {text}
              </p>
            ))}
          </div>

          {examples && examples.length > 0 && (
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs font-semibold text-gray-600 mb-2">
                Exemplos:
              </p>
              <ul className="space-y-1.5">
                {examples.map((example, idx) => (
                  <li 
                    key={idx} 
                    className="text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded border border-gray-200"
                  >
                    {example}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default HelpTooltip;
