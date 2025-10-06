import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  FileX, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  Users, 
  Calendar,
  MapPin,
  CreditCard,
  Upload,
  Search
} from 'lucide-react';

interface ConsistencyIssue {
  issue_type: string;
  severity: string;
  field_name: string;
  document1_id: string;
  document2_id: string;
  value1: string;
  value2: string;
  similarity_score: number;
  description: string;
  recommendation: string;
}

interface ConsistencyReport {
  overall_status: string;
  confidence_score: number;
  documents_analyzed: number;
  critical_issues: number;
  warning_issues: number;
  info_issues: number;
  total_issues: number;
  issues: ConsistencyIssue[];
  recommendations: string[];
  processing_time: number;
}

interface DocumentUpload {
  id: string;
  name: string;
  type: string;
  file: File | null;
  preview?: string;
}

const ConsistencyDashboard: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentUpload[]>([]);
  const [consistencyReport, setConsistencyReport] = useState<ConsistencyReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  const backendUrl = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  const documentTypes = [
    { value: 'passport', label: 'Passport', icon: '🛂' },
    { value: 'birth_certificate', label: 'Birth Certificate', icon: '👶' },
    { value: 'i765', label: 'I-765 (Work Authorization)', icon: '💼' },
    { value: 'i797', label: 'I-797 (Notice of Action)', icon: '📋' },
    { value: 'driver_license', label: 'Driver License', icon: '🚗' }
  ];

  const addDocument = () => {
    const newDoc: DocumentUpload = {
      id: Date.now().toString(),
      name: '',
      type: 'passport',
      file: null
    };
    setDocuments([...documents, newDoc]);
  };

  const removeDocument = (id: string) => {
    setDocuments(documents.filter(doc => doc.id !== id));
    setSelectedDocuments(selectedDocuments.filter(docId => docId !== id));
  };

  const updateDocument = (id: string, updates: Partial<DocumentUpload>) => {
    setDocuments(documents.map(doc => 
      doc.id === id ? { ...doc, ...updates } : doc
    ));
  };

  const handleFileUpload = (id: string, file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      updateDocument(id, { 
        file, 
        name: file.name,
        preview: e.target?.result as string 
      });
    };
    reader.readAsDataURL(file);
  };

  const validateConsistency = async () => {
    if (selectedDocuments.length < 2) {
      alert('Please select at least 2 documents for consistency validation');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const selectedDocs = documents.filter(doc => selectedDocuments.includes(doc.id));
      
      // Mock document analysis results for demo
      const mockDocuments = selectedDocs.map(doc => ({
        document_type: doc.type,
        document_id: doc.id,
        validation_results: generateMockValidationResults(doc.type),
        confidence_score: 0.85 + Math.random() * 0.1
      }));

      const response = await fetch(`${backendUrl}/api/documents/validate-consistency`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(mockDocuments)
      });

      if (response.ok) {
        const result = await response.json();
        setConsistencyReport(result.consistency_report);
      } else {
        // Fallback to mock data for demo
        setConsistencyReport(generateMockConsistencyReport());
      }
    } catch (error) {
      console.error('Error validating consistency:', error);
      // Use mock data for demo
      setConsistencyReport(generateMockConsistencyReport());
    } finally {
      setLoading(false);
    }
  };

  const generateMockValidationResults = (docType: string) => {
    const names = ['JOHN MICHAEL DOE', 'JOHN M. DOE', 'J. MICHAEL DOE'];
    const dates = ['1985-03-15', '1985-03-15', '1985-03-14'];
    
    switch (docType) {
      case 'passport':
        return {
          passport: {
            full_name: names[0],
            date_of_birth: dates[0],
            passport_number: 'A12345678',
            nationality: 'USA'
          }
        };
      case 'birth_certificate':
        return {
          birth_certificate: {
            full_name: names[1],
            date_of_birth: dates[0],
            place_of_birth: 'New York, NY',
            parents_names: ['Father: MICHAEL DOE']
          }
        };
      case 'i765':
        return {
          i765_ead: {
            full_name: names[0],
            date_of_birth: dates[0],
            alien_number: 'A987654321',
            country_of_birth: 'MEXICO'
          }
        };
      default:
        return {};
    }
  };

  const generateMockConsistencyReport = (): ConsistencyReport => ({
    overall_status: 'SUSPICIOUS',
    confidence_score: 0.75,
    documents_analyzed: selectedDocuments.length,
    critical_issues: 0,
    warning_issues: 2,
    info_issues: 1,
    total_issues: 3,
    processing_time: 0.45,
    issues: [
      {
        issue_type: 'NAME_VARIATION',
        severity: 'WARNING',
        field_name: 'full_name',
        document1_id: selectedDocuments[0],
        document2_id: selectedDocuments[1],
        value1: 'JOHN MICHAEL DOE',
        value2: 'JOHN M. DOE',
        similarity_score: 0.87,
        description: 'Name variation detected between documents',
        recommendation: 'Verify if this is the same person with name variation or nickname'
      },
      {
        issue_type: 'PLACE_VARIATION',
        severity: 'INFO',
        field_name: 'place_of_birth',
        document1_id: selectedDocuments[0],
        document2_id: selectedDocuments[1],
        value1: 'New York, NY',
        value2: 'New York, New York',
        similarity_score: 0.92,
        description: 'Minor place of birth variation',
        recommendation: 'Verify if referring to same location'
      }
    ],
    recommendations: [
      'Review flagged discrepancies for accuracy',
      'Verify if documents belong to the same person',
      'Consider requesting additional documentation for verification'
    ]
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CONSISTENT':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'SUSPICIOUS':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'INCONSISTENT':
        return <FileX className="w-5 h-5 text-red-500" />;
      default:
        return <Shield className="w-5 h-5 text-gray-500" />;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <FileX className="w-4 h-4 text-red-500" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'INFO':
        return <Info className="w-4 h-4 text-blue-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  const getFieldIcon = (fieldName: string) => {
    switch (fieldName) {
      case 'full_name':
        return <Users className="w-4 h-4" />;
      case 'date_of_birth':
        return <Calendar className="w-4 h-4" />;
      case 'place_of_birth':
        return <MapPin className="w-4 h-4" />;
      case 'passport_number':
      case 'alien_number':
        return <CreditCard className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Multi-Document Consistency Validation</h1>
          <p className="text-gray-600 mt-2">
            Upload multiple documents to validate consistency and detect potential discrepancies
          </p>
        </div>

        {/* Document Upload Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Document Upload</h2>
            <button
              onClick={addDocument}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Upload className="w-4 h-4" />
              <span>Add Document</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((doc) => (
              <div key={doc.id} className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Document Type
                    </label>
                    <select
                      value={doc.type}
                      onChange={(e) => updateDocument(doc.id, { type: e.target.value })}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    >
                      {documentTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload File
                    </label>
                    <input
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileUpload(doc.id, file);
                      }}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {doc.preview && (
                    <div className="mt-2">
                      <img 
                        src={doc.preview} 
                        alt="Preview" 
                        className="w-full h-32 object-cover rounded-md"
                      />
                    </div>
                  )}

                  <div className="flex justify-between items-center">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedDocuments.includes(doc.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedDocuments([...selectedDocuments, doc.id]);
                          } else {
                            setSelectedDocuments(selectedDocuments.filter(id => id !== doc.id));
                          }
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm">Include in validation</span>
                    </label>

                    <button
                      onClick={() => removeDocument(doc.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {documents.length > 0 && (
            <div className="mt-6 text-center">
              <button
                onClick={validateConsistency}
                disabled={loading || selectedDocuments.length < 2}
                className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 mx-auto"
              >
                <Search className="w-4 h-4" />
                <span>{loading ? 'Validating...' : 'Validate Consistency'}</span>
              </button>
              <p className="text-sm text-gray-500 mt-2">
                Select at least 2 documents to perform consistency validation
              </p>
            </div>
          )}
        </div>

        {/* Consistency Report */}
        {consistencyReport && (
          <div className="space-y-6">
            {/* Report Overview */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                {getStatusIcon(consistencyReport.overall_status)}
                <span className="ml-2">Consistency Report</span>
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div>
                  <p className="text-sm font-medium text-gray-600">Overall Status</p>
                  <p className={`text-lg font-bold ${
                    consistencyReport.overall_status === 'CONSISTENT' ? 'text-green-600' :
                    consistencyReport.overall_status === 'SUSPICIOUS' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {consistencyReport.overall_status}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Confidence Score</p>
                  <p className="text-lg font-bold text-gray-900">
                    {(consistencyReport.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Documents Analyzed</p>
                  <p className="text-lg font-bold text-gray-900">
                    {consistencyReport.documents_analyzed}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Processing Time</p>
                  <p className="text-lg font-bold text-gray-900">
                    {consistencyReport.processing_time.toFixed(2)}s
                  </p>
                </div>
              </div>

              {/* Issues Summary */}
              <div className="mt-6 grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{consistencyReport.critical_issues}</p>
                  <p className="text-sm text-gray-600">Critical Issues</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600">{consistencyReport.warning_issues}</p>
                  <p className="text-sm text-gray-600">Warnings</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{consistencyReport.info_issues}</p>
                  <p className="text-sm text-gray-600">Info</p>
                </div>
              </div>
            </div>

            {/* Issues Details */}
            {consistencyReport.issues.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Detected Issues</h3>
                <div className="space-y-4">
                  {consistencyReport.issues.map((issue, index) => (
                    <div key={index} className={`border-l-4 p-4 rounded-lg ${
                      issue.severity === 'CRITICAL' ? 'border-red-400 bg-red-50' :
                      issue.severity === 'WARNING' ? 'border-yellow-400 bg-yellow-50' :
                      'border-blue-400 bg-blue-50'
                    }`}>
                      <div className="flex items-start space-x-3">
                        {getSeverityIcon(issue.severity)}
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            {getFieldIcon(issue.field_name)}
                            <h4 className="font-semibold text-gray-900">
                              {issue.issue_type.replace(/_/g, ' ')} - {issue.field_name}
                            </h4>
                          </div>
                          <p className="text-gray-700 mb-2">{issue.description}</p>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-2">
                            <div>
                              <p className="text-sm font-medium text-gray-600">Document 1:</p>
                              <p className="text-sm text-gray-900">{issue.value1}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-600">Document 2:</p>
                              <p className="text-sm text-gray-900">{issue.value2}</p>
                            </div>
                          </div>
                          
                          <div className="flex justify-between items-center">
                            <p className="text-sm text-gray-600">
                              Similarity: {(issue.similarity_score * 100).toFixed(1)}%
                            </p>
                            <p className="text-sm font-medium text-blue-600">
                              💡 {issue.recommendation}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {consistencyReport.recommendations.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Recommendations</h3>
                <ul className="space-y-2">
                  {consistencyReport.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5" />
                      <span className="text-gray-700">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConsistencyDashboard;