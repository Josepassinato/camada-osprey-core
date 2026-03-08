import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface B2BPrivateRouteProps {
  children: React.ReactNode;
}

export function B2BPrivateRoute({ children }: B2BPrivateRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#060d14',
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            border: '3px solid rgba(201,168,76,0.2)',
            borderTopColor: '#C9A84C',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
