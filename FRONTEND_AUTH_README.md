# Frontend Google Authentication

This document explains how to use Google Authentication from your frontend application with the Handball App Backend.

## Overview

The backend now supports two authentication methods:
1. **Cookie-based authentication** - Used for OpenAPI documentation and server-side sessions
2. **Bearer token authentication** - Used for frontend applications (using standardized APIKeyHeader)

## Frontend Authentication Flow

### 1. Get Google ID Token from Frontend

Your frontend should implement Google Sign-In using the Google Identity Services library. Here's a basic example:

```javascript
// Load Google Identity Services
google.accounts.id.initialize({
  client_id: 'YOUR_GOOGLE_CLIENT_ID',
  callback: handleCredentialResponse
});

// Handle the credential response
function handleCredentialResponse(response) {
  // response.credential contains the ID token
  const idToken = response.credential;
  
  // Send this token to your backend
  authenticateWithBackend(idToken);
}

// Trigger Google Sign-In
google.accounts.id.prompt();
```

### 2. Send ID Token to Backend

Send the Google ID token to the backend authentication endpoint:

```javascript
async function authenticateWithBackend(idToken) {
  try {
    const response = await fetch('/auth/frontend', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id_token: idToken
      })
    });

    if (response.ok) {
      const authData = await response.json();
      
      // Store the access token
      localStorage.setItem('access_token', authData.access_token);
      
      // Store user info if needed
      localStorage.setItem('user', JSON.stringify(authData.user));
      
      console.log('Authentication successful:', authData);
    } else {
      console.error('Authentication failed');
    }
  } catch (error) {
    console.error('Error during authentication:', error);
  }
}
```

### 3. Use Access Token for API Calls

Include the access token in the Authorization header for subsequent API calls:

```javascript
async function fetchClubInfo(clubId) {
  const accessToken = localStorage.getItem('access_token');
  
  try {
    const response = await fetch(`/clubs/${clubId}/info`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      const clubInfo = await response.json();
      console.log('Club info:', clubInfo);
    } else {
      console.error('Failed to fetch club info');
    }
  } catch (error) {
    console.error('Error fetching club info:', error);
  }
}
```

## API Endpoints

### POST /auth/frontend

Authenticates a user using a Google ID token from the frontend.

**Request Body:**
```json
{
  "id_token": "google_id_token_here"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "user_uuid",
    "email": "user@example.com",
    "google_account_id": "google_sub_id"
  }
}
```

### GET /clubs/{club_id}/info (Protected)

Example of a protected endpoint that requires Bearer token authentication.

**Headers:**
```
Authorization: Bearer your_access_token_here
```

**Note**: This endpoint now uses FastAPI's standardized `APIKeyHeader` for authentication, providing better security and consistency.

## Error Handling

The backend will return appropriate HTTP status codes:

- `200` - Authentication successful
- `401` - Invalid or expired token
- `500` - Server error during authentication

## Security Notes

1. **Never store sensitive tokens in localStorage** in production - use secure storage methods
2. **Always use HTTPS** in production
3. **Implement token refresh** logic for long-lived sessions
4. **Validate tokens** on the frontend before making API calls
5. **Use standardized Authorization header** format: `Bearer <token>`

## Dependencies

Make sure your frontend includes the Google Identity Services library:

```html
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

## Example Frontend Implementation

Here's a complete example of a React component:

```jsx
import React, { useEffect, useState } from 'react';

function GoogleAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Initialize Google Sign-In
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: 'YOUR_GOOGLE_CLIENT_ID',
        callback: handleCredentialResponse
      });
    }
  }, []);

  const handleCredentialResponse = async (response) => {
    try {
      const result = await authenticateWithBackend(response.credential);
      setIsAuthenticated(true);
      setUser(result.user);
    } catch (error) {
      console.error('Authentication failed:', error);
    }
  };

  const signIn = () => {
    if (window.google) {
      window.google.accounts.id.prompt();
    }
  };

  const signOut = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <div>
      {!isAuthenticated ? (
        <button onClick={signIn}>Sign in with Google</button>
      ) : (
        <div>
          <p>Welcome, {user?.email}!</p>
          <button onClick={signOut}>Sign Out</button>
        </div>
      )}
    </div>
  );
}

export default GoogleAuth;
```

## Testing

You can test the frontend authentication using tools like Postman or curl:

```bash
# First, get a Google ID token from your frontend
# Then authenticate with the backend
curl -X POST "http://localhost:8000/auth/frontend" \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your_google_id_token_here"}'

# Use the returned access token to call protected endpoints
curl -H "Authorization: Bearer your_access_token_here" \
  "http://localhost:8000/clubs/your_club_id/info"
```

## Authentication Header Format

The backend now uses FastAPI's standardized `APIKeyHeader` for authentication:

- **Header Name**: `Authorization`
- **Format**: `Bearer <access_token>`
- **Example**: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

This standardized approach provides:
- **Better security** through FastAPI's built-in header validation
- **Consistent error handling** across all endpoints
- **Automatic OpenAPI documentation** for authentication requirements
- **Standard compliance** with HTTP authentication best practices
