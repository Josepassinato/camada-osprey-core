import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';

interface PassportNameOptionProps {
  documentFileName: string;
  detectedName: string;
  registeredName: string;
  onUsePassportName: (usePassportName: boolean) => void;
  onCancel: () => void;
}

const PassportNameOption: React.FC<PassportNameOptionProps> = ({
  documentFileName,
  detectedName,
  registeredName,
  onUsePassportName,
  onCancel
}) => {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleUsePassportName = async () => {
    setIsProcessing(true);
    try {
      await onUsePassportName(true);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeepRegisteredName = async () => {
    setIsProcessing(true);
    try {
      await onUsePassportName(false);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md bg-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            ⚠️ Divergência de Nome Detectada
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="text-sm font-medium text-yellow-800 mb-2">
              📄 Documento: {documentFileName}
            </p>
            <p className="text-sm text-yellow-700">
              O nome no documento não corresponde ao nome cadastrado inicialmente.
            </p>
          </div>
          
          <div className="space-y-3">
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-medium text-blue-800">Nome no Cadastro:</p>
              <p className="text-sm text-blue-600">👤 {registeredName}</p>
            </div>
            
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm font-medium text-green-800">Nome no Passaporte:</p>
              <p className="text-sm text-green-600">📋 {detectedName}</p>
            </div>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700 mb-3">
              <strong>Escolha uma opção:</strong>
            </p>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• <strong>Usar nome do passaporte:</strong> Atualizaremos seus dados com o nome oficial do passaporte</p>
              <p>• <strong>Manter nome atual:</strong> O documento será rejeitado por divergência de nome</p>
            </div>
          </div>
          
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={onCancel}
              disabled={isProcessing}
              className="flex-1"
            >
              Cancelar
            </Button>
            
            <Button
              variant="outline"
              onClick={handleKeepRegisteredName}
              disabled={isProcessing}
              className="flex-1"
            >
              Manter Nome Atual
            </Button>
            
            <Button
              onClick={handleUsePassportName}
              disabled={isProcessing}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white"
            >
              {isProcessing ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Processando...
                </div>
              ) : (
                'Usar Nome do Passaporte'
              )}
            </Button>
          </div>
          
          <div className="text-xs text-gray-500 text-center">
            ℹ️ Esta escolha atualizará seus dados cadastrais permanentemente
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PassportNameOption;