import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  FileText, 
  User, 
  Signature,
  Lock,
  Calendar
} from "lucide-react";

interface ResponsibilityConfirmationProps {
  type: 'document_authenticity' | 'form_data_review' | 'letter_verification' | 'final_declaration';
  onConfirm: (confirmationData: any) => void;
  onCancel: () => void;
  data?: any;
}

const ResponsibilityConfirmation = ({ 
  type, 
  onConfirm, 
  onCancel, 
  data 
}: ResponsibilityConfirmationProps) => {
  const [confirmations, setConfirmations] = useState<Record<string, boolean>>({});
  const [digitalSignature, setDigitalSignature] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const getConfirmationConfig = () => {
    const configs = {
      document_authenticity: {
        title: "Confirmação de Autenticidade dos Documentos",
        icon: <FileText className="h-6 w-6 text-blue-600" />,
        description: "Confirme que os documentos enviados são autênticos e foram fornecidos pessoalmente por você.",
        confirmations: [
          {
            id: "authentic_documents",
            text: "Confirmo que TODOS os documentos enviados são autênticos e originais, sem alterações ou falsificações."
          },
          {
            id: "personal_submission", 
            text: "Declaro que EU PESSOALMENTE enviei estes documentos e sou o titular legítimo de todos eles."
          },
          {
            id: "responsibility_documents",
            text: "Assumo total responsabilidade pela veracidade e autenticidade dos documentos fornecidos."
          },
          {
            id: "legal_consequences",
            text: "Entendo que documentos falsos podem resultar em negação permanente do visto e consequências legais."
          }
        ],
        legalText: "Esta confirmação é registrada com data/hora e constitui declaração formal de autenticidade dos documentos para fins de imigração americana."
      },
      
      form_data_review: {
        title: "Revisão e Confirmação dos Dados do Formulário",
        icon: <CheckCircle className="h-6 w-6 text-green-600" />,
        description: "Revise cuidadosamente todas as informações do formulário oficial antes da confirmação.",
        confirmations: [
          {
            id: "reviewed_all_data",
            text: "Revisei CUIDADOSAMENTE todas as informações contidas no formulário oficial USCIS."
          },
          {
            id: "accurate_information",
            text: "Confirmo que TODAS as informações estão corretas e foram fornecidas pessoalmente por mim."
          },
          {
            id: "complete_responsibility",
            text: "Assumo TOTAL RESPONSABILIDADE por todas as informações contidas neste formulário."
          },
          {
            id: "platform_assistance_only", 
            text: "Entendo que a plataforma OSPREY atuou apenas como auxílio tecnológico para organizar minhas informações."
          }
        ],
        legalText: "Esta confirmação registra sua responsabilidade total pelos dados do formulário oficial que será submetido ao USCIS."
      },

      letter_verification: {
        title: "Verificação e Aprovação da Carta Gerada",
        icon: <Signature className="h-6 w-6 text-purple-600" />,
        description: "Revise a carta gerada pela IA e confirme que todas as informações são verdadeiras.",
        confirmations: [
          {
            id: "reviewed_letter_content",
            text: "Li COMPLETAMENTE a carta gerada e revisei todo o conteúdo linha por linha."
          },
          {
            id: "truthful_information",
            text: "Confirmo que TODAS as informações descritas na carta são verdadeiras e foram fornecidas por mim."
          },
          {
            id: "no_fabricated_facts",
            text: "Declaro que NÃO há informações inventadas, exageradas ou falsas na carta."
          },
          {
            id: "personal_information_source",
            text: "Todas as informações da carta foram fornecidas PESSOALMENTE por mim e são de minha responsabilidade."
          }
        ],
        legalText: "A IA organizou apenas as informações que você forneceu. Você mantém total responsabilidade pelo conteúdo da carta."
      },

      final_declaration: {
        title: "Declaração Final de Responsabilidade",
        icon: <Shield className="h-6 w-6 text-red-600" />,
        description: "Declaração final antes do download dos documentos para submissão ao USCIS.",
        confirmations: [
          {
            id: "complete_application_review",
            text: "Revisei TODA a aplicação: documentos, formulários, cartas e declarações."
          },
          {
            id: "exclusive_personal_information",
            text: "Declaro que TODOS os documentos e informações foram construídos UNICAMENTE com dados fornecidos por mim."
          },
          {
            id: "platform_technological_assistance",
            text: "Confirmo que a plataforma OSPREY atuou SOMENTE como auxílio tecnológico para organização da aplicação."
          },
          {
            id: "full_responsibility_assumption",
            text: "Assumo TOTAL e EXCLUSIVA responsabilidade por todos os documentos, informações e declarações."
          },
          {
            id: "legal_liability_understanding",
            text: "Entendo que sou o ÚNICO responsável pela veracidade e que informações falsas têm consequências legais."
          },
          {
            id: "self_petitioner_confirmation",
            text: "Confirmo que sou um SELF-PETITIONER e que esta aplicação foi preparada sob minha total responsabilidade."
          }
        ],
        legalText: "Esta é sua declaração final de responsabilidade. Será anexada à sua aplicação como comprovante de que você assume total responsabilidade como self-petitioner.",
        requiresSignature: true
      }
    };

    return configs[type];
  };

  const config = getConfirmationConfig();
  const allConfirmed = config.confirmations.every(conf => confirmations[conf.id]);
  const signatureRequired = config.requiresSignature && digitalSignature.trim().length < 3;

  const handleConfirmationChange = (id: string, checked: boolean) => {
    setConfirmations(prev => ({
      ...prev,
      [id]: checked
    }));
  };

  const handleSubmit = async () => {
    if (!allConfirmed || (config.requiresSignature && signatureRequired)) {
      return;
    }

    setIsProcessing(true);

    const confirmationData = {
      type,
      confirmations,
      digitalSignature: config.requiresSignature ? digitalSignature : null,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      ipTimestamp: Date.now(),
      data
    };

    try {
      await onConfirm(confirmationData);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="border-2 border-black">
        <CardHeader className="bg-gray-50 border-b border-black">
          <CardTitle className="flex items-center space-x-3">
            {config.icon}
            <span>{config.title}</span>
          </CardTitle>
          <p className="text-gray-700">{config.description}</p>
        </CardHeader>

        <CardContent className="p-6">
          {/* Confirmations List */}
          <div className="space-y-4 mb-6">
            {config.confirmations.map((confirmation, index) => (
              <div key={confirmation.id} className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={confirmations[confirmation.id] || false}
                    onChange={(e) => handleConfirmationChange(confirmation.id, e.target.checked)}
                    className="mt-1 h-4 w-4 accent-black"
                  />
                  <div className="flex-1">
                    <span className="text-sm font-medium text-gray-900">
                      {index + 1}. {confirmation.text}
                    </span>
                  </div>
                </label>
              </div>
            ))}
          </div>

          {/* Digital Signature (if required) */}
          {config.requiresSignature && (
            <div className="mb-6 p-4 border-2 border-dashed border-gray-300 rounded-lg">
              <div className="flex items-center space-x-2 mb-3">
                <Signature className="h-5 w-5 text-gray-600" />
                <span className="font-medium text-gray-800">Assinatura Digital Obrigatória</span>
              </div>
              <input
                type="text"
                placeholder="Digite seu nome completo como assinatura digital"
                value={digitalSignature}
                onChange={(e) => setDigitalSignature(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded focus:border-black focus:outline-none"
              />
              <p className="text-xs text-gray-600 mt-2">
                Sua assinatura digital confirma sua identidade e responsabilidade total pela aplicação.
              </p>
            </div>
          )}

          {/* Legal Text */}
          <Alert className="border-orange-400 bg-orange-50 mb-6">
            <Lock className="h-4 w-4 text-orange-600" />
            <AlertDescription>
              <div className="text-sm text-orange-800">
                <p className="font-medium mb-2">📋 Registro Legal:</p>
                <p>{config.legalText}</p>
                <div className="mt-2 flex items-center space-x-4 text-xs text-orange-700">
                  <span>📅 Data/Hora: {new Date().toLocaleString('pt-BR')}</span>
                  <span>🔒 Registro Permanente</span>
                </div>
              </div>
            </AlertDescription>
          </Alert>

          {/* Progress Indicator */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progresso das Confirmações</span>
              <span>{Object.values(confirmations).filter(Boolean).length}/{config.confirmations.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-black h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${(Object.values(confirmations).filter(Boolean).length / config.confirmations.length) * 100}%` 
                }}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <Button 
              variant="outline" 
              onClick={onCancel}
              className="border-gray-300 text-gray-700"
            >
              Cancelar
            </Button>

            <Button
              onClick={handleSubmit}
              disabled={!allConfirmed || (config.requiresSignature && signatureRequired) || isProcessing}
              className="bg-black text-white hover:bg-gray-800 disabled:bg-gray-300"
            >
              {isProcessing ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  <span>Registrando...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Shield className="h-4 w-4" />
                  <span>
                    {type === 'final_declaration' ? 'Finalizar e Assumir Responsabilidade' : 'Confirmar e Prosseguir'}
                  </span>
                </div>
              )}
            </Button>
          </div>

          {/* Validation Messages */}
          {!allConfirmed && (
            <Alert className="mt-4 border-red-400 bg-red-50">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                Você deve confirmar TODAS as declarações para prosseguir.
              </AlertDescription>
            </Alert>
          )}

          {config.requiresSignature && signatureRequired && (
            <Alert className="mt-4 border-orange-400 bg-orange-50">
              <Signature className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-orange-800">
                Assinatura digital obrigatória para finalizar a declaração.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ResponsibilityConfirmation;