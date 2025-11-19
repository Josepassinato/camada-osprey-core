import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Download, 
  Search,
  BarChart,
  Plus,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { makeApiCall } from '@/utils/api';

const AdminKnowledgeBase = () => {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState({});
  const [formTypes, setFormTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Form state
  const [selectedFile, setSelectedFile] = useState(null);
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [selectedFormTypes, setSelectedFormTypes] = useState([]);
  const [description, setDescription] = useState('');
  
  useEffect(() => {
    loadCategories();
    loadDocuments();
    loadStats();
  }, []);
  
  const loadCategories = async () => {
    try {
      const data = await makeApiCall('/admin/knowledge-base/categories', 'GET');
      setCategories(data.categories);
      setFormTypes(data.form_types);
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
    }
  };
  
  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await makeApiCall('/admin/knowledge-base/list', 'GET');
      setDocuments(data.documents);
    } catch (error) {
      console.error('Erro ao carregar documentos:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const loadStats = async () => {
    try {
      const data = await makeApiCall('/admin/knowledge-base/stats/overview', 'GET');
      setStats(data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };
  
  const handleFileSelect = (e) => {
    setSelectedFile(e.target.files[0]);
  };
  
  const handleFormTypeToggle = (formType) => {
    if (selectedFormTypes.includes(formType)) {
      setSelectedFormTypes(selectedFormTypes.filter(ft => ft !== formType));
    } else {
      setSelectedFormTypes([...selectedFormTypes, formType]);
    }
  };
  
  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile || !category || selectedFormTypes.length === 0) {
      setUploadStatus('error:Por favor, preencha todos os campos obrigatórios');
      return;
    }
    
    try {
      setLoading(true);
      setUploadStatus('uploading');
      
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('category', category);
      formData.append('subcategory', subcategory);
      formData.append('form_types', selectedFormTypes.join(','));
      formData.append('description', description);
      formData.append('uploaded_by', 'admin');
      
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/admin/knowledge-base/upload`,
        {
          method: 'POST',
          body: formData
        }
      );
      
      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`success:${result.message}`);
        
        // Limpar formulário
        setSelectedFile(null);
        setCategory('');
        setSubcategory('');
        setSelectedFormTypes([]);
        setDescription('');
        
        // Recarregar lista
        loadDocuments();
        loadStats();
        
        // Limpar input file
        const fileInput = document.getElementById('file-upload');
        if (fileInput) fileInput.value = '';
        
      } else {
        const error = await response.text();
        setUploadStatus(`error:${error}`);
      }
      
    } catch (error) {
      console.error('Erro no upload:', error);
      setUploadStatus(`error:${error.message}`);
    } finally {
      setLoading(false);
      setTimeout(() => setUploadStatus(''), 5000);
    }
  };
  
  const handleDelete = async (documentId) => {
    if (!confirm('Tem certeza que deseja deletar este documento?')) return;
    
    try {
      await makeApiCall(`/admin/knowledge-base/${documentId}`, 'DELETE');
      loadDocuments();
      loadStats();
    } catch (error) {
      alert('Erro ao deletar documento');
    }
  };
  
  const handleDownload = async (documentId, filename) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/admin/knowledge-base/${documentId}/download`
      );
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
    } catch (error) {
      alert('Erro ao fazer download');
    }
  };
  
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadDocuments();
      return;
    }
    
    try {
      const data = await makeApiCall(`/admin/knowledge-base/search?q=${searchQuery}`, 'GET');
      setDocuments(data);
    } catch (error) {
      console.error('Erro na busca:', error);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Knowledge Base Manager</h1>
          <p className="text-gray-600 mt-2">
            Base de conhecimento interna para orientação dos agentes
          </p>
        </div>
        
        {/* Estatísticas */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Documentos</p>
                    <p className="text-2xl font-bold">{stats.total_documents}</p>
                  </div>
                  <FileText className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Categorias</p>
                    <p className="text-2xl font-bold">{Object.keys(stats.by_category).length}</p>
                  </div>
                  <BarChart className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Tipos de Visto</p>
                    <p className="text-2xl font-bold">{Object.keys(stats.by_form_type).length}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Mais Acessado</p>
                    <p className="text-sm font-semibold truncate">
                      {stats.most_accessed[0]?.filename || 'N/A'}
                    </p>
                  </div>
                  <Download className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        {/* Upload Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Fazer Upload de Novo Documento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpload} className="space-y-6">
              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Arquivo PDF *
                </label>
                <Input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  required
                />
                {selectedFile && (
                  <p className="text-sm text-green-600 mt-2">✓ {selectedFile.name}</p>
                )}
              </div>
              
              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Categoria *
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  required
                >
                  <option value="">Selecione uma categoria</option>
                  {Object.entries(categories).map(([key, value]) => (
                    <option key={key} value={key}>{value}</option>
                  ))}
                </select>
              </div>
              
              {/* Subcategory */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subcategoria
                </label>
                <Input
                  type="text"
                  value={subcategory}
                  onChange={(e) => setSubcategory(e.target.value)}
                  placeholder="Ex: Checklist completa, Template formal, etc."
                />
              </div>
              
              {/* Form Types */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipos de Visto Aplicáveis *
                </label>
                <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                  {formTypes.map((formType) => (
                    <button
                      key={formType}
                      type="button"
                      onClick={() => handleFormTypeToggle(formType)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedFormTypes.includes(formType)
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {formType}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Selecione "ALL" se o documento se aplica a todos os tipos
                </p>
              </div>
              
              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descrição *
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Descreva o conteúdo e propósito deste documento..."
                  required
                />
              </div>
              
              {/* Status Message */}
              {uploadStatus && (
                <div className={`p-4 rounded-lg flex items-center gap-2 ${
                  uploadStatus.startsWith('success') 
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : uploadStatus.startsWith('error')
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-blue-50 text-blue-700 border border-blue-200'
                }`}>
                  {uploadStatus.startsWith('success') ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : uploadStatus.startsWith('error') ? (
                    <AlertCircle className="h-5 w-5" />
                  ) : (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-700"></div>
                  )}
                  <span>{uploadStatus.split(':')[1]}</span>
                </div>
              )}
              
              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Fazendo Upload...
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5 mr-2" />
                    Fazer Upload do Documento
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
        
        {/* Search */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex gap-2">
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar documentos..."
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch}>
                <Search className="h-5 w-5" />
              </Button>
            </div>
          </CardContent>
        </Card>
        
        {/* Documents List */}
        <Card>
          <CardHeader>
            <CardTitle>Documentos na Base de Conhecimento</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-gray-600 mt-4">Carregando documentos...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Nenhum documento encontrado</p>
                <p className="text-sm text-gray-500 mt-2">Faça o upload do primeiro documento acima</p>
              </div>
            ) : (
              <div className="space-y-4">
                {documents.map((doc) => (
                  <div
                    key={doc.document_id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <FileText className="h-5 w-5 text-purple-600" />
                          <h3 className="font-semibold text-gray-900">{doc.filename}</h3>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-2">{doc.description}</p>
                        
                        <div className="flex flex-wrap gap-2 mb-2">
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                            {categories[doc.category]}
                          </span>
                          {doc.form_types.map((ft) => (
                            <span key={ft} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
                              {ft}
                            </span>
                          ))}
                        </div>
                        
                        <div className="flex gap-4 text-xs text-gray-500">
                          <span>ID: {doc.document_id}</span>
                          <span>Acessos: {doc.access_count}</span>
                          <span>Páginas: {doc.metadata?.pages || 'N/A'}</span>
                          <span>Tamanho: {(doc.file_size / 1024).toFixed(1)} KB</span>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(doc.document_id, doc.filename)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(doc.document_id)}
                          className="text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminKnowledgeBase;
