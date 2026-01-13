# Osprey B2C Frontend

React-based frontend application for the Osprey B2C AI-powered immigration case processing system. This application provides a complete user interface for automated visa application package generation across 8 different U.S. visa types.

## 🎯 What This Application Does

Osprey B2C Frontend is a sophisticated multi-step wizard that guides users through the complete immigration application process:

- **Visa Type Selection**: Users select from 8 supported visa types (B-2, F-1, H-1B, I-130, I-765, I-90, EB-2 NIW, EB-1A)
- **Data Collection**: Multi-step forms collect personal, educational, and employment information
- **Document Upload**: AI-powered document upload with automatic OCR extraction via Google Document AI
- **Story-Based Input**: Natural language "user story" input for personalized case narratives
- **AI Review**: Automated completeness checking and translation services
- **Payment Processing**: Stripe-integrated payment flow with voucher support
- **Package Generation**: Real-time AI agent processing to generate complete USCIS-ready packages
- **Admin Dashboard**: RBAC-protected admin panels for managing visa updates, products, and knowledge base

## 🏗️ Technology Stack

### Core Framework
- **React 18.3.1** - UI library with hooks and functional components
- **TypeScript 5.8.3** - Type-safe JavaScript
- **Vite 5.4.19** - Lightning-fast build tool and dev server

### UI Component Library
- **Radix UI** - Headless, accessible UI components (20+ components)
- **shadcn/ui** - Beautiful, customizable component system built on Radix
- **Tailwind CSS 3.4.17** - Utility-first CSS framework
- **Lucide React** - Icon library (462 icons)
- **Framer Motion** - Animation library

### Forms & Validation
- **React Hook Form 7.61.1** - Performant form management
- **Zod 3.25.76** - TypeScript-first schema validation
- **@hookform/resolvers** - Form validation integration

### State Management & Data Fetching
- **TanStack React Query 5.83.0** - Async state management and caching
- **React Router DOM 6.30.1** - Client-side routing
- **Axios 1.13.2** - HTTP client for API calls

### Payment Integration
- **Stripe React 5.4.0** - Payment UI components
- **Stripe.js 8.5.2** - Stripe API integration

### Development Tools
- **ESLint 9.32.0** - Code linting
- **TypeScript ESLint** - TypeScript linting rules
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/              # 50+ page components (main application screens)
│   │   ├── Index.tsx       # Landing page
│   │   ├── Login.tsx       # Authentication
│   │   ├── SelectForm.tsx  # Visa type selection
│   │   ├── BasicData.tsx   # Personal information form
│   │   ├── FriendlyForm.tsx # Simplified question interface
│   │   ├── DocumentUploadAuto.tsx # Document upload with AI
│   │   ├── StoryTelling.tsx # User story input
│   │   ├── CoverLetterModule.tsx # AI cover letter generation
│   │   ├── CaseFinalizer.tsx # Final package generation
│   │   ├── EmbeddedCheckout.tsx # Stripe payment
│   │   ├── AdminVisaUpdatesPanel.tsx # Admin: visa updates
│   │   ├── AdminProductManagement.tsx # Admin: products
│   │   └── AdminKnowledgeBase.tsx # Admin: KB management
│   │
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # shadcn/ui components (40+ components)
│   │   ├── Hero.tsx       # Landing page hero section
│   │   └── VisaRequirements.tsx # Visa requirements display
│   │
│   ├── contexts/          # React Context providers
│   │   ├── LanguageContext.tsx # Multi-language support
│   │   ├── LocaleContext.tsx   # Localization
│   │   └── ProcessTypeContext.tsx # Process flow management
│   │
│   ├── hooks/             # Custom React hooks
│   │   ├── useFormSnapshot.ts # Auto-save form data
│   │   ├── useGoogleAuth.ts   # Google OAuth
│   │   ├── useOnboarding.ts   # User onboarding
│   │   ├── useSessionManager.ts # Session management
│   │   ├── use-toast.ts       # Toast notifications
│   │   └── use-mobile.tsx     # Responsive design
│   │
│   ├── utils/             # Utility functions
│   │   └── api.ts         # API configuration & helpers
│   │
│   ├── App.tsx            # Root application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
│
├── public/                # Static assets
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.ts    # Tailwind CSS configuration
├── vite.config.ts        # Vite build configuration
└── components.json       # shadcn/ui configuration

