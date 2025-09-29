/**
 * Dra. Paula Intelligent Tutor - Sistema de mensagens inteligentes
 * Integra o conhecimento especializado da Dra. Paula B2C no OspreyOwlTutor
 */

interface VisaSpecificMessage {
  id: string;
  visaType: string;
  step: string;
  trigger: 'onLoad' | 'onError' | 'onProgress' | 'onComplete' | 'onDocument' | 'proactive';
  severity: 'success' | 'info' | 'warning' | 'error';
  message: string;
  actions?: Array<{ label: string; event: string; payload?: any }>;
  draPaulaInsight: string;
  priority: number; // 1-10, 10 being highest
}

export class DraPaulaIntelligentTutor {
  private visaMessages: VisaSpecificMessage[] = [
    // H-1B Specific Messages
    {
      id: 'h1b_diploma_critical',
      visaType: 'H-1B',
      step: 'documents',
      trigger: 'onDocument',
      severity: 'warning',
      message: '🎓 **Diploma H-1B**: Deve ser Bachelor ou superior em área relacionada ao cargo.',
      actions: [{ label: 'Ver requisitos', event: 'help:diploma', payload: { docType: 'diploma' }}],
      draPaulaInsight: 'H-1B exige specialty occupation. Diploma deve qualificar a posição como especializada.',
      priority: 9
    },
    {
      id: 'h1b_salary_validation',
      visaType: 'H-1B',
      step: 'friendly_form',
      trigger: 'onProgress',
      severity: 'info',
      message: '💰 **Salário H-1B**: Verifique se atende o prevailing wage da região.',
      actions: [{ label: 'Calcular wage', event: 'help:wage' }],
      draPaulaInsight: 'Salário abaixo do prevailing wage pode causar rejeição da petição.',
      priority: 8
    },
    {
      id: 'h1b_lca_reminder',
      visaType: 'H-1B',
      step: 'documents',
      trigger: 'proactive',
      severity: 'warning',
      message: '📋 **LCA Obrigatória**: Empregador deve ter Labor Condition Application aprovada.',
      actions: [{ label: 'Info LCA', event: 'help:lca' }],
      draPaulaInsight: 'Sem LCA aprovada, não é possível submeter petição H-1B.',
      priority: 10
    },

    // L-1 Specific Messages  
    {
      id: 'l1_experience_requirement',
      visaType: 'L-1',
      step: 'friendly_form',
      trigger: 'onProgress',
      severity: 'warning',
      message: '⏰ **L-1 Experiência**: Necessário 1 ano contínuo nos últimos 3 anos na empresa relacionada.',
      actions: [{ label: 'Calcular tempo', event: 'help:experience' }],
      draPaulaInsight: 'Experiência deve ser em posição executiva, gerencial ou conhecimento especializado.',
      priority: 9
    },
    {
      id: 'l1_company_relationship',
      visaType: 'L-1',
      step: 'documents',
      trigger: 'onDocument',
      severity: 'error',
      message: '🏢 **Relacionamento Empresarial**: Comprove parent/subsidiary/affiliate entre empresas.',
      actions: [{ label: 'Ver documentos', event: 'help:relationship' }],
      draPaulaInsight: 'Sem relacionamento corporativo comprovado, L-1 será negado.',
      priority: 10
    },

    // O-1 Specific Messages
    {
      id: 'o1_extraordinary_ability',
      visaType: 'O-1',
      step: 'documents',
      trigger: 'onLoad',
      severity: 'info',
      message: '⭐ **Habilidade Extraordinária**: Precisa de 3+ critérios dos 8 requisitos USCIS.',
      actions: [{ label: 'Ver critérios', event: 'help:o1criteria' }],
      draPaulaInsight: 'O-1 é para top 1% da área. Evidências devem ser de excelência nacional/internacional.',
      priority: 8
    },

    // B-1/B-2 Specific Messages
    {
      id: 'b1b2_ties_critical',
      visaType: 'B-1/B-2',
      step: 'documents',
      trigger: 'onProgress',
      severity: 'warning',
      message: '🇧🇷 **Vínculos com Brasil**: Essencial demonstrar forte intenção de retorno.',
      actions: [{ label: 'Ver vínculos', event: 'help:ties' }],
      draPaulaInsight: 'Consulado avalia se você tem razões para retornar ao Brasil. Emprego, família, propriedades são cruciais.',
      priority: 9
    },
    {
      id: 'b1b2_financial_proof',
      visaType: 'B-1/B-2',
      step: 'documents', 
      trigger: 'onDocument',
      severity: 'warning',
      message: '💳 **Recursos Financeiros**: 3 meses de extratos + carta emprego + declaração IR.',
      actions: [{ label: 'Lista documentos', event: 'help:financial' }],
      draPaulaInsight: 'Recursos insuficientes são motivo #1 de negação B-1/B-2.',
      priority: 8
    },

    // F-1 Specific Messages
    {
      id: 'f1_i20_validation',
      visaType: 'F-1',
      step: 'documents',
      trigger: 'onDocument',
      severity: 'error',
      message: '🎓 **I-20 Válido**: Deve estar assinado pela escola e SEVIS fee pago.',
      actions: [{ label: 'Verificar I-20', event: 'help:i20' }],
      draPaulaInsight: 'I-20 inválido ou SEVIS fee não pago resulta em negação automática.',
      priority: 10
    },

    // Generic Proactive Messages
    {
      id: 'passport_expiry_check',
      visaType: 'ALL',
      step: 'documents',
      trigger: 'onDocument',
      severity: 'warning',
      message: '📔 **Validade Passaporte**: Deve ter pelo menos 6 meses de validade.',
      actions: [{ label: 'Verificar validade', event: 'check:passport' }],
      draPaulaInsight: 'Passaporte vencendo em menos de 6 meses pode causar problemas na entrada nos EUA.',
      priority: 7
    },
    {
      id: 'apostille_brazil_documents',
      visaType: 'ALL',
      step: 'documents',
      trigger: 'onDocument',
      severity: 'info',
      message: '✅ **Apostille Documentos BR**: Certidões brasileiras precisam de apostille da Haia.',
      actions: [{ label: 'Como apostilar', event: 'help:apostille' }],
      draPaulaInsight: 'Documentos brasileiros sem apostille não são aceitos pelo USCIS.',
      priority: 6
    },

    // Achievement/Gamification Messages
    {
      id: 'achievement_documents_complete',
      visaType: 'ALL',
      step: 'documents',
      trigger: 'onComplete',
      severity: 'success',
      message: '🏆 **Conquista Desbloqueada**: Documentos Completos! Você está 70% mais próximo do seu visto.',
      actions: [{ label: 'Próxima etapa', event: 'go:next' }],
      draPaulaInsight: 'Estatisticamente, aplicantes que completam documentos corretamente têm 85% mais chance de aprovação.',
      priority: 5
    },
    {
      id: 'achievement_perfect_form',
      visaType: 'ALL',
      step: 'friendly_form',
      trigger: 'onComplete',
      severity: 'success',
      message: '⭐ **Formulário Perfeito**: Todas as seções preenchidas sem erros! Excelente trabalho.',
      actions: [{ label: 'Processar IA', event: 'go:ai' }],
      draPaulaInsight: 'Formulários completos e precisos aceleram o processo de aprovação.',
      priority: 5
    }
  ];

