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
      <div className="max-w-lg w-full text-center">
        
        {/* Hero */}
        <h1 className="text-4xl md:text-5xl font-bold text-black mb-4">
          Visto Americano
        </h1>
        <p className="text-gray-600 mb-12">
          IA preenche seus formulários em 3 passos
        </p>

        {/* Three Steps - Compact */}
        <div className="space-y-6 mb-12">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
            <span className="text-left">Conte sua história</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
            <span className="text-left">IA preenche formulários</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-black text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
            <span className="text-left">Baixe e envie</span>
          </div>
        </div>

        {/* Legal - Ultra Minimal */}
        <div className="mb-8 p-4 bg-gray-50 rounded-lg text-xs text-gray-600">
          <div className="flex items-center gap-2 mb-2">
            <input
              type="checkbox"
              id="terms"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="h-3 w-3"
            />
            <label htmlFor="terms">
              Ferramenta de apoio, não consultoria jurídica
            </label>
          </div>
        </div>

        {/* CTA */}
        <Button 
          onClick={startApplication}
          disabled={!agreed || isCreating}
          className="bg-black text-white hover:bg-gray-800 px-8 py-3 rounded-full w-full"
        >
          {isCreating ? 'Iniciando...' : 'Começar'}
        </Button>
      </div>
    </div>
  );
};

export default AutoApplicationStart;