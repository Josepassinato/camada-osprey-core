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
    <div className="min-h-screen bg-white flex items-center justify-center px-4 py-8">
      <div className="max-w-sm w-full text-center">
        
        {/* Hero */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-black mb-3 sm:mb-4">
          Visto Americano
        </h1>
        <p className="text-black mb-8 sm:mb-12 text-sm sm:text-base">
          IA preenche seus formulários em 3 passos
        </p>

        {/* Three Steps - Mobile Optimized */}
        <div className="space-y-4 sm:space-y-6 mb-8 sm:mb-12">
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black text-white rounded-full flex items-center justify-center text-xs sm:text-sm font-bold flex-shrink-0">1</div>
            <span className="text-left text-sm sm:text-base text-black">Conte sua história</span>
          </div>
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black text-white rounded-full flex items-center justify-center text-xs sm:text-sm font-bold flex-shrink-0">2</div>
            <span className="text-left text-sm sm:text-base text-black">IA preenche formulários</span>
          </div>
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black text-white rounded-full flex items-center justify-center text-xs sm:text-sm font-bold flex-shrink-0">3</div>
            <span className="text-left text-sm sm:text-base text-black">Baixe e envie</span>
          </div>
        </div>

        {/* Legal - Mobile Optimized */}
        <div className="mb-6 sm:mb-8 p-3 sm:p-4 bg-white border border-black rounded-lg">
          <div className="flex items-start gap-2 sm:gap-3">
            <input
              type="checkbox"
              id="terms"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="h-4 w-4 mt-0.5 accent-black border-black flex-shrink-0"
            />
            <label htmlFor="terms" className="text-xs sm:text-sm text-black text-left leading-tight">
              Ferramenta de apoio, não consultoria jurídica
            </label>
          </div>
        </div>

        {/* CTA - Mobile Optimized */}
        <Button 
          onClick={startApplication}
          disabled={!agreed || isCreating}
          className="bg-black text-white hover:bg-gray-900 active:bg-gray-900 disabled:bg-gray-400 px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg font-medium rounded-full w-full transition-colors"
        >
          {isCreating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-white mr-2"></div>
              Iniciando...
            </>
          ) : (
            <>
              Começar
              <ArrowRight className="h-4 w-4 sm:h-5 sm:w-5 ml-2" />
            </>
          )}
        </Button>

        {/* Mobile Safe Area */}
        <div className="h-4 sm:h-0"></div>
      </div>
    </div>
  );
};

export default AutoApplicationStart;