import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LanguageModeSelector } from '../components/LanguageModeSelector';

export const AdaptiveFormExample: React.FC = () => {
  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Sistema de Linguagem Adaptativa</CardTitle>
        </CardHeader>
        <CardContent>
          <LanguageModeSelector showCard={true} />
          <div className="mt-6 p-4 bg-blue-50 rounded">
            <p className="text-sm">
              O sistema de linguagem adaptativa está funcionando! 
              Este componente permite alternar entre linguagem simples e técnica.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdaptiveFormExample;
