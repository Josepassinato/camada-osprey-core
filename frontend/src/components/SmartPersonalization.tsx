import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Brain, Target, TrendingUp, Award, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useUserGuidanceHistory } from '@/hooks/useUserGuidanceHistory';

interface PersonalizationEngine {
  userProfile: any;
  visaType: string;
  currentStep: string;
  formData?: any;
}

export class SmartPersonalizationEngine {
  
  static generateSmartSuggestions(context: PersonalizationEngine): Array<{
    id: string;
    type: 'document' | 'form_field' | 'process_tip' | 'deadline_alert';
    priority: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    action?: string;
    dueDate?: Date;
  }> {
    const suggestions: any[] = [];
    const { userProfile, visaType, currentStep, formData } = context;

    // Document suggestions based on visa type and profile
    if (currentStep === 'documents') {
      if (visaType === 'H-1B') {
        // Check if user has uploaded diploma
        if (!formData?.documents?.some((doc: any) => doc.id === 'diploma' && doc.uploaded)) {
          suggestions.push({
            id: 'h1b_diploma_missing',
            type: 'document',
            priority: 'high',
            title: '🎓 Diploma Universitário Pendente',
            description: 'Para H-1B, o diploma de Bachelor ou superior é OBRIGATÓRIO. Sem ele, a petição será rejeitada.',
            action: 'upload_diploma',
            dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
          });
        }

        // Smart suggestion based on user's education background
        if (userProfile?.basicData?.education?.includes('mestrado') || userProfile?.basicData?.education?.includes('master')) {
          suggestions.push({
            id: 'h1b_advanced_degree',
            type: 'process_tip',
            priority: 'medium',
            title: '🏆 Vantagem: Diploma Avançado',
            description: 'Seu mestrado/doutorado pode qualificar para H-1B cap exemption ou master\'s cap. Destaque isso na petição!',
            action: 'highlight_advanced_degree'
          });
        }
      }

      if (visaType === 'L-1') {
        suggestions.push({
          id: 'l1_experience_validation',
          type: 'process_tip',
          priority: 'high',
          title: '⏰ Validar Experiência L-1',
          description: 'Confirme que tem pelo menos 1 ano contínuo na empresa nos últimos 3 anos. Documente datas exatas.',
          action: 'validate_experience'
        });
      }
    }

    // Form field suggestions based on common errors
    if (currentStep === 'friendly_form') {
      if (userProfile?.commonErrors?.includes('friendly_form_date_of_birth')) {
        suggestions.push({
          id: 'date_format_reminder',
          type: 'form_field',
          priority: 'medium',
          title: '📅 Formato de Data Correto',
          description: 'Lembre-se: use MM/DD/YYYY para datas em formulários americanos. Você teve dificuldade com isso antes.',
          action: 'focus_date_field'
        });
      }

      // Smart suggestion based on incomplete sections
      if (formData?.sections) {
        const incompleteSection = formData.sections.find((s: any) => !s.completed && s.required);
        if (incompleteSection) {
          suggestions.push({
            id: `complete_section_${incompleteSection.id}`,
            type: 'form_field',
            priority: 'high',
            title: `📝 Completar: ${incompleteSection.title}`,
            description: 'Esta seção é obrigatória e ainda não está completa. Finalize para continuar.',
            action: `focus_section_${incompleteSection.id}`
          });
        }
      }
    }

    // Deadline alerts based on visa type
    const deadlineAlerts = this.generateDeadlineAlerts(visaType, currentStep);
    suggestions.push(...deadlineAlerts);

    // Personalized tips based on learning progress
    if (userProfile?.learningProgress) {
      const personalizedTips = this.generatePersonalizedLearningTips(userProfile.learningProgress, currentStep);
      suggestions.push(...personalizedTips);
    }

    return suggestions.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  static generateDeadlineAlerts(visaType: string, currentStep: string): Array<any> {
    const alerts: any[] = [];
    const now = new Date();

    if (visaType === 'H-1B' && currentStep !== 'completed') {
      // H-1B cap season alert
      const capDate = new Date(now.getFullYear() + 1, 3, 1); // April 1st next year
      const daysToCapSeason = Math.ceil((capDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      
      if (daysToCapSeason <= 90 && daysToCapSeason > 0) {
        alerts.push({
          id: 'h1b_cap_season_alert',
          type: 'deadline_alert',
          priority: 'high',
          title: '🚨 H-1B Cap Season Aproximando',
          description: `Faltam ${daysToCapSeason} dias para o período de submissão H-1B. Acelere seu processo!`,
          dueDate: capDate,
          action: 'expedite_process'
        });
      }
    }

    if (visaType === 'F-1') {
      // SEVIS fee reminder
      alerts.push({
        id: 'f1_sevis_fee_reminder',
        type: 'deadline_alert',
        priority: 'high',
        title: '💳 SEVIS Fee Obrigatória',
        description: 'Não esqueça de pagar a taxa SEVIS ($350) pelo menos 3 dias antes da entrevista consular.',
        action: 'pay_sevis_fee'
      });
    }

    return alerts;
  }

  static generatePersonalizedLearningTips(learningProgress: any, currentStep: string): Array<any> {
    const tips: any[] = [];

    if (learningProgress.documentsKnowledge < 50 && currentStep === 'documents') {
      tips.push({
        id: 'documents_learning_tip',
        type: 'process_tip',
        priority: 'low',
        title: '📚 Dica de Aprendizado',
        description: 'Você está aprendendo sobre documentos. Cada documento tem requisitos específicos - leia as dicas da Dra. Paula!',
        action: 'show_document_guide'
      });
    }

    if (learningProgress.formsKnowledge > 80) {
      tips.push({
        id: 'forms_expert_tip',
        type: 'process_tip',
        priority: 'low',
        title: '🏆 Expert em Formulários!',
        description: 'Você domina o preenchimento de formulários. Considere ajudar outros usuários na comunidade.',
        action: 'join_community'
      });
    }

    return tips;
  }

  static getPersonalizedGreeting(userProfile: any, visaType: string): string {
    const name = userProfile?.basicData?.firstName || 'Aplicante';
    const timeOfDay = new Date().getHours();
    let greeting = '';

    if (timeOfDay < 12) {
      greeting = 'Bom dia';
    } else if (timeOfDay < 18) {
      greeting = 'Boa tarde';
    } else {
      greeting = 'Boa noite';
    }

    const visaExperience = userProfile?.visaHistory?.length || 0;
    let experienceNote = '';
    
    if (visaExperience === 0) {
      experienceNote = 'Vejo que esta é sua primeira aplicação de visto americano.';
    } else if (visaExperience === 1) {
      experienceNote = 'Vejo que você já tem experiência com vistos americanos.';
    } else {
      experienceNote = `Impressionante! Você já tem experiência com ${visaExperience} tipos de vistos.`;
    }

    return `${greeting}, ${name}! ${experienceNote} Vamos trabalhar juntos no seu ${visaType}! 🚀`;
  }

  static generateProgressMilestones(visaType: string, completedSteps: string[]): Array<{
    id: string;
    title: string;
    description: string;
    completed: boolean;
    progress: number;
    estimatedTime?: string;
  }> {
    const allSteps = [
      { id: 'basic_data', title: 'Dados Básicos', description: 'Informações pessoais coletadas' },
      { id: 'documents', title: 'Upload de Documentos', description: 'Documentos necessários enviados e validados' },
      { id: 'friendly_form', title: 'Formulário Amigável', description: 'Informações detalhadas preenchidas' },
      { id: 'ai_review', title: 'Processamento do Sistema', description: 'Sistema revisa e traduz suas informações' },
      { id: 'uscis_form', title: 'Formulário Oficial', description: 'Revisão e autorização do formulário USCIS' },
      { id: 'payment', title: 'Pagamento', description: 'Pagamento processado e documentos gerados' }
    ];

    return allSteps.map((step, index) => {
      const isCompleted = completedSteps.includes(step.id);
      const progress = isCompleted ? 100 : (completedSteps.length > index ? 50 : 0);
      
      // Estimated time based on visa type and step
      let estimatedTime = '';
      if (!isCompleted) {
        switch (step.id) {
          case 'documents':
            estimatedTime = visaType === 'H-1B' ? '30-60 min' : '20-40 min';
            break;
          case 'friendly_form':
            estimatedTime = '15-25 min';
            break;
          case 'ai_review':
            estimatedTime = '5-10 min';
            break;
          case 'uscis_form':
            estimatedTime = '10-15 min';
            break;
          case 'payment':
            estimatedTime = '5 min';
            break;
          default:
            estimatedTime = '10 min';
        }
      }

      return {
        ...step,
        completed: isCompleted,
        progress,
        estimatedTime: isCompleted ? undefined : estimatedTime
      };
    });
  }
}

interface SmartPersonalizationProps {
  visaType: string;
  currentStep: string;
  formData?: any;
  className?: string;
}

export const SmartPersonalization: React.FC<SmartPersonalizationProps> = ({
  visaType,
  currentStep,
  formData,
  className = ''
}) => {
  const { userProfile, getPersonalizedTips, addGuidanceRecord } = useUserGuidanceHistory({
    visaType,
    enablePersonalization: true
  });

  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [milestones, setMilestones] = useState<any[]>([]);
  const [personalizedGreeting, setPersonalizedGreeting] = useState<string>('');

  useEffect(() => {
    if (userProfile) {
      // Generate smart suggestions
      const smartSuggestions = SmartPersonalizationEngine.generateSmartSuggestions({
        userProfile,
        visaType,
        currentStep,
        formData
      });
      setSuggestions(smartSuggestions);

      // Generate progress milestones
      const progressMilestones = SmartPersonalizationEngine.generateProgressMilestones(
        visaType,
        userProfile.completedSteps || []
      );
      setMilestones(progressMilestones);

      // Generate personalized greeting
      const greeting = SmartPersonalizationEngine.getPersonalizedGreeting(userProfile, visaType);
      setPersonalizedGreeting(greeting);
    }
  }, [userProfile, visaType, currentStep, formData]);

  const handleSuggestionAction = (suggestion: any) => {
    // Record that user interacted with suggestion
    addGuidanceRecord(
      'tip',
      `Usuário interagiu com sugestão: ${suggestion.title}`,
      'system',
      currentStep,
      { suggestionId: suggestion.id, action: suggestion.action }
    );

    // Handle specific actions
    switch (suggestion.action) {
      case 'upload_diploma':
        document.getElementById('upload-diploma')?.scrollIntoView({ behavior: 'smooth' });
        break;
      case 'focus_date_field':
        document.getElementById('date_of_birth')?.focus();
        break;
      // Add more action handlers as needed
    }
  };

  if (!userProfile) return null;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Personalized Greeting */}
      {personalizedGreeting && (
        <Card className="border-orange-200 bg-gradient-to-r from-orange-50 to-white">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-orange-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-800">{personalizedGreeting}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Smart Suggestions */}
      {suggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Brain className="h-4 w-4" />
              Sugestões Inteligentes
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {suggestions.slice(0, 3).map((suggestion) => (
              <motion.div
                key={suggestion.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg border-l-4 ${
                  suggestion.priority === 'high' 
                    ? 'border-red-400 bg-red-50' 
                    : suggestion.priority === 'medium'
                    ? 'border-orange-400 bg-orange-50'
                    : 'border-blue-400 bg-blue-50'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-800">
                      {suggestion.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {suggestion.description}
                    </p>
                    {suggestion.dueDate && (
                      <div className="flex items-center gap-1 mt-2">
                        <Clock className="h-3 w-3 text-orange-600" />
                        <span className="text-xs text-orange-600">
                          Prazo: {suggestion.dueDate.toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${
                        suggestion.priority === 'high' 
                          ? 'border-red-400 text-red-600'
                          : suggestion.priority === 'medium'
                          ? 'border-orange-400 text-orange-600'
                          : 'border-blue-400 text-blue-600'
                      }`}
                    >
                      {suggestion.priority === 'high' ? 'Urgente' : 
                       suggestion.priority === 'medium' ? 'Importante' : 'Dica'}
                    </Badge>
                    {suggestion.action && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs h-6"
                        onClick={() => handleSuggestionAction(suggestion)}
                      >
                        Ação
                      </Button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Progress Milestones */}
      {milestones.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Target className="h-4 w-4" />
              Seu Progresso no {visaType}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {milestones.map((milestone, index) => (
                <div key={milestone.id} className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                    milestone.completed 
                      ? 'bg-green-100 text-green-600' 
                      : milestone.progress > 0
                      ? 'bg-orange-100 text-orange-600'
                      : 'bg-gray-100 text-gray-400'
                  }`}>
                    {milestone.completed ? '✓' : index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className={`text-sm ${
                        milestone.completed ? 'text-green-600 font-medium' : 'text-gray-700'
                      }`}>
                        {milestone.title}
                      </span>
                      {milestone.estimatedTime && (
                        <span className="text-xs text-gray-500">
                          ⏱️ {milestone.estimatedTime}
                        </span>
                      )}
                    </div>
                    {milestone.progress > 0 && milestone.progress < 100 && (
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div 
                          className="bg-orange-500 h-1.5 rounded-full transition-all"
                          style={{ width: `${milestone.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SmartPersonalization;