  public getMessagesForContext(
    visaType: string,
    step: string,
    trigger: string,
    contextData?: any
  ): VisaSpecificMessage[] {
    return this.visaMessages
      .filter(msg => 
        (msg.visaType === visaType || msg.visaType === 'ALL') &&
        msg.step === step &&
        msg.trigger === trigger
      )
      .sort((a, b) => b.priority - a.priority)
      .slice(0, 3); // Max 3 messages at a time
  }

  public getProactiveMessages(
    visaType: string,
    step: string,
    formData?: any
  ): VisaSpecificMessage[] {
    const messages = this.getMessagesForContext(visaType, step, 'proactive');
    
    // Add contextual filtering based on form data
    if (formData && step === 'documents') {
      // Check for specific document-related proactive messages
      if (!formData.documents?.some((doc: any) => doc.id === 'passport' && doc.uploaded)) {
        messages.unshift(this.visaMessages.find(m => m.id === 'passport_expiry_check')!);
      }
    }

    return messages.slice(0, 2); // Max 2 proactive messages
  }

  public getAchievementMessage(
    visaType: string,
    step: string,
    completionData: any
  ): VisaSpecificMessage | null {
    if (step === 'documents' && completionData.allDocumentsUploaded) {
      return this.visaMessages.find(m => m.id === 'achievement_documents_complete') || null;
    }
    
    if (step === 'friendly_form' && completionData.allSectionsComplete) {
      return this.visaMessages.find(m => m.id === 'achievement_perfect_form') || null;
    }

    return null;
  }

  public convertToTutorMessage(draPaulaMessage: VisaSpecificMessage): any {
    return {
      id: draPaulaMessage.id,
      severity: draPaulaMessage.severity,
      text: `${draPaulaMessage.message}\n\n💡 **Dra. Paula**: ${draPaulaMessage.draPaulaInsight}`,
      actions: draPaulaMessage.actions || [],
      meta: {
        draPaulaAdvice: true,
        disclaimer: true
      }
    };
  }
}

// Singleton instance
export const draPaulaIntelligentTutor = new DraPaulaIntelligentTutor();