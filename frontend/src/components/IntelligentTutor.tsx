import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  MessageCircle, 
  X, 
  Settings,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Star,
  TrendingUp,
  Brain,
  Target,
  Zap
} from "lucide-react";
import { makeApiCall } from "@/utils/api";

interface TutorMessage {
  id: string;
  title: string;
  message: string;
  action_type: 'explain' | 'guide' | 'validate' | 'suggest' | 'warn' | 'celebrate' | 'correct';
  personality: 'friendly' | 'professional' | 'mentor' | 'patient';
  visa_type: string;
  current_step: string;
  user_level: string;
  quick_actions: Array<{label: string; action: string}>;
  related_help: string[];
  next_steps: string[];
  priority: number;
  show_duration: number;
  can_dismiss: boolean;
  requires_action: boolean;
  timestamp: string;
}

interface UserProgress {
  user_id: string;
  visa_type: string;
  immigration_knowledge: number;
  documents_knowledge: number;
  forms_knowledge: number;
  process_knowledge: number;
  completed_steps: string[];
  common_mistakes: string[];
  successful_actions: string[];
  preferred_personality: string;
  detail_level: string;
  language_preference: string;
  total_interactions: number;
  help_requests: number;
  errors_corrected: number;
  achievements_earned: number;
}

interface IntelligentTutorProps {
  userId: string;
  visaType: string;
  currentStep: string;
  context?: Record<string, any>;
  onTutorAction?: (action: string, data?: any) => void;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  isMinimized?: boolean;
}

const IntelligentTutor: React.FC<IntelligentTutorProps> = ({
  userId,
  visaType,
  currentStep,
  context = {},
  onTutorAction,
  position = 'bottom-right',
  isMinimized = false
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentMessage, setCurrentMessage] = useState<TutorMessage | null>(null);
  const [suggestions, setSuggestions] = useState<TutorMessage[]>([]);
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showProgress, setShowProgress] = useState(false);

  // Carregar progresso do usuário
  useEffect(() => {
    loadUserProgress();
  }, [userId, visaType]);

  // Carregar sugestões proativas
  useEffect(() => {
    if (isVisible && !isMinimized) {
      loadProactiveSuggestions();
    }
  }, [currentStep, isVisible]);

  const loadUserProgress = async () => {
    try {
      const response = await makeApiCall(`/tutor/progress/${userId}/${visaType}`);
      if (response.ok) {
        const data = await response.json();
        setUserProgress(data.progress);
      }
    } catch (error) {
      console.error('Error loading user progress:', error);
    }
  };

  const loadProactiveSuggestions = async () => {
    try {
      const response = await makeApiCall(`/tutor/suggestions/${userId}/${visaType}?current_step=${currentStep}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions);
        
        // Mostrar sugestão de maior prioridade automaticamente
        if (data.suggestions.length > 0) {
          const topSuggestion = data.suggestions[0];
          setCurrentMessage(topSuggestion);
        }
      }
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const generateTutorMessage = async (actionType: string, customContext: Record<string, any> = {}) => {
    try {
      setIsLoading(true);
      
      const requestData = {
        user_id: userId,
        visa_type: visaType,
        action_type: actionType,
        context: {
          current_step: currentStep,
          ...context,
          ...customContext
        }
      };

      const response = await makeApiCall('/tutor/message', {
        method: 'POST',
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentMessage(data.message);
        setIsVisible(true);
      }
    } catch (error) {
      console.error('Error generating tutor message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    try {
      // Registrar interação
      if (currentMessage) {
        await recordInteraction(action);
      }

      // Processar ação
      if (action === 'acknowledge') {
        setCurrentMessage(null);
      } else if (action.startsWith('explain_')) {
        const concept = action.replace('explain_', '').replace('_detail', '');
        await explainConcept(concept);
      } else if (action === 'request_help') {
        await generateTutorMessage('guide');
      } else if (action === 'show_progress') {
        setShowProgress(true);
      } else if (action.startsWith('go_')) {
        const nextStep = action.replace('go_', '');
        onTutorAction?.(action, { nextStep });
      } else {
        onTutorAction?.(action);
      }
    } catch (error) {
      console.error('Error handling quick action:', error);
    }
  };

  const explainConcept = async (concept: string) => {
    try {
      const response = await makeApiCall('/tutor/explain', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          visa_type: visaType,
          concept: concept,
          context: { current_step: currentStep }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentMessage(data.tutor_message);
      }
    } catch (error) {
      console.error('Error explaining concept:', error);
    }
  };

  const recordInteraction = async (action: string) => {
    try {
      await makeApiCall('/tutor/interaction', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          message: currentMessage,
          user_action: action
        })
      });
      
      // Atualizar progresso local
      await loadUserProgress();
    } catch (error) {
      console.error('Error recording interaction:', error);
    }
  };

  const updatePreferences = async (preferences: Partial<UserProgress>) => {
    try {
      const response = await makeApiCall('/tutor/update-preferences', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          visa_type: visaType,
          preferences
        })
      });

      if (response.ok) {
        await loadUserProgress();
        setShowSettings(false);
      }
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case 'explain': return <HelpCircle className="h-4 w-4" />;
      case 'guide': return <Target className="h-4 w-4" />;
      case 'validate': return <CheckCircle2 className="h-4 w-4" />;
      case 'suggest': return <Lightbulb className="h-4 w-4" />;
      case 'warn': return <AlertTriangle className="h-4 w-4" />;
      case 'celebrate': return <Star className="h-4 w-4" />;
      case 'correct': return <Zap className="h-4 w-4" />;
      default: return <MessageCircle className="h-4 w-4" />;
    }
  };

  const getPersonalityColor = (personality: string) => {
    switch (personality) {
      case 'friendly': return 'bg-green-100 text-green-800 border-green-200';
      case 'professional': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'mentor': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'patient': return 'bg-orange-100 text-orange-800 border-orange-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const positionClasses = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4'
  };

  if (isMinimized) {
    return (
      <div className={`fixed ${positionClasses[position]} z-50`}>
        <Button
          onClick={() => setIsVisible(!isVisible)}
          className="rounded-full w-14 h-14 bg-[#FF6B35] hover:bg-[#FF6B35]/90 shadow-lg"
          size="lg"
        >
          <Brain className="h-6 w-6 text-white" />
        </Button>
        
        {suggestions.length > 0 && (
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
            <span className="text-xs text-white font-bold">{suggestions.length}</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`fixed ${positionClasses[position]} z-50 max-w-sm`}>
      {/* Botão Principal do Tutor */}
      {!isVisible && (
        <div className="relative">
          <Button
            onClick={() => setIsVisible(true)}
            className="rounded-full w-16 h-16 bg-[#FF6B35] hover:bg-[#FF6B35]/90 shadow-lg"
            size="lg"
          >
            <Brain className="h-7 w-7 text-white" />
          </Button>
          
          {suggestions.length > 0 && (
            <div className="absolute -top-2 -right-2 w-7 h-7 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
              <span className="text-sm text-white font-bold">{suggestions.length}</span>
            </div>
          )}
        </div>
      )}

      {/* Painel Principal do Tutor */}
      {isVisible && (
        <Card className="w-full shadow-xl border-2 border-[#FF6B35]/20">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-[#FF6B35] rounded-full flex items-center justify-center">
                  <Brain className="h-4 w-4 text-white" />
                </div>
                <div>
                  <CardTitle className="text-sm font-semibold text-gray-900">
                    Tutor IA {userProgress?.preferred_personality === 'friendly' ? '😊' : '🤖'}
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Nível: {userProgress && (
                      ['Iniciante', 'Intermediário', 'Avançado'][
                        Math.floor(((userProgress.immigration_knowledge + 
                                   userProgress.documents_knowledge + 
                                   userProgress.forms_knowledge + 
                                   userProgress.process_knowledge) / 4) / 34)
                      ] || 'Iniciante'
                    )}
                  </CardDescription>
                </div>
              </div>
              
              <div className="flex space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSettings(!showSettings)}
                  className="w-8 h-8 p-0"
                >
                  <Settings className="h-4 w-4" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsVisible(false)}
                  className="w-8 h-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-0">
            {/* Configurações */}
            {showSettings && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium mb-2">Personalidade do Tutor:</h4>
                <div className="grid grid-cols-2 gap-1">
                  {[
                    { key: 'friendly', label: '😊 Amigável', desc: 'Encorajador e caloroso' },
                    { key: 'professional', label: '💼 Profissional', desc: 'Direto e formal' },
                    { key: 'mentor', label: '👨‍🏫 Mentor', desc: 'Experiente e sábio' },
                    { key: 'patient', label: '🧘 Paciente', desc: 'Calmo e compreensivo' }
                  ].map((personality) => (
                    <Button
                      key={personality.key}
                      variant={userProgress?.preferred_personality === personality.key ? "default" : "outline"}
                      size="sm"
                      onClick={() => updatePreferences({ preferred_personality: personality.key })}
                      className="text-xs h-8"
                    >
                      {personality.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Progresso do Usuário */}
            {showProgress && userProgress && (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                <h4 className="text-sm font-medium mb-2 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Seu Progresso
                </h4>
                
                <div className="space-y-2">
                  {[
                    { label: 'Imigração', value: userProgress.immigration_knowledge },
                    { label: 'Documentos', value: userProgress.documents_knowledge },
                    { label: 'Formulários', value: userProgress.forms_knowledge },
                    { label: 'Processo', value: userProgress.process_knowledge }
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">{item.label}:</span>
                      <div className="flex items-center space-x-1">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-[#FF6B35] h-2 rounded-full" 
                            style={{width: `${Math.min(item.value, 100)}%`}}
                          />
                        </div>
                        <span className="text-xs font-medium w-8 text-right">{item.value}%</span>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-2 pt-2 border-t border-blue-200 text-xs text-gray-600">
                  🏆 {userProgress.achievements_earned} conquistas • 
                  💬 {userProgress.total_interactions} interações • 
                  ✅ {userProgress.errors_corrected} correções
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowProgress(false)}
                  className="w-full mt-2 text-xs"
                >
                  Fechar
                </Button>
              </div>
            )}

            {/* Mensagem Atual do Tutor */}
            {currentMessage && (
              <div className={`p-3 rounded-lg border-2 ${getPersonalityColor(currentMessage.personality)} mb-3`}>
                <div className="flex items-start space-x-2 mb-2">
                  {getActionIcon(currentMessage.action_type)}
                  <div className="flex-1">
                    <h4 className="text-sm font-medium">{currentMessage.title}</h4>
                    <div className="text-sm whitespace-pre-wrap mt-1">
                      {currentMessage.message}
                    </div>
                  </div>
                </div>
                
                {/* Ações Rápidas */}
                {currentMessage.quick_actions.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {currentMessage.quick_actions.map((action, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction(action.action)}
                        className="text-xs h-6 px-2"
                        disabled={isLoading}
                      >
                        {action.label}
                      </Button>
                    ))}
                  </div>
                )}

                {/* Próximos Passos */}
                {currentMessage.next_steps.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <div className="text-xs font-medium text-gray-600 mb-1">Próximos passos:</div>
                    <ul className="text-xs space-y-1">
                      {currentMessage.next_steps.slice(0, 3).map((step, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-[#FF6B35] mr-1">•</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Ações Rápidas do Tutor */}
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => generateTutorMessage('explain')}
                disabled={isLoading}
                className="text-xs"
              >
                <HelpCircle className="h-3 w-3 mr-1" />
                Explicar
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => generateTutorMessage('guide')}
                disabled={isLoading}
                className="text-xs"
              >
                <Target className="h-3 w-3 mr-1" />
                Guiar
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowProgress(!showProgress)}
                className="text-xs"
              >
                <TrendingUp className="h-3 w-3 mr-1" />
                Progresso
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => generateTutorMessage('suggest')}
                disabled={isLoading}
                className="text-xs"
              >
                <Lightbulb className="h-3 w-3 mr-1" />
                Sugestões
              </Button>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#FF6B35]"></div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default IntelligentTutor;