# Kiro Configuration for Osprey Platform

This directory contains Kiro-specific configuration files to help the AI assistant work effectively with the Osprey immigration platform codebase.

## Directory Structure

```
.kiro/
├── README.md                           # This file
└── steering/                           # Steering rules for AI assistance
    ├── osprey-core-architecture.md     # Project overview and structure
    ├── backend-patterns.md             # Python/FastAPI coding patterns
    ├── frontend-patterns.md            # React/TypeScript coding patterns
    ├── security-best-practices.md      # Security guidelines
    ├── ai-integration-patterns.md      # AI/LLM integration patterns
    ├── common-tasks.md                 # Common development tasks
    └── quick-reference.md              # Quick reference guide
```

## Steering Files

### Always Included (Automatic)
These files are automatically included in every Kiro interaction:

1. **osprey-core-architecture.md**
   - Project overview and tech stack
   - Repository structure
   - Key documentation files
   - API documentation links

2. **security-best-practices.md**
   - Security rules (NEVER/ALWAYS)
   - Environment variable usage
   - Input validation patterns
   - Error handling best practices

3. **quick-reference.md**
   - File structure reference
   - Quick commands
   - Success metrics
   - Key development principles

### Conditionally Included (File Match)
These files are automatically included when working with specific file types:

1. **backend-patterns.md** (matches: `backend/**/*.py`)
   - Async/await patterns
   - Pydantic validation
   - MongoDB serialization
   - Structured logging
   - API router templates

2. **frontend-patterns.md** (matches: `frontend/**/*.{ts,tsx}`)
   - makeApiCall usage
   - Controlled input patterns
   - TypeScript type definitions
   - Error handling
   - Component templates

3. **ai-integration-patterns.md** (matches: `**/agents/**/*.py`)
   - LLM integration patterns
   - Agent architecture
   - Multi-agent orchestration
   - Token usage logging
   - Rate limit handling

### Manually Included (On Demand)
These files can be referenced explicitly when needed:

1. **common-tasks.md**
   - Add new API endpoint
   - Add database collection
   - Add AI agent
   - Add React page
   - Run tests

## How to Use

### For Developers
The steering files work automatically - Kiro will reference them based on:
- What files you're working with
- What tasks you're performing
- What context is needed

### Referencing Steering Files
You can explicitly reference steering files in chat:
```
"Follow the patterns in #common-tasks to add a new API endpoint"
```

### Adding New Steering Rules
To add new steering rules:

1. Create a new `.md` file in `.kiro/steering/`
2. Add front-matter to control inclusion:

```markdown
---
inclusion: always
---
# Your steering content here
```

Or for conditional inclusion:
```markdown
---
inclusion: fileMatch
fileMatchPattern: 'tests/**/*.py'
---
# Your steering content here
```

Or for manual inclusion:
```markdown
---
inclusion: manual
---
# Your steering content here
```

### Including External Files
Steering files can reference other files using:
```markdown
#[[file:relative/path/to/file.py]]
```

## Key Patterns Enforced

### Backend (Python/FastAPI)
- ✅ Async/await for all I/O operations
- ✅ Pydantic validation on all endpoints
- ✅ MongoDB serialization before JSON return
- ✅ Structured logging (no print statements)
- ✅ datetime.now(timezone.utc) instead of utcnow()
- ✅ Proper HTTP status codes

### Frontend (React/TypeScript)
- ✅ makeApiCall for all API requests
- ✅ Controlled inputs never undefined
- ✅ TypeScript types (no 'any')
- ✅ Error handling on all API calls
- ✅ Native buttons for custom hover states

### Security
- ✅ Environment variables for secrets
- ✅ Input validation everywhere
- ✅ Generic error messages to users
- ✅ Structured logging for security events

## Documentation Hierarchy

1. **AI_AGENT_GUIDE.md** - Universal guide for all AI assistants
2. **.kiro/steering/** - Kiro-specific steering rules (this directory)
3. **README.md** - Root project documentation
4. **backend/README.md** - Backend deep dive
5. **frontend/README.md** - Frontend deep dive
6. **SECURITY_AUDIT_2026-01-13.md** - Latest security audit

## Maintenance

### When to Update Steering Files
- New architectural patterns are established
- Security vulnerabilities are discovered
- Common mistakes are repeatedly made
- New best practices are adopted
- Project structure changes significantly

### Version Control
All steering files are committed to git and versioned with the project.

## Support

For questions about Kiro configuration:
1. Review this README
2. Check individual steering files
3. Refer to AI_AGENT_GUIDE.md
4. Consult project documentation

---

**Last Updated**: 2026-01-13
**Maintained By**: Osprey Development Team
