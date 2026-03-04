# Clerk Authentication Setup Guide

## Overview

Clerk has been integrated into the Osprey platform to provide secure, modern authentication with minimal configuration. This guide will help you set up and use Clerk authentication.

## Prerequisites

- Node.js 18+ installed
- A Clerk account (sign up at https://clerk.com)
- Access to the Osprey frontend codebase

## Step 1: Create a Clerk Application

1. Go to https://dashboard.clerk.com
2. Click "Add application" or select an existing application
3. Choose your authentication methods (Email, Google, etc.)
4. Note your application's **Publishable Key**

## Step 2: Configure Environment Variables

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Open `.env` and add your Clerk Publishable Key:
   ```bash
   VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
   ```

   **Important:** 
   - Use `pk_test_` keys for development
   - Use `pk_live_` keys for production
   - Never commit `.env` files to git

## Step 3: Install Dependencies

The Clerk React SDK has already been installed. If you need to reinstall:

```bash
cd frontend
npm install @clerk/clerk-react@latest
```

## Step 4: Start the Development Server

```bash
cd frontend
npm run dev
```

The app will be available at http://localhost:5173

## Available Routes

### Clerk Authentication Pages
- `/clerk-demo` - Interactive demo showcasing Clerk features
- `/clerk-login` - Dedicated sign-in page with Clerk UI
- `/clerk-signup` - Dedicated sign-up page with Clerk UI

### Legacy Authentication (Backward Compatible)
- `/login` - Original custom login page
- `/signup` - Original custom signup page

### Protected Routes
- `/dashboard` - Example of a protected route (requires authentication)

## Using Clerk Components

### 1. Conditional Rendering Based on Auth State

```typescript
import { SignedIn, SignedOut } from "@clerk/clerk-react";

function MyComponent() {
  return (
    <>
      <SignedOut>
        <p>Please sign in to continue</p>
      </SignedOut>
      
      <SignedIn>
        <p>Welcome! You are signed in.</p>
      </SignedIn>
    </>
  );
}
```

### 2. Sign In/Sign Up Buttons

```typescript
import { SignInButton, SignUpButton } from "@clerk/clerk-react";

function Header() {
  return (
    <div>
      <SignInButton mode="modal">
        <button>Sign In</button>
      </SignInButton>
      
      <SignUpButton mode="modal">
        <button>Sign Up</button>
      </SignUpButton>
    </div>
  );
}
```

### 3. User Profile Button

```typescript
import { UserButton } from "@clerk/clerk-react";

function Header() {
  return (
    <div>
      <UserButton afterSignOutUrl="/" />
    </div>
  );
}
```

### 4. Access User Data

```typescript
import { useUser } from "@clerk/clerk-react";

function Profile() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) return <div>Loading...</div>;

  return (
    <div>
      <p>Email: {user?.primaryEmailAddress?.emailAddress}</p>
      <p>Name: {user?.fullName}</p>
      <p>User ID: {user?.id}</p>
    </div>
  );
}
```

### 5. Protect Routes

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

## Architecture

### Files Created/Modified

**New Files:**
- `frontend/src/components/ProtectedRoute.tsx` - Route protection wrapper
- `frontend/src/components/ClerkHeader.tsx` - Header with Clerk auth buttons
- `frontend/src/pages/ClerkLogin.tsx` - Clerk sign-in page
- `frontend/src/pages/ClerkSignup.tsx` - Clerk sign-up page
- `frontend/src/pages/ClerkDemo.tsx` - Interactive demo page

**Modified Files:**
- `frontend/src/main.tsx` - Added ClerkProvider wrapper
- `frontend/src/App.tsx` - Added Clerk routes
- `frontend/.env.example` - Added VITE_CLERK_PUBLISHABLE_KEY

### ClerkProvider Configuration

The app is wrapped with `ClerkProvider` in `main.tsx`:

```typescript
<ClerkProvider 
  publishableKey={PUBLISHABLE_KEY} 
  afterSignOutUrl="/"
>
  <App />
</ClerkProvider>
```

## Customization

### Styling Clerk Components

Clerk components can be customized using the `appearance` prop:

```typescript
<SignIn 
  appearance={{
    elements: {
      rootBox: "w-full",
      card: "glass border-0 shadow-elegant",
      formButtonPrimary: "bg-black hover:bg-gray-800",
    }
  }}
/>
```

### Redirect URLs

Configure where users go after authentication:

```typescript
<SignIn 
  afterSignInUrl="/dashboard"
  afterSignUpUrl="/onboarding"
/>
```

## Backend Integration (Future)

To integrate Clerk with the FastAPI backend:

1. Install Clerk Python SDK:
   ```bash
   pip install clerk-backend-api
   ```

2. Verify JWT tokens from Clerk in your API endpoints
3. Use Clerk user IDs instead of custom user management

## Security Best Practices

✅ **DO:**
- Store Clerk keys in environment variables only
- Use `pk_test_` keys for development
- Use `pk_live_` keys for production only
- Keep `.env` files out of version control

❌ **DON'T:**
- Hardcode Clerk keys in source code
- Commit `.env` files to git
- Share publishable keys publicly (though they're safe for client-side use)
- Use test keys in production

## Troubleshooting

### "Missing Clerk Publishable Key" Error

**Problem:** App throws error on startup

**Solution:** 
1. Ensure `.env` file exists in `frontend/` directory
2. Verify `VITE_CLERK_PUBLISHABLE_KEY` is set
3. Restart the dev server after adding environment variables

### Clerk Components Not Rendering

**Problem:** Clerk components show blank or don't appear

**Solution:**
1. Check browser console for errors
2. Verify ClerkProvider is wrapping your app in `main.tsx`
3. Ensure publishable key is valid

### Authentication State Not Updating

**Problem:** `SignedIn`/`SignedOut` components don't update

**Solution:**
1. Check that ClerkProvider is at the root level
2. Verify no conflicting authentication logic
3. Clear browser cache and cookies

## Testing

Visit `/clerk-demo` to test all Clerk features:
- Sign in/sign up flows
- User profile display
- Protected route access
- Sign out functionality

## Migration from Legacy Auth

To migrate from the existing custom authentication:

1. **Phase 1:** Run both systems in parallel (current state)
   - Keep `/login` and `/signup` for existing users
   - Use `/clerk-login` and `/clerk-signup` for new users

2. **Phase 2:** Migrate existing users
   - Export user data from MongoDB
   - Import users into Clerk via API
   - Update user references in database

3. **Phase 3:** Switch to Clerk completely
   - Update all routes to use Clerk
   - Remove legacy auth code
   - Update backend to verify Clerk tokens

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk React Quickstart](https://clerk.com/docs/quickstarts/react)
- [Clerk Dashboard](https://dashboard.clerk.com)
- [Clerk Component Reference](https://clerk.com/docs/components/overview)

## Support

For issues or questions:
1. Check the [Clerk Documentation](https://clerk.com/docs)
2. Visit the [Clerk Discord](https://clerk.com/discord)
3. Review this guide's troubleshooting section
