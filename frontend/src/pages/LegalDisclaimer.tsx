import React from 'react';
import { AlertTriangle, Scale, XCircle, Info, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const LegalDisclaimer: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-red-800 text-white py-16">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="h-10 w-10" />
            <h1 className="text-4xl font-bold">Aviso Legal / Disclaimer</h1>
          </div>
          <p className="text-xl text-red-100">
            Limitações importantes sobre nossos serviços
          </p>
          <p className="text-sm text-red-200 mt-2">
            LEIA ATENTAMENTE ANTES DE USAR A PLATAFORMA
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 max-w-5xl">
        
        {/* Aviso Principal */}
        <Alert className="mb-8 border-red-400 bg-red-50">
          <AlertTriangle className="h-6 w-6 text-red-600" />
          <AlertDescription className="text-red-900">
            <p className="font-bold text-xl mb-3">⚠️ AVISO LEGAL IMPORTANTE</p>
            <p className="text-lg mb-2">
              <strong>DOCSIMPLE NÃO É UM ESCRITÓRIO DE ADVOCACIA E NÃO OFERECE SERVIÇOS JURÍDICOS.</strong>
            </p>
            <p className="text-base">
              Somos uma plataforma tecnológica que fornece ferramentas de organização de documentos. 
              Nenhum conteúdo, serviço ou informação fornecida por esta plataforma constitui 
              aconselhamento jurídico, consultoria de imigração, ou cria uma relação advogado-cliente.
            </p>
          </AlertDescription>
        </Alert>

        {/* 1. Não Somos Advogados */}
        <Card className="mb-6 border-red-200">
          <CardHeader className="bg-red-50">
            <CardTitle className="flex items-center gap-2 text-xl text-red-900">
              <Scale className="h-6 w-6" />
              1. NÃO Somos Advogados de Imigração
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700 pt-4">
            <div className="bg-white border-l-4 border-red-500 p-4">
              <h3 className="font-bold text-red-900 mb-3">O que isto significa:</h3>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>NÃO analisamos</strong> casos de imigração individuais sob uma perspectiva legal
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>NÃO recomendamos</strong> qual tipo de visto você deve solicitar
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>NÃO avaliamos</strong> suas chances de sucesso em obter um visto
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>NÃO interpretamos</strong> leis de imigração para seu caso específico
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>NÃO representamos</strong> você perante USCIS ou qualquer autoridade governamental
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>NÃO oferecemos</strong> estratégias legais ou táticas para seu caso
                  </span>
                </li>
              </ul>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
              <p className="font-semibold text-yellow-900 mb-2">⚠️ Você deve saber:</p>
              <p className="text-yellow-800">
                Apenas advogados licenciados podem oferecer aconselhamento jurídico. Se você precisa 
                de aconselhamento sobre qual visto solicitar, avaliação de elegibilidade, ou estratégia 
                legal, <strong>você DEVE consultar um advogado de imigração qualificado</strong>.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 2. O Que Realmente Fazemos */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Info className="h-6 w-6 text-blue-600" />
              2. O Que Realmente Fazemos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p className="font-semibold">
              DocSimple é uma ferramenta tecnológica que:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-2">
              <li>
                <strong>Organiza documentos:</strong> Ajudamos você a organizar e preparar documentos 
                necessários para aplicações de imigração
              </li>
              <li>
                <strong>Preenche formulários:</strong> Preenchemos formulários oficiais USCIS com os 
                dados que VOCÊ fornece
              </li>
              <li>
                <strong>Fornece checklists:</strong> Criamos listas de documentos baseadas no tipo 
                de visto que VOCÊ escolheu
              </li>
              <li>
                <strong>Facilita compreensão:</strong> Traduzimos formulários complexos para português 
                para facilitar o entendimento
              </li>
              <li>
                <strong>Gera PDFs:</strong> Criamos versões PDF dos formulários preenchidos para você revisar
              </li>
            </ul>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mt-4">
              <p className="font-semibold text-blue-900 mb-2">💡 Importante Entender:</p>
              <p className="text-blue-800">
                Somos como uma "calculadora" ou "processador de texto" - fornecemos a ferramenta, 
                mas <strong>VOCÊ é responsável</strong> por saber o que calcular ou o que escrever. 
                Não decidimos por você, apenas facilitamos o processo administrativo.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 3. Sem Garantias */}
        <Card className="mb-6 border-orange-200">
          <CardHeader className="bg-orange-50">
            <CardTitle className="flex items-center gap-2 text-xl text-orange-900">
              <XCircle className="h-6 w-6" />
              3. NÃO Oferecemos Garantias
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700 pt-4">
            <p className="font-bold text-orange-900 text-lg">
              NÃO GARANTIMOS APROVAÇÃO DE VISTOS
            </p>
            <ul className="space-y-2 ml-4">
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span>
                  A decisão de aprovar ou negar um visto é <strong>exclusivamente do USCIS</strong>
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span>
                  Não temos controle ou influência sobre decisões de imigração
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span>
                  Mesmo formulários perfeitamente preenchidos podem ser negados por razões legais
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span>
                  Cada caso é único e depende de circunstâncias individuais
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold">•</span>
                <span>
                  Sua elegibilidade para um visto é determinada por leis de imigração complexas
                </span>
              </li>
            </ul>

            <div className="bg-red-50 border border-red-300 p-4 rounded mt-4">
              <p className="text-red-900 font-semibold">
                ⚠️ ATENÇÃO: Qualquer pessoa ou serviço que GARANTE aprovação de visto está 
                sendo desonesta. Ninguém pode garantir aprovação - nem advogados, nem nós, nem ninguém.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 4. Responsabilidade do Usuário */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl">4. Você É Responsável</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p className="font-semibold text-lg">
              Ao usar nossa plataforma, você reconhece e aceita que:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-2">
              <li>
                <strong>Você escolhe</strong> qual tipo de visto solicitar (recomendamos consultar advogado)
              </li>
              <li>
                <strong>Você é responsável</strong> pela veracidade e precisão de todas as informações fornecidas
              </li>
              <li>
                <strong>Você deve revisar</strong> cuidadosamente todos os formulários antes de enviar ao USCIS
              </li>
              <li>
                <strong>Você entende</strong> que estamos fornecendo apenas uma ferramenta, não aconselhamento
              </li>
              <li>
                <strong>Você assume</strong> todas as consequências de suas decisões e ações
              </li>
              <li>
                <strong>Você reconhece</strong> que deve buscar aconselhamento jurídico para decisões legais
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* 5. Limitação de Responsabilidade */}
        <Card className="mb-6 border-red-300">
          <CardHeader className="bg-red-50">
            <CardTitle className="text-xl text-red-900">5. Limitação de Responsabilidade</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700 pt-4">
            <p className="font-bold text-red-900">
              DocSimple Tech Solutions LLC NÃO é responsável por:
            </p>
            <ul className="space-y-2 ml-4">
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Negação de vistos ou aplicações</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Atrasos no processamento pelo USCIS</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Erros causados por informações incorretas que você forneceu</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Mudanças nas leis ou políticas de imigração</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Decisões tomadas com base em nossas ferramentas</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Consequências legais de aplicações de imigração</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Perdas financeiras relacionadas a imigração</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600">✗</span>
                <span>Escolha inadequada de tipo de visto</span>
              </li>
            </ul>

            <p className="text-red-800 font-semibold mt-4 text-center p-4 bg-red-100 rounded">
              Nossa responsabilidade está limitada ao valor pago pelo uso da plataforma.
            </p>
          </CardContent>
        </Card>

        {/* 6. Recomendação de Consulta Jurídica */}
        <Card className="mb-6 border-green-300 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl text-green-900">
              <Scale className="h-6 w-6" />
              6. Recomendamos Fortemente: Consulte um Advogado
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-4">
            <p className="text-gray-800 text-lg font-semibold">
              Recomendamos que você consulte um advogado de imigração qualificado se:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-2 text-gray-700">
              <li>Você não tem certeza de qual tipo de visto solicitar</li>
              <li>Você tem histórico de negações anteriores</li>
              <li>Você tem questões criminais ou de inadmissibilidade</li>
              <li>Seu caso tem qualquer complexidade legal</li>
              <li>Você quer maximizar suas chances de aprovação</li>
              <li>Você tem dúvidas sobre elegibilidade</li>
              <li>Você precisa de estratégia legal para seu caso</li>
            </ul>

            <div className="bg-white border border-green-400 p-4 rounded mt-4">
              <p className="font-semibold text-green-900 mb-2">🔗 Encontre um Advogado:</p>
              <a 
                href="https://www.aila.org/find-a-lawyer"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium"
              >
                <ExternalLink className="h-4 w-4" />
                American Immigration Lawyers Association (AILA)
              </a>
              <p className="text-sm text-gray-600 mt-2">
                AILA é a associação nacional de advogados de imigração dos EUA
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 7. Informações Podem Estar Desatualizadas */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl">7. Informações Podem Estar Desatualizadas</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 space-y-3">
            <p>
              Leis e políticas de imigração <strong>mudam frequentemente</strong>. Embora nos esforcemos 
              para manter nossa plataforma atualizada:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Não podemos garantir que todas as informações estão 100% atualizadas</li>
              <li>Formulários do USCIS são atualizados periodicamente</li>
              <li>Requisitos podem mudar sem aviso prévio</li>
              <li>Você deve verificar informações oficiais no site do USCIS</li>
            </ul>
            <p className="font-semibold text-blue-700 mt-3">
              Sempre consulte o site oficial do USCIS (www.uscis.gov) para informações mais recentes.
            </p>
          </CardContent>
        </Card>

        {/* 8. Nenhuma Relação Advogado-Cliente */}
        <Card className="mb-6 border-purple-200">
          <CardHeader className="bg-purple-50">
            <CardTitle className="text-xl text-purple-900">
              8. Nenhuma Relação Advogado-Cliente é Criada
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 pt-4">
            <p className="mb-3">
              O uso de nossa plataforma <strong>NÃO cria</strong> uma relação advogado-cliente, 
              relação de consultoria, ou qualquer tipo de relacionamento profissional legal.
            </p>
            <p>
              Comunicações com nossa equipe de suporte são para questões técnicas sobre a plataforma 
              e <strong>não são protegidas por privilégio advogado-cliente</strong>.
            </p>
          </CardContent>
        </Card>

        {/* Aceitação */}
        <div className="mt-8 p-6 bg-gradient-to-r from-red-600 to-red-800 text-white rounded-lg">
          <h2 className="text-2xl font-bold mb-3 text-center">Aceitação deste Aviso Legal</h2>
          <p className="text-center text-lg mb-4">
            Ao usar a plataforma DocSimple, você reconhece que leu, compreendeu e aceita 
            completamente este Aviso Legal e todas as suas limitações.
          </p>
          <p className="text-center text-red-100">
            Se você não concorda ou não compreende este aviso, 
            <strong> NÃO use nossa plataforma</strong> e consulte um advogado.
          </p>
        </div>

        {/* Contato */}
        <Card className="mt-8 border-gray-300">
          <CardHeader>
            <CardTitle>Dúvidas sobre este Aviso Legal?</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-3">
              Se você tem dúvidas sobre este aviso ou sobre as limitações de nossos serviços:
            </p>
            <div className="bg-gray-100 p-4 rounded">
              <p><strong>Email:</strong> legal@docsimple.com</p>
              <p><strong>Telefone:</strong> +1 (302) 555-0123</p>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
};

export default LegalDisclaimer;
