import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Download, ArrowLeft, FileText, Lock } from 'lucide-react';

const RequestPackageEmail: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDownload = async () => {
    setLoading(true);
    setError('');

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
      
      // Criar um link temporário para fazer o download
      const downloadUrl = `${backendUrl}/api/auto-application/case/${caseId}/download-package`;
      
      // Abrir em nova aba ou fazer download direto
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `Pacote_Completo_${caseId}.pdf`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Aguardar um pouco para dar feedback visual
      setTimeout(() => {
        setLoading(false);
      }, 1000);
      
    } catch (err: any) {
      setError('Erro ao baixar o pacote. Tente novamente.');
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '48px',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>📄</div>
          <h1 style={{ color: '#1f2937', marginBottom: '8px', fontSize: '28px' }}>
            Baixar Pacote Completo
          </h1>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>
            Case ID: {caseId}
          </p>
        </div>

        <div style={{
          background: '#e0f2fe',
          border: '1px solid #0ea5e9',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '32px'
        }}>
          <p style={{ margin: 0, color: '#075985', fontSize: '14px' }}>
            <strong>📦 O que você vai baixar:</strong><br/>
            • PDF completo com todos os documentos<br/>
            • Passaporte, cartas e comprovantes<br/>
            • Formulário USCIS preenchido<br/>
            • Instruções para submissão<br/>
            • Pronto para imprimir e enviar
          </p>
        </div>

        <div style={{
          background: '#fef3c7',
          border: '1px solid #f59e0b',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '32px',
          textAlign: 'left'
        }}>
          <p style={{ margin: 0, color: '#92400e', fontSize: '14px' }}>
            <strong>⚠️ Importante:</strong><br/>
            • Salve o arquivo em local seguro<br/>
            • Faça backup do documento<br/>
            • Imprima em alta qualidade<br/>
            • Revise antes de enviar ao USCIS
          </p>
        </div>

        {error && (
          <div style={{
            background: '#fee2e2',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '24px'
          }}>
            <p style={{ margin: 0, color: '#991b1b', fontSize: '14px' }}>
              ❌ {error}
            </p>
          </div>
        )}

        <Button
          onClick={handleDownload}
          disabled={loading}
          className="w-full h-14 text-lg font-semibold mb-4"
          size="lg"
          style={{
            background: loading ? '#9ca3af' : '#10b981',
            color: 'white'
          }}
        >
          {loading ? (
            <>
              <Download className="mr-2 h-5 w-5 animate-spin" />
              Preparando Download...
            </>
          ) : (
            <>
              <Download className="mr-2 h-5 w-5" />
              Baixar Pacote Completo (PDF)
            </>
          )}
        </Button>

        <Button
          type="button"
          onClick={() => navigate(-1)}
          variant="outline"
          className="w-full h-12"
          size="lg"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>

        <div style={{
          marginTop: '32px',
          padding: '16px',
          background: '#f9fafb',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#6b7280',
          textAlign: 'center'
        }}>
          <p style={{ margin: 0 }}>
            🔒 <strong>Segurança:</strong> Seu documento é gerado de forma segura e permanece privado.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RequestPackageEmail;
