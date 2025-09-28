import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  CheckCircle,
  AlertTriangle,
  Download,
  FileText,
  DollarSign,
  MapPin,
  Clock,
  Phone,
  Mail,
  ExternalLink,
  Copy,
  Printer,
  Info,
  CreditCard,
  Building,
  CalendarDays
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface SubmissionInstructions {
  case_id: string;
  form_code: string;
  submission_info: {
    filing_office: string;
    address: {
      name: string;
      street: string;
      city: string;
      state: string;
      zip: string;
    };
    po_box?: string;
    filing_fee: string;
    additional_fees: Record<string, string>;
    processing_time: string;
    online_application?: string;
  };
  required_documents: Array<{
    item: string;
    required: boolean;
    notes?: string;
    page?: string;
  }>;
  signature_guide: {
    [key: string]: {
      location: string;
      instructions: string;
    };
    important_notes: string[];
  };
  payment_info: {
    total_amount: string;
    payment_method: string;
    payable_to?: string;
    additional_fees?: string[];
    instructions: string[];
  };
  submission_steps: Array<{
    step: number;
    title: string;
    description: string;
  }>;
  important_notes: string[];
}

interface USCISSubmissionGuideProps {
  caseId: string;
  onDownloadPackage: () => void;
}

const USCISSubmissionGuide = ({ caseId, onDownloadPackage }: USCISSubmissionGuideProps) => {
  const [instructions, setInstructions] = useState<SubmissionInstructions | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState("overview");
  const { toast } = useToast();

  useEffect(() => {
    fetchSubmissionInstructions();
  }, [caseId]);

  const fetchSubmissionInstructions = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}/submission-instructions`);
      if (response.ok) {
        const data = await response.json();
        setInstructions(data);
      } else {
        throw new Error('Failed to fetch instructions');
      }
    } catch (error) {
      console.error('Error fetching submission instructions:', error);
      toast({
        title: "Erro",
        description: "Erro ao carregar instruções de submissão",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copiado!",
      description: "Endereço copiado para a área de transferência",
    });
  };

  const formatAddress = (address: any) => {
    return `${address.name}\n${address.street}\n${address.city}, ${address.state} ${address.zip}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  if (!instructions) {
    return (
      <div className="text-center p-8">
        <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-gray-500" />
        <p className="text-gray-600">Erro ao carregar instruções</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <Card className="border-black">
        <CardHeader className="bg-black text-white">
          <CardTitle className="flex items-center gap-3">
            <FileText className="h-6 w-6" />
            Instruções Completas para Submissão ao USCIS
          </CardTitle>
          <p className="text-gray-200">
            Case ID: {instructions.case_id} | Formulário: {instructions.form_code}
          </p>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <Clock className="h-8 w-8 mx-auto mb-2 text-black" />
              <p className="font-medium">Tempo de Processamento</p>
              <p className="text-sm text-gray-600">{instructions.submission_info.processing_time}</p>
            </div>
            <div className="text-center">
              <DollarSign className="h-8 w-8 mx-auto mb-2 text-black" />
              <p className="font-medium">Taxa Total</p>
              <p className="text-sm text-gray-600">{instructions.payment_info.total_amount}</p>
            </div>
            <div className="text-center">
              <Building className="h-8 w-8 mx-auto mb-2 text-black" />
              <p className="font-medium">Escritório</p>
              <p className="text-sm text-gray-600">{instructions.submission_info.filing_office}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg border">
        {[
          { id: "overview", label: "Visão Geral", icon: Info },
          { id: "documents", label: "Documentos", icon: FileText },
          { id: "signatures", label: "Assinaturas", icon: CheckCircle },
          { id: "payment", label: "Pagamento", icon: CreditCard },
          { id: "steps", label: "Passo a Passo", icon: CalendarDays },
          { id: "address", label: "Endereço", icon: MapPin }
        ].map(({ id, label, icon: Icon }) => (
          <Button
            key={id}
            variant={activeSection === id ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveSection(id)}
            className={activeSection === id ? "bg-black text-white" : ""}
          >
            <Icon className="h-4 w-4 mr-2" />
            {label}
          </Button>
        ))}
      </div>

      {/* Content Sections */}
      {activeSection === "overview" && (
        <Card className="border-black">
          <CardHeader>
            <CardTitle>Visão Geral da Submissão</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Info className="h-4 w-4" />
                  Informações Básicas
                </h4>
                <div className="space-y-2 text-sm">
                  <p><strong>Formulário:</strong> {instructions.form_code}</p>
                  <p><strong>Taxa USCIS:</strong> {instructions.submission_info.filing_fee}</p>
                  <p><strong>Processamento:</strong> {instructions.submission_info.processing_time}</p>
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-500" />
                  Notas Importantes
                </h4>
                <div className="space-y-2">
                  {instructions.important_notes.slice(0, 3).map((note, index) => (
                    <div key={index} className="text-sm p-3 bg-orange-50 border-l-4 border-orange-400 rounded">
                      {note}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeSection === "documents" && (
        <Card className="border-black">
          <CardHeader>
            <CardTitle>Checklist de Documentos Obrigatórios</CardTitle>
            <p className="text-sm text-gray-600">
              Verifique cada item antes da submissão
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {instructions.required_documents.map((doc, index) => (
                <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
                  <div className="mt-1">
                    {doc.required ? (
                      <CheckCircle className="h-5 w-5 text-red-500" />
                    ) : (
                      <CheckCircle className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium">{doc.item}</p>
                      {doc.required && (
                        <Badge variant="destructive" className="text-xs">Obrigatório</Badge>
                      )}
                      {doc.page && (
                        <Badge variant="outline" className="text-xs">
                          {doc.page}
                        </Badge>
                      )}
                    </div>
                    {doc.notes && (
                      <p className="text-sm text-gray-600">{doc.notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeSection === "signatures" && (
        <Card className="border-black">
          <CardHeader>
            <CardTitle>Guia de Assinaturas</CardTitle>
            <p className="text-sm text-gray-600">
              Onde e como assinar os documentos
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {Object.entries(instructions.signature_guide).map(([key, value]) => {
              if (key === 'important_notes') return null;
              return (
                <div key={key} className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2 capitalize">
                    {key.replace('_', ' ')}
                  </h4>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-medium text-gray-700">Local:</p>
                      <p className="bg-gray-100 p-2 rounded font-mono">{value.location}</p>
                    </div>
                    <div>
                      <p className="font-medium text-gray-700">Instruções:</p>
                      <p>{value.instructions}</p>
                    </div>
                  </div>
                </div>
              );
            })}
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <Info className="h-4 w-4 text-blue-600" />
                Dicas Importantes
              </h4>
              <ul className="space-y-1 text-sm">
                {instructions.signature_guide.important_notes?.map((note, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <div className="w-1 h-1 bg-blue-400 rounded-full"></div>
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {activeSection === "payment" && (
        <Card className="border-black">
          <CardHeader>
            <CardTitle>Informações de Pagamento</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Valor Total</h4>
                  <div className="text-2xl font-bold text-green-600">
                    {instructions.payment_info.total_amount}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Método de Pagamento</h4>
                  <p className="bg-gray-100 p-3 rounded">
                    {instructions.payment_info.payment_method}
                  </p>
                </div>

                {instructions.payment_info.payable_to && (
                  <div>
                    <h4 className="font-medium mb-2">Favorecido</h4>
                    <p className="bg-gray-100 p-3 rounded font-mono">
                      {instructions.payment_info.payable_to}
                    </p>
                  </div>
                )}
              </div>

              <div>
                <h4 className="font-medium mb-3">Instruções de Pagamento</h4>
                <div className="space-y-2">
                  {instructions.payment_info.instructions.map((instruction, index) => (
                    <div key={index} className="flex items-start gap-2 text-sm">
                      <div className="w-1 h-1 bg-black rounded-full mt-2"></div>
                      <p>{instruction}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {instructions.payment_info.additional_fees && (
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">Taxas Adicionais</h4>
                <div className="space-y-2">
                  {instructions.payment_info.additional_fees.map((fee, index) => (
                    <div key={index} className="bg-orange-50 p-3 rounded text-sm">
                      {fee}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeSection === "steps" && (
        <Card className="border-black">
          <CardHeader>
            <CardTitle>Passo a Passo para Submissão</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {instructions.submission_steps.map((step, index) => (
                <div key={index} className="flex gap-4 p-4 border rounded-lg">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center font-bold">
                      {step.step}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium mb-1">{step.title}</h4>
                    <p className="text-sm text-gray-600">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeSection === "address" && (
        <Card className="border-black">
          <CardHeader>
            <CardTitle>Endereço para Envio</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Endereço Completo
                </h4>
                <div className="bg-gray-100 p-4 rounded-lg">
                  <pre className="whitespace-pre-line text-sm font-mono">
                    {formatAddress(instructions.submission_info.address)}
                  </pre>
                </div>
                
                <div className="flex gap-2 mt-3">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(formatAddress(instructions.submission_info.address))}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copiar
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.print()}
                  >
                    <Printer className="h-4 w-4 mr-2" />
                    Imprimir
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                {instructions.submission_info.po_box && (
                  <div>
                    <h4 className="font-medium mb-2">Caixa Postal (Alternativa)</h4>
                    <div className="bg-blue-50 p-3 rounded text-sm">
                      {instructions.submission_info.po_box}
                    </div>
                  </div>
                )}

                {instructions.submission_info.online_application && (
                  <div>
                    <h4 className="font-medium mb-2">Aplicação Online</h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(instructions.submission_info.online_application, '_blank')}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Acessar Site
                    </Button>
                  </div>
                )}

                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>💡 Dica:</strong> Use correio registrado com confirmação de entrega</p>
                  <p><strong>📋 Recomendação:</strong> Faça cópias de todos os documentos antes do envio</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t">
        <Button
          onClick={onDownloadPackage}
          className="bg-black text-white hover:bg-gray-800 flex-1"
        >
          <Download className="h-4 w-4 mr-2" />
          Baixar Pacote Completo
        </Button>
        
        <Button
          variant="outline"
          onClick={() => window.print()}
          className="flex-1"
        >
          <Printer className="h-4 w-4 mr-2" />
          Imprimir Instruções
        </Button>
      </div>

      {/* Important Notes Section */}
      <Card className="border-orange-400 bg-orange-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-800">
            <AlertTriangle className="h-5 w-5" />
            Avisos Importantes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {instructions.important_notes.map((note, index) => (
              <div key={index} className="text-sm text-yellow-800 p-3 bg-yellow-100 rounded">
                {note}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default USCISSubmissionGuide;