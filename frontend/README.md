# Osprey B2C Frontend

Enterprise-grade React TypeScript application for Osprey's AI-powered U.S. immigration case processing system. Provides a complete end-to-end user experience for automated USCIS visa application package generation across 8 visa types.

## 🎯 What This Application Does

Osprey B2C Frontend is a sophisticated multi-step wizard that guides users through the complete immigration application process:

- **Visa Type Selection**: Users select from 8 supported visa types (B-2, F-1, H-1B, I-130, I-765, I-90, EB-2 NIW, EB-1A)
- **Payment Processing**: Stripe-integrated checkout with voucher support and test mode
- **Data Collection**: Multi-step forms collect personal, educational, and employment information
- **Document Upload**: AI-powered document upload with automatic OCR extraction via Google Document AI
- **Story-Based Input**: Natural language "user story" input for personalized case narratives
- **Cover Letter Generation**: AI-powered cover letter creation with Dr. Paula agent
- **AI Review**: Automated completeness checking and translation services
- **Package Generation**: Real-time AI agent processing to generate complete USCIS-ready packages
- **Admin Dashboard**: RBAC-protected admin panels for managing visa updates, products, and knowledge base

## 🏗️ Technology Stack

### Core Framework
- **React 18.3.1** - UI library with hooks and functional components
- **TypeScript 5.8.3** - Type-safe JavaScript with strict mode enabled
- **Vite 5.4.19** - Lightning-fast build tool and dev server with HMR

### UI Component Library
- **Radix UI** - Headless, accessible UI primitives (20+ components)
- **shadcn/ui** - Beautiful, customizable component system built on Radix
- **Tailwind CSS 3.4.17** - Utility-first CSS framework with custom design system
- **Lucide React** - Modern icon library (462 icons)
- **Framer Motion** - Production-ready animation library

### Forms & Validation
- **React Hook Form 7.61.1** - Performant form management with uncontrolled components
- **Zod 3.25.76** - TypeScript-first schema validation
- **@hookform/resolvers** - Seamless RHF + Zod integration

### State Management & Data Fetching
- **TanStack React Query 5.83.0** - Powerful async state management and caching
- **React Router DOM 6.30.1** - Client-side routing with data loaders
- **Axios 1.13.2** - HTTP client for API calls

### Payment Integration
- **Stripe React 5.4.0** - PCI-compliant payment UI components
- **Stripe.js 8.5.2** - Stripe API integration with Elements

### Development Tools
- **ESLint 9.32.0** - Code linting with TypeScript support
- **TypeScript ESLint** - TypeScript-specific linting rules
- **PostCSS** - CSS processing and optimization
- **Autoprefixer** - Automatic vendor prefixing

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/              # 50+ page components (main application screens)
│   │   ├── Index.tsx       # Landing page with hero section
│   │   ├── NewHomepage.tsx # New landing page variant
│   │   ├── Login.tsx       # Authentication (login/register)
│   │   ├── SelectForm.tsx  # Visa type selection with pricing
│   │   ├── EmbeddedCheckout.tsx # Stripe payment with vouchers
│   │   ├── BasicData.tsx   # Personal information form
│   │   ├── FriendlyForm.tsx # Simplified question interface
│   │   ├── DocumentUploadAuto.tsx # Document upload with AI classification
│   │   ├── StoryTelling.tsx # User story narrative input
│   │   ├── CoverLetterModule.tsx # AI cover letter generation
│   │   ├── AIReviewAndTranslation.tsx # Completeness review
│   │   ├── CaseFinalizer.tsx # Final package generation
│   │   ├── Dashboard.tsx   # User dashboard with cases
│   │   ├── AdminVisaUpdatesPanel.tsx # Admin: visa policy updates
│   │   ├── AdminProductManagement.tsx # Admin: pricing & products
│   │   └── AdminKnowledgeBase.tsx # Admin: KB management
│   │
│   ├── components/         # 40+ reusable UI components
│   │   ├── ui/            # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   └── ... (35+ more)
│   │   │
│   │   ├── BetaBanner.tsx  # Site-wide beta notification
│   │   ├── Hero.tsx        # Landing page hero
│   │   ├── VisaRequirements.tsx # Visa details display
│   │   ├── ProactiveAlertsDisplay.tsx # Alert system
│   │   ├── SaveAndContinueModal.tsx # Progress save modal
│   │   └── ... (10+ more)
│   │
│   ├── contexts/          # React Context providers
│   │   ├── LanguageContext.tsx # Multi-language support (en/pt)
│   │   ├── LocaleContext.tsx   # Localization and formatting
│   │   └── ProcessTypeContext.tsx # Process flow state management
│   │
│   ├── hooks/             # Custom React hooks
│   │   ├── useFormSnapshot.ts # Auto-save form data to backend
│   │   ├── useGoogleAuth.ts   # Google OAuth integration
│   │   ├── useOnboarding.ts   # User onboarding flow
│   │   ├── useSessionManager.ts # JWT session management
│   │   ├── use-toast.ts       # Toast notification system
│   │   └── use-mobile.tsx     # Responsive design utilities
│   │
│   ├── utils/             # Utility functions and helpers
│   │   └── api.ts         # API configuration & makeApiCall utility
│   │
│   ├── App.tsx            # Root application component with routing
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles and Tailwind directives
│
├── public/                # Static assets
├── build/                 # Production build output (generated)
├── .env                   # Environment variables (NOT in git)
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── package.json          # Dependencies and npm scripts
├── tsconfig.json         # TypeScript compiler configuration
├── tailwind.config.ts    # Tailwind CSS custom configuration
├── vite.config.ts        # Vite build configuration
└── components.json       # shadcn/ui CLI configuration

