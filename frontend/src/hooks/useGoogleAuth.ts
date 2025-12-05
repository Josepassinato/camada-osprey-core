import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const useGoogleAuth = () => {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if there's a session_id in the URL fragment
    const hash = window.location.hash;
    
    if (hash && hash.includes('session_id=')) {
      processGoogleAuth(hash);
    }
  }, []);

  const processGoogleAuth = async (hash: string) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Extract session_id from URL fragment
      const params = new URLSearchParams(hash.substring(1));
      const sessionId = params.get('session_id');

      if (!sessionId) {
        throw new Error('Session ID not found');
      }

      console.log('🔐 Processing Google OAuth session...');

      // Call Emergent Auth API to get session data
      const response = await fetch('https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data', {
        method: 'GET',
        headers: {
          'X-Session-ID': sessionId,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get session data');
      }

      const sessionData = await response.json();
      console.log('✅ Google OAuth session data received:', sessionData);

      // Now send this to our backend to create/update user and set cookie
      const backendResponse = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auth/google-callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for cookies
        body: JSON.stringify({
          session_token: sessionData.session_token,
          email: sessionData.email,
          name: sessionData.name,
          picture: sessionData.picture,
          id: sessionData.id,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error('Failed to authenticate with backend');
      }

      const userData = await backendResponse.json();
      console.log('✅ User authenticated:', userData);

      // Store user data in localStorage
      localStorage.setItem('osprey_user', JSON.stringify(userData.user));
      localStorage.setItem('osprey_token', userData.token || sessionData.session_token);

      // Clean up URL
      window.history.replaceState(null, '', window.location.pathname);

      // Redirect to dashboard
      navigate('/dashboard');
      
    } catch (err) {
      console.error('❌ Google Auth error:', err);
      setError(err instanceof Error ? err.message : 'Authentication failed');
      
      // Clean up URL on error
      window.history.replaceState(null, '', window.location.pathname);
      
      // Redirect to login after a delay
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } finally {
      setIsProcessing(false);
    }
  };

  return { isProcessing, error };
};
