import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  Plane, 
  Home, 
  MapPin,
  Clock,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Info,
  ArrowRight
} from "lucide-react";

interface ProcessTypeSelectorProps {
  onSelect: (processType: 'consular' | 'change_of_status') => void;
  visaType?: string;
}

const ProcessTypeSelector: React.FC<ProcessTypeSelectorProps> = ({ onSelect, visaType }) => {
  const [selectedType, setSelectedType] = useState<'consular' | 'change_of_status' | null>(null);

  const handleSelect = (type: 'consular' | 'change_of_status') => {
    setSelectedType(type);
  };

  const handleContinue = () => {
    if (selectedType) {
      onSelect(selectedType);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Como você pretende aplicar?
          </h1>
          <p className="text-gray-600">
            Escolha o tipo de processo que se aplica à sua situação
          </p>
        </div>

        {/* Important Info Alert */}
        <Alert className="mb-8 border-blue-200 bg-blue-50">
          <Info className="h-4 w-4" />
          <AlertDescription>
            <p className="font-medium text-blue-900 mb-2">Por que essa escolha é importante?</p>
            <p className="text-sm text-blue-700">
              Os processos de <strong>Consulado</strong> e <strong>Mudança de Status</strong> têm 
              formulários diferentes, taxas diferentes e tempos de processamento diferentes. 
              Sua escolha determinará todo o fluxo da aplicação.
            </p>
          </AlertDescription>
        </Alert>

        {/* Process Type Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Consular Process */}
          <Card 
            className={`cursor-pointer transition-all ${
              selectedType === 'consular' 
                ? 'ring-2 ring-blue-500 border-blue-500 shadow-lg' 
                : 'hover:shadow-md border-gray-200'
            }`}
            onClick={() => handleSelect('consular')}
          >
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Plane className="h-6 w-6 text-blue-600" />
                </div>
                {selectedType === 'consular' && (
                  <CheckCircle className="h-6 w-6 text-blue-600" />
                )}
              </div>
              <CardTitle className="text-xl">Processo Consular</CardTitle>
              <CardDescription>Aplicação através de consulado dos EUA</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-2">
                <MapPin className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-600">
                  Você está <strong>fora dos EUA</strong> (no Brasil ou outro país)
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-900">✅ Ideal para:</p>
                <ul className="text-sm text-gray-600 space-y-1 ml-4">
                  <li>• Primeira vez aplicando para visto</li>
                  <li>• Renovação de visto expirado</li>
                  <li>• Você está no Brasil atualmente</li>
                  <li>• Não tem visto válido nos EUA</li>
                </ul>
              </div>

              <div className="border-t pt-3 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Tempo típico:</span>
                  <Badge variant="outline">2-6 semanas</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Formulário:</span>
                  <Badge variant="outline">DS-160</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Change of Status */}
          <Card 
            className={`cursor-pointer transition-all ${
              selectedType === 'change_of_status' 
                ? 'ring-2 ring-orange-500 border-orange-500 shadow-lg' 
                : 'hover:shadow-md border-gray-200'
            }`}
            onClick={() => handleSelect('change_of_status')}
          >
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <Home className="h-6 w-6 text-orange-600" />
                </div>
                {selectedType === 'change_of_status' && (
                  <CheckCircle className="h-6 w-6 text-orange-600" />
                )}
              </div>
              <CardTitle className="text-xl">Mudança de Status</CardTitle>
              <CardDescription>Aplicação dentro dos Estados Unidos</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-2">
                <Home className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-600">
                  Você <strong>já está nos EUA</strong> com visto válido
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-900">✅ Ideal para:</p>
                <ul className="text-sm text-gray-600 space-y-1 ml-4">
                  <li>• Você está legalmente nos EUA</li>
                  <li>• Quer mudar para outro tipo de visto</li>
                  <li>• Quer estender seu visto atual</li>
                  <li>• Não quer/pode viajar ao consulado</li>
                </ul>
              </div>

              <div className="border-t pt-3 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Tempo típico:</span>
                  <Badge variant="outline">3-10 meses</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Formulário:</span>
                  <Badge variant="outline">I-539, I-485, etc</Badge>
                </div>
              </div>

              <Alert className="border-orange-200 bg-orange-50 mt-4">
                <AlertTriangle className="h-3 w-3" />
                <AlertDescription className="text-xs text-orange-700">
                  ⚠️ Não pode viajar enquanto pendente
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>

        {/* Comparison Table */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-lg">Comparação Rápida</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium text-gray-700">Aspecto</th>
                    <th className="text-left py-2 font-medium text-blue-700">
                      <div className="flex items-center space-x-1">
                        <Plane className="h-4 w-4" />
                        <span>Consulado</span>
                      </div>
                    </th>
                    <th className="text-left py-2 font-medium text-orange-700">
                      <div className="flex items-center space-x-1">
                        <Home className="h-4 w-4" />
                        <span>Mudança Status</span>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr>
                    <td className="py-2 text-gray-600">Localização</td>
                    <td className="py-2">Fora dos EUA</td>
                    <td className="py-2">Dentro dos EUA</td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Tempo médio</td>
                    <td className="py-2">2-6 semanas</td>
                    <td className="py-2">3-10 meses</td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Pode viajar?</td>
                    <td className="py-2 text-green-600">✓ Sim</td>
                    <td className="py-2 text-red-600">✗ Não durante processo</td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Entrevista</td>
                    <td className="py-2">Sempre no consulado</td>
                    <td className="py-2">Às vezes no USCIS</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Continue Button */}
        <div className="flex justify-center">
          <Button 
            size="lg"
            className="w-full md:w-auto"
            disabled={!selectedType}
            onClick={handleContinue}
          >
            {selectedType ? (
              <>
                Continuar com {selectedType === 'consular' ? 'Processo Consular' : 'Mudança de Status'}
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            ) : (
              'Selecione uma opção acima'
            )}
          </Button>
        </div>

        {/* Help Section */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500 mb-2">Não tem certeza qual escolher?</p>
          <Alert className="border-gray-200 bg-gray-50">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-sm text-gray-700">
              <p className="font-medium mb-2">Regra simples:</p>
              <ul className="text-left space-y-1">
                <li>• Se você está no Brasil → <strong>Processo Consular</strong></li>
                <li>• Se você está nos EUA com visto válido → <strong>Mudança de Status</strong></li>
              </ul>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </div>
  );
};

export default ProcessTypeSelector;
