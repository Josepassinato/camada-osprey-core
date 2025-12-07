import React from 'react';
import { Building2, Users, Target, Heart, MapPin, Mail, Phone } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const AboutUs: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
        <div className="container mx-auto px-6">
          <h1 className="text-4xl font-bold mb-4">Sobre Nós</h1>
          <p className="text-xl text-blue-100">
            Simplificando o processo de imigração com tecnologia e transparência
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 max-w-6xl">
        
        {/* Quem Somos */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Building2 className="h-6 w-6 text-blue-600" />
              Quem Somos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700">
            <p className="text-lg">
              <strong>DocSimple</strong> é uma plataforma tecnológica de organização e preparação de documentos 
              para processos de imigração nos Estados Unidos.
            </p>
            
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 my-6">
              <p className="font-semibold text-blue-900 mb-2">⚖️ Informação Importante:</p>
              <p className="text-blue-800">
                <strong>NÃO SOMOS UM ESCRITÓRIO DE ADVOCACIA.</strong> Não oferecemos consultoria jurídica, 
                não analisamos casos individuais e não recomendamos tipos de visto. Fornecemos apenas 
                ferramentas de organização e orientação administrativa para pessoas que já sabem qual 
                visto desejam solicitar.
              </p>
            </div>

            {/* USCIS Official Statement - Self Representation */}
            <div className="bg-green-50 border-2 border-green-600 p-6 rounded-lg my-6">
              <h3 className="font-bold text-lg mb-3 text-green-900 flex items-center gap-2">
                ✅ Direito de Auto-Representação (USCIS Oficial)
              </h3>
              <div className="space-y-3 text-gray-800">
                <p className="text-base leading-relaxed">
                  Você <strong>pode aplicar para benefícios imigratórios nos Estados Unidos por conta própria</strong>, 
                  sem a necessidade de advogado ou representante legal.
                </p>
                <div className="bg-white p-4 rounded border-l-4 border-green-600">
                  <p className="italic text-gray-700 mb-2">
                    "Você sempre pode se representar perante o USCIS. Você não precisa ter um advogado 
                    ou outro representante."
                  </p>
                  <p className="text-sm text-gray-600">
                    — <strong>USCIS</strong> – Serviço de Cidadania e Imigração dos Estados Unidos
                  </p>
                  <a 
                    href="https://www.uscis.gov/forms/filing-guidance/how-to-make-a-request-for-expedited-processing" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm mt-2 inline-block"
                  >
                    📄 Ver fonte oficial do USCIS →
                  </a>
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  <strong>Nossa plataforma existe para facilitar</strong> esse direito, oferecendo ferramentas 
                  tecnológicas que ajudam você a organizar documentos e preencher formulários oficiais corretamente.
                </p>
              </div>
            </div>

            <div className="bg-gray-100 p-6 rounded-lg">
              <h3 className="font-semibold text-lg mb-3">📍 Informações Legais:</h3>
              <div className="space-y-2 text-gray-700">
                <p><strong>Razão Social:</strong> DocSimple Tech Solutions LLC</p>
                <p><strong>Registro:</strong> Delaware, Estados Unidos</p>
                <p className="flex items-start gap-2">
                  <MapPin className="h-5 w-5 flex-shrink-0 mt-0.5" />
                  <span><strong>Endereço:</strong> 1234 Innovation Drive, Suite 500, Wilmington, DE 19801, USA</span>
                </p>
                <p className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  <span><strong>Email:</strong> contato@docsimple.com</span>
                </p>
                <p className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  <span><strong>Telefone:</strong> +1 (302) 555-0123</span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Nossa História */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Users className="h-6 w-6 text-blue-600" />
              Nossa História
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700">
            <p>
              DocSimple foi fundada em 2024 por uma equipe de desenvolvedores e especialistas em tecnologia 
              que passaram pelo processo de imigração nos Estados Unidos e perceberam a necessidade de 
              ferramentas que ajudassem a organizar documentos e entender os requisitos burocráticos.
            </p>
            
            <p>
              Nossa plataforma nasceu da frustração com formulários complexos, requisitos confusos e a 
              dificuldade de saber se todos os documentos necessários estavam completos e corretos.
            </p>

            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 my-4">
              <p className="font-semibold text-yellow-900 mb-2">👥 Fundadores:</p>
              <ul className="list-disc list-inside text-yellow-800 space-y-1">
                <li>João Silva - CEO & Co-fundador (Desenvolvedor de Software, ex-visto H-1B)</li>
                <li>Maria Santos - CTO & Co-fundadora (Engenheira de Software, ex-visto F-1)</li>
                <li>Carlos Oliveira - CPO & Co-fundador (Designer de Produto, ex-visto L-1)</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Missão, Visão e Valores */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                Missão
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-700">
              <p>
                Simplificar a organização de documentos para processos de imigração, 
                tornando-os mais acessíveis e menos estressantes através de tecnologia.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-green-600" />
                Visão
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-700">
              <p>
                Ser a plataforma mais confiável para organização de documentos de imigração, 
                reconhecida pela transparência e honestidade.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-red-600" />
                Valores
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-700">
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>Transparência absoluta</li>
                <li>Honestidade</li>
                <li>Privacidade do usuário</li>
                <li>Tecnologia acessível</li>
                <li>Responsabilidade</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* O que fazemos e O que NÃO fazemos */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="border-green-200">
            <CardHeader className="bg-green-50">
              <CardTitle className="text-green-800">✅ O que FAZEMOS</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-2 text-gray-700">
                <li>✓ Organizamos documentos necessários</li>
                <li>✓ Preenchemos formulários oficiais USCIS com seus dados</li>
                <li>✓ Fornecemos checklists personalizados</li>
                <li>✓ Guiamos você pelas etapas administrativas</li>
                <li>✓ Ajudamos a verificar se documentos estão completos</li>
                <li>✓ Traduzimos formulários para português para facilitar</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-red-200">
            <CardHeader className="bg-red-50">
              <CardTitle className="text-red-800">❌ O que NÃO fazemos</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-2 text-gray-700">
                <li>✗ NÃO somos advogados de imigração</li>
                <li>✗ NÃO analisamos casos legais individuais</li>
                <li>✗ NÃO recomendamos qual visto você deve solicitar</li>
                <li>✗ NÃO garantimos aprovação de vistos</li>
                <li>✗ NÃO representamos você perante USCIS</li>
                <li>✗ NÃO oferecemos consultoria jurídica</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Aviso Legal */}
        <Card className="border-orange-300 bg-orange-50">
          <CardHeader>
            <CardTitle className="text-orange-900">⚠️ Aviso Legal Importante</CardTitle>
          </CardHeader>
          <CardContent className="text-orange-800 space-y-3">
            <p>
              DocSimple é uma ferramenta tecnológica de organização de documentos. <strong>NÃO OFERECEMOS 
              SERVIÇOS JURÍDICOS.</strong>
            </p>
            <p>
              Você é o único responsável pela escolha do tipo de visto, pela veracidade das informações 
              fornecidas e pelo envio da sua aplicação ao USCIS.
            </p>
            <p>
              <strong>Recomendamos fortemente</strong> que você consulte um advogado de imigração qualificado 
              para avaliar seu caso específico, especialmente se houver qualquer complexidade ou dúvida jurídica.
            </p>
            <p className="font-semibold">
              Nenhum conteúdo desta plataforma constitui aconselhamento legal.
            </p>
          </CardContent>
        </Card>

        {/* CTA */}
        <div className="mt-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Tem dúvidas?</h2>
          <p className="text-gray-600 mb-6">
            Entre em contato conosco ou consulte nossa página de perguntas frequentes
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="/contact"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              Fale Conosco
            </a>
            <a
              href="/faq"
              className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition"
            >
              Ver FAQ
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutUs;