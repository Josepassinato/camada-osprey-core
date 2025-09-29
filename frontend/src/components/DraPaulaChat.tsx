import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, Send, X, Bot, User, Loader2 } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ChatMessage {
  id: string;
  sender: 'user' | 'dra_paula';
  message: string;
  timestamp: Date;
  type: 'text' | 'suggestion' | 'alert';
  visaContext?: string;
}

interface DraPaulaChatProps {
  visaType?: string;
  currentStep?: string;
  userProfile?: any;
  isOpen: boolean;
  onClose: () => void;
  onSuggestion?: (suggestion: string) => void;
}

export const DraPaulaChat: React.FC<DraPaulaChatProps> = ({
  visaType = 'H-1B',
  currentStep = 'documents',
  userProfile,
  isOpen,
  onClose,
  onSuggestion
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        sender: 'dra_paula',
        message: `Olá! 👋 Sou a **Dra. Paula B2C**, especialista em imigração americana.\n\nEstou aqui para responder suas dúvidas específicas sobre o processo **${visaType}**. Como posso ajudar você hoje?`,
        timestamp: new Date(),
        type: 'text',
        visaContext: visaType
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, visaType]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getDraPaulaResponse = async (userMessage: string): Promise<string> => {
    // Simulate API call to Dra. Paula's knowledge base
    setIsTyping(true);
    
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing time
    
    // Smart response based on user message and context
    const responses = getDraPaulaSmartResponse(userMessage, visaType, currentStep);
    
    setIsTyping(false);
    return responses;
  };

  const getDraPaulaSmartResponse = (message: string, visa: string, step: string): string => {
    const lowerMsg = message.toLowerCase();
    
    // H-1B specific responses
    if (visa === 'H-1B') {
      if (lowerMsg.includes('salario') || lowerMsg.includes('salary') || lowerMsg.includes('wage')) {
        return `💰 **Salário H-1B**: O salário deve atender ao *prevailing wage* da sua área e região. Recomendo:\n\n✅ Consultar o site do Departamento do Trabalho (DOL)\n✅ Verificar se o empregador já tem a LCA aprovada\n✅ Documentar que o salário está acima do mínimo exigido\n\nSalários muito baixos podem causar rejeição da petição!`;
      }
      
      if (lowerMsg.includes('diploma') || lowerMsg.includes('bachelor') || lowerMsg.includes('educacao')) {
        return `🎓 **Diploma para H-1B**: Essencial que seja *Bachelor degree ou superior* na área relacionada ao cargo:\n\n✅ Diploma deve ser de instituição reconhecida\n✅ Área de estudo deve qualificar como "specialty occupation"\n✅ Se diploma estrangeiro, considere evaluation credencial\n✅ Nome no diploma deve ser idêntico ao passaporte\n\nÁreas STEM têm maior taxa de aprovação!`;
      }
      
      if (lowerMsg.includes('lca') || lowerMsg.includes('labor condition')) {
        return `📋 **LCA (Labor Condition Application)**: Documento OBRIGATÓRIO que o empregador deve ter:\n\n✅ Deve ser aprovado ANTES da petição H-1B\n✅ Especifica salário, local de trabalho, condições\n✅ Válido apenas para locais especificados\n✅ Empregador deve manter cópias disponíveis\n\n⚠️ **SEM LCA = SEM H-1B!**`;
      }
    }
    
    // L-1 specific responses
    if (visa === 'L-1') {
      if (lowerMsg.includes('experiencia') || lowerMsg.includes('1 ano') || lowerMsg.includes('experience')) {
        return `⏰ **Experiência L-1**: Requisito CRÍTICO de 1 ano contínuo:\n\n✅ 1 ano nos últimos 3 anos na empresa relacionada\n✅ Deve ser em posição executiva, gerencial ou especializada\n✅ Tempo deve ser CONTÍNUO (não quebrado)\n✅ Comprove com cartas detalhadas do empregador\n\nDocumentação insuficiente = negação garantida!`;
      }
      
      if (lowerMsg.includes('empresa') || lowerMsg.includes('relacionamento') || lowerMsg.includes('subsidiary')) {
        return `🏢 **Relacionamento Empresarial L-1**: Deve provar conexão entre empresas:\n\n✅ Parent/Subsidiary/Affiliate relationship\n✅ Organograma corporativo detalhado\n✅ Contratos, acordos, documentos societários\n✅ Fluxo financeiro entre empresas se aplicável\n\nSem relacionamento comprovado = L-1 negado!`;
      }
    }
    
    // B-1/B-2 specific responses
    if (visa === 'B-1/B-2') {
      if (lowerMsg.includes('vinculos') || lowerMsg.includes('brasil') || lowerMsg.includes('ties')) {
        return `🇧🇷 **Vínculos com Brasil**: ESSENCIAL demonstrar intenção de retorno:\n\n✅ Emprego estável (carta do empregador)\n✅ Propriedades no Brasil (escrituras)\n✅ Família no Brasil (certidões)\n✅ Contas bancárias movimentadas\n✅ Compromissos futuros comprovados\n\nConsulado avalia se você tem razões para voltar!`;
      }
      
      if (lowerMsg.includes('financeiro') || lowerMsg.includes('dinheiro') || lowerMsg.includes('financial')) {
        return `💳 **Recursos Financeiros B-1/B-2**: Prove capacidade de se manter:\n\n✅ 3 meses de extratos bancários\n✅ Declaração de Imposto de Renda\n✅ Carta do empregador com salário\n✅ Comprovantes de renda adicional\n✅ Cálculo de gastos esperados nos EUA\n\nRecursos insuficientes = motivo #1 de negação!`;
      }
    }
    
    // Generic helpful responses
    if (lowerMsg.includes('prazo') || lowerMsg.includes('tempo') || lowerMsg.includes('deadline')) {
      return `⏱️ **Prazos Importantes**: Cada visto tem timelines específicos:\n\n• **H-1B**: Processo 2-4 meses (15 dias com premium)\n• **L-1**: 2-3 meses regulares\n• **B-1/B-2**: Agendamento + entrevista consular\n• **F-1**: Após I-20, processo 2-8 semanas\n\n⚠️ **SEMPRE** considere margem para imprevistos!`;
    }
    
    if (lowerMsg.includes('taxa') || lowerMsg.includes('fee') || lowerMsg.includes('custo')) {
      return `💰 **Taxas USCIS 2024**:\n\n• **H-1B**: $555 + $1,500 + possível $4,000\n• **L-1**: $555 + $1,440\n• **B-1/B-2**: $185 (consular)\n• **F-1**: $185 + $350 (SEVIS)\n\n💡 **Dica**: Valores podem mudar. Sempre verifique site oficial USCIS!`;
    }
    
    // Default helpful response
    return `Entendo sua dúvida sobre **${visa}**. Como especialista, recomendo:\n\n🔍 **Seja específico**: Descreva sua situação particular\n📋 **Documente tudo**: USCIS exige evidências detalhadas\n⏰ **Não deixe para última hora**: Processos levam tempo\n🎯 **Foque nos requisitos**: Cada visto tem critérios específicos\n\nPode reformular sua pergunta com mais detalhes? Assim posso dar uma orientação mais precisa! 😊`;
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      message: inputValue,
      timestamp: new Date(),
      type: 'text'
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    // Get Dra. Paula's response
    const response = await getDraPaulaResponse(inputValue);
    
    const draPaulaMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      sender: 'dra_paula',
      message: response,
      timestamp: new Date(),
      type: 'text',
      visaContext: visaType
    };
    
    setMessages(prev => [...prev, draPaulaMessage]);
    
    // Save to chat history
    setChatHistory(prev => [...prev, userMessage, draPaulaMessage]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="fixed bottom-4 right-4 w-96 h-[500px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm">Dra. Paula B2C</h3>
                <p className="text-xs opacity-90">Especialista em Imigração • Online</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start gap-2 max-w-[80%] ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  msg.sender === 'user' 
                    ? 'bg-gray-200' 
                    : 'bg-orange-100'
                }`}>
                  {msg.sender === 'user' ? (
                    <User className="h-3 w-3 text-gray-600" />
                  ) : (
                    <Bot className="h-3 w-3 text-orange-600" />
                  )}
                </div>
                <div className={`p-3 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-gray-100 text-gray-800'
                    : 'bg-orange-50 border border-orange-200'
                }`}>
                  <div className="text-sm whitespace-pre-wrap">{msg.message}</div>
                  <div className="text-xs opacity-60 mt-1">
                    {msg.timestamp.toLocaleTimeString('pt-BR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-orange-100 rounded-full flex items-center justify-center">
                  <Bot className="h-3 w-3 text-orange-600" />
                </div>
                <div className="bg-orange-50 border border-orange-200 p-3 rounded-lg">
                  <div className="flex items-center gap-1">
                    <Loader2 className="h-3 w-3 animate-spin text-orange-600" />
                    <span className="text-sm text-orange-600">Dra. Paula está digitando...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Digite sua dúvida sobre imigração..."
              className="flex-1"
              disabled={isTyping}
            />
            <Button 
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="bg-orange-500 hover:bg-orange-600"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Quick suggestions */}
          <div className="flex flex-wrap gap-1 mt-2">
            {[
              `Requisitos ${visaType}`,
              'Prazos importantes',
              'Documentos obrigatórios',
              'Taxas USCIS'
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setInputValue(suggestion)}
                className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DraPaulaChat;