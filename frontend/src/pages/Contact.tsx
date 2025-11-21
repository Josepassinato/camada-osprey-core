import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, MessageSquare, Phone, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Contact = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Aqui você pode integrar com um serviço de email
    console.log('Form submitted:', formData);
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Header */}
      <div style={{ padding: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <Button
          onClick={() => navigate('/')}
          variant="ghost"
          style={{ color: 'white' }}
        >
          <ArrowLeft className="mr-2" />
          Voltar
        </Button>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '60px 20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
          
          {/* Contact Info */}
          <div style={{ background: 'white', borderRadius: '16px', padding: '50px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
            <h1 style={{ fontSize: '42px', fontWeight: 'bold', marginBottom: '20px', color: '#1f2937' }}>
              Entre em Contato
            </h1>
            
            <p style={{ fontSize: '18px', color: '#6b7280', marginBottom: '40px' }}>
              Estamos aqui para ajudar! Entre em contato conosco por qualquer um dos canais abaixo.
            </p>

            {/* Contact Methods */}
            <div style={{ marginBottom: '30px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '20px', background: '#f9fafb', borderRadius: '12px', marginBottom: '15px' }}>
                <Mail style={{ color: '#667eea', width: '24px', height: '24px' }} />
                <div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>Email</div>
                  <a href="mailto:contact@goosprey.com" style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937', textDecoration: 'none' }}>
                    contact@goosprey.com
                  </a>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '20px', background: '#f9fafb', borderRadius: '12px', marginBottom: '15px' }}>
                <MessageSquare style={{ color: '#667eea', width: '24px', height: '24px' }} />
                <div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>Chat ao Vivo</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937' }}>
                    Disponível 24/7
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '20px', background: '#f9fafb', borderRadius: '12px' }}>
                <Phone style={{ color: '#667eea', width: '24px', height: '24px' }} />
                <div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>Horário de Atendimento</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937' }}>
                    Segunda a Sexta: 9h - 18h EST
                  </div>
                </div>
              </div>
            </div>

            {/* FAQ Link */}
            <div style={{ padding: '25px', background: '#eff6ff', border: '2px solid #3b82f6', borderRadius: '12px' }}>
              <p style={{ fontSize: '16px', color: '#1e40af', margin: 0 }}>
                💡 <strong>Dica:</strong> Confira nossa Central de Ajuda para respostas rápidas às perguntas mais frequentes!
              </p>
            </div>
          </div>

          {/* Contact Form */}
          <div style={{ background: 'white', borderRadius: '16px', padding: '50px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
            <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '30px', color: '#1f2937' }}>
              Envie uma Mensagem
            </h2>

            {submitted ? (
              <div style={{ padding: '40px', textAlign: 'center', background: '#d1fae5', borderRadius: '12px' }}>
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>✅</div>
                <h3 style={{ fontSize: '24px', fontWeight: 'bold', color: '#065f46', marginBottom: '10px' }}>
                  Mensagem Enviada!
                </h3>
                <p style={{ fontSize: '16px', color: '#047857' }}>
                  Entraremos em contato em breve.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '25px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold', color: '#374151' }}>
                    Nome Completo *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '16px' }}
                    placeholder="Seu nome"
                  />
                </div>

                <div style={{ marginBottom: '25px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold', color: '#374151' }}>
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '16px' }}
                    placeholder="seu@email.com"
                  />
                </div>

                <div style={{ marginBottom: '25px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold', color: '#374151' }}>
                    Assunto *
                  </label>
                  <select
                    required
                    value={formData.subject}
                    onChange={(e) => setFormData({...formData, subject: e.target.value})}
                    style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '16px' }}
                  >
                    <option value="">Selecione um assunto</option>
                    <option value="suporte">Suporte Técnico</option>
                    <option value="duvida">Dúvida sobre Visto</option>
                    <option value="bug">Reportar Bug</option>
                    <option value="feedback">Feedback/Sugestão</option>
                    <option value="outro">Outro</option>
                  </select>
                </div>

                <div style={{ marginBottom: '25px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold', color: '#374151' }}>
                    Mensagem *
                  </label>
                  <textarea
                    required
                    value={formData.message}
                    onChange={(e) => setFormData({...formData, message: e.target.value})}
                    rows={6}
                    style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '16px', resize: 'vertical' }}
                    placeholder="Descreva sua dúvida ou questão..."
                  />
                </div>

                <Button
                  type="submit"
                  style={{ width: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '16px', fontSize: '18px', fontWeight: 'bold' }}
                >
                  <Send className="mr-2" />
                  Enviar Mensagem
                </Button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;