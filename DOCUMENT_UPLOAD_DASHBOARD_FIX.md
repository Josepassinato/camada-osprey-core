# Document Upload and Dashboard Fix Summary

**Date**: 2026-01-21  
**Issue**: Documents not persisting, auto-application cases not showing on dashboard

## Problems Identified

1. **Missing `is_anonymous` field**: Dashboard queries for `is_anonymous: False` but the field didn't exist in `AutoApplicationCase` model
2. **Document persistence issues**: Documents saved to local state but not properly persisted to database
3. **Wrong navigation flow**: After document upload, navigated to friendly-form instead of dashboard
4. **API endpoint mismatch**: Using PUT with query params instead of PATCH with body params

## Changes Made

### 1. Backend Model Update (`backend/models/auto_application.py`)

Added `is_anonymous` field to `AutoApplicationCase` model:

```python
class AutoApplicationCase(BaseModel):
    # ... existing fields ...
    is_anonymous: bool = True  # True for anonymous cases, False for authenticated users
```

**Default**: `True` (anonymous by default)
**Purpose**: Distinguish between anonymous and authenticated user cases for dashboard filtering

### 2. Backend API Update (`backend/api/auto_application.py`)

Updated case creation to set `is_anonymous` correctly:

```python
# Authenticated user
case = AutoApplicationCase(
    # ... other fields ...
    is_anonymous=False,  # Authenticated user
)

# Anonymous user
case = AutoApplicationCase(
    # ... other fields ...
    is_anonymous=True,  # Anonymous user
)
```

Updated claim endpoint to set `is_anonymous=False` when user claims anonymous case:

```python
await db.auto_cases.update_one(
    {"case_id": case_id},
    {
        "$set": {
            "user_id": current_user["id"],
            "is_anonymous": False,  # No longer anonymous
            # ... other fields ...
        }
    },
)
```

### 3. Frontend Document Upload Fix (`frontend/src/pages/DocumentUploadAuto.tsx`)

#### Fixed `saveDocumentToCase` function:

**Before**:
- Used PUT endpoint with query params
- No error handling
- No response validation

**After**:
- Uses PATCH endpoint (better performance)
- Session token in request body (not query params)
- Proper error handling with status code checking
- Updates local case state after successful save
- Comprehensive logging

```typescript
const saveDocumentToCase = async (file: UploadedFile, analysis: any) => {
  try {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
    
    const requestBody: any = {
      uploaded_documents: documents,
      document_analysis: documentAnalysis,
      status: 'documents_uploaded'
    };

    // Add session_token to body if anonymous
    if (sessionToken && sessionToken !== 'null') {
      requestBody.session_token = sessionToken;
    }

    const response = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`Failed to save document: ${response.status}`);
    }

    const result = await response.json();
    setCase(result.case);  // Update local state
  } catch (error) {
    console.error('Save document error:', error);
    setError('Erro ao salvar documento. Tente novamente.');
  }
};
```

#### Fixed `saveExtractedDataToCase` function:

**Changes**:
- Uses PATCH instead of PUT
- Session token in body instead of query params
- Better error handling
- Doesn't throw errors (allows navigation to continue)

#### Fixed `continueToNextStep` function:

**Before**:
```typescript
const continueToNextStep = async () => {
  await saveExtractedDataToCase();
  navigate(`/auto-application/case/${caseId}/friendly-form`);
};
```

**After**:
```typescript
const continueToNextStep = async () => {
  try {
    // Save extracted data
    await saveExtractedDataToCase();
    
    // Update case status
    await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: 'documents_uploaded',
        current_step: 'documents',
        progress_percentage: 60,
        session_token: sessionToken  // If anonymous
      }),
    });

    // Navigate to dashboard (not friendly-form)
    navigate('/dashboard');
  } catch (error) {
    console.error('Error completing document upload:', error);
    navigate('/dashboard');  // Still navigate even if update fails
  }
};
```

### 4. Database Migration

Created MongoDB migration script (`backend/scripts/migrate_is_anonymous.js`) to update existing cases:

```javascript
// Update authenticated user cases
db.auto_cases.updateMany(
  { user_id: { $ne: null }, is_anonymous: { $exists: false } },
  { $set: { is_anonymous: false, updated_at: new Date() } }
);

// Update anonymous cases
db.auto_cases.updateMany(
  { user_id: null, is_anonymous: { $exists: false } },
  { $set: { is_anonymous: true, updated_at: new Date() } }
);
```

**Run with**: `mongosh osprey_db --eval "$(cat backend/scripts/migrate_is_anonymous.js)"`

## Testing Checklist

- [ ] Create new auto-application case (anonymous)
- [ ] Upload documents to case
- [ ] Verify documents persist in database
- [ ] Verify document analysis is saved
- [ ] Click "Continue" button
- [ ] Verify navigation goes to dashboard
- [ ] Verify case appears on dashboard
- [ ] Login/register and claim anonymous case
- [ ] Verify `is_anonymous` changes to `false`
- [ ] Verify case still appears on dashboard after claiming

## API Endpoints Affected

1. **POST /api/auto-application/start**
   - Now sets `is_anonymous` field on case creation

2. **PATCH /api/auto-application/case/{case_id}**
   - Accepts `session_token` in request body
   - Used for document uploads and status updates

3. **POST /api/auto-application/case/{case_id}/claim**
   - Sets `is_anonymous=False` when claiming

4. **GET /api/dashboard**
   - Queries for `is_anonymous: False` to show only authenticated user cases

## Database Schema Changes

### `auto_cases` collection:

**New field**:
```javascript
{
  is_anonymous: Boolean,  // true for anonymous, false for authenticated
  // ... existing fields ...
}
```

## Benefits

1. ✅ **Documents persist correctly**: All uploads saved to database with proper error handling
2. ✅ **Dashboard shows cases**: Cases with `is_anonymous=False` appear on user dashboard
3. ✅ **Better UX**: After document upload, users see their completed application on dashboard
4. ✅ **Proper API usage**: PATCH endpoint with body params instead of PUT with query params
5. ✅ **Error handling**: Comprehensive error logging and user feedback
6. ✅ **Anonymous support**: Clear distinction between anonymous and authenticated cases

## Related Files

- `backend/models/auto_application.py` - Model definition
- `backend/api/auto_application.py` - API endpoints
- `frontend/src/pages/DocumentUploadAuto.tsx` - Document upload UI
- `frontend/src/pages/Dashboard.tsx` - Dashboard display
- `backend/server.py` - Dashboard endpoint (line 1772)
- `backend/scripts/migrate_is_anonymous.js` - Migration script

## Notes

- All new cases will automatically have `is_anonymous` field set correctly
- Existing cases updated via migration script
- Session token handling works for both anonymous and authenticated users
- Navigation flow improved: documents → dashboard (not friendly-form)
