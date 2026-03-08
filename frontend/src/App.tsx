import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "./contexts/LanguageContext";
import { LocaleProvider } from "./contexts/LocaleContext";
import { ProcessTypeProvider } from "./contexts/ProcessTypeContext";
import { AuthProvider } from "./contexts/AuthContext";
// BetaBanner moved to homepage only
import Index from "./pages/Index";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import B2BLogin from "./pages/B2BLogin";
import B2BRegister from "./pages/B2BRegister";
import B2BDashboard from "./pages/B2BDashboard";
import B2BCases from "./pages/B2BCases";
import { B2BPrivateRoute } from "./components/B2BPrivateRoute";
import ClerkLogin from "./pages/ClerkLogin";
import ClerkSignup from "./pages/ClerkSignup";
import ClerkDemo from "./pages/ClerkDemo";
import Dashboard from "./pages/Dashboard";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Documents from "./pages/Documents";
import DocumentUpload from "./pages/DocumentUpload";
import Education from "./pages/Education";
import GuideDetail from "./pages/GuideDetail";
import InterviewSimulator from "./pages/InterviewSimulator";
import Chat from "./pages/Chat";
import Applications from "./pages/Applications";
import NewApplication from "./pages/NewApplication";
import ApplicationDetail from "./pages/ApplicationDetail";
import NewHomepage from "./pages/NewHomepage";
import AdminKnowledgeBase from "./pages/AdminKnowledgeBase";
import RequestPackageEmail from "./pages/RequestPackageEmail";
import SelectForm from "./pages/SelectForm";
import VisaPreview from "./pages/VisaPreview";
import EmbeddedCheckout from "./pages/EmbeddedCheckout";
import BasicData from "./pages/BasicData";
import DocumentUploadAuto from "./pages/DocumentUploadAuto";
import USCISFormFilling from "./pages/USCISFormFilling";
import SystemReviewAndTranslation from "./pages/AIReviewAndTranslation";
import StoryTelling from "./pages/StoryTelling";
import FriendlyForm from "./pages/FriendlyForm";
import VisualReview from "./pages/VisualReview";
import PaymentAndDownload from "./pages/PaymentAndDownload";
import CoverLetterModule from "./pages/CoverLetterModule";
import CaseFinalizer from "./pages/CaseFinalizer";
import { OwlAgent } from "./pages/OwlAgent";
import { OwlQuestionnairePage } from "./pages/OwlQuestionnairePage";
import { OwlPaymentPage } from "./pages/OwlPaymentPage";
import { OwlPaymentSuccessPage } from "./pages/OwlPaymentSuccessPage";
import AdminVisaUpdatesPanel from "./pages/AdminVisaUpdatesPanel";
import AdminProductManagement from "./pages/AdminProductManagement";
import ProtectedAdminRoute from "./components/ProtectedAdminRoute";
// import AdaptiveFormExample from "./pages/AdaptiveFormExample"; // Temporariamente desabilitado
import ProactiveAlertsDemo from "./pages/ProactiveAlertsDemo";
import PaymentPage from "./pages/PaymentPage";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentCancel from "./pages/PaymentCancel";
import NotFound from "./pages/NotFound";
import AboutUs from "./pages/AboutUs";
import Contact from "./pages/Contact";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfUse from "./pages/TermsOfUse";
import LegalDisclaimer from "./pages/LegalDisclaimer";
import FAQ from "./pages/FAQ";
import GoogleAuthCallback from "./components/GoogleAuthCallback";
import OspreyLegalChat from "./pages/OspreyLegalChat";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <LocaleProvider>
      <LanguageProvider>
        <ProcessTypeProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <AuthProvider>
            <BrowserRouter>
            <Routes>
            {/* B2B Authentication Routes */}
            <Route path="/login" element={<B2BLogin />} />
            <Route path="/register" element={<B2BRegister />} />

            {/* B2B Protected Routes */}
            <Route path="/app/dashboard" element={<B2BPrivateRoute><B2BDashboard /></B2BPrivateRoute>} />
            <Route path="/app/cases" element={<B2BPrivateRoute><B2BCases /></B2BPrivateRoute>} />
            <Route path="/app/chat" element={<B2BPrivateRoute><OspreyLegalChat /></B2BPrivateRoute>} />

            {/* Clerk Authentication Routes */}
            <Route path="/clerk-login" element={<ClerkLogin />} />
            <Route path="/clerk-signup" element={<ClerkSignup />} />
            <Route path="/clerk-demo" element={<ClerkDemo />} />

            {/* Legacy Authentication Routes (keep for backward compatibility) */}
            <Route path="/legacy-login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/auth/google/callback" element={<GoogleAuthCallback />} />
            
            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/upload" element={<DocumentUpload />} />
          <Route path="/education" element={<Education />} />
          <Route path="/education/guides/:visaType" element={<GuideDetail />} />
          <Route path="/education/interview" element={<InterviewSimulator />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/applications" element={<Applications />} />
          <Route path="/applications/new" element={<NewApplication />} />
          <Route path="/applications/:applicationId" element={<ApplicationDetail />} />
          <Route path="/auto-application/start" element={<NewHomepage />} />
          <Route path="/" element={<NewHomepage />} />
          <Route path="/auto-application/select-form" element={<SelectForm />} />
          <Route path="/auto-application/visa-preview" element={<VisaPreview />} />
          <Route path="/checkout" element={<EmbeddedCheckout />} />
          <Route path="/auto-application/case/:caseId/basic-data" element={<BasicData />} />
          <Route path="/auto-application/case/:caseId/friendly-form" element={<FriendlyForm />} />
          <Route path="/auto-application/case/:caseId/ai-review" element={<SystemReviewAndTranslation />} />
          <Route path="/auto-application/case/:caseId/uscis-form" element={<USCISFormFilling />} />
          <Route path="/auto-application/case/:caseId/cover-letter" element={<CoverLetterModule />} />
          <Route path="/auto-application/case/:caseId/documents" element={<DocumentUploadAuto />} />
          <Route path="/auto-application/case/:caseId/story" element={<StoryTelling />} />
          <Route path="/auto-application/case/:caseId/friendly-form" element={<FriendlyForm />} />
          <Route path="/auto-application/case/:caseId/review" element={<VisualReview />} />
          <Route path="/auto-application/case/:caseId/payment" element={<PaymentAndDownload />} />
          <Route path="/auto-application/case/:caseId/finalize" element={<CaseFinalizer />} />
          {/* Payment Routes */}
          <Route path="/payment" element={<PaymentPage />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/payment/cancel" element={<PaymentCancel />} />
          {/* Owl Agent Routes */}
          <Route path="/owl-agent" element={<OwlAgent />} />
          <Route path="/owl-agent/questionnaire" element={<OwlQuestionnairePage />} />
          <Route path="/owl-agent/payment" element={<OwlPaymentPage />} />
          <Route path="/owl-agent/payment-success" element={<OwlPaymentSuccessPage />} />
          {/* Admin Panel Routes - PROTECTED */}
          <Route path="/admin/visa-updates" element={
            <ProtectedAdminRoute>
              <AdminVisaUpdatesPanel />
            </ProtectedAdminRoute>
          } />
          <Route path="/admin/knowledge-base" element={
            <ProtectedAdminRoute>
              <AdminKnowledgeBase />
            </ProtectedAdminRoute>
          } />
          <Route path="/admin/products" element={
            <ProtectedAdminRoute>
              <AdminProductManagement />
            </ProtectedAdminRoute>
          } />
          
          {/* Request Package Email */}
          <Route path="/request-package-email/:caseId" element={<RequestPackageEmail />} />
          {/* Demo/Example Routes */}
          {/* <Route path="/demo/adaptive-language" element={<AdaptiveFormExample />} /> */}
          <Route path="/demo/proactive-alerts" element={<ProactiveAlertsDemo />} />
          
          {/* Static Pages Routes */}
          <Route path="/about" element={<AboutUs />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/terms-of-use" element={<TermsOfUse />} />
          <Route path="/legal-disclaimer" element={<LegalDisclaimer />} />
          
          {/* Osprey Legal Chat */}
          <Route path="/legal-chat" element={<OspreyLegalChat />} />

          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </TooltipProvider>
    </ProcessTypeProvider>
    </LanguageProvider>
    </LocaleProvider>
  </QueryClientProvider>
);

export default App;
