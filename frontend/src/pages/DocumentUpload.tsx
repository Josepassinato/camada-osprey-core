import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  X, 
  Calendar,
  Tag,
  ArrowRight,
  Sparkles
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface UploadedFile {
  file: File;
  preview?: string;
  id: string;
}

const DocumentUpload = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [documentType, setDocumentType] = useState("");
  const [tags, setTags] = useState("");
  const [expirationDate, setExpirationDate] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState<string[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const documentTypes = [
    { value: "passport", label: "Passaporte" },
    { value: "birth_certificate", label: "Certidão de Nascimento" },
    { value: "marriage_certificate", label: "Certidão de Casamento" },
    { value: "divorce_certificate", label: "Certidão de Divórcio" },
    { value: "education_diploma", label: "Diploma de Educação" },
    { value: "education_transcript", label: "Histórico Escolar" },
    { value: "employment_letter", label: "Carta de Trabalho" },
    { value: "bank_statement", label: "Extrato Bancário" },
    { value: "tax_return", label: "Declaração de IR" },
    { value: "medical_exam", label: "Exame Médico" },
    { value: "police_clearance", label: "Antecedentes Criminais" },
    { value: "sponsor_documents", label: "Documentos do Sponsor" },
    { value: "photos", label: "Fotos" },
    { value: "form_i130", label: "Formulário I-130" },
    { value: "form_ds160", label: "Formulário DS-160" },
    { value: "other", label: "Outros" }
  ];

  const supportedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(file => {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError(`Arquivo ${file.name} muito grande (máximo 10MB)`);
        return false;
      }
      if (!supportedTypes.includes(file.type)) {
        setError(`Tipo de arquivo ${file.type} não suportado`);
        return false;
      }
      return true;
    });

    const uploadedFiles: UploadedFile[] = validFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));

    setFiles(prev => [...prev, ...uploadedFiles]);
    setError(""); // Clear errors on successful file selection
  };

  const removeFile = (id: string) => {
    setFiles(prev => {
      const fileToRemove = prev.find(f => f.id === id);
      if (fileToRemove?.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return prev.filter(f => f.id !== id);
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError("Selecione pelo menos um arquivo");
      return;
    }

    if (!documentType) {
      setError("Selecione o tipo de documento");
      return;
    }

    setIsUploading(true);
    setError("");
    setSuccess([]);

    const token = localStorage.getItem('osprey_token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Upload each file individually
    const uploadPromises = files.map(async (uploadedFile) => {
      const formData = new FormData();
      formData.append('file', uploadedFile.file);
      formData.append('document_type', documentType);
      formData.append('tags', tags);
      if (expirationDate) formData.append('expiration_date', expirationDate + 'T23:59:59Z');
      if (issueDate) formData.append('issue_date', issueDate + 'T00:00:00Z');

      try {
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/documents/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          return {
            success: true,
            filename: uploadedFile.file.name,
            message: result.message,
            documentId: result.document_id
          };
        } else {
          const error = await response.json();
          return {
            success: false,
            filename: uploadedFile.file.name,
            error: error.detail || 'Erro no upload'
          };
        }
      } catch (error) {
        return {
          success: false,
          filename: uploadedFile.file.name,
          error: 'Erro de conexão'
        };
      }
    });

    try {
      const results = await Promise.all(uploadPromises);
      
      const successes = results.filter(r => r.success);
      const failures = results.filter(r => !r.success);

      if (successes.length > 0) {
        setSuccess(successes.map(s => `${s.filename}: Upload realizado com sucesso`));
        
        // Clear form for successful uploads
        setFiles([]);
        setTags("");
        setExpirationDate("");
        setIssueDate("");
      }

      if (failures.length > 0) {
        setError(`Falhas: ${failures.map(f => `${f.filename}: ${f.error}`).join(', ')}`);
      }

      // If all succeeded, redirect after a delay
      if (failures.length === 0) {
        setTimeout(() => {
          navigate('/documents');
        }, 2000);
      }

    } catch (error) {
      setError('Erro no upload dos documentos');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/documents')}
              className="p-2"
            >
              ← Voltar
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <Upload className="h-8 w-8 text-black" />
                Upload de Documentos
              </h1>
              <p className="text-muted-foreground">
                Faça upload dos seus documentos para análise com IA
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-4xl mx-auto">
          
          {error && (
            <Alert className="mb-6 border-destructive/50 text-destructive bg-destructive/10">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success.length > 0 && (
            <Alert className="mb-6 border-success/50 text-success bg-success/10">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  {success.map((msg, index) => (
                    <div key={index}>{msg}</div>
                  ))}
                  <div className="mt-2 text-xs">Redirecionando para documentos...</div>
                </div>
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* File Upload Area */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Selecionar Arquivos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive 
                      ? "border-primary bg-primary/5" 
                      : "border-border hover:border-primary/50"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png,.tiff,.doc,.docx"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isUploading}
                  />
                  
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                      <Upload className="h-8 w-8 text-black" />
                    </div>
                    
                    <div>
                      <h3 className="font-medium text-foreground mb-2">
                        Arraste arquivos aqui ou clique para selecionar
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Suporta PDF, JPG, PNG, TIFF, DOC, DOCX até 10MB
                      </p>
                    </div>

                    <div className="flex flex-wrap justify-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="secondary">PDF</Badge>
                      <Badge variant="secondary">JPEG/PNG</Badge>
                      <Badge variant="secondary">Word</Badge>
                      <Badge variant="secondary">TIFF</Badge>
                    </div>
                  </div>
                </div>

                {/* File List */}
                {files.length > 0 && (
                  <div className="mt-6 space-y-3">
                    <h4 className="font-medium text-foreground">Arquivos Selecionados:</h4>
                    {files.map((uploadedFile) => (
                      <div key={uploadedFile.id} className="flex items-center gap-4 p-4 bg-white/30 rounded-lg">
                        {uploadedFile.preview && (
                          <img 
                            src={uploadedFile.preview} 
                            alt="Preview" 
                            className="w-12 h-12 object-cover rounded border"
                          />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">{uploadedFile.file.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {formatFileSize(uploadedFile.file.size)} • {uploadedFile.file.type}
                          </p>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(uploadedFile.id)}
                          disabled={isUploading}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Document Details */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" />
                  Detalhes do Documento
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                
                {/* Document Type */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Tipo de Documento *
                  </label>
                  <select
                    value={documentType}
                    onChange={(e) => setDocumentType(e.target.value)}
                    className="w-full px-3 py-2 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    required
                    disabled={isUploading}
                  >
                    <option value="">Selecione o tipo...</option>
                    {documentTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    <Tag className="inline h-4 w-4 mr-1" />
                    Tags (opcional)
                  </label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="brasil, urgente, original (separadas por vírgula)"
                    className="w-full px-3 py-2 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    disabled={isUploading}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Use tags para organizar seus documentos
                  </p>
                </div>

                {/* Dates */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      <Calendar className="inline h-4 w-4 mr-1" />
                      Data de Emissão
                    </label>
                    <input
                      type="date"
                      value={issueDate}
                      onChange={(e) => setIssueDate(e.target.value)}
                      className="w-full px-3 py-2 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                      disabled={isUploading}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      <Calendar className="inline h-4 w-4 mr-1" />
                      Data de Expiração
                    </label>
                    <input
                      type="date"
                      value={expirationDate}
                      onChange={(e) => setExpirationDate(e.target.value)}
                      className="w-full px-3 py-2 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                      disabled={isUploading}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Receberá alertas próximo ao vencimento
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Analysis Info */}
            <Card className="glass border-0 bg-gradient-to-r from-primary/5 to-accent/5">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Sparkles className="h-6 w-6 text-black" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-foreground mb-2">
                      Análise Automática com IA
                    </h4>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <p>✅ Verificação automática de completude</p>
                      <p>✅ Identificação de informações importantes</p>
                      <p>✅ Sugestões de melhorias</p>
                      <p>✅ Alertas de validade</p>
                    </div>
                    <p className="text-xs text-muted-foreground mt-3 italic">
                      * Esta é uma ferramenta de orientação para auto-aplicação. Não substitui consultoria jurídica.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/documents')}
                disabled={isUploading}
              >
                Cancelar
              </Button>
              
              <Button
                type="submit"
                disabled={isUploading || files.length === 0}
                className="bg-black text-white hover:bg-gray-800 group"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Processando...
                  </>
                ) : (
                  <>
                    Fazer Upload e Analisar
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;