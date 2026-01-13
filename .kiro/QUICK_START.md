# Kiro Quick Start Guide

## 🎯 You're Ready to Go!

Kiro now has full context about the Osprey platform. Here's how to use it effectively:

## 💬 Example Requests

### Backend Development
```
"Add a new API endpoint for uploading passport photos"
→ Kiro will automatically use async/await, Pydantic validation, and proper logging

"Create a new database collection for tracking user sessions"
→ Kiro will use MongoDB patterns and document the schema

"Add an AI agent for validating I-539 forms"
→ Kiro will use the agent architecture pattern with proper error handling
```

### Frontend Development
```
"Create a new dashboard page for case management"
→ Kiro will use makeApiCall, TypeScript types, and proper error handling

"Add a form component for collecting passport information"
→ Kiro will ensure controlled inputs are never undefined

"Fix the hover state on the submit button"
→ Kiro knows to use native <button> for custom hover states
```

### Debugging
```
"Why is this MongoDB query failing?"
→ Kiro will check for serialization issues

"This API call returns 500 error"
→ Kiro will check async/await, error handling, and logging

"TypeScript is complaining about undefined values"
→ Kiro will check controlled input initialization
```

## 🔍 What Kiro Knows Automatically

### Always Active
- ✅ Project architecture and structure
- ✅ Security best practices
- ✅ Quick reference commands
- ✅ File structure and organization

### When Editing Python Files
- ✅ Async/await patterns
- ✅ Pydantic validation
- ✅ MongoDB serialization
- ✅ Structured logging
- ✅ API router templates

### When Editing TypeScript Files
- ✅ makeApiCall usage
- ✅ Controlled input patterns
- ✅ TypeScript type safety
- ✅ Error handling
- ✅ Component templates

### When Editing Agent Files
- ✅ LLM integration patterns
- ✅ Token usage logging
- ✅ Rate limit handling
- ✅ Multi-agent orchestration

## 🚫 What Kiro Will Prevent

### Backend
- ❌ Synchronous database calls
- ❌ print() statements
- ❌ Missing serialization
- ❌ datetime.utcnow() (deprecated)
- ❌ Hardcoded secrets

### Frontend
- ❌ Direct fetch() calls
- ❌ Undefined controlled inputs
- ❌ 'any' types
- ❌ Unhandled API errors
- ❌ Hardcoded API URLs

### Security
- ❌ Hardcoded secrets
- ❌ Unvalidated user input
- ❌ Raw error messages to users
- ❌ eval() or exec() on user input

## 📖 Need More Details?

- **Setup Info**: `.kiro/SETUP_SUMMARY.md`
- **Full Docs**: `.kiro/README.md`
- **Original Guide**: `AI_AGENT_GUIDE.md`
- **Common Tasks**: Reference with `#common-tasks`

## 🎓 Pro Tips

1. **Let Kiro lead**: Just describe what you want, Kiro knows the patterns
2. **Trust the patterns**: Kiro will follow established code style
3. **Review suggestions**: Kiro enforces best practices automatically
4. **Ask questions**: Kiro has full project context

## 🚀 Start Building!

Just tell Kiro what you want to build, and it will:
- ✅ Use the right patterns
- ✅ Follow security guidelines
- ✅ Write type-safe code
- ✅ Include proper error handling
- ✅ Add appropriate logging

Example:
```
"I need to add a feature for users to upload their visa documents"
```

Kiro will:
1. Create the backend API endpoint with async/await and Pydantic
2. Add MongoDB collection access with serialization
3. Create the frontend component with makeApiCall and TypeScript
4. Include error handling and logging
5. Follow security best practices

---

**Ready?** Start coding! 🎉
