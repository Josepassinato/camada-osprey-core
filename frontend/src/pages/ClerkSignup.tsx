import { SignUp } from "@clerk/clerk-react";
import { Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const ClerkSignup = () => {
  return (
    <div className="min-h-screen bg-gradient-subtle flex items-center justify-center section-padding">
      {/* Background decorations */}
      <div className="absolute inset-0">
        <div className="absolute top-20 right-20 w-72 h-72 bg-black/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-accent/5 rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-12 h-12 bg-black rounded-xl flex items-center justify-center shadow-glow">
              <Sparkles className="h-7 w-7 text-white" />
            </div>
            <div>
              <div className="text-2xl font-bold text-foreground">OSPREY</div>
              <div className="text-sm text-muted-foreground -mt-1">Immigration Platform</div>
            </div>
          </div>
          
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Create Your Account
          </h1>
          <p className="text-muted-foreground">
            Start your immigration journey today
          </p>
        </div>

        {/* Clerk Sign Up Component */}
        <div className="flex justify-center">
          <SignUp 
            routing="path"
            path="/signup"
            signInUrl="/login"
            afterSignUpUrl="/dashboard"
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "glass border-0 shadow-elegant",
              }
            }}
          />
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-muted-foreground">
          <p>
            By signing up, you agree to our{" "}
            <Link to="/terms-of-use" className="text-black hover:underline">
              Terms of Use
            </Link>{" "}
            and{" "}
            <Link to="/privacy-policy" className="text-black hover:underline">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ClerkSignup;
