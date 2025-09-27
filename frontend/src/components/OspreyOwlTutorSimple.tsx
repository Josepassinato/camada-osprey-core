import React from 'react';

interface SimpleOwlProps {
  snapshot?: any;
  onAction?: (event: string, payload?: any) => void;
  isEnabled?: boolean;
  position?: string;
}

const OspreyOwlTutorSimple: React.FC<SimpleOwlProps> = ({
  snapshot,
  onAction,
  isEnabled = true,
  position = 'bottom-right'
}) => {
  if (!isEnabled) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center text-white cursor-pointer shadow-lg">
        🦉
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-white text-black text-xs font-bold rounded-full flex items-center justify-center">
          85%
        </div>
      </div>
    </div>
  );
};

export default OspreyOwlTutorSimple;