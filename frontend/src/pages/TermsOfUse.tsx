import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';

const TermsOfUse = () => {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Button
            onClick={() => navigate('/')}
            variant="ghost"
            style={{ color: 'white' }}
          >
            <ArrowLeft className="mr-2" />
            Voltar
          </Button>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '60px 20px' }}>
        <div style={{ background: 'white', borderRadius: '16px', padding: '60px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '30px' }}>
            <FileText style={{ width: '40px', height: '40px', color: '#667eea' }} />
            <h1 style={{ fontSize: '42px', fontWeight: 'bold', color: '#1f2937', margin: 0 }}>
              Termos de Uso
            </h1>
          </div>

          <p style={{ fontSize: '16px', color: '#6b7280', marginBottom: '40px' }}>
            Última atualização: Novembro de 2024
          </p>

          {/* Sections */}
          <div style={{ lineHeight: '1.8' }}>
            
            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                1. Aceitação dos Termos
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Ao acessar e usar a plataforma Osprey, você concorda em cumprir e estar vinculado a estes Termos de Uso. 
                Se você não concorda com qualquer parte destes termos, não deve usar nossa plataforma.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                2. Descrição do Serviço
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                A Osprey é uma <strong>plataforma de auxílio tecnológico</strong> que fornece ferramentas e recursos para 
                ajudar usuários a preparar e organizar documentos de imigração. Nossa plataforma utiliza inteligência 
                artificial para auxiliar no preenchimento de formulários do USCIS.
              </p>
              <div style={{ padding: '20px', background: '#fef3c7', border: '2px solid #f59e0b', borderRadius: '8px', marginTop: '15px' }}>
                <p style={{ fontSize: '16px', color: '#92400e', margin: 0 }}>
                  <strong>⚠️ IMPORTANTE:</strong> A Osprey NÃO é um escritório de advocacia, não fornece consultoria jurídica 
                  e não representa clientes perante o USCIS ou qualquer órgão governamental.
                </p>
              </div>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                3. Elegibilidade
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Para usar nossa plataforma, você deve:
              </p>
              <ul style={{ fontSize: '16px', color: '#4b5563', marginLeft: '30px' }}>
                <li>Ter pelo menos 18 anos de idade</li>
                <li>Ter capacidade legal para celebrar contratos vinculativos</li>
                <li>Fornecer informações verdadeiras, precisas e completas</li>
                <li>Manter a confidencialidade de suas credenciais de acesso</li>
              </ul>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                4. Uso Aceitável
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Você concorda em usar a plataforma apenas para fins legais e de acordo com estes termos. É proibido:
              </p>
              <ul style={{ fontSize: '16px', color: '#4b5563', marginLeft: '30px' }}>
                <li>Fornecer informações falsas ou enganosas</li>
                <li>Violar quaisquer leis ou regulamentos aplicáveis</li>
                <li>Tentar acessar áreas restritas da plataforma</li>
                <li>Usar a plataforma para fins fraudulentos ou ilegais</li>
                <li>Copiar, modificar ou distribuir o conteúdo da plataforma sem autorização</li>
              </ul>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                5. Propriedade Intelectual
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Todo o conteúdo, design, gráficos, código-fonte e funcionalidades da plataforma Osprey são propriedade 
                exclusiva da Osprey ou de seus licenciadores e são protegidos por leis de propriedade intelectual.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                6. Privacidade e Proteção de Dados
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Sua privacidade é importante para nós. Nossa coleta, uso e proteção de dados pessoais são regidos por 
                nossa Política de Privacidade, que faz parte integrante destes Termos de Uso.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                7. Limitação de Responsabilidade
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                A Osprey fornece a plataforma "como está" e "conforme disponível". Não garantimos que:
              </p>
              <ul style={{ fontSize: '16px', color: '#4b5563', marginLeft: '30px' }}>
                <li>Seu pedido de imigração será aprovado</li>
                <li>A plataforma estará livre de erros ou interrupções</li>
                <li>Os resultados obtidos serão precisos ou confiáveis</li>
              </ul>
              <p style={{ fontSize: '16px', color: '#4b5563', marginTop: '15px' }}>
                Você é o único responsável pela revisão e submissão de todos os documentos ao USCIS.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                8. Pagamentos e Reembolsos
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Todos os pagamentos são processados de forma segura através de nosso provedor de pagamentos terceirizado (Stripe). 
                Nossa política de reembolso está disponível mediante solicitação.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                9. Modificações dos Termos
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Reservamo-nos o direito de modificar estes termos a qualquer momento. Alterações significativas serão 
                comunicadas aos usuários por email ou através da plataforma.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                10. Lei Aplicável
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Estes termos são regidos pelas leis dos Estados Unidos da América. Quaisquer disputas serão resolvidas 
                nos tribunais competentes.
              </p>
            </section>

            <section style={{ marginBottom: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1f2937', marginBottom: '15px' }}>
                11. Contato
              </h2>
              <p style={{ fontSize: '16px', color: '#4b5563', marginBottom: '15px' }}>
                Para questões sobre estes Termos de Uso, entre em contato:
              </p>
              <div style={{ padding: '20px', background: '#f9fafb', borderRadius: '8px', border: '2px solid #e5e7eb' }}>
                <p style={{ fontSize: '16px', color: '#1f2937', margin: 0 }}>
                  📧 Email: <a href="mailto:contact@goosprey.com" style={{ color: '#667eea', textDecoration: 'none', fontWeight: 'bold' }}>contact@goosprey.com</a>
                </p>
              </div>
            </section>
          </div>

          {/* Acceptance */}
          <div style={{ marginTop: '50px', padding: '30px', background: '#eff6ff', border: '2px solid #3b82f6', borderRadius: '12px', textAlign: 'center' }}>
            <p style={{ fontSize: '16px', color: '#1e40af', margin: 0 }}>
              Ao continuar usando a plataforma Osprey, você reconhece que leu, entendeu e concorda com estes Termos de Uso.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsOfUse;