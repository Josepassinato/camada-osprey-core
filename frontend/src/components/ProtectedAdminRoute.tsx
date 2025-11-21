import { Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

interface ProtectedAdminRouteProps {
  children: React.ReactNode;
}

/**
 * ProtectedAdminRoute - Componente de proteção de rotas administrativas
 * 
 * Verifica se o usuário está autenticado e se possui role de 'admin' ou 'superadmin'
 * Caso contrário, redireciona para a página de login ou dashboard
 */
const ProtectedAdminRoute = ({ children }: ProtectedAdminRouteProps) => {
  const [isChecking, setIsChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Verificar autenticação e role do usuário
    const checkAdminAccess = () => {
      try {
        // Buscar dados do usuário do localStorage
        const userStr = localStorage.getItem('osprey_user');
        const token = localStorage.getItem('osprey_token');

        if (!userStr || !token) {
          // Usuário não está autenticado
          setIsAdmin(false);
          setIsChecking(false);
          return;
        }

        const user = JSON.parse(userStr);
        
        // Verificar se o usuário tem role de admin ou superadmin
        const userRole = user.role || 'user';
        
        if (userRole === 'admin' || userRole === 'superadmin') {
          setIsAdmin(true);
        } else {
          setIsAdmin(false);
          console.warn('Acesso negado: Usuário não possui permissões de administrador');
        }
      } catch (error) {
        console.error('Erro ao verificar permissões de admin:', error);
        setIsAdmin(false);
      } finally {
        setIsChecking(false);
      }
    };

    checkAdminAccess();
  }, []);

  // Mostrar loading enquanto verifica
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Verificando permissões...</p>
        </div>
      </div>
    );
  }

  // Se não for admin, redirecionar para dashboard
  if (!isAdmin) {
    // Mostrar mensagem de erro brevemente antes de redirecionar
    return (
      <Navigate to="/dashboard" replace />
    );
  }

  // Usuário é admin, renderizar o componente filho
  return <>{children}</>;
};

export default ProtectedAdminRoute;
