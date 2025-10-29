import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { 
  CheckCircle2, 
  Circle,
  AlertTriangle,
  FileText,
  Shield,
  ExternalLink
} from 'lucide-react';

interface ChecklistItem {
  field: string;
  category: string;
  description: string;
  required: boolean;
  completed?: boolean;
}

interface VisaChecklistData {
  success: boolean;
  visa_type: string;
  visa_name: string;
  total_items: number;
  checklist_items: ChecklistItem[];
  source: string;
  disclaimer: string;
}

interface VisaChecklistProps {
  visaType: string;
  userData?: Record<string, any>;
  onChecklistComplete?: (completed: boolean) => void;
  showProgress?: boolean;
}

export const VisaChecklist: React.FC<VisaChecklistProps> = ({
  visaType,
  userData = {},
  onChecklistComplete,
  showProgress = true
}) => {
  const [checklist, setChecklist] = useState<VisaChecklistData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userChecked, setUserChecked] = useState<Set<string>>(new Set());
  const [groupedItems, setGroupedItems] = useState<Record<string, ChecklistItem[]>>({});

  const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (visaType) {
      fetchChecklist();
    }
  }, [visaType]);

  useEffect(() => {
    if (checklist && userData) {
      // Auto-check items based on user data
      const autoChecked = new Set<string>();
      checklist.checklist_items.forEach(item => {
        if (userData[item.field] && String(userData[item.field]).trim() !== '') {
          autoChecked.add(item.field);
        }
      });
      setUserChecked(autoChecked);
    }
  }, [checklist, userData]);

  useEffect(() => {
    if (checklist) {
      // Group items by category
      const grouped: Record<string, ChecklistItem[]> = {};
      checklist.checklist_items.forEach(item => {
        if (!grouped[item.category]) {
          grouped[item.category] = [];
        }
        grouped[item.category].push(item);
      });
      setGroupedItems(grouped);
    }
  }, [checklist]);

  useEffect(() => {
    if (onChecklistComplete && checklist) {
      const allChecked = checklist.checklist_items.every(item => 
        userChecked.has(item.field)
      );
      onChecklistComplete(allChecked);
    }
  }, [userChecked, checklist]);

  const fetchChecklist = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/visa-checklist/${visaType}`);
      
      if (!response.ok) {
        throw new Error('Falha ao carregar checklist');
      }

      const data = await response.json();
      setChecklist(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleCheck = (field: string) => {
    const newChecked = new Set(userChecked);
    if (newChecked.has(field)) {
      newChecked.delete(field);
    } else {
      newChecked.add(field);
    }
    setUserChecked(newChecked);
  };

  const getCompletionPercentage = () => {
    if (!checklist) return 0;
    return Math.round((userChecked.size / checklist.total_items) * 100);
  };

  const getCompletionColor = () => {
    const percentage = getCompletionPercentage();
    if (percentage < 70) return 'text-red-600';
    if (percentage < 90) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span>Carregando checklist...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Erro ao Carregar Checklist</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!checklist) {
    return null;
  }

  const completionPercentage = getCompletionPercentage();
  const canSubmit = completionPercentage >= 70;

  return (
    <div className="space-y-4">
      {/* Header with Progress */}
      <Card className={`border-2 ${
        completionPercentage >= 90 ? 'border-green-200 bg-green-50' :
        completionPercentage >= 70 ? 'border-yellow-200 bg-yellow-50' :
        'border-red-200 bg-red-50'
      }`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>Checklist - {checklist.visa_name}</span>
              </CardTitle>
              <CardDescription className="mt-2">
                Baseado em requisitos públicos do USCIS
              </CardDescription>
            </div>
            {showProgress && (
              <div className="text-center">
                <div className={`text-4xl font-bold ${getCompletionColor()}`}>
                  {completionPercentage}%
                </div>
                <div className="text-sm text-gray-600">
                  {userChecked.size}/{checklist.total_items} completos
                </div>
              </div>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Status Alert */}
      {!canSubmit && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>❌ Não Pode Finalizar</AlertTitle>
          <AlertDescription>
            Esta aplicação não pode ser finalizada no estado atual. Complete pelo menos 70% dos itens obrigatórios.
          </AlertDescription>
        </Alert>
      )}

      {canSubmit && completionPercentage < 90 && (
        <Alert className="border-yellow-200 bg-yellow-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>⚠️ Necessita Melhorias</AlertTitle>
          <AlertDescription>
            Você pode prosseguir, mas recomendamos fortemente completar todos os itens e consultar um advogado.
          </AlertDescription>
        </Alert>
      )}

      {completionPercentage >= 90 && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>✅ Pronta para Revisão</AlertTitle>
          <AlertDescription>
            Todos os itens essenciais estão completos. Recomendamos revisar com advogado antes de enviar ao USCIS.
          </AlertDescription>
        </Alert>
      )}

      {/* Checklist Items by Category */}
      {Object.entries(groupedItems).map(([category, items]) => (
        <Card key={category}>
          <CardHeader>
            <CardTitle className="text-lg flex items-center justify-between">
              <span>{category}</span>
              <Badge variant="outline">
                {items.filter(item => userChecked.has(item.field)).length}/{items.length}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {items.map((item) => {
              const isChecked = userChecked.has(item.field);
              const hasData = userData[item.field] && String(userData[item.field]).trim() !== '';
              
              return (
                <div
                  key={item.field}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isChecked 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-gray-200 bg-white hover:border-blue-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      checked={isChecked}
                      onCheckedChange={() => toggleCheck(item.field)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${isChecked ? 'line-through text-gray-500' : ''}`}>
                          {item.field}
                        </span>
                        {item.required && (
                          <Badge variant="destructive" className="text-xs">Obrigatório</Badge>
                        )}
                        {hasData && !isChecked && (
                          <Badge variant="outline" className="text-xs bg-blue-50">Dados Fornecidos</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      {hasData && userData[item.field] && (
                        <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                          <span className="font-medium">Seu valor: </span>
                          <span className="text-gray-700">
                            {String(userData[item.field]).substring(0, 100)}
                            {String(userData[item.field]).length > 100 && '...'}
                          </span>
                        </div>
                      )}
                    </div>
                    {isChecked && (
                      <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                    )}
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      ))}

      {/* Source and Disclaimer */}
      <Alert className="border-gray-200 bg-gray-50">
        <Shield className="h-4 w-4" />
        <AlertTitle className="flex items-center justify-between">
          <span>Informações Importantes</span>
          <Button
            variant="link"
            size="sm"
            className="h-auto p-0"
            onClick={() => window.open('https://www.uscis.gov', '_blank')}
          >
            <ExternalLink className="w-3 h-3 mr-1" />
            Visite USCIS.gov
          </Button>
        </AlertTitle>
        <AlertDescription className="text-xs space-y-2">
          <p><strong>Fonte:</strong> {checklist.source}</p>
          <p>{checklist.disclaimer}</p>
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default VisaChecklist;
