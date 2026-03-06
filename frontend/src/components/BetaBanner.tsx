import React, { useState } from 'react';

const BetaBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        fontSize: '14px'
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        maxWidth: '1200px',
        width: '100%',
        justifyContent: 'center',
        flexWrap: 'wrap'
      }}>
        {/* Badge BETA */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.25)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          padding: '4px 12px',
          borderRadius: '20px',
          fontWeight: 'bold',
          fontSize: '12px',
          letterSpacing: '1px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span style={{ fontSize: '16px' }}>🚀</span>
          BETA
        </div>

        {/* Mensagem */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '13px'
        }}>
          <span style={{ fontSize: '16px' }}>⚡</span>
          <span>
            <strong>Estamos em fase BETA!</strong> Seu feedback é muito importante para nós.
          </span>
        </div>

        {/* Link de Feedback (opcional) */}
        <a
          href="mailto:contact@goosprey.com"
          style={{
            color: 'white',
            textDecoration: 'none',
            background: 'rgba(255, 255, 255, 0.2)',
            padding: '6px 16px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            transition: 'all 0.3s',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          <span>💬</span>
          Enviar Feedback
        </a>

        {/* Botão de fechar */}
        <button
          onClick={() => setIsVisible(false)}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.4)',
            color: 'white',
            cursor: 'pointer',
            padding: '6px 10px',
            fontSize: '16px',
            fontWeight: 'bold',
            borderRadius: '4px',
            transition: 'all 0.3s',
            marginLeft: 'auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: '32px',
            minHeight: '32px'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
          title="Fechar banner"
          aria-label="Fechar banner"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default BetaBanner;