Total: ~50 pages, ~40 UI components, 7 hooks, 3 contexts
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Backend API** running on `http://localhost:8001` (see `../backend/README.md`)
- **Stripe Account** for payment integration (test mode keys for development)
- **MongoDB** running (required by backend)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file from template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor

# Start development server
npm run dev
```

The application will open at **http://localhost:3000**

### Development Server Features

- ⚡ **Hot Module Replacement (HMR)** - Instant updates without page reload
- 🔄 **Auto-reload** - Automatic reload on file changes
- 🎯 **TypeScript** - Real-time type checking in terminal
- 📱 **Responsive** - Preview on different device sizes
- 🐛 **Source Maps** - Debug original TypeScript code in browser

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# Backend API Configuration
VITE_BACKEND_URL=http://localhost:8001
VITE_API_URL=http://localhost:8001

# Stripe Configuration
# Get test keys from: https://dashboard.stripe.com/test/apikeys
# Get live keys from: https://dashboard.stripe.com/apikeys
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here

# Environment
NODE_ENV=development
```

**Important Security Notes:**
- ✅ `.env` is in `.gitignore` - **NEVER commit secrets to git**
- ✅ Use test keys (`pk_test_...`) for development
- ✅ Use live keys (`pk_live_...`) only in production
- ✅ The `VITE_` prefix is **required** for Vite to expose variables to the client
- ✅ Never hardcode API keys or secrets in source code
- ✅ Use `.env.example` as a template for required variables

### API Integration

The frontend communicates with the FastAPI backend via REST APIs using a centralized utility.

**API Utility** (`src/utils/api.ts`):

```typescript
import { getApiUrl, makeApiCall } from '@/utils/api';

// GET request
const cases = await makeApiCall('/cases', 'GET');

// POST request with body
const newCase = await makeApiCall('/cases', 'POST', {
  form_code: 'I-539',
  basic_data: { name: 'John Doe' }
});

// PUT request
const updated = await makeApiCall(`/cases/${id}`, 'PUT', {
  status: 'completed'
});
```

**Function Signature:**
```typescript
makeApiCall(endpoint: string, method: string = 'GET', body?: any): Promise<any>
```

**Important Details:**
- Returns the **parsed JSON response data** (not the Response object)
- Automatically throws errors for non-2xx responses
- Automatically prefixes endpoint with `/api`
- Automatically adds `Content-Type: application/json` header
- Base URL from `VITE_BACKEND_URL` environment variable

**Base URL Resolution:**
- Development: `http://localhost:8001` (from `.env`)
- Production: Set via `VITE_BACKEND_URL` environment variable
- All endpoints automatically prefixed with `/api`

## 📱 Application Flow

### User Journey (Non-Admin)

```
1. Landing Page (Index.tsx / NewHomepage.tsx)
   ↓
2. Register/Login (Login.tsx)
   - Email/password authentication
   - JWT token stored in localStorage
   ↓
3. Visa Type Selection (SelectForm.tsx)
   - 8 visa types with descriptions and pricing
   - Premium visa types highlighted (EB-2, EB-1A, I-765)
   - View detailed requirements before selection
   ↓
4. Payment (EmbeddedCheckout.tsx)
   - Stripe checkout with PaymentElement
   - Voucher code application (with validation)
   - Test mode bypass for development
   - Multiple payment methods (card, Apple Pay, Google Pay)
   ↓
5. Basic Data Collection (BasicData.tsx)
   - Personal information (name, DOB, country of birth)
   - Contact details (address, phone, email)
   - Current immigration status
   - Auto-save functionality
   ↓
6. Simplified Questions (FriendlyForm.tsx)
   - Visa-specific questions
   - Natural language input
   - Dynamic question sets based on visa type
   ↓
7. Document Upload (DocumentUploadAuto.tsx)
   - Multi-file drag-and-drop upload
   - AI document classification
   - OCR data extraction via Google Document AI
   - Document completeness validation
   ↓
8. User Story (StoryTelling.tsx)
   - Narrative-based input
   - AI-powered story analysis
   - Context gathering for personalized applications
   ↓
9. Cover Letter (CoverLetterModule.tsx)
   - AI-generated cover letters via Dr. Paula agent
   - User review and editing
   - Multi-step generation with Q&A
   - Official formatting
   ↓
10. AI Review (AIReviewAndTranslation.tsx)
    - Completeness check
    - Quality scoring
    - Translation services (if needed)
    - Final validation
    ↓
11. Package Generation (CaseFinalizer.tsx)
    - Multi-agent AI processing
    - Real-time status updates via WebSocket
    - Progress tracking with step-by-step logs
    - PDF package generation
    - Instant download
    ↓
12. Dashboard (Dashboard.tsx)
    - View all cases
    - Download packages
    - Track status
    - Manage applications
```

### Admin Journey

```
Admin Login (elevated credentials)
   ↓
Admin Dashboard
   ├─→ Visa Updates Panel (AdminVisaUpdatesPanel.tsx)
   │   - Review USCIS policy updates
   │   - Approve/reject changes
   │   - Automatic agent knowledge base updates
   │   - Track update history
   │
   ├─→ Product Management (AdminProductManagement.tsx)
   │   - Configure visa package pricing
   │   - Manage payment options
   │   - Create and manage vouchers
   │   - Track revenue and conversions
   │
   └─→ Knowledge Base (AdminKnowledgeBase.tsx)
       - Upload training documents
       - Update agent knowledge
       - View lessons learned
       - Manage AI model fine-tuning data
```

## 🎨 Key Features

### 1. Multi-Step Form Wizard
- **State Persistence**: Auto-save with `useFormSnapshot` hook
- **Progress Tracking**: Visual progress indicators on each step
- **Validation**: Real-time Zod schema validation with error messages
- **Navigation**: Forward/backward navigation with data retention
- **Session Management**: JWT token refresh and session persistence

### 2. AI-Powered Document Processing
- **Upload**: Drag-and-drop or file picker interface
- **Classification**: Automatic document type detection via AI
- **OCR**: Google Document AI integration for data extraction
- **Validation**: Completeness checking and quality scoring
- **Preview**: In-browser document preview

### 3. Payment Integration (Stripe)
- **Stripe Elements**: PCI-compliant payment forms with PaymentElement
- **Multiple Packages**: Different pricing tiers per visa type
- **Vouchers**: Discount code system with percentage-based discounts
- **Test Mode**: Development bypass for testing without payments
- **Webhooks**: Automatic payment confirmation
- **Error Handling**: Graceful payment failure recovery

