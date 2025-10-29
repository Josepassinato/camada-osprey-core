import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  MessageCircle, 
  Mic, 
  MicOff, 
  Send,
  Loader2,
  Volume2,
  HelpCircle,
  Sparkles,
  User,
  Bot
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  suggestions?: string[];
}

interface ConversationalAssistantProps {
  sessionId: string;
  visaType?: string;
  languageMode?: 'simple' | 'technical';
  userContext?: Record<string, any>;
  onLanguageModeChange?: (mode: 'simple' | 'technical') => void;
}

export const ConversationalAssistant: React.FC<ConversationalAssistantProps> = ({
  sessionId,
  visaType,
  languageMode = 'simple',
  userContext,
  onLanguageModeChange
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [currentMode, setCurrentMode] = useState<'simple' | 'technical'>(languageMode);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://agente-coruja-1.preview.emergentagent.com';

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize Web Speech API
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'pt-BR';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setError('Erro ao reconhecer voz. Tente novamente.');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      setError('Seu navegador não suporta reconhecimento de voz.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      setError(null);
      recognitionRef.current.start();
    }
  };

  const sendMessage = async (message?: string) => {
    const messageToSend = message || inputMessage.trim();
    
    if (!messageToSend) return;

    setIsLoading(true);
    setError(null);

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: messageToSend,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await fetch(`${backendUrl}/api/conversational/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageToSend,
          language_mode: currentMode,
          visa_type: visaType,
          user_context: userContext
        })
      });

      if (!response.ok) {
        throw new Error('Falha ao enviar mensagem');
      }

      const data = await response.json();

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        suggestions: data.suggestions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setError('Erro ao processar sua mensagem. Tente novamente.');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleLanguageMode = () => {
    const newMode = currentMode === 'simple' ? 'technical' : 'simple';
    setCurrentMode(newMode);
    if (onLanguageModeChange) {
      onLanguageModeChange(newMode);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const getInitialSuggestions = () => {
    const suggestions = [
      "O que é peticionário?",
      "Que documentos eu preciso?",
      "Quanto tempo demora?",
      "Quanto custa o processo?"
    ];
    return suggestions;
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MessageCircle className="w-5 h-5 text-blue-600" />
            <CardTitle>Assistente de Imigração</CardTitle>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={toggleLanguageMode}
            className="text-xs"
          >
            <Sparkles className="w-3 h-3 mr-1" />
            {currentMode === 'simple' ? 'Simples' : 'Técnico'}
          </Button>
        </div>
        <CardDescription>
          {currentMode === 'simple' 
            ? '💬 Faça perguntas em linguagem simples. Use o microfone ou escreva!'
            : '📋 Modo técnico com terminologia oficial do USCIS'
          }
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">
                Olá! 👋 Como posso te ajudar hoje?
              </p>
              <div className="space-y-2">
                <p className="text-sm text-gray-500 mb-3">Sugestões de perguntas:</p>
                {getInitialSuggestions().map((suggestion, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="mr-2 mb-2"
                  >
                    <HelpCircle className="w-3 h-3 mr-1" />
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                    <div className={`flex items-start space-x-2 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        msg.role === 'user' ? 'bg-blue-600' : 'bg-green-600'
                      }`}>
                        {msg.role === 'user' ? (
                          <User className="w-5 h-5 text-white" />
                        ) : (
                          <Bot className="w-5 h-5 text-white" />
                        )}
                      </div>
                      <div className={`flex-1 rounded-lg p-3 ${
                        msg.role === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                    
                    {/* Suggestions */}
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <div className="mt-2 ml-10 space-y-1">
                        <p className="text-xs text-gray-500">Perguntas relacionadas:</p>
                        {msg.suggestions.map((suggestion, sIdx) => (
                          <Button
                            key={sIdx}
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSuggestionClick(suggestion)}
                            className="text-xs mr-2"
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="bg-gray-100 rounded-lg p-3">
                      <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        {/* Error Display */}
        {error && (
          <div className="px-4 pb-2">
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-sm text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex items-center space-x-2">
            <Button
              variant={isListening ? "destructive" : "outline"}
              size="icon"
              onClick={toggleVoiceInput}
              disabled={isLoading}
            >
              {isListening ? (
                <MicOff className="w-4 h-4" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </Button>
            
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isListening ? "Ouvindo..." : "Digite sua pergunta ou use o microfone..."}
              disabled={isLoading || isListening}
              className="flex-1"
            />
            
            <Button
              onClick={() => sendMessage()}
              disabled={!inputMessage.trim() || isLoading || isListening}
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {isListening && (
            <div className="mt-2 flex items-center justify-center space-x-2 text-sm text-blue-600">
              <Volume2 className="w-4 h-4 animate-pulse" />
              <span>Escutando... Fale agora!</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ConversationalAssistant;
