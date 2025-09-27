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
import StoryTelling from "./pages/StoryTelling";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
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
          <Route path="/auto-application/case/:caseId/documents" element={<DocumentUploadAuto />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
