import { useState } from "react";
import { useClerkAuth } from "@/hooks/useClerkAuth";
import { makeApiCall } from "@/utils/clerkApi";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

/**
 * Example component demonstrating Clerk authentication with API calls
 * 
 * This shows the recommended pattern for making authenticated API requests
 * using Clerk tokens in the Osprey platform.
 */
export function ClerkApiExample() {
  const { isSignedIn, user, getAuthToken, isLoading } = useClerkAuth();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleApiCall = async () => {
    if (!isSignedIn) {
      toast.error("Please sign in first");
      return;
    }

    setLoading(true);
    try {
      // Get Clerk token
      const token = await getAuthToken();
      
      if (!token) {
        toast.error("Failed to get authentication token");
        return;
      }

      // Make API call with Clerk token
      const response = await makeApiCall('/user/profile', {
        method: 'GET',
        clerkToken: token
      });

      setApiResponse(response);
      toast.success("API call successful!");
    } catch (error: any) {
      console.error("API call failed:", error);
      toast.error(error.message || "API call failed");
    } finally {
      setLoading(false);
    }
  };

  const handleProtectedPost = async () => {
    if (!isSignedIn) {
      toast.error("Please sign in first");
      return;
    }

    setLoading(true);
    try {
      const token = await getAuthToken();
      
      if (!token) {
        toast.error("Failed to get authentication token");
        return;
      }

      // Example POST request
      const response = await makeApiCall('/cases', {
        method: 'POST',
        clerkToken: token,
        body: {
          form_code: 'I-539',
          visa_type: 'b2',
          user_email: user?.email
        }
      });

      setApiResponse(response);
      toast.success("Case created successfully!");
    } catch (error: any) {
      console.error("API call failed:", error);
      toast.error(error.message || "Failed to create case");
    } finally {
      setLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  if (!isSignedIn) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">
            Please sign in to test API calls
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Clerk API Integration Example</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Signed in as: <strong>{user?.email}</strong>
          </p>
          <p className="text-sm text-muted-foreground">
            User ID: <code className="bg-gray-100 px-2 py-1 rounded">{user?.id}</code>
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleApiCall}
            disabled={loading}
            variant="default"
          >
            {loading ? "Loading..." : "Test GET Request"}
          </Button>

          <Button
            onClick={handleProtectedPost}
            disabled={loading}
            variant="outline"
          >
            {loading ? "Loading..." : "Test POST Request"}
          </Button>
        </div>

        {apiResponse && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">API Response:</h4>
            <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto max-h-64">
              {JSON.stringify(apiResponse, null, 2)}
            </pre>
          </div>
        )}

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">Code Example:</h4>
          <pre className="text-xs text-blue-800 overflow-auto">
{`import { useClerkAuth } from "@/hooks/useClerkAuth";
import { makeApiCall } from "@/utils/clerkApi";

function MyComponent() {
  const { getAuthToken } = useClerkAuth();

  const fetchData = async () => {
    const token = await getAuthToken();
    const data = await makeApiCall('/endpoint', {
      method: 'GET',
      clerkToken: token
    });
    return data;
  };
}`}
          </pre>
        </div>
      </CardContent>
    </Card>
  );
}
