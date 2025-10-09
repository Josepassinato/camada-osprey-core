import React, { useState, useEffect } from 'react';

interface TutorGuidanceResponse {
  success: boolean;
  guidance?: {
    guidance: string;
    personality: string;
    action: string;
    timestamp: string;
  };
}

interface TutorChecklistResponse {
  success: boolean;
  checklist?: {
    checklist: {
      required_documents: Array<{
        document: string;
        status: 'uploaded' | 'pending' | 'optional';
        description: string;
        tips: string[];
        where_to_get: string;
        validity_period: string;
        priority: 'high' | 'medium' | 'low';
      }>;
      next_priority: string;
      completion_percentage: number;
    };
  };
}

interface IntelligentTutorProps {
  currentStep?: string;
  visaType?: string;
  userId?: string;
}

const IntelligentTutor: React.FC<IntelligentTutorProps> = ({ 
  currentStep = "document_upload", 
  visaType = "h1b",
  userId 
}) => {
  // Don't render if no userId is available
  if (!userId) {
    console.log('IntelligentTutor: No userId provided, not rendering');
    return null;
  }
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'guidance' | 'checklist' | 'progress' | 'mistakes' | 'interview'>('guidance');
  const [guidance, setGuidance] = useState<string>('');
  const [checklist, setChecklist] = useState<any>(null);
  const [progressAnalysis, setProgressAnalysis] = useState<any>(null);
  const [commonMistakes, setCommonMistakes] = useState<any>(null);
  const [interviewPrep, setInterviewPrep] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const backendUrl = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  const fetchGuidance = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${backendUrl}/api/tutor/guidance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_step: currentStep,
          visa_type: visaType,
          personality: 'friendly',
          action: 'next_steps'
        })
      });

      const data: TutorGuidanceResponse = await response.json();
      
      if (data.success && data.guidance) {
        setGuidance(data.guidance.guidance);
      } else {
        setError('Não foi possível obter orientações no momento.');
      }
    } catch (err) {
      setError('Erro ao conectar com o tutor. Tente novamente.');
      console.error('Error fetching guidance:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchChecklist = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${backendUrl}/api/tutor/checklist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          visa_type: visaType
        })
      });

      const data: TutorChecklistResponse = await response.json();
      
      if (data.success && data.checklist) {
        setChecklist(data.checklist.checklist);
      } else {
        setError('Não foi possível obter checklist no momento.');
      }
    } catch (err) {
      setError('Erro ao conectar com o tutor. Tente novamente.');
      console.error('Error fetching checklist:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProgressAnalysis = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${backendUrl}/api/tutor/progress-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          visa_type: visaType
        })
      });

      const data = await response.json();
      
      if (data.success && data.analysis) {
        setProgressAnalysis(data.analysis.analysis);
      } else {
        setError('Não foi possível obter análise de progresso no momento.');
      }
    } catch (err) {
      setError('Erro ao conectar com o tutor. Tente novamente.');
      console.error('Error fetching progress analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCommonMistakes = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${backendUrl}/api/tutor/common-mistakes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_step: currentStep,
          visa_type: visaType
        })
      });

      const data = await response.json();
      
      if (data.success && data.mistakes) {
        setCommonMistakes(data.mistakes.mistakes_analysis);
      } else {
        setError('Não foi possível obter erros comuns no momento.');
      }
    } catch (err) {
      setError('Erro ao conectar com o tutor. Tente novamente.');
      console.error('Error fetching common mistakes:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchInterviewPrep = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${backendUrl}/api/tutor/interview-preparation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          visa_type: visaType
        })
      });

      const data = await response.json();
      
      if (data.success && data.preparation) {
        setInterviewPrep(data.preparation.interview_prep);
      } else {
        setError('Não foi possível obter preparação de entrevista no momento.');
      }
    } catch (err) {
      setError('Erro ao conectar com o tutor. Tente novamente.');
      console.error('Error fetching interview preparation:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isExpanded && activeTab === 'guidance' && !guidance) {
      fetchGuidance();
    }
  }, [isExpanded, activeTab, currentStep, visaType]);

  const handleTabChange = (tab: typeof activeTab) => {
    setActiveTab(tab);
    setError('');
    
    switch (tab) {
      case 'guidance':
        if (!guidance) fetchGuidance();
        break;
      case 'checklist':
        if (!checklist) fetchChecklist();
        break;
      case 'progress':
        if (!progressAnalysis) fetchProgressAnalysis();
        break;
      case 'mistakes':
        if (!commonMistakes) fetchCommonMistakes();
        break;
      case 'interview':
        if (!interviewPrep) fetchInterviewPrep();
        break;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploaded': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'optional': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg shadow-sm mb-6">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-blue-100 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <span className="text-3xl">🤖</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-blue-900">
              Assistente IA - Tutor Especializado
            </h3>
            <p className="text-sm text-blue-700">
              Orientação personalizada para seu processo de {visaType?.toUpperCase() || 'visto'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
            IA Avançada
          </span>
          <button className="text-blue-500 hover:text-blue-700 transition-colors">
            {isExpanded ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-blue-200">
          {/* Tab Navigation */}
          <div className="flex flex-wrap bg-blue-50 px-4 py-2 space-x-1">
            {[
              { key: 'guidance', label: '🎯 Orientações', emoji: '🎯' },
              { key: 'checklist', label: '📋 Checklist', emoji: '📋' },
              { key: 'progress', label: '📊 Progresso', emoji: '📊' },
              { key: 'mistakes', label: '⚠️ Evitar Erros', emoji: '⚠️' },
              { key: 'interview', label: '🎤 Entrevista', emoji: '🎤' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => handleTabChange(tab.key as typeof activeTab)}
                className={`px-3 py-2 text-sm rounded-md transition-colors ${
                  activeTab === tab.key
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-blue-700 hover:bg-blue-100'
                }`}
              >
                <span className="mr-1">{tab.emoji}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="p-4">
            {loading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-blue-700">Analisando sua situação...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <span className="text-red-400">⚠️</span>
                  <div className="ml-2">
                    <p className="text-red-800 text-sm">{error}</p>
                    <button 
                      onClick={() => handleTabChange(activeTab)}
                      className="text-red-600 hover:text-red-800 text-sm underline mt-1"
                    >
                      Tentar novamente
                    </button>
                  </div>
                </div>
              </div>
            )}

            {!loading && !error && (
              <div>
                {/* Guidance Tab */}
                {activeTab === 'guidance' && (guidance || (!loading && !error)) && (
                  <div className="bg-white rounded-lg p-4 border">
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <span className="mr-2">🎯</span>
                      Orientação Personalizada
                    </h4>
                    <div className="prose prose-blue max-w-none">
                      <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                        {guidance || 'Clique para carregar orientações personalizadas...'}
                      </p>
                      {!guidance && (
                        <button 
                          onClick={fetchGuidance}
                          className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                          Carregar Orientações
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {/* Checklist Tab */}
                {activeTab === 'checklist' && (checklist || (!loading && !error)) && (
                  <div className="bg-white rounded-lg p-4 border">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-900 flex items-center">
                        <span className="mr-2">📋</span>
                        Checklist de Documentos
                      </h4>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">Progresso</div>
                        <div className="text-lg font-bold text-blue-600">
                          {checklist?.completion_percentage || 0}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      {checklist.required_documents?.map((doc: any, index: number) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h5 className="font-medium text-gray-900">{doc.document}</h5>
                                <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(doc.status)}`}>
                                  {doc.status === 'uploaded' ? 'Carregado' : 
                                   doc.status === 'pending' ? 'Pendente' : 'Opcional'}
                                </span>
                                <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(doc.priority)}`}>
                                  {doc.priority === 'high' ? 'Alta' : 
                                   doc.priority === 'medium' ? 'Média' : 'Baixa'} Prioridade
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mb-2">{doc.description}</p>
                              <div className="text-xs text-gray-500">
                                <div><strong>Onde obter:</strong> {doc.where_to_get}</div>
                                <div><strong>Validade:</strong> {doc.validity_period}</div>
                              </div>
                              {doc.tips?.length > 0 && (
                                <div className="mt-2">
                                  <div className="text-xs font-medium text-blue-700 mb-1">💡 Dicas:</div>
                                  <ul className="text-xs text-gray-600 list-disc list-inside">
                                    {doc.tips.map((tip: string, tipIndex: number) => (
                                      <li key={tipIndex}>{tip}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {checklist.next_priority && (
                      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <h5 className="font-medium text-blue-900 mb-1">🎯 Próximo Passo Prioritário</h5>
                        <p className="text-blue-800 text-sm">{checklist.next_priority}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Progress Tab */}
                {activeTab === 'progress' && progressAnalysis && (
                  <div className="bg-white rounded-lg p-4 border">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <span className="mr-2">📊</span>
                      Análise de Progresso
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="bg-blue-50 rounded-lg p-3">
                        <div className="text-2xl font-bold text-blue-600">
                          {progressAnalysis.progress_percentage}%
                        </div>
                        <div className="text-sm text-blue-700">Progresso Geral</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3">
                        <div className="text-lg font-semibold text-green-600">
                          {progressAnalysis.current_phase}
                        </div>
                        <div className="text-sm text-green-700">Fase Atual</div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {progressAnalysis.strengths?.length > 0 && (
                        <div>
                          <h5 className="font-medium text-green-900 mb-2 flex items-center">
                            <span className="mr-2">✅</span>Pontos Fortes
                          </h5>
                          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                            {progressAnalysis.strengths.map((strength: string, index: number) => (
                              <li key={index}>{strength}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {progressAnalysis.areas_for_improvement?.length > 0 && (
                        <div>
                          <h5 className="font-medium text-yellow-900 mb-2 flex items-center">
                            <span className="mr-2">🔧</span>Áreas para Melhorar
                          </h5>
                          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                            {progressAnalysis.areas_for_improvement.map((area: string, index: number) => (
                              <li key={index}>{area}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {progressAnalysis.next_milestones?.length > 0 && (
                        <div>
                          <h5 className="font-medium text-blue-900 mb-2 flex items-center">
                            <span className="mr-2">🎯</span>Próximos Marcos
                          </h5>
                          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                            {progressAnalysis.next_milestones.map((milestone: string, index: number) => (
                              <li key={index}>{milestone}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {progressAnalysis.encouragement && (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <h5 className="font-medium text-green-900 mb-1 flex items-center">
                            <span className="mr-2">🌟</span>Mensagem Motivacional
                          </h5>
                          <p className="text-green-800 text-sm">{progressAnalysis.encouragement}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Common Mistakes Tab */}
                {activeTab === 'mistakes' && commonMistakes && (
                  <div className="bg-white rounded-lg p-4 border">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <span className="mr-2">⚠️</span>
                      Erros Comuns - {commonMistakes.step}
                    </h4>
                    
                    {commonMistakes.common_mistakes?.length > 0 && (
                      <div className="space-y-3 mb-4">
                        {commonMistakes.common_mistakes.map((mistake: any, index: number) => (
                          <div key={index} className="border border-orange-200 rounded-lg p-3 bg-orange-50">
                            <div className="flex items-start">
                              <span className="text-orange-500 mr-2 mt-0.5">
                                {mistake.severity === 'high' ? '🚨' : mistake.severity === 'medium' ? '⚠️' : '💡'}
                              </span>
                              <div className="flex-1">
                                <h5 className="font-medium text-orange-900 mb-1">{mistake.mistake}</h5>
                                <p className="text-sm text-orange-800 mb-2">{mistake.why_it_happens}</p>
                                <div className="text-sm">
                                  <div className="mb-1">
                                    <span className="font-medium text-green-700">Como evitar:</span> {mistake.how_to_avoid}
                                  </div>
                                  <div className="text-red-700">
                                    <span className="font-medium">Consequência:</span> {mistake.consequence}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {commonMistakes.prevention_tips?.length > 0 && (
                      <div className="mb-4">
                        <h5 className="font-medium text-blue-900 mb-2 flex items-center">
                          <span className="mr-2">🛡️</span>Dicas de Prevenção
                        </h5>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {commonMistakes.prevention_tips.map((tip: string, index: number) => (
                            <li key={index}>{tip}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {commonMistakes.success_strategies?.length > 0 && (
                      <div>
                        <h5 className="font-medium text-green-900 mb-2 flex items-center">
                          <span className="mr-2">🏆</span>Estratégias de Sucesso
                        </h5>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {commonMistakes.success_strategies.map((strategy: string, index: number) => (
                            <li key={index}>{strategy}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Interview Preparation Tab */}
                {activeTab === 'interview' && interviewPrep && (
                  <div className="bg-white rounded-lg p-4 border">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <span className="mr-2">🎤</span>
                      Preparação para Entrevista
                    </h4>
                    
                    {interviewPrep.day_of_interview && (
                      <div className="bg-blue-50 rounded-lg p-4 mb-4">
                        <h5 className="font-medium text-blue-900 mb-3 flex items-center">
                          <span className="mr-2">📅</span>Dia da Entrevista
                        </h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <h6 className="font-medium text-blue-800 mb-1">O que levar:</h6>
                            <ul className="list-disc list-inside text-blue-700 space-y-1">
                              {interviewPrep.day_of_interview.what_to_bring?.map((item: string, index: number) => (
                                <li key={index}>{item}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h6 className="font-medium text-blue-800 mb-1">Vestuário:</h6>
                            <p className="text-blue-700">{interviewPrep.day_of_interview.what_to_wear}</p>
                            <h6 className="font-medium text-blue-800 mb-1 mt-2">Chegada:</h6>
                            <p className="text-blue-700">{interviewPrep.day_of_interview.arrival_time}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {interviewPrep.practice_questions?.length > 0 && (
                      <div className="mb-4">
                        <h5 className="font-medium text-gray-900 mb-3 flex items-center">
                          <span className="mr-2">❓</span>Perguntas Práticas
                        </h5>
                        <div className="space-y-3">
                          {interviewPrep.practice_questions.slice(0, 3).map((question: any, index: number) => (
                            <div key={index} className="border border-gray-200 rounded-lg p-3">
                              <div className="mb-2">
                                <div className="font-medium text-gray-900">{question.question}</div>
                                <div className="text-sm text-gray-600 italic">{question.portuguese_translation}</div>
                              </div>
                              {question.good_answer_example && (
                                <div className="bg-green-50 rounded p-2 text-sm">
                                  <span className="font-medium text-green-800">Exemplo de boa resposta:</span>
                                  <p className="text-green-700 mt-1">{question.good_answer_example}</p>
                                </div>
                              )}
                              <div className="flex items-center mt-2">
                                <span className={`px-2 py-1 text-xs rounded ${
                                  question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                                  question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {question.difficulty === 'easy' ? 'Fácil' :
                                   question.difficulty === 'medium' ? 'Médio' : 'Difícil'}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {interviewPrep.confidence_boosters?.length > 0 && (
                      <div>
                        <h5 className="font-medium text-green-900 mb-2 flex items-center">
                          <span className="mr-2">💪</span>Aumente sua Confiança
                        </h5>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {interviewPrep.confidence_boosters.map((booster: string, index: number) => (
                            <li key={index}>{booster}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligentTutor;