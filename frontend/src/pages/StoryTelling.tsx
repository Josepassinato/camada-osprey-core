import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  ArrowRight,
  Mic,
  MicOff,
  FileText,
  CheckCircle,
  AlertTriangle,
  Save,
  RefreshCw,
  Info,
  MessageSquare,
  Lightbulb,
  User,
  Bot,
  Volume2,
  StopCircle
} from "lucide-react";

interface AIAssistanceMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ExtractedFacts {
  [key: string]: any;
  personal_info?: any;
  immigration_history?: any;
  family_details?: any;
  employment_info?: any;
  education?: any;
  travel_history?: any;
}

const StoryTelling = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [case_, setCase] = useState<any>(null);
  const [visaSpecs, setVisaSpecs] = useState<any>(null);
  const [userStory, setUserStory] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [extractedFacts, setExtractedFacts] = useState<ExtractedFacts>({});
  const [aiMessages, setAIMessages] = useState<AIAssistanceMessage[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }
      
      const response = await fetch(url);

      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        // Load existing story if available
        if (data.case.user_story_text) {
          setUserStory(data.case.user_story_text);
        }
        
        // Load extracted facts if available
        if (data.case.ai_extracted_facts) {
          setExtractedFacts(data.case.ai_extracted_facts);
        }
        
        if (data.case.form_code) {
          await fetchVisaSpecs(data.case.form_code);
        }
      } else {
        setError('Caso não encontrado');
      }
    } catch (error) {
      console.error('Fetch case error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchVisaSpecs = async (formCode: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/visa-specs/${formCode}`
      );

      if (response.ok) {
        const data = await response.json();
        setVisaSpecs(data);
        
        // Initialize AI assistance with visa-specific questions
        initializeAIAssistance(data);
      }
    } catch (error) {
      console.error('Fetch visa specs error:', error);
    }
  };

  const initializeAIAssistance = (specs: any) => {
    const welcomeMessage: AIAssistanceMessage = {
      id: Date.now().toString(),
      type: 'assistant',
      content: `Olá! Vou te ajudar a estruturar sua história para ${specs.specifications.title}. 

Conte-me sobre sua situação de forma natural e conversacional. Não se preocupe com a formatação - eu vou extrair as informações importantes automaticamente.

Algumas coisas que podem ser úteis mencionar:
• Sua situação atual e por que precisa desta aplicação
• Histórico pessoal e familiar relevante
• Experiência educacional e profissional
• Viagens e mudanças de endereço
• Desafios ou circunstâncias especiais

Pode começar falando ou escrevendo como preferir. Eu vou fazer perguntas para esclarecer pontos importantes conforme necessário.`,
      timestamp: new Date()
    };
    
    setAIMessages([welcomeMessage]);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        processAudioToText(audioBlob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Erro ao acessar microfone. Verifique as permissões.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      
      // Stop all tracks
      const stream = mediaRecorder.current.stream;
      stream.getTracks().forEach(track => track.stop());
    }
  };

  const processAudioToText = async (audioBlob: Blob) => {
    // Simulate audio to text conversion
    setIsLoadingAI(true);
    
    try {
      // For now, simulate the transcription process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const simulatedText = "Esta é uma simulação da transcrição de áudio. Em um ambiente real, isso seria convertido usando um serviço de speech-to-text.";
      
      const newText = userStory + (userStory ? "\n\n" : "") + simulatedText;
      setUserStory(newText);
      
      // Auto-resize textarea
      if (textAreaRef.current) {
        textAreaRef.current.style.height = 'auto';
        textAreaRef.current.style.height = textAreaRef.current.scrollHeight + 'px';
      }
      
    } catch (error) {
      console.error('Audio processing error:', error);
      setError('Erro ao processar áudio');
    } finally {
      setIsLoadingAI(false);
    }
  };

  const handleStoryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserStory(e.target.value);
    
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  };

  const askAIAssistance = async () => {
    if (!currentQuestion.trim()) return;
    
    const userMessage: AIAssistanceMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentQuestion,
      timestamp: new Date()
    };
    
    setAIMessages(prev => [...prev, userMessage]);
    setCurrentQuestion("");
    setIsLoadingAI(true);
    
    try {
      // Simulate AI response
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const aiResponse: AIAssistanceMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Baseado na sua pergunta "${userMessage.content}", aqui está minha sugestão:

Isso é uma informação importante para ${visaSpecs?.specifications.title}. Certifique-se de incluir detalhes específicos sobre:

• Datas exatas quando possível
• Documentos de suporte que você tem
• Nomes completos e endereços
• Qualquer circunstância especial

Você pode adicionar essas informações no seu texto acima. Se precisar de mais orientações específicas, me pergunte!`,
        timestamp: new Date()
      };
      
      setAIMessages(prev => [...prev, aiResponse]);
      
    } catch (error) {
      console.error('AI assistance error:', error);
    } finally {
      setIsLoadingAI(false);
    }
  };

  const extractFactsFromStory = async () => {
    if (!userStory.trim()) {
      setError('Por favor, escreva sua história primeiro.');
      return;
    }
    
    setIsLoadingAI(true);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/extract-facts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          story_text: userStory,
          form_code: case_.form_code
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setExtractedFacts(data.extracted_facts);
        
        // Add AI message about extraction
        const extractionMessage: AIAssistanceMessage = {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Ótimo! Analisei sua história e extraí ${Object.keys(data.extracted_facts).length} categorias de informações importantes. 

Você pode ver as informações organizadas na lateral direita. Se algo estiver incorreto ou se eu perdi algum detalhe importante, você pode:

1. Editar sua história acima
2. Me perguntar sobre informações específicas
3. Clicar em "Extrair Fatos" novamente após as alterações

As informações extraídas serão usadas para preencher automaticamente os formulários oficiais na próxima etapa.`,
          timestamp: new Date()
        };
        
        setAIMessages(prev => [...prev, extractionMessage]);
        
      } else {
        setError('Erro ao extrair informações da história');
      }
      
    } catch (error) {
      console.error('Extract facts error:', error);
      setError('Erro de conexão ao extrair fatos');
    } finally {
      setIsLoadingAI(false);
    }
  };

  const saveStory = async () => {
    setIsSaving(true);
    
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }

      await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_story_text: userStory,
          ai_extracted_facts: extractedFacts,
          status: 'story_completed'
        }),
      });
      
      // Show success message
      const saveMessage: AIAssistanceMessage = {
        id: Date.now().toString(),
        type: 'assistant',
        content: 'História salva com sucesso! Suas informações foram organizadas e estão prontas para a próxima etapa.',
        timestamp: new Date()
      };
      
      setAIMessages(prev => [...prev, saveMessage]);

    } catch (error) {
      console.error('Save story error:', error);
      setError('Erro ao salvar história');
    } finally {
      setIsSaving(false);
    }
  };

  const canContinue = () => {
    return userStory.trim().length > 50 && Object.keys(extractedFacts).length > 0;
  };

  const continueToNextStep = () => {
    navigate(`/auto-application/case/${caseId}/friendly-form`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando assistente de história...</p>
        </div>
      </div>
    );
  }

  if (error && !case_) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <Card className="glass border-0 max-w-md">
          <CardContent className="text-center p-8">
            <AlertTriangle className="h-12 w-12 text-gray-700 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">
              {error || 'Caso não encontrado'}
            </h2>
            <Button onClick={() => navigate('/auto-application/start')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate(`/auto-application/case/${caseId}/documents`)}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <MessageSquare className="h-8 w-8 text-black" />
                  {visaSpecs?.specifications.title || case_.form_code}
                </h1>
                <p className="text-muted-foreground">
                  Etapa 3 de 6: Conte sua História • Caso: {case_.case_id}
                </p>
              </div>
            </div>
            <Badge className="bg-gray-100 text-gray-800 border-gray-200">
              {userStory.length > 50 ? 'História Iniciada' : 'Aguardando'}
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-3 gap-8">
          
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Story Input */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Sua História Pessoal
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Conte sua história de forma natural. Nossa IA vai extrair as informações importantes automaticamente.
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative">
                  <textarea
                    ref={textAreaRef}
                    value={userStory}
                    onChange={handleStoryChange}
                    placeholder={`Exemplo para ${case_?.form_code}:\n\nMeu nome é [Nome] e sou [nacionalidade]. Atualmente estou [situação atual]. Preciso desta aplicação porque [motivo]...\n\nConte sobre sua família, trabalho, educação, viagens e qualquer circunstância especial relevante para sua aplicação.`}
                    className="w-full min-h-[300px] p-4 text-sm border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-black focus:border-black bg-white"
                    style={{ lineHeight: '1.6' }}
                  />
                  <div className="absolute bottom-4 right-4 text-xs text-muted-foreground">
                    {userStory.length} caracteres
                  </div>
                </div>
                
                {/* Recording Controls */}
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Button
                      variant={isRecording ? "destructive" : "outline"}
                      size="sm"
                      onClick={isRecording ? stopRecording : startRecording}
                      disabled={isLoadingAI}
                    >
                      {isRecording ? (
                        <>
                          <StopCircle className="h-4 w-4" />
                          Parar Gravação
                        </>
                      ) : (
                        <>
                          <Mic className="h-4 w-4" />
                          Gravar Áudio
                        </>
                      )}
                    </Button>
                    
                    {isRecording && (
                      <div className="flex items-center gap-2 text-red-600">
                        <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
                        <span className="text-xs">Gravando...</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    Você pode gravar sua história e ela será transcrita automaticamente
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-3">
                  <Button
                    onClick={extractFactsFromStory}
                    disabled={!userStory.trim() || isLoadingAI}
                    className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
                  >
                    {isLoadingAI ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Lightbulb className="h-4 w-4" />
                    )}
                    Extrair Fatos Importantes
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={saveStory}
                    disabled={isSaving || !userStory.trim()}
                  >
                    {isSaving ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Salvar
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* AI Assistant */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  Assistente IA
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Messages */}
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {aiMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`p-3 rounded-lg text-sm ${
                            message.type === 'user'
                              ? 'bg-black text-white'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {message.content.split('\n').map((line, index) => (
                            <p key={index} className={index > 0 ? 'mt-2' : ''}>
                              {line}
                            </p>
                          ))}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                      <div className={`${message.type === 'user' ? 'order-1' : 'order-2'}`}>
                        {message.type === 'user' ? (
                          <User className="h-6 w-6 text-gray-600" />
                        ) : (
                          <Bot className="h-6 w-6 text-black" />
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {isLoadingAI && (
                    <div className="flex gap-3 justify-start">
                      <Bot className="h-6 w-6 text-black" />
                      <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                        <div className="flex items-center gap-2">
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          <span className="text-sm">Pensando...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Question Input */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={currentQuestion}
                    onChange={(e) => setCurrentQuestion(e.target.value)}
                    placeholder="Faça uma pergunta sobre sua aplicação..."
                    className="flex-1 p-2 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-black focus:border-black"
                    onKeyPress={(e) => e.key === 'Enter' && askAIAssistance()}
                  />
                  <Button
                    onClick={askAIAssistance}
                    disabled={!currentQuestion.trim() || isLoadingAI}
                    size="sm"
                  >
                    Perguntar
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-between items-center">
              <div className="text-sm text-muted-foreground">
                {canContinue() ? (
                  <div className="flex items-center gap-2 text-gray-700">
                    <CheckCircle className="h-4 w-4" />
                    <span>História completa e fatos extraídos</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-gray-700" />
                    <span>
                      {!userStory.trim() || userStory.length < 50 
                        ? 'Escreva uma história mais detalhada (mín. 50 caracteres)'
                        : 'Clique em "Extrair Fatos Importantes" para continuar'
                      }
                    </span>
                  </div>
                )}
              </div>

              <Button 
                onClick={continueToNextStep}
                disabled={!canContinue()}
                className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
              >
                Continuar para Formulário
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Extracted Facts */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-black" />
                  Fatos Extraídos
                </CardTitle>
              </CardHeader>
              <CardContent>
                {Object.keys(extractedFacts).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(extractedFacts).map(([category, data]) => (
                      <div key={category} className="p-3 bg-gray-50 rounded-lg">
                        <h4 className="font-medium text-sm text-gray-800 mb-2 capitalize">
                          {category.replace(/_/g, ' ')}
                        </h4>
                        <div className="text-xs text-gray-600 space-y-1">
                          {typeof data === 'object' && data ? (
                            Object.entries(data).map(([key, value]) => (
                              <p key={key}>
                                <strong>{key}:</strong> {String(value)}
                              </p>
                            ))
                          ) : (
                            <p>{String(data)}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Conte sua história acima e clique em "Extrair Fatos" para ver as informações organizadas aqui.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Progress Steps */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Progresso da Aplicação</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Dados Básicos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Carta de Apresentação</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Upload de Documentos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-black text-white rounded-full flex items-center justify-center text-xs font-bold">
                      4
                    </div>
                    <span className="text-sm font-medium">Conte sua História</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      5
                    </div>
                    <span className="text-sm text-muted-foreground">Formulário Amigável</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      6
                    </div>
                    <span className="text-sm text-muted-foreground">Revisão Final</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      7
                    </div>
                    <span className="text-sm text-muted-foreground">Pagamento & Download</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="glass border-0 bg-gray-50">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-gray-700 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground mb-1">Dicas para sua História</p>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Seja honesto e detalhado</li>
                      <li>• Inclua datas importantes</li>
                      <li>• Mencione documentos que você tem</li>
                      <li>• Nossa IA organiza as informações automaticamente</li>
                      <li>• Você pode gravar ao invés de escrever</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryTelling;