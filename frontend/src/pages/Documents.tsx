import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  FileText, 
  Upload, 
  Eye, 
  RotateCcw, 
  Edit, 
  Trash2, 
  Calendar, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Search,
  Download,
  Plus
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Document {
  id: string;
  filename: string;
  original_filename: string;
  document_type: string;
  status: string;
  priority: string;
  file_size: number;
  mime_type: string;
  tags: string[];
  expiration_date?: string;
  issue_date?: string;
  ai_analysis?: {
    completeness_score: number;
    validity_status: string;
    key_information: string[];
    missing_information: string[];
    suggestions: string[];
    expiration_warnings: string[];
    quality_issues: string[];
    next_steps: string[];
  };
  created_at: string;
  updated_at: string;
}

interface DocumentStats {
  total: number;
  approved: number;
  expired: number;
  pending: number;
  completion_rate: number;
}

interface UpcomingExpiration {
  document_id: string;
  document_type: string;
  filename: string;
  expiration_date: string;
  days_to_expire: number;
}

const Documents = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [upcomingExpirations, setUpcomingExpirations] = useState<UpcomingExpiration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents);
        setStats(data.stats);
        setUpcomingExpirations(data.upcoming_expirations || []);
      } else if (response.status === 401) {
        localStorage.removeItem('osprey_token');
        localStorage.removeItem('osprey_user');
        navigate('/login');
      } else {
        setError('Erro ao carregar documentos');
      }
    } catch (error) {
      console.error('Documents error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'approved': 'bg-gray-100 text-black border-gray-200',
      'pending_review': 'bg-gray-200 text-black border-gray-300',
      'requires_improvement': 'bg-gray-300 text-black border-gray-400',
      'expired': 'bg-gray-400 text-white border-gray-500',
      'missing_info': 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      'approved': CheckCircle,
      'pending_review': Clock,
      'requires_improvement': AlertTriangle,
      'expired': AlertTriangle,
      'missing_info': AlertTriangle,
    };
    const IconComponent = icons[status as keyof typeof icons] || Clock;
    return <IconComponent className="h-4 w-4" />;
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      'high': 'text-black bg-gray-200 border-gray-300',
      'medium': 'text-black bg-gray-100 border-gray-200',
      'low': 'text-gray-600 bg-gray-50 border-gray-100',
    };
    return colors[priority as keyof typeof colors] || 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const getDocumentTypeLabel = (type: string) => {
    const labels = {
      'passport': 'Passaporte',
      'birth_certificate': 'Certidão de Nascimento',
      'marriage_certificate': 'Certidão de Casamento',
      'divorce_certificate': 'Certidão de Divórcio',
      'education_diploma': 'Diploma de Educação',
      'education_transcript': 'Histórico Escolar',
      'employment_letter': 'Carta de Trabalho',
      'bank_statement': 'Extrato Bancário',
      'tax_return': 'Declaração de IR',
      'medical_exam': 'Exame Médico',
      'police_clearance': 'Antecedentes Criminais',
      'sponsor_documents': 'Documentos do Sponsor',
      'photos': 'Fotos',
      'form_i130': 'Formulário I-130',
      'form_ds160': 'Formulário DS-160',
      'other': 'Outros',
    };
    return labels[type as keyof typeof labels] || type.toUpperCase();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getDaysUntilExpiration = (expirationDate: string) => {
    const expDate = new Date(expirationDate);
    const now = new Date();
    const diffTime = expDate.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         getDocumentTypeLabel(doc.document_type).toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterStatus === "all" || doc.status === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  const handleReanalyze = async (documentId: string) => {
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/documents/${documentId}/reanalyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        await fetchDocuments(); // Refresh the list
        setError(""); // Clear any previous errors
      } else {
        setError('Erro ao reprocessar documento');
      }
    } catch (error) {
      console.error('Reanalyze error:', error);
      setError('Erro de conexão');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando documentos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <FileText className="h-8 w-8 text-black" />
                Meus Documentos
              </h1>
              <p className="text-muted-foreground">
                Gerencie seus documentos de imigração com análise IA
              </p>
            </div>
            
            <Button 
              className="bg-black text-white hover:bg-gray-800"
              onClick={() => setShowUpload(true)}
            >
              <Plus className="h-4 w-4" />
              Upload Documento
            </Button>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        
        {error && (
          <Alert className="mb-6 border-destructive/50 text-destructive bg-destructive/10">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Stats Overview */}
        {stats && (
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            <Card className="glass border-0 card-hover">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-black/10 rounded-lg flex items-center justify-center">
                    <FileText className="h-6 w-6 text-black" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">{stats.total}</div>
                    <div className="text-sm text-muted-foreground">Total</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-0 card-hover">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center">
                    <CheckCircle className="h-6 w-6 text-success" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">{stats.approved}</div>
                    <div className="text-sm text-muted-foreground">Aprovados</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-0 card-hover">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Clock className="h-6 w-6 text-gray-700" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">{stats.pending}</div>
                    <div className="text-sm text-muted-foreground">Pendentes</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-0 card-hover">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="h-6 w-6 text-gray-700" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">{stats.expired}</div>
                    <div className="text-sm text-muted-foreground">Expirados</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-0 card-hover">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                    <div className="text-lg font-bold text-accent">{stats.completion_rate}%</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">Taxa</div>
                    <div className="text-sm text-muted-foreground">Conclusão</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Main Document List */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Search and Filter */}
            <Card className="glass border-0">
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Buscar documentos..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-4 py-2 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="all">Todos os status</option>
                    <option value="approved">Aprovados</option>
                    <option value="pending_review">Pendentes</option>
                    <option value="requires_improvement">Precisam melhorar</option>
                    <option value="expired">Expirados</option>
                  </select>
                </div>
              </CardContent>
            </Card>

            {/* Documents Grid */}
            {filteredDocuments.length === 0 ? (
              <Card className="glass border-0">
                <CardContent className="p-12 text-center">
                  <div className="w-16 h-16 bg-black/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="h-8 w-8 text-black" />
                  </div>
                  <h3 className="font-medium text-foreground mb-2">
                    {documents.length === 0 ? "Nenhum documento ainda" : "Nenhum documento encontrado"}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {documents.length === 0 
                      ? "Comece fazendo upload dos seus documentos de imigração"
                      : "Tente ajustar os filtros de busca"
                    }
                  </p>
                  {documents.length === 0 && (
                    <Button className="bg-black text-white hover:bg-gray-800" onClick={() => setShowUpload(true)}>
                      <Upload className="h-4 w-4" />
                      Fazer Upload
                    </Button>
                  )}
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {filteredDocuments.map((doc) => (
                  <Card key={doc.id} className="glass border-0 card-hover">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 bg-black/10 rounded-lg flex items-center justify-center">
                            <FileText className="h-6 w-6 text-black" />
                          </div>
                          <div>
                            <h4 className="font-medium text-foreground">
                              {getDocumentTypeLabel(doc.document_type)}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {doc.original_filename}
                            </p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge className={`${getStatusColor(doc.status)} border`}>
                                {getStatusIcon(doc.status)}
                                {doc.status.replace('_', ' ')}
                              </Badge>
                              <Badge className={`${getPriorityColor(doc.priority)} border`}>
                                {doc.priority}
                              </Badge>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => setSelectedDocument(doc)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleReanalyze(doc.id)}
                          >
                            <RotateCcw className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      {/* AI Analysis Summary */}
                      {doc.ai_analysis && (
                        <div className="bg-white/30 rounded-lg p-4 space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-foreground">Análise IA</span>
                            <Badge className="bg-black/10 text-black border-primary/20">
                              {doc.ai_analysis.completeness_score}% completo
                            </Badge>
                          </div>
                          
                          <Progress value={doc.ai_analysis.completeness_score} className="h-2" />
                          
                          {doc.ai_analysis.suggestions.length > 0 && (
                            <div className="text-xs text-muted-foreground">
                              <strong>Próximas ações:</strong> {doc.ai_analysis.suggestions[0]}
                              {doc.ai_analysis.suggestions.length > 1 && ` (+${doc.ai_analysis.suggestions.length - 1} mais)`}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Document Info */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 pt-4 border-t border-white/20">
                        <div>
                          <div className="text-xs text-muted-foreground">Tamanho</div>
                          <div className="text-sm font-medium">{formatFileSize(doc.file_size)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground">Criado</div>
                          <div className="text-sm font-medium">{formatDate(doc.created_at)}</div>
                        </div>
                        {doc.expiration_date && (
                          <div>
                            <div className="text-xs text-muted-foreground">Expira em</div>
                            <div className="text-sm font-medium flex items-center gap-1">
                              {getDaysUntilExpiration(doc.expiration_date) <= 30 && (
                                <AlertTriangle className="h-3 w-3 text-orange-500" />
                              )}
                              {getDaysUntilExpiration(doc.expiration_date)} dias
                            </div>
                          </div>
                        )}
                        {doc.tags.length > 0 && (
                          <div>
                            <div className="text-xs text-muted-foreground">Tags</div>
                            <div className="text-sm font-medium truncate">
                              {doc.tags.join(', ')}
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Upload Section */}
            <Card className="glass border-0">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold">Upload Rápido</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => setShowUpload(true)}
                >
                  <Upload className="h-4 w-4" />
                  Novo Documento
                </Button>
              </CardContent>
            </Card>

            {/* Upcoming Expirations */}
            {upcomingExpirations.length > 0 && (
              <Card className="glass border-0">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-orange-500" />
                    Próximas Expirações
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {upcomingExpirations.slice(0, 5).map((exp, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <AlertTriangle className="h-4 w-4 text-gray-700" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground line-clamp-1">
                          {getDocumentTypeLabel(exp.document_type)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {exp.days_to_expire} dias restantes
                        </p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Tips */}
            <Card className="glass border-0">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold">💡 Dicas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm text-muted-foreground space-y-2">
                  <p>• Mantenha documentos atualizados</p>
                  <p>• Faça upload de arquivos em alta qualidade</p>
                  <p>• Use tags para organizar</p>
                  <p>• Monitore datas de expiração</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Document Details Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-white/20">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-foreground">
                  {getDocumentTypeLabel(selectedDocument.document_type)}
                </h3>
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedDocument(null)}
                >
                  ✕
                </Button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Nome do arquivo</div>
                  <div className="font-medium">{selectedDocument.original_filename}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Status</div>
                  <Badge className={`${getStatusColor(selectedDocument.status)} border mt-1`}>
                    {getStatusIcon(selectedDocument.status)}
                    {selectedDocument.status.replace('_', ' ')}
                  </Badge>
                </div>
              </div>

              {/* AI Analysis Details */}
              {selectedDocument.ai_analysis && (
                <div className="bg-white/30 rounded-lg p-4 space-y-4">
                  <h4 className="font-medium text-foreground">Análise Detalhada da IA</h4>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Completude</div>
                      <div className="font-bold text-lg">
                        {selectedDocument.ai_analysis.completeness_score}%
                      </div>
                      <Progress value={selectedDocument.ai_analysis.completeness_score} className="h-2 mt-1" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Validade</div>
                      <div className="font-medium capitalize">
                        {selectedDocument.ai_analysis.validity_status}
                      </div>
                    </div>
                  </div>

                  {selectedDocument.ai_analysis.key_information.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-foreground mb-2">✅ Informações Encontradas</div>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {selectedDocument.ai_analysis.key_information.map((info, index) => (
                          <li key={index}>• {info}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selectedDocument.ai_analysis.suggestions.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-foreground mb-2">💡 Sugestões</div>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {selectedDocument.ai_analysis.suggestions.map((suggestion, index) => (
                          <li key={index}>• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selectedDocument.ai_analysis.next_steps.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-foreground mb-2">🎯 Próximos Passos</div>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {selectedDocument.ai_analysis.next_steps.map((step, index) => (
                          <li key={index}>• {step}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => handleReanalyze(selectedDocument.id)}
                >
                  <RotateCcw className="h-4 w-4" />
                  Reprocessar
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => setSelectedDocument(null)}
                >
                  Fechar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Documents;