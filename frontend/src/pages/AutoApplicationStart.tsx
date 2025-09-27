import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  ArrowRight,
  CheckCircle,
  AlertTriangle,
  Clock,
  Shield,
  Zap
} from "lucide-react";

const AutoApplicationStart = () => {
  const navigate = useNavigate();
  const [agreed, setAgreed] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const startApplication = async () => {
    if (!agreed) {
      alert('Por favor, aceite os termos para continuar.');
      return;
    }

    setIsCreating(true);
    
    try {
      // Generate session token for anonymous tracking
      const sessionToken = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('osprey_session_token', sessionToken);
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_token: sessionToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Navigate to form selection with case ID
        navigate('/auto-application/select-form', { 
          state: { caseId: data.case.case_id, sessionToken } 
        });
      } else {
        throw new Error('Falha ao criar aplicação');
      }
    } catch (error) {
      console.error('Error starting application:', error);
      alert('Erro ao iniciar aplicação. Tente novamente.');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        
        {/* Hero */}
        <div className="mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-black mb-6 tracking-tight">
            Imigração
            <br />
            <span className="text-gray-600">Simplificada</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 font-light">
            Complete sua aplicação de visto americano em apenas 3 passos simples
          </p>
          
          {/* Benefits */}
          <div className="flex items-center justify-center gap-8 text-sm text-gray-500 mb-12">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>15 min</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              <span>Seguro</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <span>IA</span>
            </div>
          </div>
        </div>

        {/* Three Steps */}
        <div className="mb-16">
          <h2 className="text-2xl font-semibold text-black mb-12">Como funciona</h2>
          
          <div className="space-y-12">
            {/* Step 1 */}
            <div className="flex items-center gap-8">
              <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
                1
              </div>
              <div className="text-left">
                <h3 className="text-xl font-semibold text-black mb-2">Conte sua história</h3>
                <p className="text-gray-600">Nossa IA analisa sua situação e organiza as informações automaticamente</p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-center gap-8">
              <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
                2
              </div>
              <div className="text-left">
                <h3 className="text-xl font-semibold text-black mb-2">Formulários automáticos</h3>
                <p className="text-gray-600">Preenchemos os formulários oficiais do USCIS com suas informações</p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-center gap-8">
              <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
                3
              </div>
              <div className="text-left">
                <h3 className="text-xl font-semibold text-black mb-2">Baixe e envie</h3>
                <p className="text-gray-600">Receba tudo organizado com instruções claras para submissão</p>
              </div>
            </div>
          </div>
        </div>

        {/* What's Included - Simplified */}
        <div className="mb-12 bg-gray-50 rounded-2xl p-8">
          <h3 className="text-lg font-semibold text-black mb-6">Você recebe:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
              <span className="text-sm text-gray-700">Formulários USCIS preenchidos</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
              <span className="text-sm text-gray-700">Lista de documentos necessários</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
              <span className="text-sm text-gray-700">Instruções de submissão</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
              <span className="text-sm text-gray-700">Suporte por 30 dias</span>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer - Minimal */}
        <div className="mb-12 p-6 bg-yellow-50 border border-yellow-200 rounded-xl">
          <div className="flex items-start gap-3 text-left">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-yellow-800 font-medium mb-1">
                Ferramenta de apoio tecnológico
              </p>
              <p className="text-xs text-yellow-700">
                Esta ferramenta organiza documentos baseados nas suas informações. 
                Não constitui consultoria jurídica. Para casos complexos, consulte um advogado.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 mt-4">
            <input
              type="checkbox"
              id="terms"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="h-4 w-4 text-black focus:ring-black border-gray-300 rounded"
            />
            <label htmlFor="terms" className="text-xs text-yellow-800">
              Entendo e aceito os termos
            </label>
          </div>
        </div>

        {/* CTA */}
        <div>
          <Button 
            onClick={startApplication}
            disabled={!agreed || isCreating}
            className="bg-black text-white hover:bg-gray-800 px-12 py-4 text-lg font-medium rounded-full transition-all duration-200 transform hover:scale-105"
          >
            {isCreating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Iniciando...
              </>
            ) : (
              <>
                Começar Agora
                <ArrowRight className="h-5 w-5 ml-2" />
              </>
            )}
          </Button>
          
          <p className="text-xs text-gray-400 mt-4">
            Gratuito para começar • Pague apenas se decidir continuar
          </p>
        </div>
      </div>
    </div>
  );
};

export default AutoApplicationStart;