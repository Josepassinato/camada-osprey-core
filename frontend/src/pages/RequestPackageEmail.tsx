import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const RequestPackageEmail: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
      
      const response = await axios.post(
        `${backendUrl}/api/auto-application/case/${caseId}/send-email`,
        {
          case_id: caseId,
          user_email: email
        }
      );

      if (response.data.success) {
        setSuccess(true);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao enviar email. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
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
          textAlign: 'center',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '24px' }}>✅</div>
          <h2 style={{ color: '#10b981', marginBottom: '16px', fontSize: '28px' }}>
            Email Enviado com Sucesso!
          </h2>
          <p style={{ color: '#6b7280', marginBottom: '32px', fontSize: '16px' }}>
            Seu pacote completo foi enviado para:
          </p>
          <p style={{ 
            color: '#1f2937', 
            fontWeight: 'bold', 
            fontSize: '18px',
            marginBottom: '32px',
            background: '#f3f4f6',
            padding: '12px',
            borderRadius: '8px'
          }}>
            {email}
          </p>
          <div style={{
            background: '#fef3c7',
            border: '1px solid #f59e0b',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '32px',
            textAlign: 'left'
          }}>
            <p style={{ margin: 0, color: '#92400e', fontSize: '14px' }}>
              <strong>📧 Verifique sua caixa de entrada</strong><br/>
              O email pode levar alguns minutos para chegar. Não esqueça de verificar a pasta de spam.
            </p>
          </div>
          <button
            onClick={() => navigate('/')}
            style={{
              background: '#667eea',
              color: 'white',
              border: 'none',
              padding: '12px 32px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = '#5568d3'}
            onMouseOut={(e) => e.currentTarget.style.background = '#667eea'}
          >
            Voltar ao Início
          </button>
        </div>
      </div>
    );
  }

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
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>📧</div>
          <h1 style={{ color: '#1f2937', marginBottom: '8px', fontSize: '28px' }}>
            Receber Pacote por Email
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
            <strong>📦 O que você vai receber:</strong><br/>
            • PDF completo com todos os documentos<br/>
            • Passaporte, cartas e comprovantes<br/>
            • Formulário USCIS preenchido<br/>
            • Instruções para submissão<br/>
            • Pronto para imprimir e enviar
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#374151',
              fontWeight: 'bold',
              fontSize: '14px'
            }}>
              Seu Email *
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="seu@email.com"
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                boxSizing: 'border-box',
                transition: 'border-color 0.3s'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = '#667eea'}
              onBlur={(e) => e.currentTarget.style.borderColor = '#e5e7eb'}
            />
            <p style={{ 
              margin: '8px 0 0 0', 
              fontSize: '12px', 
              color: '#6b7280' 
            }}>
              Digite o email onde deseja receber o pacote completo
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

          <button
            type="submit"
            disabled={loading || !email}
            style={{
              width: '100%',
              background: loading ? '#9ca3af' : '#10b981',
              color: 'white',
              border: 'none',
              padding: '16px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              marginBottom: '16px'
            }}
            onMouseOver={(e) => {
              if (!loading) e.currentTarget.style.background = '#059669';
            }}
            onMouseOut={(e) => {
              if (!loading) e.currentTarget.style.background = '#10b981';
            }}
          >
            {loading ? '📤 Enviando...' : '📧 Enviar Pacote por Email'}
          </button>

          <button
            type="button"
            onClick={() => navigate(-1)}
            style={{
              width: '100%',
              background: 'transparent',
              color: '#6b7280',
              border: '2px solid #e5e7eb',
              padding: '12px',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.borderColor = '#9ca3af';
              e.currentTarget.style.color = '#374151';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = '#e5e7eb';
              e.currentTarget.style.color = '#6b7280';
            }}
          >
            ← Voltar
          </button>
        </form>

        <div style={{
          marginTop: '32px',
          padding: '16px',
          background: '#f9fafb',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#6b7280'
        }}>
          <p style={{ margin: 0 }}>
            🔒 <strong>Privacidade:</strong> Seu email será usado apenas para enviar o pacote. Não compartilhamos com terceiros.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RequestPackageEmail;
