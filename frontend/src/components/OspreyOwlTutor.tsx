import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, HelpCircle, CheckCircle, AlertTriangle, Info, ArrowRight, Award, Star } from 'lucide-react';
import { draPaulaIntelligentTutor } from './DraPaulaIntelligentTutor';

// Types from specification
type FieldState = {
  name: string;
  label?: string;
  value?: string;
  valid: boolean;
  errors: string[];
  required: boolean;
};

type SectionState = {
  id: string;
  label: string;
  status: "todo" | "in_progress" | "complete";
  missing: string[];
  percent: number;
};

type Snapshot = {
  userId: string;
  formId: string;
  stepId: string;
  url: string;
  timestamp: string;
  sections: SectionState[];
  fields: FieldState[];
  siteVersionHash: string;
};

type ValidateResult = {
  ok: boolean;
  errors: Array<{ field: string; code: string; message: string }>;
  missingRequired: string[];
  suggestions: string[];
};

type TutorMsg = {
  id: string;
  severity: "success" | "info" | "warning" | "error";
  text: string;
  actions?: Array<{ label: string; event: string; payload?: any }>;
  meta?: { notVerified?: boolean; disclaimer?: boolean };
};

interface OspreyOwlTutorProps {
  snapshot?: Snapshot;
  onAction?: (event: string, payload?: any) => void;
  isEnabled?: boolean;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  className?: string;
}

