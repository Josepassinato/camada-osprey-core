import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { 
  Languages, 
  GraduationCap,
  FileText,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

interface LanguageModeSelectorProps {
  showCard?: boolean;
  showBadge?: boolean;
  onModeChange?: (mode: 'simple' | 'technical') => void;
}

export const LanguageModeSelector: React.FC<LanguageModeSelectorProps> = ({
  showCard = true,
  showBadge = false,
  onModeChange
}) => {
  const { mode, setMode } = useLanguage();

  const handleModeChange = (newMode: 'simple' | 'technical') => {
    setMode(newMode);
    if (onModeChange) {
      onModeChange(newMode);
    }
  };

  if (showBadge) {
    // Compact badge version for header/navbar
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleModeChange(mode === 'simple' ? 'technical' : 'simple')}
        className="gap-2"
      >
        <Languages className="w-4 h-4" />
        {mode === 'simple' ? (
          <>
            <Sparkles className="w-3 h-3" />
            <span>Simples</span>
          </>
        ) : (
          <>
            <GraduationCap className="w-3 h-3" />
            <span>Técnico</span>
          </>
        )}
      </Button>
    );
  }

  if (!showCard) {
    // Inline toggle
    return (
      <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
        <Languages className="w-5 h-5 text-gray-600" />
        <div className="flex-1">
          <p className="text-sm font-medium">Modo de Linguagem</p>
          <p className="text-xs text-gray-600">
            {mode === 'simple' ? 'Explicações claras e simples' : 'Termos técnicos oficiais'}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleModeChange(mode === 'simple' ? 'technical' : 'simple')}
        >
          Trocar
        </Button>
      </div>
    );
  }

  // Full card version
  return (
    <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <Languages className="w-6 h-6 text-blue-600" />
          <CardTitle>Como você prefere?</CardTitle>
        </div>
        <CardDescription>
          Escolha o jeito que é mais fácil para você entender
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <RadioGroup
          value={mode}
          onValueChange={(value) => handleModeChange(value as 'simple' | 'technical')}
        >
          {/* Simple Mode */}
          <div className={`flex items-start space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
            mode === 'simple' 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-200 hover:border-blue-300'
          }`}>
            <RadioGroupItem value="simple" id="simple" />
            <div className="flex-1" onClick={() => handleModeChange('simple')}>
              <Label htmlFor="simple" className="flex items-center space-x-2 cursor-pointer">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-lg">Linguagem Simples</span>
                {mode === 'simple' && (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                )}
              </Label>
              <p className="text-sm text-gray-600 mt-2">
                ✓ Explicações claras e fáceis<br />
                ✓ Sem termos complicados<br />
                ✓ Exemplos do dia-a-dia<br />
                ✓ Perfeito para quem está começando
              </p>
              <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                <p className="text-xs font-medium text-gray-700 mb-1">Exemplo:</p>
                <p className="text-sm text-gray-900">"Seu nome completo"</p>
                <p className="text-xs text-gray-600 mt-1">
                  Escreva seu nome exatamente como está no seu passaporte
                </p>
              </div>
            </div>
          </div>

          {/* Technical Mode */}
          <div className={`flex items-start space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
            mode === 'technical' 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-200 hover:border-blue-300'
          }`}>
            <RadioGroupItem value="technical" id="technical" />
            <div className="flex-1" onClick={() => handleModeChange('technical')}>
              <Label htmlFor="technical" className="flex items-center space-x-2 cursor-pointer">
                <GraduationCap className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-lg">Linguagem Técnica</span>
                {mode === 'technical' && (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                )}
              </Label>
              <p className="text-sm text-gray-600 mt-2">
                ✓ Termos oficiais do USCIS<br />
                ✓ Linguagem formal<br />
                ✓ Terminologia jurídica<br />
                ✓ Para quem já conhece o processo
              </p>
              <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                <p className="text-xs font-medium text-gray-700 mb-1">Example:</p>
                <p className="text-sm text-gray-900">"Full Legal Name"</p>
                <p className="text-xs text-gray-600 mt-1">
                  As it appears on your passport
                </p>
              </div>
            </div>
          </div>
        </RadioGroup>

        {/* Current Selection Badge */}
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">
              Modo selecionado:
            </span>
          </div>
          <Badge className={mode === 'simple' ? 'bg-blue-600' : 'bg-gray-600'}>
            {mode === 'simple' ? (
              <>
                <Sparkles className="w-3 h-3 mr-1" />
                Simples
              </>
            ) : (
              <>
                <GraduationCap className="w-3 h-3 mr-1" />
                Técnico
              </>
            )}
          </Badge>
        </div>

        {/* Info */}
        <div className="text-xs text-gray-600 text-center pt-2 border-t">
          💡 Você pode mudar a qualquer momento durante o preenchimento
        </div>
      </CardContent>
    </Card>
  );
};

// Compact floating toggle button
export const LanguageModeFloatingButton: React.FC = () => {
  const { mode, toggleMode } = useLanguage();

  return (
    <button
      onClick={toggleMode}
      className="fixed bottom-4 right-4 z-50 flex items-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all"
      title="Trocar modo de linguagem"
    >
      <Languages className="w-4 h-4" />
      <span className="text-sm font-medium">
        {mode === 'simple' ? 'Simples' : 'Técnico'}
      </span>
    </button>
  );
};

export default LanguageModeSelector;