### 4. Real-Time Package Generation
- **WebSocket Updates**: Live status updates during generation
- **Progress Tracking**: Step-by-step agent execution status
- **Error Handling**: Graceful error recovery with retry logic
- **Download**: Instant PDF package download
- **Status History**: Complete audit trail of generation process

### 5. Admin Dashboard (RBAC)
- **Role-Based Access**: User/Admin/Superadmin roles
- **Visa Updates**: Track and approve USCIS policy changes
- **Product Management**: Configure pricing and packages
- **Knowledge Base**: Manage agent training data
- **Analytics**: Track usage and performance metrics

### 6. Responsive Design
- **Mobile-First**: Fully responsive layouts using Tailwind breakpoints
- **Touch-Friendly**: Optimized for touch interfaces (44px minimum touch targets)
- **Adaptive UI**: Components adapt to screen size and orientation
- **Progressive Web App**: PWA-ready architecture
- **Accessibility**: WCAG AA compliant (4.5:1 contrast ratios)

## 🎨 UI Design System

### Color Palette
- **Primary**: Purple/Indigo gradient (`from-purple-600 to-indigo-600`)
- **Secondary**: Black/White high contrast
- **Accent**: Gradient overlays for premium features
- **Status Colors**: Green (success), Red (error), Yellow (warning), Blue (info)

### Typography
- **Font Family**: System UI fonts for optimal performance
- **Headings**: Bold weights (600-800)
- **Body**: Regular weight (400)
- **Code**: Monospace for technical content

### Component Patterns
- **Buttons**: Shadow effects with hover lift animation (`shadow-soft`, `hover:shadow-elegant`, `hover:-translate-y-0.5`)
- **Cards**: White background with subtle shadows and border
- **Forms**: Consistent input styling with focus states
- **Modals**: Backdrop blur with centered content

### Accessibility Features
- ✅ Semantic HTML elements
- ✅ ARIA labels and roles
- ✅ Keyboard navigation support
- ✅ Screen reader compatibility
- ✅ High contrast text (4.5:1 minimum)
- ✅ Touch targets (32x32px minimum)

## 🛠️ Development

### Available Scripts

```bash
# Start development server (port 3000)
npm run dev

# Build for production (minified, optimized)
npm run build

# Build for development (with source maps)
npm run build:dev

# Preview production build locally
npm run preview

# Run ESLint linter
npm run lint

# Type check without emitting files
npx tsc --noEmit

# Install new shadcn/ui component
npx shadcn-ui@latest add [component-name]
```

### Code Style Guidelines

**TypeScript Best Practices:**
- ✅ Use functional components with hooks
- ✅ Prefer `const` over `let`, avoid `var`
- ✅ Use TypeScript interfaces for props and data structures
- ✅ Avoid `any` type - use proper typing or `unknown`
- ✅ Use strict null checks
- ✅ Export types for reusability

**React Best Practices:**
- ✅ Use React Hook Form for forms (uncontrolled pattern)
- ✅ Use Zod for validation schemas
- ✅ Use TanStack Query for server state
- ✅ Use context sparingly (prefer props or composition)
- ✅ Memoize expensive calculations with `useMemo`
- ✅ Use `useCallback` for event handlers passed to children

**Component Organization:**
```typescript
// 1. Imports (grouped: external, internal, types)
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { makeApiCall } from '@/utils/api';

// 2. Types/Interfaces
interface MyComponentProps {
  title: string;
  onSubmit: (data: FormData) => void;
}

interface FormData {
  name: string;
  email: string;
}

// 3. Component
export const MyComponent: React.FC<MyComponentProps> = ({ title, onSubmit }) => {
  // 4. Hooks (in order: router, state, context, custom)
  const navigate = useNavigate();
  const [state, setState] = useState('');
  const [loading, setLoading] = useState(false);

  // 5. Effects
  useEffect(() => {
    // Side effects
  }, []);

  // 6. Event Handlers
  const handleClick = () => {
    // Handler logic
  };

  // 7. Render
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold">{title}</h1>
      <Button onClick={handleClick}>Submit</Button>
    </div>
  );
};
```

### Adding New Pages

1. **Create page component** in `src/pages/`:
   ```typescript
   // src/pages/MyNewPage.tsx
   import React from 'react';
   import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

   export const MyNewPage: React.FC = () => {
     return (
       <div className="container mx-auto p-6">
         <Card>
           <CardHeader>
             <CardTitle>My New Page</CardTitle>
           </CardHeader>
           <CardContent>
             <p>Page content here</p>
           </CardContent>
         </Card>
       </div>
     );
   };
   ```

2. **Add route** in `src/App.tsx`:
   ```typescript
   import { MyNewPage } from './pages/MyNewPage';

   // In Routes component:
   <Route path="/my-new-page" element={<MyNewPage />} />
   ```

3. **Add navigation** (if needed):
   ```typescript
   import { useNavigate } from 'react-router-dom';

   const navigate = useNavigate();
   navigate('/my-new-page');
   ```

### Using shadcn/ui Components

Install new components:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
npx shadcn-ui@latest add select
```

Use in your code:
```typescript
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger asChild>
    <Button variant="default">Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
    </DialogHeader>
    <p>Dialog content</p>
  </DialogContent>
</Dialog>
```

**Available Button Variants:**
- `default` - Primary purple button
- `outline` - White with border
- `ghost` - Transparent with hover
- `destructive` - Red for dangerous actions

### Common Patterns

**API Call with Error Handling:**
```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState('');

const fetchData = async () => {
  try {
    setLoading(true);
    setError('');
    const data = await makeApiCall('/endpoint', 'GET');
    // Handle success
  } catch (err: any) {
    setError(err.message || 'An error occurred');
  } finally {
    setLoading(false);
  }
};
```

**Form with Validation:**
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

type FormData = z.infer<typeof formSchema>;

const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
  resolver: zodResolver(formSchema),
});

const onSubmit = (data: FormData) => {
  console.log(data);
};
```

## 🔐 Security Considerations

### Authentication
- **JWT Tokens**: Stored in localStorage as `osprey_session_token`
- **Token Expiry**: Auto-refresh mechanism via `useSessionManager` hook
- **Protected Routes**: Admin routes require authentication + role check
- **Session Timeout**: Automatic logout after inactivity

### API Security
- **HTTPS Only**: Production enforces HTTPS
- **CORS**: Backend validates allowed origins
- **Rate Limiting**: Backend implements per-IP rate limiting
- **Input Validation**: All forms use Zod schemas for validation
- **SQL Injection**: Not applicable (MongoDB backend)
- **XSS Protection**: React's automatic escaping + CSP headers

### Data Privacy
- **No Sensitive Data in Logs**: Production logging excludes PII
- **Secure Storage**: Passwords never stored client-side
- **File Upload**: Direct backend upload with virus scanning
- **Data Encryption**: All data encrypted in transit (TLS)

### Best Practices Implemented
✅ Environment variables for secrets (no hardcoded keys)
✅ `.env` files in `.gitignore`
✅ Content Security Policy headers
✅ XSS protection via React's automatic escaping
✅ CSRF protection via JWT tokens
✅ Dependency security audits (`npm audit`)
✅ Input sanitization on all forms
✅ Output encoding for dynamic content

## 🧪 Testing

### Manual Testing Checklist

**User Flow:**
- [ ] Register new user with email/password
- [ ] Login with valid credentials
- [ ] Select visa type and view requirements
- [ ] Complete payment with test card (4242 4242 4242 4242)
- [ ] Fill basic data form with validation
- [ ] Upload sample documents (PDF, images)
- [ ] Submit user story narrative
- [ ] Generate cover letter with AI
- [ ] Review and submit for package generation
- [ ] Download final PDF package

**Admin Flow:**
- [ ] Login as admin user
- [ ] Access admin dashboard
- [ ] Review pending visa updates
- [ ] Approve/reject visa update
- [ ] Create new product/package
- [ ] Generate voucher code
- [ ] Update knowledge base entry

**Accessibility:**
- [ ] Navigate entire flow with keyboard only
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast (use browser dev tools)
- [ ] Test on mobile devices (iOS, Android)
- [ ] Verify touch targets are adequate size

### Test Cards (Stripe Test Mode)

```
✅ Success: 4242 4242 4242 4242 (any future date, any CVC)
❌ Declined: 4000 0000 0000 0002
🔐 Requires Auth: 4000 0025 0000 3155
🪙 Insufficient Funds: 4000 0000 0000 9995
```

## 🏗️ Build & Deployment

### Production Build

```bash
# Clean install dependencies
rm -rf node_modules package-lock.json
npm install

# Run security audit
npm audit
npm audit fix  # Fix vulnerabilities

# Type check
npx tsc --noEmit

# Build for production
npm run build

# Output directory: frontend/build/
# Contains: index.html, assets/ (CSS, JS, images)
```

### Build Optimization

The production build includes:
- ✅ Minification (HTML, CSS, JS)
- ✅ Code splitting (vendor chunks)
- ✅ Tree shaking (unused code removal)
- ✅ Asset optimization (image compression)
- ✅ Gzip compression ready
- ✅ Source maps (optional, for debugging)

### Deployment Checklist

**Pre-Deployment:**
- [ ] Update `.env` with production values
- [ ] Set `VITE_BACKEND_URL` to production API URL
- [ ] Use production Stripe keys (`pk_live_...`)
- [ ] Run `npm audit` and fix vulnerabilities
- [ ] Test build locally: `npm run preview`
- [ ] Review and commit all changes
- [ ] Tag release in git: `git tag v1.0.0`

**Deployment:**
- [ ] Deploy to hosting platform (Vercel, Netlify, AWS S3, etc.)
- [ ] Configure custom domain and DNS
- [ ] Set up HTTPS/SSL certificate (Let's Encrypt)
- [ ] Enable gzip/brotli compression on server
- [ ] Configure CDN (CloudFlare, CloudFront)
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Configure analytics (Google Analytics, Plausible)

**Post-Deployment:**
- [ ] Verify production site loads correctly
- [ ] Test complete user flow in production
- [ ] Check API connectivity
- [ ] Verify payment processing (with test cards first)
- [ ] Monitor error logs for issues
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)

### Environment-Specific Builds

```bash
# Development build (includes source maps)
npm run build:dev

# Production build (optimized, minified, no source maps)
npm run build
```

### Hosting Recommendations

**Static Hosting (Recommended):**
- **Vercel**: Zero-config deployment, automatic HTTPS, CDN
- **Netlify**: Similar to Vercel, great CI/CD integration
- **AWS S3 + CloudFront**: Enterprise-grade, highly scalable
- **Cloudflare Pages**: Fast global CDN, DDoS protection

**Traditional Hosting:**
- **nginx**: Serve build folder, configure HTTPS
- **Apache**: With mod_rewrite for SPA routing

## 🐛 Troubleshooting

### Common Issues

**Port 3000 already in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- --port 3001
```

**Module not found errors:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors:**
```bash
# Run type checker to see all errors
npx tsc --noEmit

# Common fixes:
# - Add missing type imports
# - Fix type mismatches
# - Update @types/* packages
```

**Build fails:**
```bash
# Clear Vite cache and rebuild
rm -rf node_modules/.vite
npm run build

# If still failing, clear everything
rm -rf node_modules package-lock.json build
npm install
npm run build
```

**API calls fail (CORS errors):**
- ✅ Check `VITE_BACKEND_URL` in `.env`
- ✅ Verify backend is running on correct port (8001)
- ✅ Check backend CORS configuration allows frontend origin
- ✅ Look for CORS errors in browser console (F12)
- ✅ Verify API endpoints are correct

**Stripe not loading:**
- ✅ Verify `VITE_STRIPE_PUBLISHABLE_KEY` is set in `.env`
- ✅ Check browser console for Stripe errors
- ✅ Use test key format: `pk_test_...`
- ✅ Ensure stable internet connection (Stripe loads from CDN)
- ✅ Check if ad blockers are interfering

**White screen after build:**
- ✅ Check browser console for errors
- ✅ Verify all assets loaded (Network tab)
- ✅ Check build output for missing files
- ✅ Ensure routing is configured correctly for SPA

**Controlled/Uncontrolled input warnings:**
- ✅ Ensure all form inputs have initial values (even if empty string)
- ✅ Never switch between `undefined` and string values
- ✅ Example: `<input value={state || ''} />`

### Debug Mode

Enable verbose logging:
```typescript
// In src/main.tsx or component
if (import.meta.env.DEV) {
  console.log('Debug mode enabled');
  // Add debug logging
}
```

## 📚 Additional Resources

### Internal Documentation
- **Main Project README**: `../README.md` - Overall system architecture
- **Backend README**: `../backend/README.md` - API documentation
- **Architecture Docs**: `../docs/architecture/` - Technical design details

### External Documentation
- [React Docs](https://react.dev) - Official React documentation
- [TypeScript Handbook](https://www.typescriptlang.org/docs/) - TypeScript guide
- [Vite Guide](https://vitejs.dev/guide/) - Vite build tool
- [Tailwind CSS](https://tailwindcss.com/docs) - Utility-first CSS
- [shadcn/ui](https://ui.shadcn.com) - Component library
- [Radix UI](https://www.radix-ui.com) - Headless UI primitives
- [React Hook Form](https://react-hook-form.com) - Form management
- [Zod](https://zod.dev) - Schema validation
- [TanStack Query](https://tanstack.com/query/latest/docs/react/overview) - Data fetching
- [Stripe React Docs](https://stripe.com/docs/stripe-js/react) - Payment integration

### Community Resources
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [TypeScript Do's and Don'ts](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [Tailwind Best Practices](https://tailwindcss.com/docs/reusing-styles)

## 🤝 Contributing

### Git Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Follow code style** guidelines above

3. **Test thoroughly**:
   ```bash
   npm run lint        # Check linting
   npx tsc --noEmit   # Check types
   npm run build      # Test build
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add visa type filter to dashboard"
   git commit -m "fix: resolve payment button visibility issue"
   git commit -m "docs: update API integration guide"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/my-feature
   # Create pull request on GitHub
   ```

### Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting, no logic change)
- `refactor:` - Code refactoring (no functional changes)
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Build process or auxiliary tool changes

## 📝 Notes for AI Coding Agents

### Critical Information

**When modifying this codebase, ALWAYS:**

1. **File Structure**:
   - Pages → `src/pages/` (route-level components)
   - Reusable components → `src/components/`
   - UI components → `src/components/ui/` (shadcn)
   - Utilities → `src/utils/`
   - Types → Define inline or in component file

2. **Routing**:
   - Update `src/App.tsx` when adding new pages
   - Use `useNavigate()` hook for navigation
   - Protected routes require auth check

3. **API Calls**:
   - **ALWAYS** use `makeApiCall` from `src/utils/api.ts`
   - **Signature**: `makeApiCall(endpoint: string, method: string = 'GET', body?: any)`
   - **Returns**: Parsed JSON data (NOT Response object)
   - **Errors**: Automatically thrown for non-2xx responses
   - **Example**:
     ```typescript
     // ❌ WRONG - don't use fetch directly
     const response = await fetch('/api/cases');

     // ❌ WRONG - incorrect parameters
     const data = await makeApiCall('/cases', { method: 'POST', body: {...} });

     // ✅ CORRECT
     const cases = await makeApiCall('/cases', 'GET');
     const newCase = await makeApiCall('/cases', 'POST', { form_code: 'I-539' });
     ```

4. **Forms**:
   - Use React Hook Form + Zod for validation
   - Always provide initial values (avoid `undefined`)
   - Use `onChange` handlers for controlled inputs
   - Example: `value={formData.field || ''}` not `value={formData.field}`

5. **UI Components**:
   - Prefer shadcn/ui components over custom HTML
   - Use native `<button>` if you need full style control
   - shadcn Button component has default hover states that override className
   - For custom hover effects, use native button with Tailwind classes

6. **Styling**:
   - Use Tailwind utility classes exclusively
   - Avoid custom CSS unless absolutely necessary
   - Use `className` not `style` (except for dynamic values)
   - For complex hover effects: use native HTML elements with explicit hover classes

7. **State Management**:
   - React Query for server state (API data)
   - Context for global client state (auth, theme)
   - Local state for component-specific data
   - Never mix server and client state

8. **Types**:
   - Create interfaces for all props
   - Type all function parameters
   - Use `z.infer<typeof schema>` for form types
   - Avoid `any` - use `unknown` if truly unknown

9. **Environment Variables**:
   - Use `import.meta.env.VITE_*` for env vars
   - Never hardcode API keys or secrets
   - Check `.env.example` for required variables

10. **Security**:
    - Never commit `.env` files
    - Sanitize user input
    - Use Zod validation on all forms
    - Never trust client-side data

### Common Patterns

**Controlled Input (IMPORTANT):**
```typescript
// ✅ CORRECT - always provide fallback
const [value, setValue] = useState('');
<input value={value || ''} onChange={(e) => setValue(e.target.value)} />

