import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { makeApiCall } from "@/utils/api";
import { CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";

interface DirectiveData {
  id: string;
  pt: string;
  en: string;
  required: boolean;
}

interface VisaDirectives {
  title: string;
  directives: DirectiveData[];
  attachments_suggested: string[];
}

interface Question {
  id: number;
  question: string;
  why_needed: string;
  category: string;
  answer?: string;
}

interface ReviewResult {
  visa_type: string;
  coverage_score: number;
  status: 'complete' | 'incomplete' | 'needs_review' | 'needs_questions' | 'ready_for_formatting';
  issues?: string[];
  missing_areas?: string[];
  questions?: Question[];
  satisfied_criteria?: string[];
  revised_letter?: string | null;
  next_action: string;
}

interface FinalLetter {
  visa_type: string;
  letter_text: string;
  improvements_made: string[];
  compliance_score: number;
  ready_for_approval: boolean;
}

const CoverLetterModule: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  
  // State management
  const [currentCard, setCurrentCard] = useState(1);
  const [visaType, setVisaType] = useState<string>('');
  const [directives, setDirectives] = useState<VisaDirectives | null>(null);
  const [directivesText, setDirectivesText] = useState<string>('');
  const [userDraft, setUserDraft] = useState<string>('');
  const [review, setReview] = useState<ReviewResult | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [finalLetter, setFinalLetter] = useState<FinalLetter | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Load case data on component mount
  useEffect(() => {
    loadCaseData();
  }, [caseId]);

  const loadCaseData = async () => {
    if (!caseId) return;
    
    try {
      setLoading(true);
      const sessionToken = localStorage.getItem('osprey_session_token');
      const response = await makeApiCall(`/auto-application/case/${caseId}?session_token=${sessionToken}`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        const formCode = data.case?.form_code;
        if (formCode) {
          setVisaType(formCode);
        } else {
          setError('Tipo de visto não encontrado no caso');
        }
      }
    } catch (error) {
      console.error('Error loading case data:', error);
      setError('Erro ao carregar dados do caso');
    } finally {
      setLoading(false);
    }
  };

  // Card 1: Visa Type Selection (Auto from case)
  useEffect(() => {
    if (visaType && currentCard === 1) {
      setCurrentCard(2);
      generateDirectives();
    }
  }, [visaType]);

  // Card 2: Generate and display directives
  const generateDirectives = async () => {
    try {
      setLoading(true);
      const response = await makeApiCall('/llm/dr-paula/generate-directives', {
        method: 'POST',
        body: JSON.stringify({
          visa_type: visaType,
          language: 'pt',
          context: 'Aplicação de visto automática'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setDirectivesText(data.directives_text);
        setDirectives(data.directives_data);
      } else {
        throw new Error('Falha ao gerar diretivas');
      }
    } catch (error) {
      console.error('Error generating directives:', error);
      setError('Erro ao gerar roteiro informativo');
    } finally {
      setLoading(false);
    }
  };

  // Card 3: User writes letter
  const proceedToWriting = () => {
    setCurrentCard(3);
  };

  // Card 4: Review letter
  const reviewLetter = async () => {
    if (!userDraft.trim()) {
      setError('Por favor, escreva sua carta antes de prosseguir');
      return;
    }

    try {
      setLoading(true);
      const response = await makeApiCall('/llm/dr-paula/review-letter', {
        method: 'POST',
        body: JSON.stringify({
          visa_type: visaType,
          applicant_letter: userDraft,
          visa_profile: directives
        })
      });

      if (response.ok) {
        const data = await response.json();
        setReview(data.review);
        
        if (data.review?.status === 'ready_for_formatting') {
          // Carta satisfatória - formatar diretamente
          await formatOfficialLetter();
        } else if (data.review?.status === 'needs_questions') {
          // Carta incompleta - fazer perguntas
          setQuestions(data.review.questions || []);
          setCurrentCard(6); // Card de perguntas
        } else if (data.review?.status === 'complete') {
          setCurrentCard(5); // Complete letter (caso existente)
        } else {
          setCurrentCard(6); // Fallback para incomplete
        }
      } else {
        throw new Error('Falha ao revisar carta');
      }
    } catch (error) {
      console.error('Error reviewing letter:', error);
      setError('Erro ao revisar carta');
    } finally {
      setLoading(false);
    }
  };

  // Formatar carta no padrão oficial (quando já está satisfatória)
  const formatOfficialLetter = async () => {
    try {
      setLoading(true);
      const response = await makeApiCall('/llm/dr-paula/format-official-letter', {
        method: 'POST',
        body: JSON.stringify({
          visa_type: visaType,
          applicant_letter: userDraft,
          visa_profile: directives
        })
      });

      if (response.ok) {
        const data = await response.json();
        setFinalLetter(data.formatted_letter);
        setCurrentCard(7); // Card de aprovação final
      } else {
        throw new Error('Falha ao formatar carta');
      }
    } catch (error) {
      console.error('Error formatting letter:', error);
      setError('Erro ao formatar carta oficial');
    } finally {
      setLoading(false);
    }
  };

  // Processar respostas das perguntas e gerar carta final
  const generateFinalLetter = async () => {
    const questionsAndAnswers = questions.map(q => ({
      question: q.question,
      answer: q.answer || '',
      category: q.category
    }));

    if (questionsAndAnswers.some(qa => !qa.answer.trim())) {
      setError('Por favor, responda todas as perguntas antes de continuar');
      return;
    }

    try {
      setLoading(true);
      const response = await makeApiCall('/llm/dr-paula/generate-final-letter', {
        method: 'POST',
        body: JSON.stringify({
          visa_type: visaType,
          original_letter: userDraft,
          questions_and_answers: questionsAndAnswers,
          visa_profile: directives
        })
      });

      if (response.ok) {
        const data = await response.json();
        setFinalLetter(data.final_letter);
        setCurrentCard(7); // Card de aprovação final
      } else {
        throw new Error('Falha ao gerar carta final');
      }
    } catch (error) {
      console.error('Error generating final letter:', error);
      setError('Erro ao gerar carta final');
    } finally {
      setLoading(false);
    }
  };

  // Atualizar resposta da pergunta
  const updateAnswer = (questionId: number, answer: string) => {
    setQuestions(prev => prev.map(q => 
      q.id === questionId ? { ...q, answer } : q
    ));
  };

  // Card 5a: Complete letter confirmation
  const confirmLetter = async () => {
    // Use carta final se disponível, senão use carta revisada
    const letterToSave = finalLetter?.letter_text || review?.revised_letter;
    if (!letterToSave) return;

    try {
      setLoading(true);
      const response = await makeApiCall(`/process/${caseId}/add-letter`, {
        method: 'POST',
        body: JSON.stringify({
          letter_text: letterToSave,
          visa_type: visaType,
          confirmed_by_applicant: true
        })
      });

      if (response.ok) {
        // Navigate back to documents or next step
        navigate(`/auto-application/case/${caseId}/documents`);
      } else {
        throw new Error('Falha ao salvar carta');
      }
    } catch (error) {
      console.error('Error saving letter:', error);
      setError('Erro ao salvar carta');
    } finally {
      setLoading(false);
    }
  };

  // Card 5b: Request complement
  const requestComplement = async () => {
    if (!review?.issues) return;

    try {
      setLoading(true);
      const response = await makeApiCall('/llm/dr-paula/request-complement', {
        method: 'POST',
        body: JSON.stringify({
          visa_type: visaType,
          issues: review.issues
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Show complement request and go back to editing
        setError(data.complement_request);
        setCurrentCard(3);
      } else {
        throw new Error('Falha ao solicitar complemento');
      }
    } catch (error) {
      console.error('Error requesting complement:', error);
      setError('Erro ao solicitar complemento');
    } finally {
      setLoading(false);
    }
  };

  const goBackToEdit = () => {
    setCurrentCard(3);
    setReview(null);
  };

  if (loading && currentCard === 1) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#FF6B35]" />
          <p className="text-gray-600">Carregando informações do caso...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Carta de Apresentação</h1>
          <p className="text-gray-600 mt-2">
            Crie sua carta de apresentação com orientação da Dra. Paula B2C
          </p>
          {visaType && (
            <Badge variant="outline" className="mt-2">
              Tipo de Visto: {visaType}
            </Badge>
          )}
        </div>

        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center space-x-4">
            {[1, 2, 3, 4, 5].map((step) => (
              <div
                key={step}
                className={`flex items-center ${
                  step < 5 ? 'flex-1' : ''
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentCard >= step
                      ? 'bg-[#FF6B35] text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step}
                </div>
                {step < 5 && (
                  <div
                    className={`flex-1 h-0.5 ml-4 ${
                      currentCard > step ? 'bg-[#FF6B35]' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Error display */}
        {error && (
          <Card className="mb-6 border-red-200">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="text-red-700 whitespace-pre-wrap">{error}</div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Card 2: Display Directives */}
        {currentCard === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-[#FF6B35]" />
                <span>Roteiro Informativo - {visaType}</span>
              </CardTitle>
              <CardDescription className="text-gray-700">
                Baseado nas exigências públicas do USCIS. Use este roteiro para estruturar sua carta.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center space-x-3">
                  <Loader2 className="h-5 w-5 animate-spin text-[#FF6B35]" />
                  <span>Gerando roteiro informativo...</span>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="whitespace-pre-wrap text-gray-700">
                      {directivesText}
                    </div>
                  </div>
                  
                  {directives?.attachments_suggested && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Anexos Sugeridos:</h4>
                      <ul className="list-disc pl-5 space-y-1 text-gray-700">
                        {directives.attachments_suggested.map((attachment, index) => (
                          <li key={index}>{attachment}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <Button onClick={proceedToWriting} className="bg-[#FF6B35] hover:bg-[#FF6B35]/90">
                    Prosseguir para Redação
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Card 3: User writes letter */}
        {currentCard === 3 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-gray-900">Redija sua Carta de Apresentação</CardTitle>
              <CardDescription className="text-gray-700">
                Baseie-se no roteiro informativo para cobrir todos os pontos necessários.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Textarea
                  value={userDraft}
                  onChange={(e) => setUserDraft(e.target.value)}
                  placeholder="Escreva sua carta de apresentação aqui. Use o roteiro como guia para garantir que todos os pontos sejam cobertos..."
                  rows={15}
                  className="min-h-[400px]"
                />
                
                <div className="flex space-x-3">
                  <Button
                    onClick={reviewLetter}
                    disabled={loading || !userDraft.trim()}
                    className="bg-[#FF6B35] hover:bg-[#FF6B35]/90"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Revisando...
                      </>
                    ) : (
                      'Revisar Carta'
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => setCurrentCard(2)}
                  >
                    Ver Roteiro Novamente
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Card 5a: Complete letter */}
        {currentCard === 5 && review?.status === 'complete' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span>Carta Revisada e Finalizada</span>
              </CardTitle>
              <CardDescription className="text-gray-700">
                Sua carta foi analisada e está completa. Revise o texto final e confirme.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <span className="font-medium text-green-800">
                      Cobertura: {Math.round((review.coverage_score || 0) * 100)}%
                    </span>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Carta Final:</h4>
                  <div className="whitespace-pre-wrap text-gray-700">
                    {review.revised_letter}
                  </div>
                </div>

                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <p className="text-yellow-800 font-medium mb-2">
                    Confirmação Importante:
                  </p>
                  <p className="text-yellow-700">
                    Você confirma que estas informações são verdadeiras e fornecidas por você?
                  </p>
                </div>

                <div className="flex space-x-3">
                  <Button
                    onClick={confirmLetter}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Salvando...
                      </>
                    ) : (
                      '✅ Sim, Confirmo'
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={goBackToEdit}
                  >
                    ❌ Corrigir
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Card 6: Questions or Issues */}
        {currentCard === 6 && (review?.status === 'needs_questions' || review?.status === 'incomplete' || review?.status === 'needs_review') && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-blue-500" />
                <span>
                  {review?.status === 'needs_questions' 
                    ? 'Perguntas Específicas para Completar sua Carta' 
                    : 'Carta Precisa de Complementação'}
                </span>
              </CardTitle>
              <CardDescription className="text-gray-700">
                {review?.status === 'needs_questions'
                  ? 'Responda às perguntas abaixo para que eu possa escrever sua carta no padrão oficial de imigração.'
                  : 'Alguns pontos importantes ainda precisam ser abordados na sua carta.'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertCircle className="h-5 w-5 text-blue-500" />
                    <span className="font-medium text-blue-800">
                      Cobertura: {Math.round((review.coverage_score || 0) * 100)}%
                    </span>
                  </div>
                  {review?.missing_areas && review.missing_areas.length > 0 && (
                    <div className="mt-2">
                      <span className="text-sm text-blue-700">
                        Áreas que precisam de mais informações: {review.missing_areas.join(', ')}
                      </span>
                    </div>
                  )}
                </div>

                {/* Perguntas específicas */}
                {review?.status === 'needs_questions' && questions.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="font-medium text-blue-700 mb-3">
                      Por favor, responda às seguintes perguntas:
                    </h4>
                    {questions.map((question, index) => (
                      <Card key={question.id} className="border-blue-200">
                        <CardContent className="p-4">
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-900 mb-1">
                                {index + 1}. {question.question}
                              </label>
                              <p className="text-xs text-gray-600 mb-2">
                                💡 {question.why_needed}
                              </p>
                              <Textarea
                                value={question.answer || ''}
                                onChange={(e) => updateAnswer(question.id, e.target.value)}
                                placeholder="Digite sua resposta aqui..."
                                rows={3}
                                className="w-full"
                              />
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {/* Issues (modo antigo) */}
                {review?.issues && review.issues.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-700 mb-2">Pontos a Complementar:</h4>
                    <ul className="list-disc pl-5 space-y-1">
                      {review.issues.map((issue, index) => (
                        <li key={index} className="text-red-600">{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="flex space-x-3">
                  {review?.status === 'needs_questions' ? (
                    <Button
                      onClick={generateFinalLetter}
                      disabled={loading || questions.some(q => !q.answer?.trim())}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Escrevendo Carta Final...
                        </>
                      ) : (
                        '✍️ Escrever Carta Oficial'
                      )}
                    </Button>
                  ) : (
                    <Button
                      onClick={requestComplement}
                      disabled={loading}
                      className="bg-[#FF6B35] hover:bg-[#FF6B35]/90"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Carregando...
                        </>
                      ) : (
                        'Ver Orientações Detalhadas'
                      )}
                    </Button>
                  )}
                  
                  <Button
                    variant="outline"
                    onClick={goBackToEdit}
                  >
                    Voltar e Editar
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Card 7: Final Letter Approval */}
        {currentCard === 7 && finalLetter && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span>Carta Oficial Pronta</span>
              </CardTitle>
              <CardDescription className="text-gray-700">
                Sua carta foi formatada no padrão oficial de imigração. Revise e aprove para continuar.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span className="font-medium text-green-800">
                        Conformidade: {Math.round((finalLetter.compliance_score || 0) * 100)}%
                      </span>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Padrão Oficial
                    </Badge>
                  </div>
                  {finalLetter.improvements_made && finalLetter.improvements_made.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-green-700 font-medium">Melhorias aplicadas:</p>
                      <ul className="text-sm text-green-600 mt-1">
                        {finalLetter.improvements_made.map((improvement, index) => (
                          <li key={index}>• {improvement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Sua Carta Final:</h4>
                  <div className="bg-gray-50 p-4 rounded-lg border max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                      {finalLetter.letter_text}
                    </pre>
                  </div>
                </div>

                <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
                    <div className="text-sm text-yellow-800">
                      <p className="font-medium">Confirmação importante:</p>
                      <p>
                        Todas as informações nesta carta são verdadeiras e foram fornecidas por você. 
                        Esta carta será salva em sua pasta de documentos.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <Button
                    onClick={confirmLetter}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Salvando...
                      </>
                    ) : (
                      '✅ Aprovar e Continuar'
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => setCurrentCard(3)}
                  >
                    Voltar e Reescrever
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CoverLetterModule;