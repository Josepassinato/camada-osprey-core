# Clerk Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "cannot_render_single_session_enabled" Error

**Error Message:**
```
Clerk: 🔒 The SignIn or SignUp modals do not render when a user is already signed in, 
unless the application allows multiple sessions. Since a user is signed in and this 
application only allows a single session, this is no-op.
```

**Cause:**
You're trying to open the SignIn modal while already signed in. Clerk prevents this by default.

**Solution:**
Wrap `SignInButton` with `<SignedOut>` component to only show it when user is not signed in:

```tsx
// ❌ WRONG - Will error if user is signed in
<SignInButton mode="modal">
  <button>Entrar</button>
</SignInButton>

// ✅ CORRECT - Only shows when signed out
<SignedOut>
  <SignInButton mode="modal">
    <button>Entrar</button>
  </SignInButton>
</SignedOut>

<SignedIn>
  <button onClick={() => navigate('/dashboard')}>Dashboard</button>
  <UserButton />
</SignedIn>
```

**Status:** ✅ Fixed in latest update

---

### Issue 2: "Missing Clerk Publishable Key" Error

**Error Message:**
```
Missing Clerk Publishable Key. Add VITE_CLERK_PUBLISHABLE_KEY to your .env file
```

**Cause:**
Environment variable not set or dev server not restarted after adding it.

**Solution:**
1. Add to `frontend/.env`:
   ```bash
   VITE_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
   ```

2. Restart dev server:
   ```bash
   npm run dev
   ```

---

### Issue 3: Clerk Components Not Rendering

**Symptoms:**
- Blank space where Clerk components should be
- No sign-in button visible
- UserButton not showing

**Possible Causes & Solutions:**

**A. ClerkProvider Not Wrapping App**

Check `main.tsx`:
```tsx
// ✅ CORRECT
<ClerkProvider publishableKey={PUBLISHABLE_KEY}>
  <App />
</ClerkProvider>

// ❌ WRONG - Missing ClerkProvider
<App />
```

**B. Invalid Publishable Key**

- Verify key starts with `pk_test_` (development) or `pk_live_` (production)
- Check for typos or extra spaces
- Get fresh key from https://dashboard.clerk.com

**C. Browser Console Errors**

Open browser DevTools (F12) and check Console tab for errors.

---

### Issue 4: Sign-In Modal Not Opening

**Symptoms:**
- Click "Entrar" button but nothing happens
- No modal appears

**Solutions:**

**A. Check if Already Signed In**
- Look for UserButton in header
- If signed in, sign out first to test sign-in flow
- Or use incognito/private browsing mode

**B. Check Browser Console**
- Look for JavaScript errors
- Check Network tab for failed requests

**C. Verify Button Implementation**
```tsx
// ✅ CORRECT
<SignInButton mode="modal">
  <button>Entrar</button>
</SignInButton>

// ❌ WRONG - Missing mode prop
<SignInButton>
  <button>Entrar</button>
</SignInButton>
```

---

### Issue 5: UserButton Not Showing After Sign-In

**Symptoms:**
- Successfully signed in
- But UserButton doesn't appear

**Solution:**

Ensure `<SignedIn>` wrapper is present:
```tsx
<SignedIn>
  <UserButton afterSignOutUrl="/" />
</SignedIn>
```

Check if component is inside ClerkProvider scope.

---

### Issue 6: Redirect Not Working After Sign-In

**Symptoms:**
- Sign in successful
- But stays on same page instead of redirecting

**Solution:**

Set redirect URLs in SignIn component:
```tsx
<SignIn 
  afterSignInUrl="/dashboard"
  afterSignUpUrl="/dashboard"
/>
```

Or in ClerkProvider:
```tsx
<ClerkProvider 
  publishableKey={PUBLISHABLE_KEY}
  afterSignInUrl="/dashboard"
  afterSignOutUrl="/"
>
```

---

### Issue 7: Styling Issues with Clerk Components

**Symptoms:**
- Clerk components look different than expected
- Colors don't match your brand

**Solution:**

Use `appearance` prop to customize:
```tsx
<UserButton 
  appearance={{
    elements: {
      avatarBox: "w-10 h-10",
      userButtonPopoverCard: "shadow-xl",
      userButtonPopoverActionButton: "hover:bg-purple-50"
    }
  }}
/>
```

For SignIn/SignUp pages:
```tsx
<SignIn 
  appearance={{
    elements: {
      rootBox: "w-full",
      card: "shadow-2xl border-2 border-purple-200",
      formButtonPrimary: "bg-purple-600 hover:bg-purple-700"
    }
  }}
/>
```

---

### Issue 8: Multiple Sessions Error

