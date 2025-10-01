import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import DocumentUpload from "./pages/DocumentUpload";
import Education from "./pages/Education";
import GuideDetail from "./pages/GuideDetail";
import InterviewSimulator from "./pages/InterviewSimulator";
import Chat from "./pages/Chat";
import Applications from "./pages/Applications";
import NewApplication from "./pages/NewApplication";
import ApplicationDetail from "./pages/ApplicationDetail";
import AutoApplicationStart from "./pages/AutoApplicationStart";
import SelectForm from "./pages/SelectForm";
import BasicData from "./pages/BasicData";
import DocumentUploadAuto from "./pages/DocumentUploadAuto";
import USCISFormFilling from "./pages/USCISFormFilling";
import AIReviewAndTranslation from "./pages/AIReviewAndTranslation";
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
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AutoApplicationStart />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/upload" element={<DocumentUpload />} />
          <Route path="/education" element={<Education />} />
          <Route path="/education/guides/:visaType" element={<GuideDetail />} />
          <Route path="/education/interview" element={<InterviewSimulator />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/applications" element={<Applications />} />
          <Route path="/applications/new" element={<NewApplication />} />
          <Route path="/applications/:applicationId" element={<ApplicationDetail />} />
          <Route path="/auto-application/start" element={<AutoApplicationStart />} />
          <Route path="/auto-application/select-form" element={<SelectForm />} />
          <Route path="/auto-application/case/:caseId/basic-data" element={<BasicData />} />
          <Route path="/auto-application/case/:caseId/friendly-form" element={<FriendlyForm />} />
          <Route path="/auto-application/case/:caseId/ai-review" element={<AIReviewAndTranslation />} />
          <Route path="/auto-application/case/:caseId/uscis-form" element={<USCISFormFilling />} />
          <Route path="/auto-application/case/:caseId/cover-letter" element={<CoverLetterModule />} />
          <Route path="/auto-application/case/:caseId/documents" element={<DocumentUploadAuto />} />
          <Route path="/auto-application/case/:caseId/story" element={<StoryTelling />} />
          <Route path="/auto-application/case/:caseId/friendly-form" element={<FriendlyForm />} />
          <Route path="/auto-application/case/:caseId/review" element={<VisualReview />} />
          <Route path="/auto-application/case/:caseId/payment" element={<PaymentAndDownload />} />
          <Route path="/auto-application/case/:caseId/finalize" element={<CaseFinalizer />} />
          {/* Owl Agent Routes */}
          <Route path="/owl-agent" element={<OwlAgent />} />
          <Route path="/owl-agent/questionnaire" element={<OwlQuestionnairePage />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
