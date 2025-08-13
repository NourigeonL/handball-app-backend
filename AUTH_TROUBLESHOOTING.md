# Bearer Token Authentication Troubleshooting

This guide helps you resolve common issues with Bearer token authentication in the Handball App Backend.

## 🎉 **NEW: Automatic "Bearer" Prefix!**

**Good news!** You can now just paste your JWT token directly in the authorization field without adding "Bearer " in front. The system will automatically detect and format it correctly.

## Common Error: "Invalid authorization header. Use 'Bearer <token>' format"

### What This Error Means

This error occurs when the `Authorization` header is either:
1. **Missing** - No header sent
2. **Wrong format** - Not using `Bearer <token>` format
3. **Empty token** - Header exists but token is missing

### How to Fix in OpenAPI/Swagger UI

#### Step 1: Get a Valid Token

First, you need to get a valid JWT token:

1. **Use the `/auth/frontend` endpoint** (POST method)
2. **Send a Google ID token** in the request body:
   ```json
   {
     "id_token": "your_google_id_token_here"
   }
   ```
3. **Copy the returned `access_token`** from the response

#### Step 2: Set the Authorization Header

In the OpenAPI/Swagger UI:

1. **Click the "Authorize" button** (🔒 icon) at the top
2. **In the "Value" field**, you can now simply paste your JWT token:
   - **Option 1 (Recommended)**: Just paste the token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Option 2 (Still works)**: Use the full format: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. **Click "Authorize"**
4. **Close the dialog**

**🎯 The system automatically detects JWT tokens and adds "Bearer " prefix when needed!**

#### Step 3: Test the Endpoint

Now try your protected endpoint again. The header should be automatically included.

### Example of Correct Header Format

#### ✅ **New Way (Just Paste Token)**
```
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzNDU2Nzg5MCIsImVtYWlsIjoiZXhhbXBsZUBnbWFpbC5jb20iLCJleHAiOjE2MzQ1Njc4OTB9.signature_here
```

#### ✅ **Traditional Way (Still Works)**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzNDU2Nzg5MCIsImVtYWlsIjoiZXhhbXBsZUBnbWFpbC5jb20iLCJleHAiOjE2MzQ1Njc4OTB9.signature_here
```

**Key Points:**
- ✅ **Just paste the token** - No need to add "Bearer " manually
- ✅ **Automatic detection** - System recognizes JWT tokens
- ✅ **Both formats work** - Traditional format still supported
- ✅ **No quotes needed** - Just the raw token

### Testing with the Test Endpoint

Use the `/auth/test-token` endpoint to verify your authentication:

1. **Set the Authorization header** as described above
2. **Call GET `/auth/test-token`**
3. **If successful**, you'll see:
   ```json
   {
     "message": "Bearer token authentication successful!",
     "user": {
       "user_id": "your_user_id",
       "email": "your_email@example.com"
     },
     "timestamp": "2024-01-01T12:00:00"
   }
   ```

## Common Mistakes

### ❌ **Wrong Format Examples (Still Avoid These)**

```
Authorization: "token"
Authorization: Bearer
Authorization: token
Authorization: Bearer: token
```

### ✅ **Correct Format Examples**

#### **New Simplified Way**
```
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### **Traditional Way (Still Works)**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Testing with curl

### Test Authentication

```bash
# Test with just the token (new way)
curl -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  "http://localhost:8000/auth/test-token"

# Test with Bearer prefix (traditional way)
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  "http://localhost:8000/auth/test-token"

# Test with missing header
curl "http://localhost:8000/auth/test-token"
```

### Expected Responses

**Success (200):**
```json
{
  "message": "Bearer token authentication successful!",
  "user": {...},
  "timestamp": "..."
}
```

**Missing Header (401):**
```json
{
  "detail": "Authorization header is required. Just paste your JWT token in the authorization field."
}
```

**Invalid Token Format (401):**
```json
{
  "detail": "Invalid token format. Please paste a valid JWT token."
}
```

## Debug Information

### Logs to Check

The backend logs will show:
- **Received header value**
- **Auto-added "Bearer " prefix** (when applicable)
- **Authentication success/failure**
- **User information** when successful

### Enable Debug Logging

To see detailed authentication logs, ensure your logging level is set to INFO or DEBUG.

## Frontend Integration

### JavaScript Example

```javascript
const token = 'your_jwt_token_here';

// Both ways work now!
fetch('/auth/test-token', {
  headers: {
    'Authorization': token  // Just the token
    // OR
    // 'Authorization': `Bearer ${token}`  // Traditional way
  }
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

### React Example

```jsx
const [user, setUser] = useState(null);

const testAuth = async () => {
  try {
    const token = localStorage.getItem('access_token');
    
    // Both ways work now!
    const response = await fetch('/auth/test-token', {
      headers: {
        'Authorization': token  // Just the token
        // OR
        // 'Authorization': `Bearer ${token}`  // Traditional way
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      setUser(data.user);
    }
  } catch (error) {
    console.error('Authentication failed:', error);
  }
};
```

## Still Having Issues?

### Check These Points

1. **Token is valid** - Not expired, properly formatted JWT
2. **Header name** - Must be exactly "Authorization"
3. **Token format** - Valid JWT token structure (contains dots, reasonable length)
4. **No extra characters** - No quotes, extra spaces, or special characters
5. **Token not empty** - Make sure you're not sending an empty string

### Get Help

If you're still experiencing issues:

1. **Check the backend logs** for detailed error information
2. **Use the test endpoint** `/auth/test-token` to isolate the issue
3. **Verify token format** with a JWT decoder
4. **Test with curl** to eliminate frontend issues

## Quick Test Checklist

- [ ] Got a valid JWT token from `/auth/frontend`
- [ ] Set Authorization header to just the token (no "Bearer " needed)
- [ ] No quotes around the header value
- [ ] Token is not expired
- [ ] Using the correct endpoint
- [ ] Checked backend logs for errors

## 🚀 **What's New**

- **Automatic "Bearer " prefix** - Just paste your JWT token
- **Smart token detection** - System recognizes JWT format
- **Backward compatibility** - Traditional format still works
- **Better error messages** - Clear guidance on what to do
- **Debug logging** - See exactly what's happening

Follow this checklist and you should be able to resolve most Bearer token authentication issues! The new automatic prefix feature makes it much easier to use.
