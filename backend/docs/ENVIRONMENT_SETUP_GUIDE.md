# Environment Setup Guide

## Overview

This guide explains how to properly configure your `.env` file for the Osprey backend. The environment configuration controls all external service integrations, API keys, and system behavior.

---

## Quick Start

1. **Copy the example file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials**

3. **Never commit `.env` to version control** (it's in `.gitignore`)

---

## Required Configuration

### 1. Database (REQUIRED)

```bash
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017

# Database name
MONGODB_DB=osprey_production
```

**How to get:**
- Local: Install MongoDB locally or use Docker
- Cloud: Use MongoDB Atlas (https://www.mongodb.com/cloud/atlas)

**Testing:**
```bash
mongosh "mongodb://localhost:27017"
```

---

### 2. Security (REQUIRED)

```bash
# JWT secret for token signing (MUST be secure in production!)
JWT_SECRET=your-secure-random-string-here
```

**How to generate:**
```bash
# Generate a secure random string
openssl rand -hex 32
```

**⚠️ CRITICAL:** Never use the default value in production!

---

### 3. AI/LLM Services (REQUIRED for AI features)

#### OpenAI (Primary LLM)

```bash
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

**How to get:**
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste into `.env`

**Used for:**
- AI agents (document analysis, form filling, QA)
- Chat features
- Text generation
- Embeddings

**Cost:** Pay-as-you-go, ~$0.01-0.03 per 1K tokens

---

#### Google Gemini (Alternative LLM)

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

**How to get:**
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Copy and paste into `.env`

**Used for:**
- Multi-modal AI (text + images)
- Alternative to OpenAI
- Fallback provider

**Cost:** Free tier available, then pay-as-you-go

---

#### Portkey (LLM Gateway - OPTIONAL but recommended)

```bash
LLM_PORTKEY_API_KEY=your-portkey-api-key-here
LLM_ENABLE_PORTKEY=true
```

**How to get:**
1. Go to https://app.portkey.ai/
2. Sign up for free account
3. Get API key from dashboard

**Benefits:**
- Unified LLM access across providers
- Cost tracking and budgets
- Observability and logging
- Automatic fallbacks
- A/B testing

**Cost:** Free tier available

---

### 4. Google Cloud Services (OPTIONAL - for Document AI)

Google Cloud provides advanced document processing capabilities. Without these credentials, the system runs in **MOCK MODE** (simulated responses for development).

#### Option 1: Service Account (RECOMMENDED for production)

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us
GOOGLE_DOCUMENT_AI_LOCATION=us
```

**How to set up:**

1. **Create Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create new project or select existing
   - Note your Project ID

2. **Enable Required APIs:**
   - Document AI API: https://console.cloud.google.com/apis/library/documentai.googleapis.com
   - Vision API: https://console.cloud.google.com/apis/library/vision.googleapis.com
   - Speech-to-Text API: https://console.cloud.google.com/apis/library/speech.googleapis.com
   - Text-to-Speech API: https://console.cloud.google.com/apis/library/texttospeech.googleapis.com

3. **Create Service Account:**
   - Go to: IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name: `osprey-backend`
   - Grant roles:
     * Document AI User
     * Cloud Vision API User
     * Cloud Speech-to-Text User
     * Cloud Text-to-Speech User

4. **Download JSON Key:**
   - Click on service account
   - Keys tab > Add Key > Create new key
   - Choose JSON format
   - Download and save securely
   - Set path in `GOOGLE_APPLICATION_CREDENTIALS`

**Used for:**
- Document OCR and analysis
- Image processing
- Voice transcription
- Text-to-speech

**Cost:** 
- Document AI: $1.50 per 1,000 pages
- Vision API: $1.50 per 1,000 images
- Speech: $0.006 per 15 seconds

---

#### Option 2: API Key (LIMITED - Vision API only)

```bash
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CLOUD_PROJECT_ID=your-project-id
```

**How to get:**
1. Go to: Cloud Console > APIs & Services > Credentials
2. Create Credentials > API Key
3. Copy and paste into `.env`

**Limitations:**
- Only works with Vision API
- Does NOT work with Document AI
- Less secure than service account

---

#### Option 3: OAuth2 (for user-based auth)

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**How to get:**
1. Go to: Cloud Console > APIs & Services > Credentials
2. Create Credentials > OAuth 2.0 Client ID
3. Application type: Web application
4. Copy Client ID and Secret

**Use case:** When users need to authenticate with their Google accounts

---

### 5. Payment Processing (OPTIONAL - for Stripe)

```bash
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_API_KEY=sk_test_your-stripe-api-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

**How to get:**
1. Go to https://dashboard.stripe.com/apikeys
2. Copy test keys for development
3. Use live keys for production

**Webhook setup:**
1. Dashboard > Developers > Webhooks
2. Add endpoint: `https://your-domain.com/api/stripe/webhook`
3. Select events to listen for
4. Copy webhook signing secret

**Used for:**
- Payment processing
- Subscription management
- Invoice generation

**Cost:** 2.9% + $0.30 per transaction

---

### 6. Email Service (OPTIONAL - for Resend)

```bash
RESEND_API_KEY=re_your-resend-api-key
```

**How to get:**
1. Go to https://resend.com/
2. Sign up for account
3. Get API key from dashboard

**Used for:**
- Transactional emails
- Password resets
- Notifications

**Cost:** Free tier: 100 emails/day, then $20/month for 50K emails

---

## Optional Configuration

### CORS Settings

```bash
# Allow all origins (development only!)
CORS_ORIGINS=*

# Production: specify allowed origins
CORS_ORIGINS=https://app.osprey.ai,https://www.osprey.ai
```

---

### Logging

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Pretty print logs (true for development, false for production)
LOG_PRETTY=true

# Log format: text or json (json recommended for production)
LOG_FORMAT=text

# Backup directory
BACKUP_DIR=./backups
```

---

### Error Tracking (Sentry)

```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
SENTRY_SERVICE_NAME=backend
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.05
```

**How to get:**
1. Go to https://sentry.io/
2. Create project
3. Copy DSN from project settings

**Used for:**
- Error tracking
- Performance monitoring
- User feedback

**Cost:** Free tier available, then $26/month

---

## Environment-Specific Configurations

### Development (.env)

```bash
# Relaxed settings for local development
LOG_LEVEL=DEBUG
LOG_PRETTY=true
LOG_FORMAT=text
CORS_ORIGINS=*
SENTRY_TRACES_SAMPLE_RATE=0.0
```

### Staging (.env.staging)

```bash
# Production-like settings for testing
LOG_LEVEL=INFO
LOG_PRETTY=false
LOG_FORMAT=json
CORS_ORIGINS=https://staging.osprey.ai
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.5
```

### Production (.env.production)

```bash
# Strict settings for production
LOG_LEVEL=WARNING
LOG_PRETTY=false
LOG_FORMAT=json
CORS_ORIGINS=https://app.osprey.ai
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_SEND_PII=false
```

---

## Verification

### Check Environment Loading

```bash
cd backend
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('✓ MongoDB URI:', os.getenv('MONGODB_URI'))
print('✓ JWT Secret:', 'SET' if os.getenv('JWT_SECRET') else 'NOT SET')
print('✓ OpenAI Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
print('✓ Google Credentials:', 'SET' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else 'NOT SET')
"
```

### Test Database Connection

```bash
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    await client.admin.command('ping')
    print('✓ MongoDB connection successful')
    client.close()

asyncio.run(test())
"
```

### Test OpenAI Connection

```bash
python3 -c "
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Say hello'}],
    max_tokens=10
)
print('✓ OpenAI connection successful')
print('Response:', response.choices[0].message.content)
"
```

---

## Troubleshooting

### "Google Document AI in MOCK MODE"

**Cause:** No valid Google Cloud credentials found

**Solutions:**
1. Set `GOOGLE_APPLICATION_CREDENTIALS` to service account JSON path
2. OR set `GOOGLE_API_KEY` (limited functionality)
3. OR accept MOCK MODE for development (simulated responses)

**To verify:**
```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
# Should print path to JSON file

# Check if file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS
```

---

### "ModuleNotFoundError: No module named 'payment_packages'"

**Cause:** Import path issue (FIXED in latest version)

**Solution:** Update to latest code or fix import:
```python
# Old (wrong)
from payment_packages import get_visa_package

# New (correct)
from backend.packages.payment_packages import get_visa_package
```

---

### "JWT Secret not configured"

**Cause:** Using default or missing JWT_SECRET

**Solution:** Generate secure secret:
```bash
openssl rand -hex 32
# Copy output to .env
```

---

### "MongoDB connection failed"

**Cause:** MongoDB not running or wrong connection string

**Solutions:**
1. Start MongoDB: `brew services start mongodb-community` (macOS)
2. Check connection string format
3. Verify MongoDB is listening on correct port

---

## Security Best Practices

### ✅ DO:
- Use strong, unique secrets for JWT_SECRET
- Rotate API keys regularly
- Use service accounts for Google Cloud (not personal accounts)
- Enable Sentry in production for error tracking
- Use environment-specific .env files
- Store .env files securely (never commit to git)

### ❌ DON'T:
- Commit .env files to version control
- Share API keys in chat/email
- Use test keys in production
- Use same JWT_SECRET across environments
- Hardcode secrets in code

---

## Cost Estimation

### Minimal Setup (Development)
- MongoDB: Free (local or Atlas free tier)
- OpenAI: ~$5-20/month (development usage)
- **Total: ~$5-20/month**

### Basic Production
- MongoDB Atlas: $57/month (M10 cluster)
- OpenAI: ~$100-500/month (depends on usage)
- Stripe: 2.9% + $0.30 per transaction
- Resend: $20/month (50K emails)
- Sentry: Free tier or $26/month
- **Total: ~$200-600/month + transaction fees**

### Full Production with Google Cloud
- Above + Google Cloud: ~$100-300/month
- **Total: ~$300-900/month + transaction fees**

---

## Support

### Documentation
- Backend README: `backend/README.md`
- API Docs: http://localhost:8001/docs (when server running)
- Security Audit: `backend/docs/SECURITY_AUDIT_2026-01-13.md`

### External Resources
- OpenAI: https://platform.openai.com/docs
- Google Cloud: https://cloud.google.com/docs
- Stripe: https://stripe.com/docs
- MongoDB: https://docs.mongodb.com/
- Portkey: https://docs.portkey.ai/

---

**Last Updated:** January 14, 2026  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
