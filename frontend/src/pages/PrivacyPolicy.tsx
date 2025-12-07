import React from 'react';
import { Shield, Lock, Eye, Database, UserCheck, AlertTriangle, FileText, Globe } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-800 text-white py-16">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="h-10 w-10" />
            <h1 className="text-4xl font-bold">Política de Privacidade</h1>
          </div>
          <p className="text-xl text-green-100">
            Como coletamos, usamos e protegemos seus dados pessoais
          </p>
          <p className="text-sm text-green-200 mt-2">
            Última atualização: Dezembro de 2024
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 max-w-5xl">
        
        {/* Introdução */}
        <Card className="mb-8 border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <p className="text-gray-800 leading-relaxed">
              A <strong>DocSimple Tech Solutions LLC</strong> ("nós", "nosso" ou "DocSimple") respeita 
              sua privacidade e está comprometida em proteger seus dados pessoais. Esta Política de 
              Privacidade descreve como coletamos, usamos, armazenamos e protegemos suas informações 
              quando você utiliza nossa plataforma.
            </p>
            <p className="mt-4 text-gray-800">
              Esta política está em conformidade com a <strong>Lei Geral de Proteção de Dados (LGPD)</strong> 
              do Brasil, o <strong>General Data Protection Regulation (GDPR)</strong> da União Europeia, 
              e leis de privacidade aplicáveis nos Estados Unidos.
            </p>
          </CardContent>
        </Card>

        {/* 1. Informações que Coletamos */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Database className="h-6 w-6 text-blue-600" />
              1. Informações que Coletamos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700">
            <div>
              <h3 className="font-semibold text-lg mb-2">1.1. Informações Fornecidas por Você:</h3>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>Dados de Cadastro:</strong> Nome completo, email, senha (criptografada)</li>
                <li><strong>Dados de Imigração:</strong> Informações pessoais necessárias para preencher formulários USCIS (nome, data de nascimento, passaporte, endereço, etc.)</li>
                <li><strong>Documentos:</strong> PDFs e imagens que você faz upload (passaportes, diplomas, cartas, etc.)</li>
                <li><strong>Comunicações:</strong> Mensagens enviadas através de formulários de contato ou suporte</li>
                <li><strong>Informações de Pagamento:</strong> Processadas por terceiros (Stripe) - não armazenamos dados de cartão</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-lg mb-2">1.2. Informações Coletadas Automaticamente:</h3>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>Dados de Uso:</strong> Páginas visitadas, tempo de sessão, cliques</li>
                <li><strong>Dados Técnicos:</strong> Endereço IP, tipo de navegador, sistema operacional, dispositivo</li>
                <li><strong>Cookies:</strong> Cookies essenciais para funcionamento da plataforma</li>
                <li><strong>Logs de Acesso:</strong> Registros de login, horários de acesso</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* 2. Como Usamos Suas Informações */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <FileText className="h-6 w-6 text-purple-600" />
              2. Como Usamos Suas Informações
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p>Usamos seus dados pessoais para os seguintes propósitos:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Fornecer Nossos Serviços:</strong> Preencher formulários, organizar documentos, gerar PDFs</li>
              <li><strong>Autenticação:</strong> Verificar sua identidade e gerenciar sua conta</li>
              <li><strong>Comunicação:</strong> Responder suas perguntas, enviar atualizações importantes sobre sua aplicação</li>
              <li><strong>Processamento de Pagamentos:</strong> Facilitar transações (através de Stripe)</li>
              <li><strong>Melhorar a Plataforma:</strong> Analisar uso para melhorar experiência do usuário</li>
              <li><strong>Segurança:</strong> Detectar e prevenir fraudes, abusos ou atividades suspeitas</li>
              <li><strong>Conformidade Legal:</strong> Cumprir obrigações legais e regulatórias</li>
            </ul>
            
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mt-4">
              <p className="font-semibold text-yellow-900 mb-2">⚠️ Importante:</p>
              <p className="text-yellow-800">
                <strong>NÃO usamos seus dados para:</strong> Vender para terceiros, marketing não solicitado, 
                análises legais de caso (não somos advogados), ou qualquer finalidade não descrita aqui.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 3. Como Armazenamos e Protegemos Seus Dados */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Lock className="h-6 w-6 text-green-600" />
              3. Como Armazenamos e Protegemos Seus Dados
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-gray-700">
            <div>
              <h3 className="font-semibold text-lg mb-2">3.1. Segurança:</h3>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>Criptografia:</strong> Conexões HTTPS/SSL para todas as transmissões de dados</li>
                <li><strong>Senhas:</strong> Armazenadas com hash bcrypt (nunca em texto plano)</li>
                <li><strong>Arquivos:</strong> Armazenados em servidores seguros com acesso restrito</li>
                <li><strong>Banco de Dados:</strong> MongoDB com autenticação e controle de acesso</li>
                <li><strong>Backups:</strong> Backups regulares criptografados</li>
                <li><strong>Monitoramento:</strong> Logs de acesso e detecção de atividades suspeitas</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-lg mb-2">3.2. Localização dos Dados:</h3>
              <p className="mb-2">
                Seus dados são armazenados em servidores seguros localizados nos Estados Unidos, 
                com infraestrutura em nuvem confiável (AWS/Google Cloud).
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-lg mb-2">3.3. Retenção de Dados:</h3>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>Dados de Conta:</strong> Mantidos enquanto sua conta estiver ativa</li>
                <li><strong>Dados de Aplicação:</strong> Mantidos por até 5 anos após conclusão (requisito legal)</li>
                <li><strong>Logs de Acesso:</strong> Mantidos por 12 meses</li>
                <li><strong>Após Exclusão:</strong> Dados são permanentemente removidos em até 30 dias</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* 4. Compartilhamento de Dados */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Globe className="h-6 w-6 text-orange-600" />
              4. Compartilhamento de Dados
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p className="font-semibold">NÃO vendemos, alugamos ou comercializamos seus dados pessoais.</p>
            
            <p>Podemos compartilhar seus dados apenas nas seguintes situações:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>
                <strong>Processadores de Pagamento:</strong> Stripe (para transações financeiras) - 
                eles têm sua própria política de privacidade
              </li>
              <li>
                <strong>Provedores de Infraestrutura:</strong> AWS/Google Cloud (hospedagem segura)
              </li>
              <li>
                <strong>Obrigações Legais:</strong> Se exigido por lei, ordem judicial ou autoridades governamentais
              </li>
              <li>
                <strong>Com Seu Consentimento:</strong> Em qualquer outro caso, apenas com sua permissão explícita
              </li>
            </ul>

            <p className="text-sm text-gray-600 italic mt-4">
              Nota: Todos os terceiros com quem compartilhamos dados são obrigados a manter o mesmo 
              nível de proteção de privacidade.
            </p>
          </CardContent>
        </Card>

        {/* 5. Seus Direitos */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <UserCheck className="h-6 w-6 text-blue-600" />
              5. Seus Direitos (LGPD/GDPR)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p>Você tem os seguintes direitos sobre seus dados pessoais:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Acesso:</strong> Solicitar uma cópia de todos os dados que temos sobre você</li>
              <li><strong>Correção:</strong> Corrigir dados imprecisos ou incompletos</li>
              <li><strong>Exclusão:</strong> Solicitar a exclusão de seus dados ("direito ao esquecimento")</li>
              <li><strong>Portabilidade:</strong> Receber seus dados em formato estruturado e legível</li>
              <li><strong>Restrição:</strong> Limitar o processamento de seus dados</li>
              <li><strong>Oposição:</strong> Se opor ao processamento de seus dados para determinados fins</li>
              <li><strong>Revogação:</strong> Revogar consentimento a qualquer momento</li>
            </ul>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mt-4">
              <p className="font-semibold text-blue-900 mb-2">Como Exercer Seus Direitos:</p>
              <p className="text-blue-800">
                Entre em contato conosco através de <strong>privacy@docsimple.com</strong> ou pelo 
                formulário de contato. Responderemos em até <strong>30 dias</strong>.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 6. Cookies */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Eye className="h-6 w-6 text-purple-600" />
              6. Cookies e Tecnologias Similares
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-700">
            <p>Usamos cookies para melhorar sua experiência na plataforma:</p>
            
            <div>
              <h3 className="font-semibold mb-2">Tipos de Cookies:</h3>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>Essenciais:</strong> Necessários para funcionamento básico (login, sessão)</li>
                <li><strong>Funcionais:</strong> Lembram suas preferências (idioma, configurações)</li>
                <li><strong>Analíticos:</strong> Ajudam a entender como você usa a plataforma (anônimos)</li>
              </ul>
            </div>

            <p className="mt-3">
              Você pode gerenciar cookies nas configurações do seu navegador. Note que desabilitar 
              cookies essenciais pode afetar o funcionamento da plataforma.
            </p>
          </CardContent>
        </Card>

        {/* 7. Menores de Idade */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              7. Menores de Idade
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700">
            <p>
              Nossa plataforma <strong>não é destinada a menores de 18 anos</strong>. Não coletamos 
              intencionalmente dados de menores. Se você é pai/mãe e acredita que seu filho forneceu 
              dados, entre em contato imediatamente para remoção.
            </p>
          </CardContent>
        </Card>

        {/* 8. Alterações */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <FileText className="h-6 w-6 text-gray-600" />
              8. Alterações nesta Política
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700">
            <p className="mb-3">
              Podemos atualizar esta Política de Privacidade periodicamente. Notificaremos você sobre 
              mudanças significativas através de:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Email para o endereço cadastrado</li>
              <li>Aviso na plataforma</li>
              <li>Atualização da data no topo desta página</li>
            </ul>
            <p className="mt-3">
              Recomendamos revisar esta política periodicamente.
            </p>
          </CardContent>
        </Card>

        {/* 9. Contato */}
        <Card className="mb-6 border-green-300 bg-green-50">
          <CardHeader>
            <CardTitle className="text-xl text-green-900">9. Contato - Privacidade e DPO</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-800 space-y-3">
            <p>
              Para questões sobre privacidade, exercer seus direitos ou entrar em contato com nosso 
              <strong> Encarregado de Proteção de Dados (DPO)</strong>:
            </p>
            
            <div className="bg-white p-4 rounded-lg">
              <p><strong>Email de Privacidade:</strong> privacy@docsimple.com</p>
              <p><strong>Email Geral:</strong> contato@docsimple.com</p>
              <p><strong>Telefone:</strong> +1 (302) 555-0123</p>
              <p><strong>Endereço:</strong></p>
              <p className="ml-4">
                DocSimple Tech Solutions LLC<br />
                Attn: Data Protection Officer<br />
                1234 Innovation Drive, Suite 500<br />
                Wilmington, DE 19801, USA
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Conformidade */}
        <Card className="border-blue-300 bg-blue-50">
          <CardContent className="pt-6">
            <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Conformidade Legal
            </h3>
            <p className="text-blue-800 text-sm">
              Esta Política de Privacidade está em conformidade com:
            </p>
            <ul className="list-disc list-inside text-blue-800 text-sm mt-2 ml-4 space-y-1">
              <li>Lei Geral de Proteção de Dados (LGPD) - Brasil (Lei nº 13.709/2018)</li>
              <li>General Data Protection Regulation (GDPR) - União Europeia</li>
              <li>California Consumer Privacy Act (CCPA) - Estados Unidos</li>
              <li>Outras leis de privacidade aplicáveis</li>
            </ul>
          </CardContent>
        </Card>

      </div>
    </div>
  );
};

export default PrivacyPolicy;
