import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import OnboardingWizard from '../pages/OnboardingWizard';

export default function OnboardingRoute() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

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

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (user.onboarding_completed) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return (
    <OnboardingWizard
      firmName={user.firm_name}
      onComplete={() => navigate('/app/dashboard')}
    />
  );
}
