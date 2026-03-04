import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton, useUser } from "@clerk/clerk-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, CheckCircle2, Shield, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { ClerkApiExample } from "@/components/ClerkApiExample";

const ClerkDemo = () => {
  const { user } = useUser();

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="text-lg font-bold">OSPREY</div>
          </Link>

          <div className="flex items-center gap-4">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-black">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="px-4 py-2 text-sm font-medium bg-black text-white rounded-lg hover:bg-gray-800">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">
              Clerk Authentication Demo
            </h1>
            <p className="text-xl text-muted-foreground">
              Secure, modern authentication for Osprey Platform
            </p>
          </div>

          {/* Authentication Status */}
          <SignedOut>
            <Card className="mb-8 border-2 border-dashed">
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                    <Shield className="h-8 w-8 text-gray-400" />
                  </div>
                  <h3 className="text-xl font-semibold">Not Signed In</h3>
                  <p className="text-muted-foreground">
                    Sign in to see your user information and access protected features
                  </p>
                  <div className="flex gap-4 justify-center pt-4">
                    <SignInButton mode="modal">
                      <button className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 font-medium">
                        Sign In
                      </button>
                    </SignInButton>
                    <SignUpButton mode="modal">
                      <button className="px-6 py-3 border-2 border-black text-black rounded-lg hover:bg-gray-50 font-medium">
                        Sign Up
                      </button>
                    </SignUpButton>
                  </div>
                </div>
              </CardContent>
            </Card>
          </SignedOut>

          <SignedIn>
            <Card className="mb-8 border-green-200 bg-green-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-green-900 mb-2">
                      Successfully Authenticated!
                    </h3>
                    <div className="space-y-2 text-green-800">
                      <p><strong>Email:</strong> {user?.primaryEmailAddress?.emailAddress}</p>
                      <p><strong>User ID:</strong> {user?.id}</p>
                      <p><strong>Name:</strong> {user?.fullName || "Not set"}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </SignedIn>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card>
              <CardHeader>
                <Shield className="h-8 w-8 mb-2 text-blue-600" />
                <CardTitle>Secure by Default</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Enterprise-grade security with built-in protection against common vulnerabilities
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="h-8 w-8 mb-2 text-yellow-600" />
                <CardTitle>Fast Integration</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Drop-in components that work out of the box with minimal configuration
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Sparkles className="h-8 w-8 mb-2 text-purple-600" />
                <CardTitle>Great UX</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Beautiful, customizable UI components that match your brand
                </p>
              </CardContent>
            </Card>
          </div>

          {/* API Integration Example */}
          <SignedIn>
            <div className="mb-12">
              <ClerkApiExample />
            </div>
          </SignedIn>

          {/* Implementation Details */}
          <Card>
            <CardHeader>
              <CardTitle>Implementation Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Components Used:</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li><code className="bg-gray-100 px-2 py-1 rounded">ClerkProvider</code> - Wraps the entire app</li>
                  <li><code className="bg-gray-100 px-2 py-1 rounded">SignedIn</code> / <code className="bg-gray-100 px-2 py-1 rounded">SignedOut</code> - Conditional rendering</li>
                  <li><code className="bg-gray-100 px-2 py-1 rounded">SignInButton</code> / <code className="bg-gray-100 px-2 py-1 rounded">SignUpButton</code> - Auth triggers</li>
                  <li><code className="bg-gray-100 px-2 py-1 rounded">UserButton</code> - User profile menu</li>
                  <li><code className="bg-gray-100 px-2 py-1 rounded">useUser</code> - Access user data</li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Routes:</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li><Link to="/clerk-login" className="text-blue-600 hover:underline">/clerk-login</Link> - Dedicated sign-in page</li>
                  <li><Link to="/clerk-signup" className="text-blue-600 hover:underline">/clerk-signup</Link> - Dedicated sign-up page</li>
                  <li><Link to="/dashboard" className="text-blue-600 hover:underline">/dashboard</Link> - Protected route example</li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Environment Variable:</h4>
                <code className="block bg-gray-100 px-4 py-2 rounded text-sm">
                  VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
                </code>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ClerkDemo;
