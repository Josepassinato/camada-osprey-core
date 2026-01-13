---
inclusion: fileMatch
fileMatchPattern: 'frontend/**/*.{ts,tsx}'
---

# Frontend Coding Patterns (React/TypeScript)

## CRITICAL RULES - MUST FOLLOW

### 1. Use makeApiCall for ALL API Requests
```typescript
// ✅ CORRECT - Centralized API client
import { makeApiCall } from '@/lib/api';

// GET request
const cases = await makeApiCall<Case[]>('/cases', 'GET');

// POST request
const newCase = await makeApiCall<Case>('/cases', 'POST', {
  form_code: 'I-539',
  visa_type: 'b2'
});

// makeApiCall:
// - Returns parsed JSON directly
// - Auto-prefixes /api
// - Handles errors centrally
// - Auto-retries on network errors

// ❌ WRONG - Direct fetch() bypasses error handling
const response = await fetch('/api/cases');
const cases = await response.json();
```

### 2. Controlled Inputs MUST NOT Be Undefined
```typescript
// ✅ CORRECT - Always initialize with empty string
const [formData, setFormData] = useState({
  firstName: data?.firstName || '',  // Never undefined
  lastName: data?.lastName || '',
  email: data?.email || ''
});

<input
  value={formData.firstName}  // Always string
  onChange={(e) => setFormData({...formData, firstName: e.target.value})}
/>

// ❌ WRONG - React warning: uncontrolled to controlled
const [formData, setFormData] = useState({
  firstName: data?.firstName  // Can be undefined!
});
```

### 3. TypeScript Types REQUIRED
```typescript
// ✅ CORRECT - Define proper interfaces
interface Case {
  case_id: string;
  user_id: string;
  status: 'created' | 'in_progress' | 'completed';
  form_code: string;
  created_at: string;
}

async function getCase(caseId: string): Promise<Case> {
  return await makeApiCall<Case>(`/cases/${caseId}`, 'GET');
}

// ❌ WRONG - Loses all type safety
async function getCase(caseId: string): Promise<any> {
  return await makeApiCall(`/cases/${caseId}`, 'GET');
}
```

### 4. Error Handling REQUIRED
```typescript
// ✅ CORRECT - Handle all API errors
try {
  const data = await makeApiCall('/cases', 'POST', formData);
  toast.success('Case created successfully');
  navigate(`/cases/${data.case_id}`);
} catch (error) {
  console.error('Failed to create case:', error);
  toast.error('Failed to create case. Please try again.');
}

// ❌ WRONG - Unhandled errors crash UI
const data = await makeApiCall('/cases', 'POST', formData);
```

### 5. Button Styling (shadcn vs Native)
```typescript
// ✅ CORRECT - Use native <button> for custom hover states
<button
  className="bg-black text-white hover:bg-gray-800 px-4 py-2 rounded"
  onClick={handleClick}
>
  Custom Button
</button>

// ✅ ALSO CORRECT - Use shadcn Button for standard styles
import { Button } from '@/components/ui/button';

<Button variant="default" onClick={handleClick}>
  Standard Button
</Button>

// ⚠️ ISSUE - shadcn Button overrides custom className hover states
<Button className="bg-purple-500 hover:bg-purple-600">
  Won't Work as Expected
</Button>
// Solution: Use native <button> for full CSS control
```

## Component Template
```typescript
import { useState } from 'react';
import { makeApiCall } from '@/lib/api';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

interface MyComponentProps {
  caseId: string;
}

interface Case {
  case_id: string;
  status: string;
  created_at: string;
}

export function MyComponent({ caseId }: MyComponentProps) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Case | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const result = await makeApiCall<Case>('/cases', 'POST', { caseId });
      setData(result);
      toast.success('Success!');
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to process request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-black text-white hover:bg-gray-800 px-4 py-2 rounded"
      >
        {loading ? 'Processing...' : 'Submit'}
      </button>
    </div>
  );
}
```

## Anti-Patterns (NEVER DO THIS!)
- ❌ Direct fetch() instead of makeApiCall
- ❌ Undefined controlled inputs
- ❌ Using `any` type
- ❌ No error handling on API calls
- ❌ Using dangerouslySetInnerHTML without sanitization
- ❌ Hardcoded API URLs (use makeApiCall)