Total: ~50 pages, ~40 UI components, 7 hooks, 3 contexts
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Backend API** running on `http://localhost:8001` (see `../backend/README.md`)
- **Stripe Account** for payment integration (test mode for development)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start development server
npm run dev
```

The application will open at **http://localhost:3000**

### Development Server Features

- ⚡ Hot Module Replacement (HMR)
- 🔄 Auto-reload on file changes
- 🎯 TypeScript type checking
- 📱 Responsive design preview

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# Backend API Configuration
VITE_BACKEND_URL=http://localhost:8001
VITE_API_URL=http://localhost:8001

# Stripe Configuration
# Development: Use test keys from https://dashboard.stripe.com/test/apikeys
# Production: Use live keys from https://dashboard.stripe.com/apikeys
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here

# Environment
NODE_ENV=development
```

**Important Security Notes:**
- ✅ `.env` is in `.gitignore` - never commit secrets to git
- ✅ Use test keys (`pk_test_...`) for development
- ✅ Use live keys (`pk_live_...`) only in production
- ✅ The `VITE_` prefix is required for Vite to expose variables to the client

### API Integration

The frontend communicates with the FastAPI backend via REST APIs:

**API Utility** (`src/utils/api.ts`):
```typescript
import { getApiUrl, makeApiCall } from '@/utils/api';

// GET request
const cases = await makeApiCall('/cases', 'GET');

// POST request
const newCase = await makeApiCall('/cases', 'POST', {
  form_code: 'I-539',
  basic_data: { name: 'John Doe' }
});
```

**Base URL Resolution**:
- Reads from `VITE_BACKEND_URL` environment variable
- Falls back to `http://localhost:8001` for local development
- Automatically prefixes endpoints with `/api`

## 📱 Application Flow

### User Journey (Non-Admin)

```
1. Landing Page (Index.tsx)
   ↓
2. Register/Login (Login.tsx)
   ↓
3. Visa Type Selection (SelectForm.tsx)
   - 8 visa types with descriptions
   ↓
4. Payment (EmbeddedCheckout.tsx)
   - Stripe checkout
   - Voucher application
   ↓
5. Basic Data Collection (BasicData.tsx)
   - Personal information
   - Contact details
   - Current status
   ↓
6. Simplified Questions (FriendlyForm.tsx)
   - Visa-specific questions
   - Natural language input
   ↓
7. Document Upload (DocumentUploadAuto.tsx)
   - Multi-file upload
   - AI document classification
   - OCR data extraction
   ↓
8. User Story (StoryTelling.tsx)
   - Narrative-based input
   - AI processing
   ↓
9. Cover Letter (CoverLetterModule.tsx)
   - AI-generated letters
   - User review and editing
   ↓
10. AI Review (AIReviewAndTranslation.tsx)
    - Completeness check
    - Translation services
    ↓
11. Package Generation (CaseFinalizer.tsx)
    - Multi-agent processing
    - Real-time status updates
    - PDF package download
    ↓
12. Dashboard (Dashboard.tsx)
    - View all cases
    - Download packages
    - Track status
```

### Admin Journey

```
Admin Login
   ↓
Admin Dashboard
   ├─→ Visa Updates Panel (AdminVisaUpdatesPanel.tsx)
   │   - Review USCIS policy updates
   │   - Approve/reject changes
   │   - Automatic agent knowledge base updates
   │
   ├─→ Product Management (AdminProductManagement.tsx)
   │   - Configure visa package pricing
   │   - Manage payment options
   │   - Create vouchers
   │
   └─→ Knowledge Base (AdminKnowledgeBase.tsx)
       - Upload training documents
       - Update agent knowledge
       - View lessons learned
```

## 🎨 Key Features

### 1. Multi-Step Form Wizard
- **State Persistence**: Auto-save with `useFormSnapshot` hook
- **Progress Tracking**: Visual progress indicators
- **Validation**: Real-time Zod schema validation
- **Navigation**: Forward/backward navigation with data retention

### 2. AI-Powered Document Processing
- **Upload**: Drag-and-drop or file picker
- **Classification**: Automatic document type detection
- **OCR**: Google Document AI integration for data extraction
- **Validation**: Completeness checking and quality scoring

### 3. Payment Integration
- **Stripe Elements**: PCI-compliant payment forms
- **Multiple Packages**: Different pricing tiers per visa type
- **Vouchers**: Discount code system
- **Webhooks**: Automatic payment confirmation

### 4. Real-Time Package Generation
- **WebSocket Updates**: Live status updates during generation
- **Progress Tracking**: Step-by-step agent execution status
- **Error Handling**: Graceful error recovery
- **Download**: Instant PDF package download

### 5. Admin Dashboard (RBAC)
- **Role-Based Access**: User/Admin/Superadmin roles
- **Visa Updates**: Track and approve USCIS policy changes
- **Product Management**: Configure pricing and packages
- **Knowledge Base**: Manage agent training data

### 6. Responsive Design
- **Mobile-First**: Fully responsive layouts
- **Touch-Friendly**: Optimized for touch interfaces
- **Adaptive UI**: Components adapt to screen size
- **Progressive Web App**: PWA-ready architecture

## 🛠️ Development

### Available Scripts

```bash
# Start development server (port 3000)
npm run dev

# Build for production
npm run build

# Build for development (with source maps)
npm run build:dev

# Preview production build
npm run preview

# Run ESLint
npm run lint

# Type check
npx tsc --noEmit
```

### Code Style Guidelines

**TypeScript Best Practices:**
- Use functional components with hooks
- Prefer `const` over `let`
- Use TypeScript interfaces for props
- Avoid `any` type - use proper typing

**React Best Practices:**
- Use React Hook Form for forms
- Use Zod for validation schemas
- Use TanStack Query for server state
- Use context sparingly (prefer props)

**Component Organization:**
```typescript
// 1. Imports
import React from 'react';
import { useNavigate } from 'react-router-dom';

// 2. Types/Interfaces
interface MyComponentProps {
  title: string;
  onSubmit: (data: FormData) => void;
}

// 3. Component
export const MyComponent: React.FC<MyComponentProps> = ({ title, onSubmit }) => {
  // 4. Hooks
  const navigate = useNavigate();
  const [state, setState] = useState('');

  // 5. Handlers
  const handleClick = () => {
    // ...
  };

  // 6. Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
};
```

### Adding New Pages

1. Create page component in `src/pages/`
2. Define route in `App.tsx`
3. Add navigation links
4. Update TypeScript types if needed

Example:
```typescript
// src/pages/MyNewPage.tsx
import React from 'react';

export const MyNewPage: React.FC = () => {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold">My New Page</h1>
    </div>
  );
};

// src/App.tsx - add route
<Route path="/my-new-page" element={<MyNewPage />} />
```

### Using shadcn/ui Components

Install new components:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
```

Use in your code:
```typescript
import { Button } from '@/components/ui/button';
import { Dialog } from '@/components/ui/dialog';

<Button variant="default" onClick={handleClick}>
  Click Me
</Button>
```

## 🔐 Security Considerations

### Authentication
- **JWT Tokens**: Stored in localStorage as `osprey_session_token`
- **Token Expiry**: Auto-refresh mechanism via `useSessionManager`
- **Protected Routes**: Admin routes require authentication + role check

### API Security
- **HTTPS Only**: Production uses HTTPS
- **CORS**: Backend validates allowed origins
- **Rate Limiting**: Backend implements rate limiting
- **Input Validation**: All forms use Zod schemas

### Data Privacy
- **No Sensitive Data in Logs**: Production logging excludes PII
- **Secure Storage**: Sensitive data not in localStorage
- **File Upload**: Direct backend upload (not client-side)

### Best Practices Implemented
✅ Environment variables for secrets (no hardcoded keys)
✅ `.env` files in `.gitignore`
✅ Content Security Policy headers
✅ XSS protection via React's automatic escaping
✅ CSRF protection via JWT tokens
✅ Dependency security audits (`npm audit`)

## 🧪 Testing

### Manual Testing Checklist

**User Flow:**
- [ ] Register new user
- [ ] Login with credentials
- [ ] Select visa type
- [ ] Complete payment (use test card: 4242 4242 4242 4242)
- [ ] Fill basic data form
- [ ] Upload documents
- [ ] Submit user story
- [ ] Generate package
- [ ] Download PDF

**Admin Flow:**
- [ ] Login as admin
- [ ] Access admin panels
- [ ] Review visa updates
- [ ] Manage products
- [ ] Update knowledge base

### Test Cards (Stripe)

```
Success: 4242 4242 4242 4242 (any future date, any CVC)
Declined: 4000 0000 0000 0002
Requires Auth: 4000 0025 0000 3155
```

## 🏗️ Build & Deployment

### Production Build

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Build
npm run build

# Output directory: frontend/build/
```

### Deployment Checklist

- [ ] Update `.env` with production values
- [ ] Set `VITE_BACKEND_URL` to production API URL
- [ ] Use production Stripe keys (`pk_live_...`)
- [ ] Run `npm audit` and fix vulnerabilities
- [ ] Test build locally: `npm run preview`
- [ ] Configure CDN/hosting (Vercel, Netlify, AWS S3, etc.)
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure domain and DNS
- [ ] Enable gzip/brotli compression
- [ ] Set up monitoring and error tracking

### Environment-Specific Builds

```bash
# Development build (with source maps)
npm run build:dev

# Production build (optimized, minified)
npm run build
```

## 🐛 Troubleshooting

### Common Issues

**Port 3000 already in use:**
```bash
lsof -ti:3000 | xargs kill -9
npm run dev
```

**Module not found errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors:**
```bash
npx tsc --noEmit
# Fix errors shown in output
```

**Build fails:**
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run build
```

**API calls fail (CORS):**
- Check `VITE_BACKEND_URL` in `.env`
- Verify backend is running on correct port
- Check backend CORS configuration

**Stripe not loading:**
- Verify `VITE_STRIPE_PUBLISHABLE_KEY` is set
- Check browser console for errors
- Use test key format: `pk_test_...`

## 📚 Additional Resources

### Documentation
- **Main Project README**: `../README.md` - Overall system architecture
- **Backend README**: `../backend/README.md` - API documentation
- **Architecture Docs**: `../docs/architecture/` - Technical details

### External Documentation
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [React Hook Form](https://react-hook-form.com)
- [TanStack Query](https://tanstack.com/query/latest/docs/react/overview)
- [Stripe React Docs](https://stripe.com/docs/stripe-js/react)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Follow the code style guidelines above
3. Test your changes thoroughly
4. Update documentation if needed
5. Commit with clear messages: `git commit -m "feat: add visa type filter"`
6. Push and create a pull request

## 📝 Notes for AI Coding Agents

**When modifying this codebase:**

1. **File Structure**: All pages go in `src/pages/`, reusable components in `src/components/`
2. **Routing**: Update `src/App.tsx` when adding new pages
3. **API Calls**: Always use `makeApiCall` from `src/utils/api.ts`
4. **Forms**: Use React Hook Form + Zod for validation
5. **UI Components**: Prefer shadcn/ui components over custom implementations
6. **Styling**: Use Tailwind utility classes, avoid custom CSS
7. **State**: Use React Query for server state, Context for global client state
8. **Types**: Create TypeScript interfaces for all props and data structures
9. **Environment**: Use `import.meta.env.VITE_*` for environment variables
10. **Security**: Never hardcode API keys, always use environment variables

**API Endpoints Pattern:**
```typescript
// Authentication
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout

// Cases
GET /api/cases
POST /api/cases
GET /api/cases/{id}
PUT /api/cases/{id}
POST /api/cases/{id}/finalize/start

// Documents
POST /api/documents/upload
GET /api/documents/{id}

// Payment
POST /api/payment/checkout
GET /api/payment/status/{id}

// Admin (requires admin role)
GET /api/admin/visa-updates/pending
POST /api/admin/visa-updates/{id}/approve
```

---

**Built with ❤️ using React, TypeScript, and Vite**

**Production URL**: https://formfiller-26.preview.emergentagent.com