**Error Message:**
```
This application does not support multiple sessions
```

**Cause:**
Trying to sign in with different account while already signed in.

**Solution:**

**Option A:** Sign out first, then sign in with new account

**Option B:** Enable multiple sessions in Clerk Dashboard:
1. Go to https://dashboard.clerk.com
2. Select your application
3. Go to Settings → Sessions
4. Enable "Allow multiple sessions"

---

### Issue 9: CORS Errors

**Error Message:**
```
Access to fetch at 'https://clerk.accounts.dev/...' has been blocked by CORS policy
```

**Cause:**
Incorrect domain configuration in Clerk Dashboard.

**Solution:**
1. Go to Clerk Dashboard → Settings → Domains
2. Add your development domain: `http://localhost:5173`
3. Add your production domain when deploying

---

### Issue 10: Session Not Persisting

**Symptoms:**
- Sign in successfully
- Refresh page → Signed out again

**Possible Causes:**

**A. Cookies Blocked**
- Check browser settings
- Ensure cookies are enabled
- Try different browser

**B. Localhost Issues**
- Clear browser cache and cookies
- Try `127.0.0.1:5173` instead of `localhost:5173`

**C. Development Mode**
- This is normal in development
- Production will persist sessions properly

---

## Debugging Checklist

When facing issues, check these in order:

1. ✅ Environment variable set: `VITE_CLERK_PUBLISHABLE_KEY`
2. ✅ Dev server restarted after adding env var
3. ✅ ClerkProvider wrapping App in `main.tsx`
4. ✅ Browser console shows no errors
5. ✅ Network tab shows successful Clerk API calls
6. ✅ Using correct Clerk components (`SignedIn`, `SignedOut`, etc.)
7. ✅ Publishable key is valid (starts with `pk_test_` or `pk_live_`)
8. ✅ Clerk Dashboard shows application is active

---

## Getting Help

If issues persist:

1. **Check Browser Console**
   - Open DevTools (F12)
   - Look for red errors
   - Copy full error message

2. **Check Network Tab**
   - Look for failed requests
   - Check response status codes

3. **Verify Clerk Dashboard**
   - Check application status
   - Verify API keys
   - Check domain settings

4. **Review Documentation**
   - [Clerk Quick Start](./CLERK_QUICK_START.md)
   - [Clerk Setup Guide](./CLERK_SETUP_GUIDE.md)
   - [Official Clerk Docs](https://clerk.com/docs)

5. **Get Support**
   - [Clerk Discord](https://clerk.com/discord)
   - [Clerk Support](mailto:support@clerk.com)
   - Check [Clerk Status Page](https://status.clerk.com)

---

## Development Tips

### Testing Sign-In Flow

Use incognito/private browsing to test sign-in without signing out:
- Chrome: Ctrl+Shift+N (Windows) or Cmd+Shift+N (Mac)
- Firefox: Ctrl+Shift+P (Windows) or Cmd+Shift+P (Mac)
- Safari: Cmd+Shift+N (Mac)

### Clearing Clerk Session

To completely clear Clerk session:
```javascript
// In browser console
localStorage.clear();
sessionStorage.clear();
// Then refresh page
```

### Checking Clerk State

To check current auth state:
```javascript
// In browser console
console.log('Clerk loaded:', window.Clerk);
console.log('User:', window.Clerk?.user);
console.log('Session:', window.Clerk?.session);
```

---

## Production Checklist

Before deploying to production:

- [ ] Use production Clerk key (`pk_live_...`)
- [ ] Add production domain to Clerk Dashboard
- [ ] Test sign-in flow in production
- [ ] Test sign-out flow
- [ ] Verify redirects work correctly
- [ ] Check mobile responsiveness
- [ ] Test with different browsers
- [ ] Enable HTTPS
- [ ] Configure proper CORS settings
- [ ] Set up error monitoring (Sentry, etc.)

---

## Quick Fixes

### Reset Everything

If nothing works, try this:

```bash
# 1. Stop dev server (Ctrl+C)

# 2. Clear node_modules and reinstall
cd frontend
rm -rf node_modules
npm install

# 3. Verify .env file
cat .env
# Should show: VITE_CLERK_PUBLISHABLE_KEY=pk_test_...

# 4. Clear browser data
# Open DevTools → Application → Clear storage → Clear site data

# 5. Restart dev server
npm run dev

# 6. Open in incognito mode
# Test sign-in flow
```

---

## Still Having Issues?

Create a minimal reproduction:

1. Note exact error message
2. Note steps to reproduce
3. Check browser console for errors
4. Check Network tab for failed requests
5. Share with team or Clerk support

Include:
- Error message
- Browser and version
- Steps to reproduce
- Screenshots if helpful
