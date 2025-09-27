import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  ArrowRight,
  Upload,
  FileText,
  CheckCircle,
  AlertTriangle,
  X,
  Eye,
  RefreshCw,
  Info,
  Camera,
  File,
  Image
} from "lucide-react";

interface DocumentRequirement {
  id: string;
  name: string;
  description: string;
  required: boolean;
  category: string;
  formats: string[];
  maxSize: string;
  uploaded: boolean;
  fileId?: string;
  fileName?: string;
  aiAnalysis?: {
    valid: boolean;
    legible: boolean;
    completeness: number;
    issues: string[];
    extracted_data: any;
  };
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  document_type: string;
}

const DocumentUploadAuto = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [case_, setCase] = useState<any>(null);
  const [visaSpecs, setVisaSpecs] = useState<any>(null);
  const [documentRequirements, setDocumentRequirements] = useState<DocumentRequirement[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }
      
      const response = await fetch(url);

      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        if (data.case.form_code) {
          await fetchVisaSpecs(data.case.form_code);
        }
      } else {
        setError('Caso não encontrado');
      }
    } catch (error) {
      console.error('Fetch case error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchVisaSpecs = async (formCode: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/visa-specs/${formCode}`
      );

      if (response.ok) {
        const data = await response.json();
        setVisaSpecs(data);
        generateDocumentRequirements(data);
      }
    } catch (error) {
      console.error('Fetch visa specs error:', error);
    }
  };

  const generateDocumentRequirements = (specs: any) => {
    const requirements: DocumentRequirement[] = [];
    
    // Base documents for all forms
    const baseDocuments = [
      {
        id: 'passport',
        name: 'Passaporte',
        description: 'Todas as páginas do passaporte válido',
        required: true,
        category: 'Identificação',
        formats: ['PDF', 'JPG', 'PNG'],
        maxSize: '10MB'
      },
      {
        id: 'photos',
        name: 'Fotos Tipo Passaporte',
        description: '2 fotos recentes no padrão USCIS',
        required: true,
        category: 'Identificação',
        formats: ['JPG', 'PNG'],
        maxSize: '5MB'
      }
    ];

    // Add base documents
    baseDocuments.forEach(doc => {
      requirements.push({
        ...doc,
        uploaded: false
      });
    });

    // Add specific documents based on visa type
    if (specs.required_documents) {
      specs.required_documents.forEach((docName: string, index: number) => {
        if (!baseDocuments.find(bd => bd.name.toLowerCase().includes(docName.toLowerCase().split(' ')[0]))) {
          requirements.push({
            id: `doc_${index}`,
            name: docName,
            description: `Documento necessário para ${specs.specifications.title}`,
            required: true,
            category: specs.specifications.category,
            formats: ['PDF', 'JPG', 'PNG'],
            maxSize: '10MB',
            uploaded: false
          });
        }
      });
    }

    setDocumentRequirements(requirements);
  };

  const handleFileUpload = async (file: File, documentType: string) => {
    setIsUploading(true);
    
    try {
      // Validate file
      if (file.size > 10 * 1024 * 1024) { // 10MB
        setError('Arquivo muito grande. Máximo 10MB.');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      formData.append('case_id', caseId || '');

      // Convert to base64 for storage
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64 = e.target?.result as string;
        
        // Simulate AI analysis
        const aiAnalysis = await simulateAIAnalysis(file, documentType);
        
        const uploadedFile: UploadedFile = {
          id: `file_${Date.now()}`,
          name: file.name,
          size: file.size,
          type: file.type,
          url: base64,
          document_type: documentType
        };

        setUploadedFiles(prev => [...prev, uploadedFile]);
        
        // Update document requirements
        setDocumentRequirements(prev => prev.map(req => 
          req.id === documentType ? {
            ...req,
            uploaded: true,
            fileId: uploadedFile.id,
            fileName: file.name,
            aiAnalysis
          } : req
        ));

        // Save to case
        await saveDocumentToCase(uploadedFile, aiAnalysis);
      };
      
      reader.readAsDataURL(file);

    } catch (error) {
      console.error('Upload error:', error);
      setError('Erro no upload. Tente novamente.');
    } finally {
      setIsUploading(false);
    }
  };

  const simulateAIAnalysis = async (file: File, documentType: string) => {
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate AI analysis results
    const isImage = file.type.startsWith('image/');
    const isPDF = file.type === 'application/pdf';
    
    const analysis = {
      valid: Math.random() > 0.1, // 90% chance of being valid
      legible: isImage || isPDF ? Math.random() > 0.05 : true, // 95% chance of being legible
      completeness: Math.floor(Math.random() * 30) + 70, // 70-100% completeness
      issues: [] as string[],
      extracted_data: {}
    };

    // Add some realistic issues
    if (analysis.completeness < 80) {
      analysis.issues.push('Documento pode estar incompleto');
    }
    if (!analysis.legible) {
      analysis.issues.push('Qualidade da imagem precisa melhorar');
    }
    if (file.size < 100000) { // Less than 100KB
      analysis.issues.push('Arquivo muito pequeno, pode estar comprimido demais');
    }

    // Extract mock data based on document type
    if (documentType === 'passport') {
      analysis.extracted_data = {
        document_number: 'BR1234567',
        full_name: 'Nome extraído do passaporte',
        expiration_date: '2030-12-31',
        country_of_issue: 'Brasil'
      };
    }

    return analysis;
  };

  const saveDocumentToCase = async (file: UploadedFile, analysis: any) => {
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }

      const documents = [...(case_?.uploaded_documents || []), file.id];
      const documentAnalysis = {
        ...(case_?.document_analysis || {}),
        [file.id]: analysis
      };

      await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          uploaded_documents: documents,
          document_analysis: documentAnalysis,
          status: 'documents_uploaded'
        }),
      });

    } catch (error) {
      console.error('Save document error:', error);
    }
  };

  const removeDocument = async (documentId: string, fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    setDocumentRequirements(prev => prev.map(req => 
      req.id === documentId ? {
        ...req,
        uploaded: false,
        fileId: undefined,
        fileName: undefined,
        aiAnalysis: undefined
      } : req
    ));
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent, documentType: string) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0], documentType);
    }
  };

  const getRequiredDocumentsCount = () => {
    return documentRequirements.filter(req => req.required).length;
  };

  const getUploadedRequiredCount = () => {
    return documentRequirements.filter(req => req.required && req.uploaded).length;
  };

  const canContinue = () => {
    const requiredUploaded = getUploadedRequiredCount();
    const totalRequired = getRequiredDocumentsCount();
    return requiredUploaded === totalRequired;
  };

  const continueToNextStep = () => {
    navigate(`/auto-application/case/${caseId}/story`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando documentos necessários...</p>
        </div>
      </div>
    );
  }

  if (error || !case_) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <Card className="glass border-0 max-w-md">
          <CardContent className="text-center p-8">
            <AlertTriangle className="h-12 w-12 text-gray-700 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">
              {error || 'Caso não encontrado'}
            </h2>
            <Button onClick={() => navigate('/auto-application/start')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate(`/auto-application/case/${caseId}/basic-data`)}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <Upload className="h-8 w-8 text-black" />
                  {visaSpecs?.specifications.title || case_.form_code}
                </h1>
                <p className="text-muted-foreground">
                  Etapa 2 de 6: Upload de Documentos • Caso: {case_.case_id}
                </p>
              </div>
            </div>
            <Badge className="bg-gray-100 text-gray-800 border-gray-200">
              {getUploadedRequiredCount()}/{getRequiredDocumentsCount()} Obrigatórios
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Progress */}
            <Card className="glass border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium">Progresso dos Documentos</span>
                  <span className="text-sm text-muted-foreground">
                    {getUploadedRequiredCount()}/{getRequiredDocumentsCount()} obrigatórios
                  </span>
                </div>
                <Progress 
                  value={(getUploadedRequiredCount() / Math.max(getRequiredDocumentsCount(), 1)) * 100} 
                  className="h-3" 
                />
              </CardContent>
            </Card>

            {/* Document Requirements */}
            <div className="space-y-4">
              {documentRequirements.map((doc) => (
                <Card key={doc.id} className="glass border-0">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-foreground">{doc.name}</h3>
                          {doc.required && (
                            <Badge variant="outline" className="text-xs">Obrigatório</Badge>
                          )}
                          <Badge className="bg-gray-100 text-gray-700 border-gray-200 text-xs">
                            {doc.category}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{doc.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>Formatos: {doc.formats.join(', ')}</span>
                          <span>Máximo: {doc.maxSize}</span>
                        </div>
                      </div>
                      
                      {doc.uploaded ? (
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-5 w-5 text-gray-700" />
                          <span className="text-sm text-gray-700">Enviado</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                          <span className="text-sm text-muted-foreground">Pendente</span>
                        </div>
                      )}
                    </div>

                    {doc.uploaded && doc.aiAnalysis ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <File className="h-4 w-4 text-gray-700" />
                            <span className="text-sm font-medium">{doc.fileName}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeDocument(doc.id, doc.fileId!)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>

                        {/* AI Analysis Results */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Análise da IA:</span>
                            <div className="flex items-center gap-2">
                              {doc.aiAnalysis.valid ? (
                                <CheckCircle className="h-4 w-4 text-gray-700" />
                              ) : (
                                <AlertTriangle className="h-4 w-4 text-gray-700" />
                              )}
                              <span>{doc.aiAnalysis.completeness}% completo</span>
                            </div>
                          </div>
                          
                          {doc.aiAnalysis.issues.length > 0 && (
                            <div className="p-3 bg-gray-100 rounded-lg">
                              <p className="text-sm font-medium text-gray-800 mb-1">Observações:</p>
                              {doc.aiAnalysis.issues.map((issue, index) => (
                                <p key={index} className="text-sm text-gray-700">• {issue}</p>
                              ))}
                            </div>
                          )}

                          {doc.aiAnalysis.extracted_data && Object.keys(doc.aiAnalysis.extracted_data).length > 0 && (
                            <div className="p-3 bg-gray-50 rounded-lg">
                              <p className="text-sm font-medium text-gray-800 mb-1">Informações Extraídas:</p>
                              {Object.entries(doc.aiAnalysis.extracted_data).map(([key, value]) => (
                                <p key={key} className="text-sm text-gray-700">
                                  <strong>{key}:</strong> {String(value)}
                                </p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div
                        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                          dragActive ? 'border-black bg-gray-50' : 'border-gray-300'
                        }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={(e) => handleDrop(e, doc.id)}
                      >
                        <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground mb-2">
                          Arraste o arquivo aqui ou clique para selecionar
                        </p>
                        <input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                              handleFileUpload(e.target.files[0], doc.id);
                            }
                          }}
                          className="hidden"
                          id={`file-${doc.id}`}
                        />
                        <Button
                          variant="outline"
                          onClick={() => document.getElementById(`file-${doc.id}`)?.click()}
                          disabled={isUploading}
                        >
                          {isUploading ? (
                            <RefreshCw className="h-4 w-4 animate-spin" />
                          ) : (
                            <>
                              <Camera className="h-4 w-4" />
                              Selecionar Arquivo
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
              <div className="text-sm text-muted-foreground">
                {canContinue() ? (
                  <div className="flex items-center gap-2 text-gray-700">
                    <CheckCircle className="h-4 w-4" />
                    <span>Todos os documentos obrigatórios foram enviados</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-gray-700" />
                    <span>
                      Faltam {getRequiredDocumentsCount() - getUploadedRequiredCount()} documento(s) obrigatório(s)
                    </span>
                  </div>
                )}
              </div>

              <Button 
                onClick={continueToNextStep}
                disabled={!canContinue()}
                className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
              >
                Continuar para História
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Requirements Summary */}
            {visaSpecs && (
              <Card className="glass border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <Info className="h-5 w-5 text-black" />
                    Documentos para {case_.form_code}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    {visaSpecs.specifications.description}
                  </p>
                  
                  <div className="text-sm">
                    <p className="font-medium text-foreground mb-1">
                      Total: {documentRequirements.length} documentos
                    </p>
                    <p className="text-muted-foreground">
                      Obrigatórios: {getRequiredDocumentsCount()}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Progress Steps */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Progresso da Aplicação</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Dados Básicos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-black text-white rounded-full flex items-center justify-center text-xs font-bold">
                      2
                    </div>
                    <span className="text-sm font-medium">Upload de Documentos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      3
                    </div>
                    <span className="text-sm text-muted-foreground">Conte sua História</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      4
                    </div>
                    <span className="text-sm text-muted-foreground">Formulário Amigável</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      5
                    </div>
                    <span className="text-sm text-muted-foreground">Revisão Final</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      6
                    </div>
                    <span className="text-sm text-muted-foreground">Pagamento & Download</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="glass border-0 bg-gray-50">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-gray-700 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground mb-1">Dicas de Upload</p>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Use arquivos de alta qualidade (mínimo 300 DPI)</li>
                      <li>• Certifique-se que o texto está legível</li>
                      <li>• Inclua todas as páginas do documento</li>
                      <li>• Nossa IA verifica automaticamente a qualidade</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadAuto;