import React, { useState } from 'react';
import { Mail, Phone, MapPin, Clock, Send, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {
      setSubmitted(true);
      setSubmitting(false);
      setFormData({ name: '', email: '', subject: '', message: '' });
    }, 1000);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
        <div className="container mx-auto px-6">
          <h1 className="text-4xl font-bold mb-4">Entre em Contato</h1>
          <p className="text-xl text-blue-100">
            Estamos aqui para responder suas dúvidas sobre nossa plataforma
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12 max-w-6xl">
        
        {/* Aviso Importante */}
        <Alert className="mb-8 border-orange-300 bg-orange-50">
          <AlertDescription className="text-orange-800">
            <p className="font-semibold mb-2">⚠️ Aviso Importante:</p>
            <p>
              <strong>NÃO oferecemos consultoria jurídica ou análise de casos individuais.</strong> 
              Se você tem dúvidas legais sobre imigração, recomendamos consultar um advogado de 
              imigração qualificado. Respondemos apenas perguntas sobre o funcionamento de nossa 
              plataforma tecnológica.
            </p>
          </AlertDescription>
        </Alert>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Contact Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Envie uma Mensagem</CardTitle>
              </CardHeader>
              <CardContent>
                {submitted ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-green-800 mb-2">
                      Mensagem Enviada!
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Obrigado por entrar em contato. Responderemos em até 48 horas úteis.
                    </p>
                    <Button 
                      onClick={() => setSubmitted(false)}
                      variant="outline"
                    >
                      Enviar Outra Mensagem
                    </Button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <Label htmlFor="name">Nome Completo *</Label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        placeholder="João Silva"
                      />
                    </div>

                    <div>
                      <Label htmlFor="email">Email *</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        placeholder="joao@example.com"
                      />
                    </div>

                    <div>
                      <Label htmlFor="subject">Assunto *</Label>
                      <Input
                        id="subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                        required
                        placeholder="Dúvida sobre a plataforma"
                      />
                    </div>

                    <div>
                      <Label htmlFor="message">Mensagem *</Label>
                      <Textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        required
                        rows={6}
                        placeholder="Descreva sua dúvida ou questão sobre nossa plataforma..."
                      />
                    </div>

                    <Button 
                      type="submit" 
                      className="w-full"
                      disabled={submitting}
                    >
                      {submitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Enviando...
                        </>
                      ) : (
                        <>
                          <Send className="mr-2 h-4 w-4" />
                          Enviar Mensagem
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </CardContent>
            </Card>

            {/* Tempo de Resposta */}
            <Card className="mt-6 bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Clock className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-blue-900 mb-1">
                      Tempo de Resposta
                    </p>
                    <p className="text-blue-800 text-sm">
                      Respondemos todas as mensagens em até <strong>48 horas úteis</strong>. 
                      Para questões urgentes sobre sua conta, entre em contato por telefone.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Contact Information */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Informações de Contato</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <Mail className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Email</h3>
                    <p className="text-gray-600">contato@docsimple.com</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Para dúvidas gerais e suporte
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-green-100 p-3 rounded-lg">
                    <Phone className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Telefone</h3>
                    <p className="text-gray-600">+1 (302) 555-0123</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Seg-Sex: 9h-18h (EST)
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-purple-100 p-3 rounded-lg">
                    <MapPin className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Endereço</h3>
                    <p className="text-gray-600">
                      DocSimple Tech Solutions LLC<br />
                      1234 Innovation Drive, Suite 500<br />
                      Wilmington, DE 19801<br />
                      Estados Unidos
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Outras Formas de Contato */}
            <Card>
              <CardHeader>
                <CardTitle>Outras Formas de Ajuda</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">📚 Central de Ajuda</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Encontre respostas rápidas em nossa página de perguntas frequentes
                  </p>
                  <a 
                    href="/faq" 
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Ver FAQ →
                  </a>
                </div>

                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2">⚖️ Precisa de Advogado?</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Para questões legais sobre imigração, recomendamos consultar um 
                    advogado qualificado. Visite:
                  </p>
                  <a 
                    href="https://www.aila.org/find-a-lawyer" 
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    American Immigration Lawyers Association (AILA) →
                  </a>
                </div>
              </CardContent>
            </Card>

            {/* Horário de Atendimento */}
            <Card className="bg-gray-50">
              <CardHeader>
                <CardTitle className="text-lg">Horário de Atendimento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Segunda a Sexta:</span>
                    <span className="font-medium">9h - 18h (EST)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Sábado:</span>
                    <span className="font-medium">10h - 14h (EST)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Domingo:</span>
                    <span className="font-medium">Fechado</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t">
                    <span className="text-gray-600">Feriados dos EUA:</span>
                    <span className="font-medium">Fechado</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Aviso Final */}
        <Card className="mt-8 border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <h3 className="font-semibold text-red-900 mb-3">
              ⚠️ Sobre o que NÃO podemos ajudar:
            </h3>
            <ul className="space-y-2 text-red-800 text-sm">
              <li>• Análise de elegibilidade para vistos (consulte um advogado)</li>
              <li>• Recomendação de qual visto você deve solicitar (consulte um advogado)</li>
              <li>• Revisão legal de documentos (consulte um advogado)</li>
              <li>• Representação perante USCIS (apenas advogados podem fazer isso)</li>
              <li>• Garantias de aprovação de visto (ninguém pode garantir isso)</li>
              <li>• Aconselhamento jurídico sobre casos de imigração (consulte um advogado)</li>
            </ul>
            <p className="mt-4 text-red-900 font-semibold">
              Podemos apenas ajudar com dúvidas sobre o uso de nossa plataforma tecnológica.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Contact;
