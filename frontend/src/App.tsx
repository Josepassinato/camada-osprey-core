import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import B2BLogin from "./pages/B2BLogin";
import B2BRegister from "./pages/B2BRegister";
import B2BDashboard from "./pages/B2BDashboard";
import B2BCases from "./pages/B2BCases";
import B2BSettings from "./pages/B2BSettings";
import { B2BPrivateRoute } from "./components/B2BPrivateRoute";
import OspreyLegalChat from "./pages/OspreyLegalChat";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Root redirects to login */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Authentication */}
            <Route path="/login" element={<B2BLogin />} />
            <Route path="/register" element={<B2BRegister />} />

            {/* B2B Protected Routes */}
            <Route path="/app/dashboard" element={<B2BPrivateRoute><B2BDashboard /></B2BPrivateRoute>} />
            <Route path="/app/cases" element={<B2BPrivateRoute><B2BCases /></B2BPrivateRoute>} />
            <Route path="/app/chat" element={<B2BPrivateRoute><OspreyLegalChat /></B2BPrivateRoute>} />
            <Route path="/app/settings" element={<B2BPrivateRoute><B2BSettings /></B2BPrivateRoute>} />

            {/* Catch-all */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
