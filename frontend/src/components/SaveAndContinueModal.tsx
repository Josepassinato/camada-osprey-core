import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  X,
  Save,
  Mail,
  Lock,
  Eye,
  EyeOff,
  User,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface SaveAndContinueModalProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
  currentStage: string;
  onSuccess: (userData: any) => void;
}

const SaveAndContinueModal = ({ 
  isOpen, 
  onClose, 
  caseId, 
  currentStage, 
  onSuccess 
}: SaveAndContinueModalProps) => {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const { toast } = useToast();

  const [loginData, setLoginData] = useState({
    email: "",
    password: ""
  });

  const [signupData, setSignupData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: ""
  });

  if (!isOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      const data = await response.json();

      if (response.ok) {
        // Store token and user data
        localStorage.setItem('osprey_token', data.token);
        localStorage.setItem('osprey_user', JSON.stringify(data.user));
        
        // Associate current case with user
        try {
          await associateCaseWithUser(data.token);
          
          onSuccess(data.user);
          toast({
            title: "Login realizado com sucesso!",
            description: "Sua aplicação foi salva em sua conta.",
          });
          onClose();
        } catch (associateError) {
          console.error('Association failed:', associateError);
          setError('Login realizado, mas falhou ao salvar aplicação. Por favor, tente novamente.');
        }
      } else {
        setError(data.message || 'Erro ao fazer login');
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    if (signupData.password !== signupData.confirmPassword) {
      setError('Senhas não coincidem');
      setIsLoading(false);
      return;
    }

    if (signupData.password.length < 6) {
      setError('Senha deve ter no mínimo 6 caracteres');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: signupData.name.split(' ')[0] || signupData.name,
          last_name: signupData.name.split(' ').slice(1).join(' ') || '',
          email: signupData.email,
          password: signupData.password,
          phone: ''
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store token and user data
        localStorage.setItem('osprey_token', data.token);
        localStorage.setItem('osprey_user', JSON.stringify(data.user));
        
        // Associate current case with user
        await associateCaseWithUser(data.token);
        
        onSuccess(data.user);
        toast({
          title: "Conta criada com sucesso!",
          description: "Sua aplicação foi salva em sua nova conta.",
        });
        onClose();
      } else {
        setError(data.message || 'Erro ao criar conta');
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const associateCaseWithUser = async (token: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}/associate-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_stage: currentStage,
          purchase_completed: false
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Failed to associate case:', errorData);
        throw new Error(errorData.detail || 'Failed to associate case');
      }
      
      const data = await response.json();
      console.log('✅ Case associated successfully:', data);
      return data;
    } catch (error) {
      console.error('❌ Error associating case with user:', error);
      throw error;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-black">
        <CardHeader className="bg-black text-white relative">
          <button
            onClick={onClose}
            className="absolute right-4 top-4 text-white hover:text-gray-300"
          >
            <X className="h-5 w-5" />
          </button>
          <CardTitle className="flex items-center gap-2">
            <Save className="h-5 w-5" />
            Salvar e Continuar Depois
          </CardTitle>
          <p className="text-gray-200 text-sm">
            Faça login ou crie uma conta para salvar seu progresso
          </p>
        </CardHeader>
        
        <CardContent className="p-6">
          <div className="mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-4 w-4 text-blue-600" />
                <p className="font-medium text-blue-800">Progresso atual</p>
              </div>
              <p className="text-sm text-blue-700">
                Case ID: {caseId} | Etapa: {currentStage}
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'login'
                  ? 'bg-white text-black shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Fazer Login
            </button>
            <button
              onClick={() => setActiveTab('signup')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'signup'
                  ? 'bg-white text-black shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Criar Conta
            </button>
          </div>

          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Login Form */}
          {activeTab === 'login' && (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="email"
                    name="email"
                    value={loginData.email}
                    onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                    placeholder="seu@email.com"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={loginData.password}
                    onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                    placeholder="Sua senha"
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-black hover:bg-gray-800"
                disabled={isLoading}
              >
                {isLoading ? "Fazendo login..." : "Fazer Login e Salvar"}
              </Button>
            </form>
          )}

          {/* Signup Form */}
          {activeTab === 'signup' && (
            <form onSubmit={handleSignupSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Nome Completo
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    name="name"
                    value={signupData.name}
                    onChange={(e) => setSignupData({...signupData, name: e.target.value})}
                    placeholder="Seu nome completo"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="email"
                    name="email"
                    value={signupData.email}
                    onChange={(e) => setSignupData({...signupData, email: e.target.value})}
                    placeholder="seu@email.com"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={signupData.password}
                    onChange={(e) => setSignupData({...signupData, password: e.target.value})}
                    placeholder="Mínimo 6 caracteres"
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Confirmar Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={signupData.confirmPassword}
                    onChange={(e) => setSignupData({...signupData, confirmPassword: e.target.value})}
                    placeholder="Confirme sua senha"
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-black hover:bg-gray-800"
                disabled={isLoading}
              >
                {isLoading ? "Criando conta..." : "Criar Conta e Salvar"}
              </Button>
            </form>
          )}

          <div className="mt-4 text-center text-sm text-gray-600">
            <p>✓ Sua aplicação será salva automaticamente</p>
            <p>✓ Continue de onde parou a qualquer momento</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SaveAndContinueModal;