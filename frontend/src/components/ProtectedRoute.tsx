import { Navigate } from "react-router-dom";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  // Check for legacy token-based auth
  const token = localStorage.getItem('osprey_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