export const OspreyOwlTutor: React.FC<OspreyOwlTutorProps> = ({
  snapshot,
  onAction,
  isEnabled = true,
  position = 'bottom-right',
  className = ''
}) => {
  const [messages, setMessages] = useState<TutorMsg[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [owlEyes, setOwlEyes] = useState({ leftEye: true, rightEye: true });
  const [lastValidation, setLastValidation] = useState<ValidateResult | null>(null);
  
  const messageHistoryRef = useRef<TutorMsg[]>([]);
  const validationCacheRef = useRef<Map<string, ValidateResult>>(new Map());

  // Owl blinking animation
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setOwlEyes({ leftEye: false, rightEye: false });
      setTimeout(() => {
        setOwlEyes({ leftEye: true, rightEye: true });
      }, 150);
    }, 3000 + Math.random() * 2000);

    return () => clearInterval(blinkInterval);
  }, []);

  // Process snapshot changes
  useEffect(() => {
    if (!snapshot || !isEnabled) return;

    const processSnapshot = async () => {
      setIsValidating(true);
      
      try {
        // Check cache first
        const cacheKey = `${snapshot.stepId}_${snapshot.timestamp}`;
        let validateResult = validationCacheRef.current.get(cacheKey);
        
        if (!validateResult) {
          // Call validation API
          validateResult = await validateSnapshot(snapshot);
          validationCacheRef.current.set(cacheKey, validateResult);
        }
        
        setLastValidation(validateResult);
        
        // Generate tutor messages
        const newMessages = toTutorMessages(validateResult, snapshot);
        
        // Update messages with deduplication
        setMessages(prev => {
          const combined = [...prev, ...newMessages];
          const unique = combined.filter((msg, index, arr) => 
            arr.findIndex(m => m.id === msg.id) === index
          );
          return unique.slice(-4); // Keep last 4 messages
        });
        
        messageHistoryRef.current = [...messageHistoryRef.current, ...newMessages].slice(-10);
        
      } catch (error) {
        console.error('Tutor validation error:', error);
      } finally {
        setIsValidating(false);
      }
    };

    // Debounce processing
    const timeoutId = setTimeout(processSnapshot, 300);
    return () => clearTimeout(timeoutId);
  }, [snapshot, isEnabled]);

  // Validate snapshot via API
  const validateSnapshot = async (snapshot: Snapshot): Promise<ValidateResult> => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stepId: snapshot.stepId,
          formData: snapshot.fields.reduce((acc, field) => {
            const keys = field.name.split('.');
            let current = acc;
            for (let i = 0; i < keys.length - 1; i++) {
              if (!current[keys[i]]) current[keys[i]] = {};
              current = current[keys[i]];
            }
            current[keys[keys.length - 1]] = field.value || '';
            return acc;
          }, {} as any)
        })
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Validation API error:', error);
      return {
        ok: false,
        errors: [{ field: 'system', code: 'network_error', message: 'Erro de conexão' }],
        missingRequired: [],
        suggestions: []
      };
    }
  };

  // Convert validation result to tutor messages (from specification)
  const toTutorMessages = (v: ValidateResult, snap: Snapshot): TutorMsg[] => {
    const msgs: TutorMsg[] = [];

    // 1) Errors first
    for (const e of v.errors.slice(0, 2)) {
      msgs.push({
        id: `err:${e.field}:${e.code}`,
        severity: "error",
        text: `O campo ${e.field} ${e.message}.`,
        actions: [{ label: "Ir ao campo", event: "help:field", payload: { field: e.field } }]
      });
    }

    // 2) Missing required fields  
    if (v.missingRequired.length && msgs.length < 2) {
      const field = v.missingRequired[0];
      msgs.push({
        id: `miss:${field}`,
        severity: "warning", 
        text: `Falta o campo obrigatório **${field}** para avançar.`,
        actions: [{ label: "Ir para campo", event: "go:field", payload: { field } }]
      });
    }

    // 3) Next step
    const step = snap.stepId;
    const currentSection = snap.sections.find(s => s.id === step);
    const complete = currentSection?.status === "complete";
    
    if (complete && msgs.length === 0) {
      const nextStepMap: { [key: string]: string } = {
        'personal': 'Endereço',
        'address': 'Documentos',
        'documents': 'História Pessoal',
        'story': 'Formulário',
        'form': 'Revisão'
      };
      
      const nextStep = nextStepMap[step] || 'próxima etapa';
      
      msgs.push({
        id: `next:${step}`,
        severity: "success",
        text: `🎯 Uhul! ${currentSection?.label || 'Seção'} concluída. Próximo: **${nextStep}**.`,
        actions: [{ label: `Ir para ${nextStep}`, event: "go:next" }]
      });
    }

    // 4) Positive reinforcement
    if (currentSection?.percent && currentSection.percent >= 80 && msgs.length === 0) {
      msgs.push({
        id: `progress:${step}:${currentSection.percent}`,
        severity: "info",
        text: `✨ Ótimo progresso! ${currentSection.percent}% completo na seção ${currentSection.label}.`,
        actions: []
      });
    }

    return msgs.slice(-3);
  };

  // Handle tutor action clicks
  const handleAction = (action: { label: string; event: string; payload?: any }) => {
    onAction?.(action.event, action.payload);
    
    // Log telemetry (without PII)
    console.log('Tutor action:', {
      event: action.event,
      label: action.label,
      stepId: snapshot?.stepId,
      timestamp: new Date().toISOString()
    });
  };

  // Get overall progress
  const getOverallProgress = (): number => {
    if (!snapshot?.sections.length) return 0;
    const totalPercent = snapshot.sections.reduce((sum, section) => sum + section.percent, 0);
    return Math.round(totalPercent / snapshot.sections.length);
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    const colors = {
      success: 'text-green-600 bg-green-50 border-green-200',
      info: 'text-blue-600 bg-blue-50 border-blue-200', 
      warning: 'text-orange-600 bg-orange-50 border-orange-200',
      error: 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[severity as keyof typeof colors] || colors.info;
  };

  // Get position classes
  const getPositionClasses = () => {
    const positions = {
      'bottom-right': 'bottom-4 right-4',
      'bottom-left': 'bottom-4 left-4',
      'top-right': 'top-4 right-4', 
      'top-left': 'top-4 left-4'
    };
    return positions[position];
  };

  if (!isEnabled || !snapshot) {
    return null;
  }

  const progress = getOverallProgress();
  const hasMessages = messages.length > 0;
  const latestMessage = messages[messages.length - 1];

  return (
    <div className={`fixed ${getPositionClasses()} z-50 ${className}`}>
      {/* Tutor Messages Panel */}
      <AnimatePresence>
        {isOpen && hasMessages && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="mb-4 w-80 max-w-sm"
          >
            <div className="bg-white border border-gray-200 rounded-lg shadow-lg">
              {/* Header */}
              <div className="flex items-center justify-between p-3 border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-black">💡 Dicas do Tutor</span>
                  {isValidating && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-3 h-3 border border-gray-400 border-t-black rounded-full"
                    />
                  )}
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Fechar dicas"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Messages */}
              <div 
                className="max-h-64 overflow-y-auto"
                role="log" 
                aria-live="polite"
                aria-label="Mensagens do tutor"
              >
                <div className="p-3 space-y-3">
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`p-3 rounded-lg border text-sm ${getSeverityColor(message.severity)}`}
                    >
                      <div className="flex items-start gap-2">
                        <div className="flex-shrink-0 mt-0.5">
                          {message.severity === 'success' && <CheckCircle className="h-4 w-4" />}
                          {message.severity === 'error' && <AlertTriangle className="h-4 w-4" />}
                          {message.severity === 'warning' && <AlertTriangle className="h-4 w-4" />}
                          {message.severity === 'info' && <Info className="h-4 w-4" />}
                        </div>
                        <div className="flex-1">
                          <p 
                            className="leading-relaxed"
                            dangerouslySetInnerHTML={{ 
                              __html: message.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') 
                            }}
                          />
                          
                          {/* Actions */}
                          {message.actions && message.actions.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-2">
                              {message.actions.map((action, actionIndex) => (
                                <button
                                  key={actionIndex}
                                  onClick={() => handleAction(action)}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white text-xs rounded hover:bg-gray-800 transition-colors"
                                >
                                  {action.label}
                                  <ArrowRight className="h-3 w-3" />
                                </button>
                              ))}
                            </div>
                          )}
                          
                          {/* Disclaimer */}
                          {message.meta?.disclaimer && (
                            <p className="mt-2 text-xs opacity-75">
                              Isto não é aconselhamento jurídico.
                            </p>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Owl Mascot */}
      <motion.div
        className="relative"
        animate={{ scale: isOpen ? 1.1 : 1 }}
        transition={{ duration: 0.2 }}
      >
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative w-16 h-16 bg-gradient-to-b from-gray-100 to-gray-200 rounded-full shadow-lg hover:shadow-xl transition-shadow focus:outline-none focus:ring-2 focus:ring-black focus:ring-opacity-50"
          aria-label={`Tutor Osprey ${isOpen ? 'aberto' : 'fechado'}. ${hasMessages ? `${messages.length} mensagem(ns) disponível(is)` : 'Nenhuma mensagem'}`}
        >
          {/* Owl SVG */}
          <div className="absolute inset-0 flex items-center justify-center">
            <svg
              width="32"
              height="32"
              viewBox="0 0 32 32"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="text-black"
            >
              {/* Owl Body */}
              <circle cx="16" cy="18" r="10" fill="currentColor" fillOpacity="0.8" />
              
              {/* Owl Head */}
              <circle cx="16" cy="12" r="8" fill="currentColor" />
              
              {/* Ear Tufts */}
              <path d="M10 6 L12 4 L14 6" stroke="currentColor" strokeWidth="2" fill="none" />
              <path d="M18 6 L20 4 L22 6" stroke="currentColor" strokeWidth="2" fill="none" />
              
              {/* Eyes */}
              <motion.circle
                cx="12"
                cy="11"
                r="2.5"
                fill="white"
                animate={{ scaleY: owlEyes.leftEye ? 1 : 0.1 }}
                transition={{ duration: 0.1 }}
              />
              <motion.circle
                cx="20"
                cy="11"
                r="2.5"
                fill="white"
                animate={{ scaleY: owlEyes.rightEye ? 1 : 0.1 }}
                transition={{ duration: 0.1 }}
              />
              
              {/* Pupils */}
              {owlEyes.leftEye && <circle cx="12" cy="11" r="1" fill="currentColor" />}
              {owlEyes.rightEye && <circle cx="20" cy="11" r="1" fill="currentColor" />}
              
              {/* Beak */}
              <path d="M15 14 L16 16 L17 14 Z" fill="orange" />
              
              {/* Wings */}
              <ellipse cx="10" cy="18" rx="3" ry="6" fill="currentColor" fillOpacity="0.6" />
              <ellipse cx="22" cy="18" rx="3" ry="6" fill="currentColor" fillOpacity="0.6" />
            </svg>
          </div>
          
          {/* Progress Badge */}
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-black text-white text-xs font-bold rounded-full flex items-center justify-center">
            {progress}%
          </div>
          
          {/* Notification Dot */}
          {hasMessages && !isOpen && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"
            />
          )}
        </button>
        
        {/* Quick Preview */}
        {!isOpen && latestMessage && (
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            className="absolute right-20 top-0 w-48 p-2 bg-black text-white text-xs rounded-lg shadow-lg pointer-events-none"
          >
            <div className="truncate">{latestMessage.text.replace(/\*\*(.*?)\*\*/g, '$1')}</div>
            <div className="absolute top-2 -right-1 w-2 h-2 bg-black rotate-45 transform"></div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default OspreyOwlTutor;