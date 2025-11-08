import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState, useEffect } from "react";
import { 
  Clock, 
  DollarSign, 
  AlertTriangle, 
  CheckCircle,
  Info,
  Users,
  Plane,
  Home,
  MapPin,
  List
} from "lucide-react";

interface VisaRequirementsProps {
  visaType: string;
  onClose: () => void;
}

const VisaRequirements = ({ visaType, onClose }: VisaRequirementsProps) => {
  const [detailedInfo, setDetailedInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetailedInfo = async () => {
      try {
        const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://owlagent.preview.emergentagent.com';
        const response = await fetch(`${backendUrl}/api/visa-detailed-info/${visaType}?process_type=both`);
        const data = await response.json();
        
        if (data.success) {
          setDetailedInfo(data.information);
        }
      } catch (error) {
        console.error('Error fetching detailed visa info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetailedInfo();
  }, [visaType]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p className="ml-3 text-gray-600">Carregando informações...</p>
      </div>
    );
  }

  if (!detailedInfo) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Informações não disponíveis para este tipo de visto.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const hasConsular = detailedInfo.processo_consular && Object.keys(detailedInfo.processo_consular).length > 0;
  const hasChangeOfStatus = detailedInfo.change_of_status && Object.keys(detailedInfo.change_of_status).length > 0;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{detailedInfo.name}</h2>
        <p className="text-gray-600 mt-1">{detailedInfo.description}</p>
      </div>

      {/* Tabs for Consular vs Change of Status */}
      {hasConsular && hasChangeOfStatus ? (
        <Tabs defaultValue="consular" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="consular" className="flex items-center space-x-2">
              <Plane className="h-4 w-4" />
              <span>Processo Consular</span>
            </TabsTrigger>
            <TabsTrigger value="change_of_status" className="flex items-center space-x-2">
              <Home className="h-4 w-4" />
              <span>Mudança de Status (Nos EUA)</span>
            </TabsTrigger>
          </TabsList>

          {/* Consular Process Tab */}
          <TabsContent value="consular" className="space-y-4">
            <Alert className="border-blue-200 bg-blue-50">
              <MapPin className="h-4 w-4" />
              <AlertDescription>
                <p className="font-medium text-blue-900 mb-1">📍 {detailedInfo.processo_consular.description}</p>
                <p className="text-sm text-blue-700">{detailedInfo.processo_consular.tempo_detalhes}</p>
              </AlertDescription>
            </Alert>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Processing Time */}
              <Card className="border-2 border-gray-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Clock className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Tempo de Processamento</p>
                      <p className="text-lg font-bold text-gray-900">{detailedInfo.processo_consular.tempo_processamento}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Fees */}
              <Card className="border-2 border-gray-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <DollarSign className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Total de Taxas</p>
                      <p className="text-lg font-bold text-gray-900">{detailedInfo.processo_consular.taxas?.total || 'N/A'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Fee Breakdown */}
            {detailedInfo.processo_consular.taxas && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <DollarSign className="h-5 w-5" />
                    <span>Detalhamento de Taxas</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(detailedInfo.processo_consular.taxas).map(([key, value]: [string, any]) => {
                      if (key === 'total') return null;
                      return (
                        <div key={key} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{value.descricao}</p>
                            <p className="text-xs text-gray-600 mt-1">
                              Pago para: {value.pago_para} • {value.quando_pagar}
                            </p>
                          </div>
                          <Badge variant="outline" className="ml-2">{value.valor}</Badge>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Steps */}
            {detailedInfo.processo_consular.etapas && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <List className="h-5 w-5" />
                    <span>Etapas do Processo</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="space-y-3">
                    {detailedInfo.processo_consular.etapas.map((step: string, index: number) => (
                      <li key={index} className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </div>
                        <p className="text-sm text-gray-700 pt-0.5">{step}</p>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Change of Status Tab */}
          <TabsContent value="change_of_status" className="space-y-4">
            <Alert className="border-orange-200 bg-orange-50">
              <Home className="h-4 w-4" />
              <AlertDescription>
                <p className="font-medium text-orange-900 mb-1">🏠 {detailedInfo.change_of_status.description}</p>
                <p className="text-sm text-orange-700">{detailedInfo.change_of_status.tempo_detalhes}</p>
              </AlertDescription>
            </Alert>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Processing Time */}
              <Card className="border-2 border-gray-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Clock className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Tempo de Processamento</p>
                      <p className="text-lg font-bold text-gray-900">{detailedInfo.change_of_status.tempo_processamento}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Fees */}
              <Card className="border-2 border-gray-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <DollarSign className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Total de Taxas</p>
                      <p className="text-lg font-bold text-gray-900">{detailedInfo.change_of_status.taxas?.total || detailedInfo.change_of_status.taxas?.total_minimo || 'N/A'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Fee Breakdown */}
            {detailedInfo.change_of_status.taxas && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <DollarSign className="h-5 w-5" />
                    <span>Detalhamento de Taxas</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(detailedInfo.change_of_status.taxas).map(([key, value]: [string, any]) => {
                      if (key.includes('total')) return null;
                      if (typeof value !== 'object') return null;
                      return (
                        <div key={key} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{value.descricao}</p>
                            <p className="text-xs text-gray-600 mt-1">
                              Pago para: {value.pago_para}
                              {value.pago_por && ` • Pago por: ${value.pago_por}`}
                              {value.quando_pagar && ` • ${value.quando_pagar}`}
                            </p>
                          </div>
                          <Badge variant="outline" className="ml-2">{value.valor}</Badge>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Special Requirements */}
            {detailedInfo.change_of_status.requisitos_especiais && (
              <Alert className="border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <p className="font-medium text-red-900 mb-2">⚠️ Requisitos Especiais para Mudança de Status:</p>
                  <ul className="text-sm text-red-700 space-y-1">
                    {detailedInfo.change_of_status.requisitos_especiais.map((req: string, index: number) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="mt-1">•</span>
                        <span>{req}</span>
                      </li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {/* Steps */}
            {detailedInfo.change_of_status.etapas && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <List className="h-5 w-5" />
                    <span>Etapas do Processo</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="space-y-3">
                    {detailedInfo.change_of_status.etapas.map((step: string, index: number) => (
                      <li key={index} className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </div>
                        <p className="text-sm text-gray-700 pt-0.5">{step}</p>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      ) : null}

      {/* General Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        {detailedInfo.dependentes && (
          <Card className="border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <Users className="h-5 w-5 text-gray-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Dependentes</p>
                  <p className="text-sm text-gray-600 mt-1">{detailedInfo.dependentes}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {detailedInfo.trabalho && (
          <Card className="border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-gray-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Autorização de Trabalho</p>
                  <p className="text-sm text-gray-600 mt-1">{detailedInfo.trabalho}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Eligibility Criteria */}
      {detailedInfo.criterios_elegibilidade && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <CheckCircle className="h-5 w-5" />
              <span>Critérios de Elegibilidade</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {detailedInfo.criterios_elegibilidade.map((criterion: string, index: number) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{criterion}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Legal Disclaimer */}
      <Alert className="border-yellow-200 bg-yellow-50">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription className="text-sm">
          <p className="font-medium text-yellow-900">⚖️ Aviso Legal</p>
          <p className="text-yellow-700 mt-1">
            Esta informação é educativa e baseada em dados públicos do USCIS. 
            NÃO constitui aconselhamento jurídico. Consulte um advogado de imigração 
            licenciado para decisões legais específicas sobre seu caso.
          </p>
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default VisaRequirements;