// ❌ WRONG - can cause controlled/uncontrolled warning
const [value, setValue] = useState();
<input value={value} onChange={(e) => setValue(e.target.value)} />
```

**Button with Custom Hover (IMPORTANT):**
```typescript
// ✅ CORRECT - native button with explicit classes
<button className="bg-black text-white hover:bg-gray-800 shadow-soft hover:shadow-elegant hover:-translate-y-0.5">
  Click Me
</button>

// ❌ WRONG - Button component overrides hover classes
<Button className="bg-black text-white hover:bg-gray-800">
  Click Me
</Button>
```

### API Endpoint Patterns

```typescript
// Authentication
POST /api/auth/register        - Register new user
POST /api/auth/login          - Login user
POST /api/auth/logout         - Logout user
GET  /api/auth/me             - Get current user

// Cases
GET    /api/auto-application/case/{id}                - Get case details
POST   /api/auto-application/case/{id}/basic-data     - Save basic data
PUT    /api/auto-application/case/{id}                - Update case
POST   /api/cases                                     - Create new case
POST   /api/cases/{id}/finalize/start                 - Start package generation

// Documents
POST /api/documents/upload    - Upload document
GET  /api/documents/{id}      - Get document
DELETE /api/documents/{id}    - Delete document

// Payment
POST /api/payment/create-payment-intent  - Create Stripe payment
GET  /api/payment/status/{id}            - Check payment status
POST /api/vouchers/validate/{code}       - Validate voucher

// Admin (requires admin role)
GET  /api/admin/visa-updates/pending          - Get pending updates
POST /api/admin/visa-updates/{id}/approve     - Approve update
GET  /api/admin/products                      - List products
POST /api/admin/products                      - Create product
POST /api/admin/vouchers                      - Create voucher
```

### Known Issues & Solutions

1. **Stripe PaymentElement mounting**: Always wait for `onReady` callback before enabling submit button
2. **Controlled input warnings**: Always provide `value || ''` never just `value`
3. **Button hover states**: Use native `<button>` if you need full control over hover styles
4. **404 on visa-specs**: Endpoint may not exist yet - handle 404 gracefully
5. **makeApiCall errors**: Check that method is string ('GET', 'POST'), not object

### Recent Fixes (2026-01-13)

- ✅ Fixed Stripe PaymentElement mounting error by adding `onReady` callback
- ✅ Fixed controlled/uncontrolled input warnings in BasicData.tsx
- ✅ Fixed 404 error handling for visa-specs endpoint
- ✅ Fixed all makeApiCall usage in CoverLetterModule.tsx (7 functions)
- ✅ Fixed button hover visibility issues (BetaBanner, SelectForm, NewHomepage)
- ✅ Removed global CSS rules that forced all buttons to white background
- ✅ Updated index.css to only target specific button classes

---

**Built with ❤️ using React, TypeScript, Vite, and Tailwind CSS**

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Production URL**: https://formfiller-26.preview.emergentagent.com
