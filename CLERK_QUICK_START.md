# Clerk Quick Start Guide

Get Clerk authentication running in your Osprey platform in 5 minutes.

## Step 1: Get Your Clerk Key (2 minutes)

1. Go to https://dashboard.clerk.com
2. Sign up or log in
3. Create a new application or select existing
4. Go to **API Keys** page
5. Copy your **Publishable Key** (starts with `pk_test_`)

## Step 2: Configure Environment (1 minute)

```bash
cd frontend
echo "VITE_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE" >> .env
```

Or manually edit `frontend/.env`:

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
VITE_BACKEND_URL=http://localhost:8001
```

## Step 3: Start the App (2 minutes)

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or: . venv/bin/activate
python3 server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Step 4: Test It Out

Visit these URLs:

- **Demo Page**: http://localhost:5173/clerk-demo
- **Sign In**: http://localhost:5173/clerk-login
- **Sign Up**: http://localhost:5173/clerk-signup

## Using Clerk in Your Code

### 1. Show/Hide Content Based on Auth

```typescript
import { SignedIn, SignedOut } from "@clerk/clerk-react";

<SignedOut>
  <p>Please sign in</p>
</SignedOut>

<SignedIn>
  <p>Welcome!</p>
</SignedIn>
```

### 2. Add Sign In/Up Buttons

```typescript
import { SignInButton, SignUpButton } from "@clerk/clerk-react";

<SignInButton mode="modal">
  <button>Sign In</button>
</SignInButton>

<SignUpButton mode="modal">
  <button>Sign Up</button>
</SignUpButton>
```

### 3. Show User Profile

```typescript
import { UserButton } from "@clerk/clerk-react";

<UserButton afterSignOutUrl="/" />
```

### 4. Access User Data

```typescript
import { useUser } from "@clerk/clerk-react";

function Profile() {
  const { user } = useUser();
  return <p>Email: {user?.primaryEmailAddress?.emailAddress}</p>;
}
```

### 5. Make Authenticated API Calls

```typescript
import { useClerkAuth } from "@/hooks/useClerkAuth";
import { makeApiCall } from "@/utils/clerkApi";

function MyComponent() {
  const { getAuthToken } = useClerkAuth();

  const fetchData = async () => {
    const token = await getAuthToken();
    const data = await makeApiCall('/cases', {
      method: 'GET',
      clerkToken: token
    });
    return data;
  };
}
```

### 6. Protect Routes

```typescript
import { ProtectedRoute } from "@/components/ProtectedRoute";

// In App.tsx
<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } 
/>
```

## Troubleshooting

### "Missing Clerk Publishable Key" Error

**Fix:** Add `VITE_CLERK_PUBLISHABLE_KEY` to `frontend/.env` and restart dev server

### Clerk Components Not Showing

**Fix:** Verify ClerkProvider is in `main.tsx` wrapping the app

### 401 Unauthorized on API Calls

**Fix:** Ensure you're passing the Clerk token:
```typescript
const token = await getAuthToken();
await makeApiCall('/endpoint', { clerkToken: token });
```

## Next Steps

- Customize Clerk appearance in dashboard
- Enable social logins (Google, GitHub, etc.)
- Set up webhooks for user events
- Configure email templates
- Add multi-factor authentication

## Resources

- [Full Setup Guide](./CLERK_SETUP_GUIDE.md)
- [Clerk Dashboard](https://dashboard.clerk.com)
- [Clerk Docs](https://clerk.com/docs)
