import React from 'react';
import { FileText, AlertTriangle, Scale, UserX, CreditCard, Ban, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const TermsOfUse: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-3 mb-4">
            <FileText className="h-10 w-10" />
            <h1 className="text-4xl font-bold">Termos de Uso</h1>
          </div>
          <p className="text-xl text-blue-100">
            Condições para uso da plataforma DocSimple
          </p>
          <p className="text-sm text-blue-200 mt-2">
            Última atualização: Dezembro de 2024
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 max-w-5xl">
        
        {/* Aviso Importante */}
        <Alert className="mb-8 border-red-300 bg-red-50">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <AlertDescription className="text-red-900">
            <p className="font-semibold mb-2">⚠️ LEIA ATENTAMENTE ANTES DE USAR:</p>
            <p>
              Ao usar a plataforma DocSimple, você concorda com estes Termos de Uso. 
              <strong> NÃO SOMOS ADVOGADOS</strong> e <strong>NÃO OFERECEMOS CONSULTORIA JURÍDICA</strong>. 
              Somos apenas uma ferramenta tecnológica de organização de documentos. Você é 
              responsável por todas as decisões relacionadas à sua aplicação de imigração.
            </p>
          </AlertDescription>
        </Alert>

        {/* 1. Aceitação dos Termos */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <FileText className="h-6 w-6 text-blue-600" />
              1. Aceitação dos Termos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p>
              Estes Termos de Uso ("Termos") constituem um acordo legal entre você ("Usuário", "você") 
              e a <strong>DocSimple Tech Solutions LLC</strong> ("DocSimple", "nós", "nosso").
            </p>
            <p>
              Ao criar uma conta, acessar ou usar nossa plataforma, você confirma que:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Leu e compreendeu estes Termos</li>
              <li>Tem pelo menos 18 anos de idade</li>
              <li>Tem capacidade legal para aceitar este acordo</li>
              <li>Concorda em cumprir todos os termos e condições aqui descritos</li>
            </ul>
            <p className="font-semibold text-red-700 mt-4">
              Se você NÃO concorda com estes Termos, NÃO use nossa plataforma.
            </p>
          </CardContent>
        </Card>

        {/* 2. Descrição do Serviço */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Shield className="h-6 w-6 text-green-600" />
              2. Descrição do Serviço
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700">
            <div>
              <h3 className="font-semibold text-lg mb-2">2.1. O que Oferecemos:</h3>
              <p>DocSimple é uma plataforma tecnológica que oferece:</p>
              <ul className="list-disc list-inside ml-4 space-y-1 mt-2">
                <li>Ferramentas para organização de documentos de imigração</li>
                <li>Preenchimento automatizado de formulários oficiais USCIS com seus dados</li>
                <li>Checklists personalizados de documentos necessários</li>
                <li>Orientação sobre etapas administrativas do processo</li>
                <li>Interface amigável em português para facilitar compreensão</li>
                <li>Geração de PDFs dos formulários preenchidos</li>
              </ul>
            </div>

            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <h3 className="font-semibold text-red-900 mb-2">2.2. O que NÃO Oferecemos:</h3>
              <ul className="list-disc list-inside ml-4 space-y-1 text-red-800">
                <li><strong>NÃO</strong> oferecemos serviços jurídicos ou consultoria de imigração</li>
                <li><strong>NÃO</strong> analisamos casos individuais</li>
                <li><strong>NÃO</strong> recomendamos qual tipo de visto você deve solicitar</li>
                <li><strong>NÃO</strong> revisamos documentos sob perspectiva legal</li>
                <li><strong>NÃO</strong> representamos você perante USCIS ou qualquer autoridade</li>
                <li><strong>NÃO</strong> garantimos aprovação de vistos</li>
                <li><strong>NÃO</strong> somos responsáveis por decisões tomadas com base em nossa plataforma</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* 3. Responsabilidades do Usuário */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Scale className="h-6 w-6 text-purple-600" />
              3. Responsabilidades do Usuário
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p className="font-semibold">Você, como usuário, é responsável por:</p>
            <ul className="list-disc list-inside ml-4 space-y-2">
              <li>
                <strong>Escolha do Visto:</strong> Determinar qual tipo de visto é apropriado para sua 
                situação (recomendamos consultar um advogado)
              </li>
              <li>
                <strong>Veracidade das Informações:</strong> Garantir que todos os dados fornecidos sejam 
                verdadeiros, precisos e completos
              </li>
              <li>
                <strong>Revisão de Documentos:</strong> Revisar cuidadosamente todos os formulários e 
                documentos gerados antes de submeter ao USCIS
              </li>
              <li>
                <strong>Conformidade Legal:</strong> Cumprir todas as leis de imigração aplicáveis
              </li>
              <li>
                <strong>Consultoria Profissional:</strong> Buscar aconselhamento jurídico qualificado 
                quando necessário
              </li>
              <li>
                <strong>Submissão ao USCIS:</strong> Você é responsável por enviar sua aplicação - 
                nós não fazemos isso por você
              </li>
              <li>
                <strong>Consequências:</strong> Assumir todas as consequências de suas decisões e ações
              </li>
            </ul>
            
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mt-4">
              <p className="font-semibold text-yellow-900 mb-2">⚠️ Aviso Importante:</p>
              <p className="text-yellow-800">
                Informações falsas em aplicações de imigração podem resultar em negação do visto, 
                banimento de entrada nos EUA, e outras consequências legais graves. Seja honesto e preciso.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 4. Conta de Usuário */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <UserX className="h-6 w-6 text-orange-600" />
              4. Conta de Usuário
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <div>
              <h3 className="font-semibold mb-2">4.1. Criação de Conta:</h3>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Você deve fornecer informações verdadeiras e atualizadas</li>
                <li>Você é responsável por manter a segurança de sua senha</li>
                <li>Você não pode compartilhar sua conta com terceiros</li>
                <li>Você deve notificar imediatamente sobre qualquer uso não autorizado</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">4.2. Suspensão/Encerramento:</h3>
              <p className="mb-2">Reservamos o direito de suspender ou encerrar sua conta se:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Você violar estes Termos de Uso</li>
                <li>Detectarmos atividade fraudulenta ou suspeita</li>
                <li>Você usar a plataforma para fins ilegais</li>
                <li>Você fornecer informações falsas intencionalmente</li>
                <li>Houver inadimplência de pagamento</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">4.3. Cancelamento pelo Usuário:</h3>
              <p>
                Você pode cancelar sua conta a qualquer momento através das configurações ou 
                entrando em contato conosco. Veja nossa política de reembolso na seção 6.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 5. Uso Aceitável */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Ban className="h-6 w-6 text-red-600" />
              5. Uso Aceitável
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p className="font-semibold">Você concorda em NÃO:</p>
            <ul className="list-disc list-inside ml-4 space-y-2">
              <li>Usar a plataforma para atividades ilegais ou fraudulentas</li>
              <li>Fornecer informações falsas intencionalmente</li>
              <li>Violar direitos de propriedade intelectual</li>
              <li>Tentar acessar áreas restritas da plataforma</li>
              <li>Fazer engenharia reversa ou copiar nosso código</li>
              <li>Usar bots, scrapers ou ferramentas automatizadas não autorizadas</li>
              <li>Interferir com o funcionamento da plataforma</li>
              <li>Usar a plataforma para spam ou marketing não autorizado</li>
              <li>Compartilhar sua conta com terceiros</li>
              <li>Revender ou redistribuir nossos serviços</li>
            </ul>
          </CardContent>
        </Card>

        {/* 6. Pagamentos e Reembolsos */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <CreditCard className="h-6 w-6 text-green-600" />
              6. Pagamentos e Reembolsos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700">
            <div>
              <h3 className="font-semibold mb-2">6.1. Pagamentos:</h3>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Pagamentos são processados através de Stripe (terceiro seguro)</li>
                <li>Você concorda em pagar todas as taxas aplicáveis</li>
                <li>Preços podem mudar com aviso prévio de 30 dias</li>
                <li>Não armazenamos dados de cartão de crédito</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">6.2. Política de Reembolso:</h3>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>
                  <strong>Garantia de 7 dias:</strong> Reembolso total se cancelar nos primeiros 7 dias 
                  sem ter gerado PDFs finais
                </li>
                <li>
                  <strong>Após uso:</strong> Não oferecemos reembolso se você já gerou e baixou formulários
                </li>
                <li>
                  <strong>Negação de visto:</strong> Não somos responsáveis - reembolso não disponível
                </li>
                <li>
                  <strong>Erros técnicos:</strong> Se houver falha técnica nossa, reembolso proporcional
                </li>
              </ul>
              <p className="text-sm text-gray-600 mt-2 italic">
                Para solicitar reembolso, entre em contato em até 30 dias: contato@docsimple.com
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">6.3. Taxas do USCIS:</h3>
              <p className="text-red-700 font-medium">
                ⚠️ Nossos preços NÃO incluem as taxas oficiais do USCIS. Você deve pagar essas 
                taxas separadamente ao governo dos EUA ao submeter sua aplicação.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 7. Limitação de Responsabilidade */}
        <Card className="mb-6 border-orange-300">
          <CardHeader className="bg-orange-50">
            <CardTitle className="flex items-center gap-2 text-xl text-orange-900">
              <AlertTriangle className="h-6 w-6" />
              7. Limitação de Responsabilidade
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700 pt-4">
            <p className="font-semibold text-orange-900">
              IMPORTANTE - LEIA COM ATENÇÃO:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-2">
              <li>
                <strong>Sem Garantias:</strong> A plataforma é fornecida "como está" sem garantias 
                de qualquer tipo
              </li>
              <li>
                <strong>Não Garantimos Aprovação:</strong> Não podemos garantir que seu visto será aprovado
              </li>
              <li>
                <strong>Não Somos Responsáveis por:</strong> Negação de visto, atrasos no USCIS, 
                erros nas suas informações, decisões que você tomar
              </li>
              <li>
                <strong>Responsabilidade Limitada:</strong> Nossa responsabilidade está limitada ao 
                valor pago pelo serviço
              </li>
              <li>
                <strong>Erros e Omissões:</strong> Não somos responsáveis por erros causados por 
                informações incorretas que você forneceu
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* 8. Propriedade Intelectual */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl">8. Propriedade Intelectual</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 space-y-2">
            <p>
              Todo conteúdo da plataforma (código, design, textos, logos, marcas) é propriedade 
              da DocSimple Tech Solutions LLC e protegido por leis de propriedade intelectual.
            </p>
            <p className="font-semibold">
              Você NÃO pode copiar, modificar, distribuir ou criar trabalhos derivados sem 
              nossa permissão por escrito.
            </p>
          </CardContent>
        </Card>

        {/* 9. Modificações */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl">9. Modificações dos Termos</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 space-y-2">
            <p>
              Reservamos o direito de modificar estes Termos a qualquer momento. Notificaremos 
              você por email sobre mudanças significativas.
            </p>
            <p>
              O uso continuado da plataforma após modificações constitui aceitação dos novos termos.
            </p>
          </CardContent>
        </Card>

        {/* 10. Lei Aplicável */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl">10. Lei Aplicável e Jurisdição</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 space-y-2">
            <p>
              Estes Termos são regidos pelas leis do Estado de Delaware, Estados Unidos, sem 
              considerar conflitos de disposições legais.
            </p>
            <p>
              Qualquer disputa será resolvida nos tribunais do Estado de Delaware.
            </p>
          </CardContent>
        </Card>

        {/* 11. Contato */}
        <Card className="border-blue-300 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-xl text-blue-900">11. Contato</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-800">
            <p className="mb-3">
              Para questões sobre estes Termos de Uso:
            </p>
            <div className="bg-white p-4 rounded-lg">
              <p><strong>Email:</strong> legal@docsimple.com</p>
              <p><strong>Email Geral:</strong> contato@docsimple.com</p>
              <p><strong>Telefone:</strong> +1 (302) 555-0123</p>
              <p><strong>Endereço:</strong></p>
              <p className="ml-4">
                DocSimple Tech Solutions LLC<br />
                Attn: Legal Department<br />
                1234 Innovation Drive, Suite 500<br />
                Wilmington, DE 19801, USA
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Aceitação Final */}
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg">
          <p className="text-center text-lg font-semibold mb-2">
            Ao usar nossa plataforma, você confirma que leu, compreendeu e concorda 
            com estes Termos de Uso.
          </p>
          <p className="text-center text-blue-100">
            Se você não concorda, por favor, não use nossos serviços.
          </p>
        </div>

      </div>
    </div>
  );
};

export default TermsOfUse;
