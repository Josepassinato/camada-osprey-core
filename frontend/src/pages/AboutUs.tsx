import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Target, Users, Award, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';

const AboutUs = () => {
  const navigate = useNavigate();

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
        <div style={{ background: 'white', borderRadius: '16px', padding: '60px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
          
          <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '20px', color: '#1f2937' }}>
            Sobre a Osprey
          </h1>
          
          <p style={{ fontSize: '20px', color: '#6b7280', marginBottom: '40px' }}>
            Transformando o processo de imigração com tecnologia e inteligência artificial
          </p>

          {/* Mission */}
          <div style={{ marginBottom: '50px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <div style={{ padding: '15px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px' }}>
                <Target style={{ color: 'white', width: '30px', height: '30px' }} />
              </div>
              <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>Nossa Missão</h2>
            </div>
            <p style={{ fontSize: '18px', lineHeight: '1.8', color: '#4b5563' }}>
              Democratizar o acesso ao sonho americano, tornando o processo de imigração mais acessível, 
              transparente e eficiente para todos. Acreditamos que a tecnologia pode eliminar barreiras e 
              simplificar processos complexos.
            </p>
          </div>

          {/* Vision */}
          <div style={{ marginBottom: '50px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <div style={{ padding: '15px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px' }}>
                <Award style={{ color: 'white', width: '30px', height: '30px' }} />
              </div>
              <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>Nossa Visão</h2>
            </div>
            <p style={{ fontSize: '18px', lineHeight: '1.8', color: '#4b5563' }}>
              Ser a plataforma líder global em soluções de imigração assistida por IA, reconhecida pela 
              excelência, inovação e compromisso com o sucesso de nossos clientes.
            </p>
          </div>

          {/* Values */}
          <div style={{ marginBottom: '50px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <div style={{ padding: '15px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px' }}>
                <Heart style={{ color: 'white', width: '30px', height: '30px' }} />
              </div>
              <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>Nossos Valores</h2>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              {[
                { title: 'Transparência', desc: 'Clareza total em cada etapa do processo' },
                { title: 'Excelência', desc: 'Comprometimento com qualidade superior' },
                { title: 'Inovação', desc: 'Uso de tecnologia de ponta para melhor experiência' },
                { title: 'Empatia', desc: 'Compreendemos a importância do seu sonho' }
              ].map((value, idx) => (
                <div key={idx} style={{ padding: '25px', background: '#f9fafb', borderRadius: '12px', border: '2px solid #e5e7eb' }}>
                  <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '10px', color: '#1f2937' }}>
                    {value.title}
                  </h3>
                  <p style={{ fontSize: '16px', color: '#6b7280' }}>{value.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Story */}
          <div style={{ marginBottom: '50px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <div style={{ padding: '15px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px' }}>
                <Users style={{ color: 'white', width: '30px', height: '30px' }} />
              </div>
              <h2 style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>Nossa História</h2>
            </div>
            <p style={{ fontSize: '18px', lineHeight: '1.8', color: '#4b5563', marginBottom: '20px' }}>
              A Osprey nasceu da experiência pessoal de nossos fundadores com o complexo processo de imigração. 
              Frustramos com a falta de transparência, os altos custos e a complexidade burocrática, decidimos 
              criar uma solução que combinasse tecnologia avançada, inteligência artificial e expertise em imigração.
            </p>
            <p style={{ fontSize: '18px', lineHeight: '1.8', color: '#4b5563' }}>
              Hoje, a Osprey é uma plataforma de auxílio tecnológico que empodera indivíduos a conduzir seus 
              próprios processos imigratórios com confiança, economia e eficiência. Nossa IA especializada 
              garante que cada documento seja preenchido corretamente, seguindo as diretrizes do USCIS.
            </p>
          </div>

          {/* Disclaimer */}
          <div style={{ padding: '30px', background: '#fef3c7', border: '2px solid #f59e0b', borderRadius: '12px' }}>
            <p style={{ fontSize: '16px', color: '#92400e', margin: 0 }}>
              <strong>Importante:</strong> A Osprey é uma plataforma de auxílio tecnológico para auto-aplicação 
              imigratória. Não somos um escritório de advocacia nem fornecemos consultoria jurídica. Nossa 
              tecnologia auxilia no preenchimento correto de formulários e organização de documentos, mas 
              recomendamos consultar um advogado de imigração para casos complexos.
            </p>
          </div>

          {/* Contact CTA */}
          <div style={{ marginTop: '50px', textAlign: 'center' }}>
            <p style={{ fontSize: '18px', color: '#6b7280', marginBottom: '20px' }}>
              Quer saber mais ou tem alguma dúvida?
            </p>
            <Button
              onClick={() => navigate('/contact')}
              style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '12px 40px', fontSize: '18px' }}
            >
              Entre em Contato
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutUs;