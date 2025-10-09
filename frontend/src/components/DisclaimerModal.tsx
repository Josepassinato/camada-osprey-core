import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle2,
  Loader2,
  FileText,
  Scale,
  Info
} from "lucide-react";

interface DisclaimerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: (consentHash: string) => Promise<void>;
  stage: 'documents' | 'forms' | 'cover_letter' | 'review' | 'final';
  caseId?: string;
  loading?: boolean;
}

const DisclaimerModal: React.FC<DisclaimerModalProps> = ({
  isOpen,
  onClose,
  onAccept,
  stage,
  caseId,
  loading = false
}) => {
  const [accepted, setAccepted] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  if (!isOpen) return null;

  const getStageInfo = () => {
    const stageData = {
      documents: {
        title: "Responsabilidade pela Documentação",
        icon: FileText,
        color: "blue",
        content: `ACEITE DE RESPONSABILIDADE - DOCUMENTAÇÃO

Ao prosseguir com o upload e validação de documentos, você confirma que:

1. **AUTENTICIDADE DOS DOCUMENTOS**
   • Todos os documentos enviados são ORIGINAIS e AUTÊNTICOS
   • Não foram alterados, modificados ou falsificados de qualquer forma
   • Você possui legal autoridade para fornecer estes documentos

2. **RESPONSABILIDADE LEGAL**
   • Você é TOTALMENTE RESPONSÁVEL pela veracidade de todos os documentos
   • Entende que documentos falsos podem resultar em negação permanente de vistos
   • Assume todas as consequências legais por documentos inadequados

3. **SISTEMA INFORMATIVO**
   • Este sistema oferece validação INFORMATIVA baseada em padrões públicos
   • NÃO substitui revisão profissional por advogado de imigração
   • Recomendamos consulta jurídica para casos complexos

4. **ISENÇÃO DE RESPONSABILIDADE**
   • O sistema não garante aprovação pelo USCIS
   • Você é responsável por verificar todos os requisitos oficiais
   • Este serviço não constitui aconselhamento jurídico`
      },
      forms: {
        title: "Responsabilidade pelo Preenchimento de Formulários",
        icon: FileText,
        color: "green",
        content: `ACEITE DE RESPONSABILIDADE - FORMULÁRIOS USCIS

Ao prosseguir com o preenchimento de formulários, você confirma que:

1. **VERACIDADE DAS INFORMAÇÕES**
   • Todas as informações fornecidas são VERDADEIRAS e COMPLETAS
   • Não omitiu nenhuma informação relevante solicitada
   • Entende que informações falsas podem resultar em consequências legais

2. **FORMULÁRIOS OFICIAIS**
   • Os formulários gerados seguem padrões públicos do USCIS
   • Você deve revisar TODA informação antes de submeter ao USCIS
   • Este sistema facilita o preenchimento mas NÃO garante aprovação

3. **RESPONSABILIDADE FINAL**
   • Você é RESPONSÁVEL por revisar e validar todos os dados
   • Deve verificar requisitos atuais no site oficial do USCIS
   • Recomendamos revisão por advogado especializado

4. **LIMITAÇÕES DO SISTEMA**
   • Este é um sistema de apoio informativo
   • Não substitui consultoria jurídica profissional
   • Para casos complexos, consulte sempre um advogado de imigração`
      },
      cover_letter: {
        title: "Responsabilidade pela Carta de Apresentação",
        icon: FileText,
        color: "purple",
        content: `ACEITE DE RESPONSABILIDADE - CARTA DE APRESENTAÇÃO

Ao prosseguir com a geração da carta de apresentação, você confirma que:

1. **CONTEÚDO BASEADO EM FATOS**
   • A carta será baseada nas informações que VOCÊ forneceu
   • Você garante que todos os fatos mencionados são VERDADEIROS
   • Não há invenção ou exagero de qualificações ou experiências

2. **REVISÃO OBRIGATÓRIA**
   • Você DEVE revisar completamente a carta antes de usar
   • É sua responsabilidade corrigir qualquer erro ou imprecisão
   • O sistema gera sugestões baseadas em suas informações

3. **USO APROPRIADO**
   • A carta é um apoio ao seu processo de aplicação
   • Não garante aprovação pelo USCIS
   • Deve ser usada como base, podendo ser personalizada

4. **CONSULTORIA JURÍDICA**
   • Para casos complexos, consulte um advogado especializado
   • Este sistema não oferece aconselhamento jurídico
   • Recomendamos revisão profissional antes da submissão final`
      },
      review: {
        title: "Responsabilidade pela Revisão do Processo",
        icon: CheckCircle2,
        color: "orange",
        content: `ACEITE DE RESPONSABILIDADE - REVISÃO FINAL

Ao prosseguir com a revisão final do seu processo, você confirma que:

1. **REVISÃO COMPLETA**
   • Revisou TODOS os documentos, formulários e cartas gerados
   • Verificou a precisão de todas as informações fornecidas
   • Confirma que tudo está correto e atualizado

2. **RESPONSABILIDADE INTEGRAL**
   • Assume TOTAL responsabilidade por todo o conteúdo do processo
   • Entende que você é o único responsável pela submissão ao USCIS
   • Qualquer erro ou omissão é de sua responsabilidade

3. **NATUREZA INFORMATIVA**
   • Este sistema oferece orientação baseada em requisitos públicos
   • NÃO constitui aconselhamento jurídico profissional
   • Não garante aprovação ou sucesso no processo

4. **RECOMENDAÇÕES FINAIS**
   • Verifique requisitos atuais no site oficial do USCIS (uscis.gov)
   • Consulte um advogado de imigração para casos complexos
   • Mantenha cópias de todos os documentos enviados`
      },
      final: {
        title: "Aceite Final de Responsabilidade",
        icon: Shield,
        color: "red",
        content: `ACEITE FINAL DE RESPONSABILIDADE - ANTES DO DOWNLOAD

IMPORTANTE: Leia cuidadosamente antes de prosseguir com o pagamento e download.

Ao finalizar este processo e fazer o download dos documentos, você declara e concorda que:

1. **RESPONSABILIDADE TOTAL**
   • Você é ÚNICA E EXCLUSIVAMENTE responsável por todas as informações fornecidas
   • Assume total responsabilidade pela veracidade de todos os documentos
   • Entende que este sistema é APENAS informativo e educacional

2. **NATUREZA DO SERVIÇO**
   • Este sistema NÃO constitui aconselhamento jurídico
   • NÃO somos escritório de advocacia ou consultoria jurídica
   • Os documentos gerados são baseados em informações públicas do USCIS

3. **LIMITAÇÕES E ISENÇÕES**
   • NÃO garantimos aprovação pelo USCIS
   • NÃO nos responsabilizamos por negações ou problemas no processo
   • Requisitos podem mudar - sempre verifique o site oficial do USCIS

4. **RECOMENDAÇÕES IMPORTANTES**
   • SEMPRE consulte um advogado de imigração qualificado
   • Verifique todos os requisitos atuais no site oficial (uscis.gov)
   • Revise TODOS os documentos antes de enviar ao USCIS

5. **CONCORDÂNCIA FINAL**
   • Ao prosseguir, você ISENTA nossa plataforma de qualquer responsabilidade
   • Entende que todo o processo é de sua responsabilidade
   • Concorda em não nos responsabilizar por qualquer resultado

PARA CASOS COMPLEXOS, SEMPRE CONSULTE UM ADVOGADO ESPECIALIZADO EM IMIGRAÇÃO.`
      }
    };

    return stageData[stage];
  };

  const generateConsentHash = (text: string): string => {
    // Hash simples para tracking de consent
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `${stage}-${Math.abs(hash).toString(16)}-${Date.now()}`;
  };

  const handleAccept = async () => {
    if (!accepted) return;
    
    setIsProcessing(true);
    try {
      const stageInfo = getStageInfo();
      const consentHash = generateConsentHash(stageInfo.content);
      await onAccept(consentHash);
    } catch (error) {
      console.error('Error accepting disclaimer:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const stageInfo = getStageInfo();
  const IconComponent = stageInfo.icon;

  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    orange: 'text-orange-600 bg-orange-100',
    red: 'text-red-600 bg-red-100'
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorClasses[stageInfo.color as keyof typeof colorClasses]}`}>
              <IconComponent className="h-5 w-5" />
            </div>
            <div>
              <div className="text-lg font-semibold">{stageInfo.title}</div>
              <div className="text-sm text-gray-600 font-normal">
                Etapa: {stage.charAt(0).toUpperCase() + stage.slice(1)} | Caso: {caseId}
              </div>
            </div>
          </CardTitle>
          <CardDescription>
            <div className="flex items-start space-x-2 mt-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm">
                Leia atentamente este aceite de responsabilidade antes de prosseguir. 
                É obrigatório para continuar com o processo.
              </span>
            </div>
          </CardDescription>
        </CardHeader>

        <CardContent className="pt-0">
          {/* Disclaimer Content */}
          <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto mb-6">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
              {stageInfo.content}
            </pre>
          </div>

          {/* Legal Notice */}
          <div className="bg-red-50 border border-red-200 p-4 rounded-lg mb-6">
            <div className="flex items-start space-x-3">
              <Scale className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="text-red-800">
                <div className="font-semibold text-sm">AVISO LEGAL IMPORTANTE</div>
                <p className="text-sm mt-1">
                  Este sistema é uma ferramenta informativa e educacional. NÃO oferecemos consultoria jurídica. 
                  Para orientação específica sobre seu caso, sempre consulte um advogado de imigração licenciado.
                </p>
              </div>
            </div>
          </div>

          {/* Consent Checkbox */}
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6">
            <label className="flex items-start space-x-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={accepted}
                onChange={(e) => setAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-blue-800">
                <strong>Li, entendi e ACEITO</strong> todos os termos de responsabilidade acima. 
                Confirmo que sou responsável por todas as informações fornecidas e entendo 
                que este sistema não constitui consultoria jurídica.
              </span>
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={loading || isProcessing}
              className="px-6"
            >
              Cancelar
            </Button>

            <div className="flex items-center space-x-3">
              <div className="flex items-center text-xs text-gray-500">
                <Info className="h-3 w-3 mr-1" />
                Aceite obrigatório para continuar
              </div>
              
              <Button
                onClick={handleAccept}
                disabled={!accepted || loading || isProcessing}
                className={`px-8 ${
                  accepted ? 'bg-[#FF6B35] hover:bg-[#FF6B35]/90' : 'bg-gray-400'
                }`}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processando...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    Aceitar e Continuar
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DisclaimerModal;