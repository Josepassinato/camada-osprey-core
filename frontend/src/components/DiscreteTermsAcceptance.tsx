import { useState } from "react";
import { AlertTriangle, Scale, ExternalLink, Check } from "lucide-react";
import { Link } from "react-router-dom";

interface DiscreteTermsAcceptanceProps {
  onAcceptanceChange: (accepted: boolean) => void;
}

const DiscreteTermsAcceptance = ({ onAcceptanceChange }: DiscreteTermsAcceptanceProps) => {
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);

  const handleTermsChange = (accepted: boolean) => {
    setTermsAccepted(accepted);
    onAcceptanceChange(accepted && privacyAccepted);
  };

  const handlePrivacyChange = (accepted: boolean) => {
    setPrivacyAccepted(accepted);
    onAcceptanceChange(termsAccepted && accepted);
  };

  return (
    <div className="bg-orange-50 border border-orange-200 rounded-xl p-6 mb-6">
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <Scale className="h-6 w-6 text-orange-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-orange-900 mb-2">
            ⚖️ Termos Legais Importantes
          </h3>
          <p className="text-orange-800 text-sm leading-relaxed">
            Antes de prosseguir, é importante que você entenda que <strong>a OSPREY é uma ferramenta tecnológica</strong> para organizar aplicações de imigração. <strong>Não somos um escritório de advocacia</strong> e não fornecemos aconselhamento jurídico.
          </p>
        </div>
      </div>

      {/* Key Points */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="space-y-3">
          <h4 className="font-semibold text-orange-900 text-sm">⚠️ O que NÃO fazemos:</h4>
          <ul className="text-xs text-orange-800 space-y-1">
            <li>• Não fornecemos aconselhamento jurídico</li>
            <li>• Não decidimos qual visto solicitar</li>
            <li>• Não representamos você no USCIS</li>
          </ul>
        </div>
        
        <div className="space-y-3">
          <h4 className="font-semibold text-orange-900 text-sm">✅ O que fazemos:</h4>
          <ul className="text-xs text-orange-800 space-y-1">
            <li>• Organizamos sua aplicação</li>
            <li>• Validamos documentos</li>
            <li>• Seguimos instruções públicas do USCIS</li>
          </ul>
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-white rounded-lg p-4 mb-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-gray-800">
              <strong>Para casos complexos ou excepcionais</strong>, recomendamos fortemente consultar um advogado de imigração licenciado antes de prosseguir.
            </p>
          </div>
        </div>
      </div>

      {/* Links to full documents */}
      <div className="bg-white rounded-lg p-4 mb-6">
        <p className="text-sm text-gray-700 mb-3">
          📄 <strong>Documentos completos disponíveis:</strong>
        </p>
        <div className="flex flex-wrap gap-4 text-sm">
          <Link 
            to="/terms-of-service" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            Termos de Uso Completos <ExternalLink className="h-3 w-3" />
          </Link>
          <Link 
            to="/privacy-policy" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            Política de Privacidade <ExternalLink className="h-3 w-3" />
          </Link>
        </div>
      </div>

      {/* Acceptance Checkboxes */}
      <div className="space-y-3">
        <label className="flex items-start gap-3 cursor-pointer group">
          <div className="relative mt-1">
            <input
              type="checkbox"
              checked={termsAccepted}
              onChange={(e) => handleTermsChange(e.target.checked)}
              className="sr-only"
            />
            <div className={`
              w-5 h-5 rounded border-2 flex items-center justify-center transition-all
              ${termsAccepted 
                ? 'bg-blue-600 border-blue-600' 
                : 'bg-white border-gray-400 group-hover:border-blue-500'}
            `}>
              {termsAccepted && <Check className="h-3 w-3 text-white" />}
            </div>
          </div>
          <span className="text-sm text-gray-800">
            <strong>Li e aceito os Termos de Uso</strong> - Entendo que a OSPREY é uma ferramenta tecnológica e não um escritório de advocacia
          </span>
        </label>

        <label className="flex items-start gap-3 cursor-pointer group">
          <div className="relative mt-1">
            <input
              type="checkbox"
              checked={privacyAccepted}
              onChange={(e) => handlePrivacyChange(e.target.checked)}
              className="sr-only"
            />
            <div className={`
              w-5 h-5 rounded border-2 flex items-center justify-center transition-all
              ${privacyAccepted 
                ? 'bg-blue-600 border-blue-600' 
                : 'bg-white border-gray-400 group-hover:border-blue-500'}
            `}>
              {privacyAccepted && <Check className="h-3 w-3 text-white" />}
            </div>
          </div>
          <span className="text-sm text-gray-800">
            <strong>Li e aceito a Política de Privacidade</strong> - Entendo como meus dados são coletados, usados e protegidos
          </span>
        </label>
      </div>

      {/* Status indicator */}
      {termsAccepted && privacyAccepted && (
        <div className="mt-4 flex items-center gap-2 text-green-700 text-sm">
          <Check className="h-4 w-4" />
          <span>Termos aceitos - você pode prosseguir</span>
        </div>
      )}
    </div>
  );
};

export default DiscreteTermsAcceptance;