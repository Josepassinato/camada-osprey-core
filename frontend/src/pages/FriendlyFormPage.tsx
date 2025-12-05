import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DynamicFriendlyForm } from '@/components/DynamicFriendlyForm';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

const FriendlyFormPage: React.FC = () => {
  const { visaType, caseId } = useParams<{ visaType: string; caseId: string }>();
  const navigate = useNavigate();

  const handleSubmitSuccess = (result: any) => {
    console.log('Form submitted successfully:', result);
    
    // Navigate to next step based on validation status
    if (result.validation_status === 'approved') {
      // Go to document upload or PDF generation
      navigate(`/case/${caseId}/documents`);
    }
  };

  if (!visaType || !caseId) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">
            Erro: Parâmetros inválidos
          </h1>
          <Button onClick={() => navigate('/visa-selection')}>
            Voltar para Seleção de Visto
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/visa-selection')}
            className="mb-2"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para Seleção de Visto
          </Button>
          <div className="text-sm text-muted-foreground">
            Caso ID: <span className="font-mono">{caseId}</span>
          </div>
        </div>
      </div>

      <DynamicFriendlyForm
        visaType={visaType}
        caseId={caseId}
        onSubmitSuccess={handleSubmitSuccess}
      />
    </div>
  );
};

export default FriendlyFormPage;
