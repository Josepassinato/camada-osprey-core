import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, HelpCircle, CheckCircle, AlertTriangle, Info, ArrowRight, Award, Star, MessageCircle, Brain } from 'lucide-react';
import { draPaulaIntelligentTutor } from './DraPaulaIntelligentTutor';
import DraPaulaChat from './DraPaulaChat';
import { SmartPersonalization } from './SmartPersonalization';
import { useUserGuidanceHistory } from '@/hooks/useUserGuidanceHistory';

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
  meta?: { notVerified?: boolean; disclaimer?: boolean; draPaulaAdvice?: boolean };
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
  const [achievements, setAchievements] = useState<string[]>([]);
  const [currentVisaType, setCurrentVisaType] = useState<string>('');
  const [currentStep, setCurrentStep] = useState<string>('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [showPersonalization, setShowPersonalization] = useState(false);

  // User guidance history integration
  const { addGuidanceRecord, getPersonalizedTips } = useUserGuidanceHistory({
    visaType: currentVisaType,
    enablePersonalization: true
  });
  const [isOpen, setIsOpen] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [owlEyes, setOwlEyes] = useState({ leftEye: true, rightEye: true });
  const [lastValidation, setLastValidation] = useState<ValidateResult | null>(null);

  // Initialize with Dra. Paula welcome message
  useEffect(() => {
    if (snapshot?.visa_type && snapshot?.step) {
      setCurrentVisaType(snapshot.visa_type);
      setCurrentStep(snapshot.step);
      
      // Welcome message with visa-specific context
      const welcomeMessage = {
        id: 'welcome',
        severity: 'info' as const,
        text: `🦉 Olá! Sou a Coruja do Osprey, integrada com o conhecimento da **Dra. Paula B2C**!\n\nVou te guiar no seu processo ${snapshot.visa_type} com dicas especializadas. Juntas, vamos garantir o sucesso da sua aplicação! ✨`,
        actions: [],
        meta: { draPaulaAdvice: true, disclaimer: false }
      };

      setMessages([welcomeMessage]);
      
      // Load initial proactive messages from Dra. Paula
      loadProactiveMessages();
    }
  }, [snapshot?.visa_type, snapshot?.step]);

  // Monitor for proactive opportunities
  useEffect(() => {
    if (!snapshot || !currentVisaType || !currentStep) return;

    const checkProactiveOpportunities = () => {
      const proactiveMessages: Message[] = [];

      // Document-specific proactive messages
      if (currentStep === 'documents' && snapshot.documents) {
        snapshot.documents.forEach((doc: any) => {
          if (doc.uploaded && doc.analyzed && doc.aiAnalysis) {
            const contextMessages = draPaulaIntelligentTutor.getMessagesForContext(
              currentVisaType,
              currentStep,
              'onDocument',
              { documentType: doc.id, analysis: doc.aiAnalysis }
            );
            
            contextMessages.forEach(msg => {
              proactiveMessages.push(draPaulaIntelligentTutor.convertToTutorMessage(msg));
            });
          }
        });
      }

      // Form progress proactive messages
      if (currentStep === 'friendly_form' && snapshot.completion_percentage) {
        if (snapshot.completion_percentage > 50 && snapshot.completion_percentage < 80) {
          const progressMessages = draPaulaIntelligentTutor.getMessagesForContext(
            currentVisaType,
            currentStep,
            'onProgress'
          );
          
          progressMessages.forEach(msg => {
            proactiveMessages.push(draPaulaIntelligentTutor.convertToTutorMessage(msg));
          });
        }
      }

      // Add new proactive messages (avoid duplicates)
      if (proactiveMessages.length > 0) {
        setMessages(prev => {
          const existingIds = new Set(prev.map(m => m.id));
          const newMessages = proactiveMessages.filter(m => !existingIds.has(m.id));
          return [...prev, ...newMessages].slice(-6); // Keep last 6 messages
        });
      }
    };

    // Debounce proactive checks
    const timeoutId = setTimeout(checkProactiveOpportunities, 2000);
    return () => clearTimeout(timeoutId);
  }, [snapshot, currentVisaType, currentStep]);

  const loadProactiveMessages = () => {
    if (!currentVisaType || !currentStep) return;

    const proactiveMessages = draPaulaIntelligentTutor.getProactiveMessages(
      currentVisaType,
      currentStep,
      snapshot
    );

    const newMessages = proactiveMessages.map(msg => 
      draPaulaIntelligentTutor.convertToTutorMessage(msg)
    );

    if (newMessages.length > 0) {
      setMessages(prev => [...prev, ...newMessages]);
    }
  };

  const checkForAchievements = (result: ValidateResult) => {
    const newAchievements: string[] = [];
    
    // Check for completion-based achievements
    if (result.ok && result.errors.length === 0 && result.missingRequired.length === 0) {
      const achievementMsg = draPaulaIntelligentTutor.getAchievementMessage(
        currentVisaType,
        currentStep,
        { 
          allSectionsComplete: true,
          allDocumentsUploaded: snapshot?.documents?.every((doc: any) => doc.uploaded),
          errorFree: true
        }
      );

      if (achievementMsg) {
        const achievementTutorMsg = draPaulaIntelligentTutor.convertToTutorMessage(achievementMsg);
        setMessages(prev => [...prev, achievementTutorMsg]);
        
        if (!achievements.includes(achievementMsg.id)) {
          newAchievements.push(achievementMsg.id);
        }
      }
    }

    // Update achievements
    if (newAchievements.length > 0) {
      setAchievements(prev => [...prev, ...newAchievements]);
      showAchievementNotification(newAchievements[0]);
    }
  };

  const showAchievementNotification = (achievementId: string) => {
    // Show floating achievement notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
    notification.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="text-xl">🏆</span>
        <span class="font-bold">Conquista Desbloqueada!</span>
      </div>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 4000);
  };

  const handleDocumentAnalysis = (documentId: string, analysis: any) => {
    if (!currentVisaType || !currentStep) return;

    // Get document-specific messages from Dra. Paula
    const docMessages = draPaulaIntelligentTutor.getMessagesForContext(
      currentVisaType,
      'documents',
      'onDocument',
      { documentType: documentId, analysis }
    );

    const newMessages = docMessages.map(msg => {
      const tutorMsg = draPaulaIntelligentTutor.convertToTutorMessage(msg);
      return {
        ...tutorMsg,
        text: `📄 **${documentId.toUpperCase()}**: ${tutorMsg.text}`,
        meta: { ...tutorMsg.meta, documentAnalysis: true }
      };
    });

    if (newMessages.length > 0) {
      setMessages(prev => [...prev, ...newMessages]);
    }

    // Check if this completes all documents for achievement
    if (analysis.valid && snapshot?.documents) {
      const allValid = snapshot.documents.every((doc: any) => 
        doc.uploaded && doc.aiAnalysis?.valid
      );

      if (allValid) {
        const achievementMsg = draPaulaIntelligentTutor.getAchievementMessage(
          currentVisaType,
          'documents',
          { allDocumentsUploaded: true, allDocumentsValid: true }
        );

        if (achievementMsg) {
          const achievementTutorMsg = draPaulaIntelligentTutor.convertToTutorMessage(achievementMsg);
          setMessages(prev => [...prev, achievementTutorMsg]);
          
          if (!achievements.includes(achievementMsg.id)) {
            setAchievements(prev => [...prev, achievementMsg.id]);
            showAchievementNotification(achievementMsg.id);
          }
        }
      }
    }
  };

  const handleValidationSuccess = (result: ValidateResult) => {
    const newMessages: TutorMsg[] = [];
    
    if (result.ok && result.errors.length === 0) {
      newMessages.push({
        id: `success-${Date.now()}`,
        severity: 'success',
        text: '✅ Excelente! Todos os campos estão preenchidos corretamente.',
        actions: [],
        meta: { draPaulaAdvice: false, disclaimer: false }
      });

      // Check for achievements after successful validation
      checkForAchievements(result);
    }
    
    // Add contextual Dra. Paula messages for errors
    if (result.errors.length > 0 || result.missingRequired.length > 0) {
      const contextualMessages = draPaulaIntelligentTutor.getMessagesForContext(
        currentVisaType,
        currentStep,
        'onError'
      );

      contextualMessages.forEach(msg => {
        newMessages.push(draPaulaIntelligentTutor.convertToTutorMessage(msg));
      });
    }
    
    // Add error messages
    result.errors.forEach((error, index) => {
      newMessages.push({
        id: `error-${Date.now()}-${index}`,
        severity: 'error',
        text: `❌ ${error}`,
        actions: [],
        meta: { draPaulaAdvice: false, disclaimer: false }
      });
    });
    
    // Add missing field messages  
    result.missingRequired.forEach((missing, index) => {
      newMessages.push({
        id: `missing-${Date.now()}-${index}`,
        severity: 'warning',
        text: `⚠️ Campo obrigatório: ${missing}`,
        actions: [],
        meta: { draPaulaAdvice: false, disclaimer: false }
      });
    });
    
    // Add suggestions with Dra. Paula insights
    result.suggestions.forEach((suggestion, index) => {
      newMessages.push({
        id: `suggestion-${Date.now()}-${index}`,
        severity: 'info', 
        text: `💡 ${suggestion}`,
        actions: [],
        meta: { draPaulaAdvice: true, disclaimer: false }
      });
    });

    setMessages(prev => [...prev, ...newMessages]);
    setLastValidation(result);
  };
  
  const messageHistoryRef = useRef<TutorMsg[]>([]);
  const validationCacheRef = useRef<Map<string, ValidateResult>>(new Map());

  // Expose document analysis handler
  useEffect(() => {
    if (onAction) {
      // Add document analysis listener
      (window as any).draPaulaDocumentAnalysis = handleDocumentAnalysis;
    }
    
    return () => {
      delete (window as any).draPaulaDocumentAnalysis;
    };
  }, [onAction, currentVisaType, currentStep, achievements]);

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
        
        // Use the new handleValidationSuccess function
        handleValidationSuccess(validateResult);
        
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
                      className={`p-3 rounded-lg border text-sm ${getSeverityColor(message.severity)} ${
                        message.meta?.draPaulaAdvice 
                          ? 'border-l-4 border-orange-400 bg-gradient-to-r from-orange-50 to-transparent' 
                          : ''
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {message.meta?.draPaulaAdvice && (
                          <div className="text-orange-600 font-bold text-xs">👩‍⚕️ Dra. Paula:</div>
                        )}
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
                                  className="text-xs px-2 py-1 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                                >
                                  {action.label}
                                </button>
                              ))}
                            </div>
                          )}
                          
                          {/* Disclaimer */}
                          {message.meta?.disclaimer && (
                            <p className="mt-2 text-xs opacity-75">
                              ℹ️ Esta é uma orientação geral. Consulte um advogado para casos específicos.
                            </p>
                          )}

                          {message.meta?.draPaulaAdvice && (
                            <div className="text-xs mt-2 text-orange-700 bg-orange-100 p-2 rounded">
                              💡 **Dica da Dra. Paula B2C** - Especialista em Imigração Americana
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}

                  {achievements.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-3 rounded-lg"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Award className="h-4 w-4" />
                        <span className="font-bold text-sm">Suas Conquistas</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {achievements.map((achievement, index) => (
                          <span key={achievement} className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">
                            🏆 {index + 1}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  )}
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