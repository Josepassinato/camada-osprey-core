import { useState, useEffect } from "react";
import { AlertTriangle, Scale, Check, X } from "lucide-react";
import { Link } from "react-router-dom";

interface TermsAcceptanceModalProps {
  isOpen: boolean;
  onAccept: () => void;
  onDecline: () => void;
}

const TermsAcceptanceModal = ({ isOpen, onAccept, onDecline }: TermsAcceptanceModalProps) => {
  const [hasScrolledToBottom, setHasScrolledToBottom] = useState(false);
  const [privacyChecked, setPrivacyChecked] = useState(false);
  const [termsChecked, setTermsChecked] = useState(false);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollTop + clientHeight >= scrollHeight - 10) {
      setHasScrolledToBottom(true);
    }
  };

  const canAccept = hasScrolledToBottom && privacyChecked && termsChecked;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
            <Scale className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Termos de Uso e Privacidade</h2>
            <p className="text-gray-600">Por favor, leia e aceite para continuar</p>
          </div>
        </div>

        {/* Scrollable Content */}
        <div 
          className="flex-1 overflow-y-auto p-6 space-y-6"
          onScroll={handleScroll}
        >
          {/* Important Notice */}
          <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-orange-900 mb-2">⚖️ Aviso Legal Importante</h3>
                <div className="text-orange-800 text-sm space-y-2">
                  <p><strong>A OSPREY não é um escritório de advocacia</strong> e não fornece aconselhamento jurídico.</p>
                  <p>Somos uma ferramenta tecnológica para organizar e validar aplicações de imigração.</p>
                  <p>Para casos complexos, recomendamos consultar um advogado especializado.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Key Terms Summary */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Scale className="h-5 w-5" />
                Principais Termos
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Não somos advogados:</strong> OSPREY é uma plataforma tecnológica de auxílio.</p>
                </div>
                
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Sua responsabilidade:</strong> Você permanece totalmente responsável pela sua aplicação.</p>
                </div>
                
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Uso legal:</strong> Use apenas para fins legais e forneça informações precisas.</p>
                </div>
                
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Casos complexos:</strong> Recomendamos advogado para situações excepcionais.</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">🔒 Privacidade dos Dados</h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Uso temporário:</strong> Dados usados apenas durante a preparação da aplicação.</p>
                </div>
                
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Descarte seguro:</strong> Dados excluídos automaticamente após conclusão.</p>
                </div>
                
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Não compartilhamos:</strong> Seus dados nunca são vendidos ou comercializados.</p>
                </div>
                
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Criptografia:</strong> Todas as comunicações são seguras (HTTPS/SSL).</p>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Sections */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">📋 Limitações de Responsabilidade</h3>
            <div className="bg-gray-50 rounded-xl p-4 text-sm space-y-2">
              <p>• <strong>A OSPREY não fornece aconselhamento jurídico</strong></p>
              <p>• <strong>A OSPREY não decide qual tipo de visto solicitar</strong></p>
              <p>• <strong>A OSPREY não representa você perante o USCIS</strong></p>
              <p>• Todas as exigências são baseadas em instruções públicas do USCIS</p>
              <p>• <strong>Você é totalmente responsável por revisar e submeter sua aplicação</strong></p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">✅ Uso Aceitável</h3>
            <div className="bg-green-50 rounded-xl p-4 text-sm space-y-2">
              <p>Ao usar a OSPREY, você concorda em:</p>
              <p>• Usar a plataforma apenas para fins legais</p>
              <p>• Fornecer informações precisas e verdadeiras</p>
              <p>• Reconhecer que somos uma ferramenta de auxílio, não substituto de advogado</p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">🔗 Documentos Completos</h3>
            <div className="bg-blue-50 rounded-xl p-4 text-sm">
              <p className="mb-2">Para informações detalhadas, consulte os documentos completos:</p>
              <div className="space-y-1">
                <Link to="/terms-of-service" className="text-blue-600 hover:underline block">
                  → Termos de Uso Completos
                </Link>
                <Link to="/privacy-policy" className="text-blue-600 hover:underline block">
                  → Política de Privacidade Completa
                </Link>
              </div>
            </div>
          </div>

          {/* Scroll Indicator */}
          {!hasScrolledToBottom && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500 animate-pulse">
                ⬇️ Continue rolando para ler todos os termos
              </p>
            </div>
          )}
        </div>

        {/* Footer with Checkboxes and Actions */}
        <div className="p-6 border-t border-gray-200 space-y-4">
          {/* Checkboxes */}
          <div className="space-y-3">
            <label className="flex items-start gap-3 cursor-pointer group">
              <div className="relative mt-1">
                <input
                  type="checkbox"
                  checked={termsChecked}
                  onChange={(e) => setTermsChecked(e.target.checked)}
                  disabled={!hasScrolledToBottom}
                  className="sr-only"
                />
                <div className={`
                  w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                  ${termsChecked 
                    ? 'bg-blue-600 border-blue-600' 
                    : 'bg-white border-gray-300 group-hover:border-blue-400'}
                  ${!hasScrolledToBottom ? 'opacity-50' : ''}
                `}>
                  {termsChecked && <Check className="h-3 w-3 text-white" />}
                </div>
              </div>
              <span className={`text-sm ${!hasScrolledToBottom ? 'text-gray-400' : 'text-gray-700'}`}>
                Li e aceito os <Link to="/terms-of-service" className="text-blue-600 hover:underline">Termos de Uso</Link> da OSPREY
              </span>
            </label>

            <label className="flex items-start gap-3 cursor-pointer group">
              <div className="relative mt-1">
                <input
                  type="checkbox"
                  checked={privacyChecked}
                  onChange={(e) => setPrivacyChecked(e.target.checked)}
                  disabled={!hasScrolledToBottom}
                  className="sr-only"
                />
                <div className={`
                  w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                  ${privacyChecked 
                    ? 'bg-blue-600 border-blue-600' 
                    : 'bg-white border-gray-300 group-hover:border-blue-400'}
                  ${!hasScrolledToBottom ? 'opacity-50' : ''}
                `}>
                  {privacyChecked && <Check className="h-3 w-3 text-white" />}
                </div>
              </div>
              <span className={`text-sm ${!hasScrolledToBottom ? 'text-gray-400' : 'text-gray-700'}`}>
                Li e aceito a <Link to="/privacy-policy" className="text-blue-600 hover:underline">Política de Privacidade</Link> da OSPREY
              </span>
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={onDecline}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <X className="h-4 w-4" />
              Recusar
            </button>
            
            <button
              onClick={onAccept}
              disabled={!canAccept}
              className={`
                flex-1 px-6 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2
                ${canAccept
                  ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              <Check className="h-4 w-4" />
              Aceitar e Continuar
            </button>
          </div>

          <p className="text-xs text-gray-500 text-center">
            Ao aceitar, você confirma ter lido e entendido todos os termos acima
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsAcceptanceModal;