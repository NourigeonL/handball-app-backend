# Club Authorization System

This document explains the club authorization system implemented in the Handball App Backend, which ensures users can only access and interact with clubs they're authorized for.

## Overview

The club authorization system provides fine-grained access control for all club-related operations. It's designed to be easy to use while maintaining security and flexibility.

**Important**: Authorization decisions are made against domain models directly for **immediate consistency**, not against read facades which are eventually consistent.

**Note**: The club authorization functionality is now part of the unified `AuthService`, providing a single service for all authentication and authorization needs.

## Access Levels

### 1. **Owner Access** (`can_manage: true`)
- **Full control** over the club
- Can view, create, update, and delete club resources
- Can manage players, collectives, and other club data
- Can change club ownership and add/remove coaches

### 2. **Coach Access** (`can_manage: false`)
- **Read-only access** to club information
- Can view players, collectives, and club data
- Cannot modify club resources
- Cannot manage players or collectives

### 3. **No Access** (`access_level: "none"`)
- Cannot access club information
- Cannot perform any club-related operations
- Returns 403 Forbidden error

## How It Works

### 1. **Club Ownership**
- When a club is created, the creator becomes the owner
- Owner ID is stored in the club model and read facades
- Only owners can perform management operations

### 2. **Coach Assignment**
- Coaches can be added to clubs (currently through events)
- Coaches have read access but no management rights
- Coach list is maintained in the club model

### 3. **Authorization Checks**
- All club endpoints use authorization dependencies
- Access is checked before any operation
- Unauthorized access returns 403 Forbidden
- **Authorization uses domain models directly for immediate consistency**

### 4. **Consistency Model**
- **Authorization decisions**: Domain models (immediate consistency)
- **Data display**: Read facades (eventually consistent)
- This ensures security is never compromised by eventual consistency

### 5. **Unified Service Architecture**
- **`AuthService`** handles both authentication and authorization
- **Single service** for all user and club access control
- **Simplified dependency injection** and service management

## Usage Examples

### Basic Club Access Check

```python
from src.dependencies import require_club_access

@router.get("/{club_id}/players")
async def get_club_players(
    club_id: str, 
    current_user: UserSession = Depends(require_club_access)
):
    # User must have access to the club to view players
    # Authorization is checked against domain model for immediate consistency
    return await service_locator.public_read_facade.get_club_players(club_id)
```

### Club Management Check

```python
from src.dependencies import require_club_management

@router.post("/register")
async def register_player(
    register_player_request: RegisterPlayerRequest, 
    current_user: UserSession = Depends(require_club_management)
):
    # User must have management access to register players
    # Authorization is checked against domain model for immediate consistency
    await service_locator.player_service.handle(RegisterPlayerCommand(...))
```

### Manual Authorization Check

```python
# Check if user can access a club (uses unified AuthService)
if not await service_locator.auth_service.can_access_club(user_id, club_id):
    raise HTTPException(status_code=403, detail="Access denied")

# Check if user can manage a club (uses unified AuthService)
if not await service_locator.auth_service.can_manage_club(user_id, club_id):
    raise HTTPException(status_code=403, detail="Management access denied")
```

## API Endpoints with Authorization

### Club Endpoints

| Endpoint | Method | Access Required | Description |
|----------|--------|-----------------|-------------|
| `/clubs/create` | POST | Authenticated | Create new club (becomes owner) |
| `/clubs` | GET | Authenticated | List all clubs |
| `/clubs/{club_id}/players` | GET | Club Access | View club players |
| `/clubs/{club_id}/collectives` | GET | Club Access | View club collectives |
| `/clubs/{club_id}/collectives/{collective_id}` | GET | Club Access | View specific collective |
| `/clubs/{club_id}/info` | GET | Club Access | Get club info (frontend) |
| `/clubs/{club_id}/access` | GET | Club Access | Get user's access level |
| `/clubs/my-clubs` | GET | Authenticated | Get user's accessible clubs |

### Player Endpoints

| Endpoint | Method | Access Required | Description |
|----------|--------|-----------------|-------------|
| `/players/register` | POST | Club Management | Register new player |

### Collective Endpoints

| Endpoint | Method | Access Required | Description |
|----------|--------|-----------------|-------------|
| `/collectives/create` | POST | Club Management | Create new collective |
| `/collectives/{collective_id}/add-player` | POST | Club Management | Add player to collective |
| `/collectives/{collective_id}/remove-player` | POST | Club Management | Remove player from collective |

## Dependencies

### `require_club_access`
- **Purpose**: Ensures user has basic access to a club
- **Use case**: Read operations (view players, collectives, etc.)
- **Access levels**: Owner, Coach
- **Error**: 403 Forbidden if no access
- **Consistency**: Uses domain model directly (immediate)
- **Service**: Unified AuthService

### `require_club_management`
- **Purpose**: Ensures user has management access to a club
- **Use case**: Write operations (create, update, delete)
- **Access levels**: Owner only
- **Error**: 403 Forbidden if no management access
- **Consistency**: Uses domain model directly (immediate)
- **Service**: Unified AuthService

## Frontend Integration

### Getting User's Club Access

```javascript
// Get user's access level for a specific club
const response = await fetch(`/clubs/${clubId}/access`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const accessInfo = await response.json();
// Returns: { club_id, name, access_level, can_manage }

if (accessInfo.can_manage) {
  // Show management UI
  showManagementControls();
} else if (accessInfo.access_level === 'coach') {
  // Show read-only UI
  showReadOnlyUI();
} else {
  // No access
  showAccessDenied();
}
```

### Getting User's Clubs

```javascript
// Get all clubs the user has access to
const response = await fetch('/clubs/my-clubs', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const myClubs = await response.json();
// Returns: [{ club: {...}, access: {...} }, ...]

myClubs.forEach(({ club, access }) => {
  console.log(`Club: ${club.name}, Access: ${access.access_level}`);
});
```

## Security Features

### 1. **Automatic Authorization**
- All club endpoints automatically check access
- No need to manually verify permissions
- Consistent security across the application

### 2. **Role-Based Access Control**
- Different access levels for different user types
- Granular permissions (read vs. management)
- Easy to extend with new roles

### 3. **Immediate Consistency for Security**
- Authorization decisions use domain models directly
- No eventual consistency delays for security checks
- Read facades only used for data display, never for authorization

### 4. **Unified Service Architecture**
- Single `AuthService` for all authentication and authorization
- Consistent interface across all access control operations
- Simplified service management and dependency injection

### 5. **Audit Trail**
- All operations are logged with actor information
- Track who performed what actions
- Maintain accountability

### 6. **Error Handling**
- Clear error messages for access denied
- Proper HTTP status codes (403 Forbidden)
- Consistent error format

## Architecture Benefits

### **Security First**
- Authorization decisions are made against the source of truth
- No risk of security bypass due to eventual consistency
- Immediate enforcement of access controls

### **Performance Optimized**
- Authorization checks are lightweight and direct
- No need to wait for read facade updates
- Fast response times for security decisions

### **Scalable Design**
- Clear separation between security (domain models) and display (read facades)
- Easy to optimize each layer independently
- Maintains consistency guarantees where they matter most

### **Simplified Architecture**
- Single service for all authentication and authorization needs
- Reduced complexity in service locator and dependency injection
- Easier to maintain and extend

## Service Structure

### **Unified AuthService**
```python
class AuthService:
    # User Authentication Methods
    async def sign_up_user_from_google_account(...)
    async def verify_google_id_token(...)
    async def authenticate_user_from_frontend(...)
    
    # Club Authorization Methods
    async def can_access_club(...)
    async def can_manage_club(...)
    async def get_user_clubs(...)
    async def require_club_access(...)
    async def require_club_management(...)
```

### **Service Dependencies**
- **`AuthService`** requires: `AuthRepository`, `UserRepository`, `ClubRepository`
- **All authorization** goes through the unified service
- **Single point of truth** for access control logic

## Extending the System

### Adding New Roles

```python
def _has_club_access(self, user_id: str, club: Club) -> bool:
    # Owner has access
    if club.owner_id == user_id:
        return True
    
    # Coaches have access
    if user_id in club.coaches:
        return True
    
    # Add new roles here
    if user_id in club.admins:  # New admin role
        return True
    
    if user_id in club.members:  # New member role
        return True
    
    return False
```

### Adding New Permission Types

```python
async def can_edit_club_settings(self, user_id: str, club_id: str) -> bool:
    """Check if user can edit club settings"""
    try:
        club = await self._club_repo.get_by_id(club_id)
        # Only owners and admins can edit settings
        return (club.owner_id == user_id or 
                user_id in club.admins)
    except Exception:
        return False
```

## Testing

### Unit Tests

```python
def test_club_authorization():
    # Test owner access
    assert auth_service.can_access_club(owner_id, club_id) == True
    assert auth_service.can_manage_club(owner_id, club_id) == True
    
    # Test coach access
    assert auth_service.can_access_club(coach_id, club_id) == True
    assert auth_service.can_manage_club(coach_id, club_id) == False
    
    # Test no access
    assert auth_service.can_access_club(unauthorized_id, club_id) == False
    assert auth_service.can_manage_club(unauthorized_id, club_id) == False
```

### Integration Tests

```python
async def test_club_endpoint_authorization():
    # Test with owner
    response = await client.get(f"/clubs/{club_id}/players", 
                               headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    
    # Test with coach
    response = await client.get(f"/clubs/{club_id}/players", 
                               headers={"Authorization": f"Bearer {coach_token}"})
    assert response.status_code == 200
    
    # Test with unauthorized user
    response = await client.get(f"/clubs/{club_id}/players", 
                               headers={"Authorization": f"Bearer {unauthorized_token}"})
    assert response.status_code == 403
```

## Best Practices

### 1. **Always Use Dependencies**
- Use `require_club_access` for read operations
- Use `require_club_management` for write operations
- Don't manually check permissions in endpoint logic

### 2. **Consistent Error Handling**
- Use proper HTTP status codes
- Provide clear error messages
- Log authorization failures for audit purposes

### 3. **Performance Considerations**
- Authorization checks are lightweight and direct
- Domain model access is optimized for security checks
- Read facades used only for data display

### 4. **Security First**
- Default to deny access
- Explicitly grant permissions
- Authorization decisions use domain models for immediate consistency
- Regularly audit access patterns

### 5. **Service Architecture**
- Use the unified `AuthService` for all access control
- Keep authorization logic centralized
- Maintain clear separation of concerns

## Troubleshooting

### Common Issues

1. **403 Forbidden on club endpoints**
   - Check if user has access to the club
   - Verify club_id parameter is correct
   - Ensure user is authenticated

2. **Authorization dependency not working**
   - Check dependency order in router
   - Verify club_id parameter is first in path
   - Ensure dependency is properly imported

3. **Access level not updating**
   - Check if coach events are being applied
   - Verify domain model is handling events correctly
   - Authorization service uses domain models directly

### Debug Mode

Enable debug logging to see authorization decisions:

```python
# In your logging configuration
app_logger.setLevel(logging.DEBUG)
```

This will show detailed information about access checks and decisions.

## Consistency Model Summary

| Operation | Data Source | Consistency | Reason |
|-----------|-------------|-------------|---------|
| **Authorization** | Domain Models | Immediate | Security must be consistent |
| **Data Display** | Read Facades | Eventual | Performance and scalability |
| **User Input** | Domain Models | Immediate | Data integrity |
| **Audit Logs** | Domain Models | Immediate | Compliance and security |

This architecture ensures that security is never compromised while maintaining high performance and scalability for data display operations.

## Migration Notes

### **From Separate Services to Unified Service**
- **Before**: `ClubAuthorizationService` + `AuthService`
- **After**: Single unified `AuthService`
- **Benefits**: Simplified architecture, easier maintenance, single point of truth
- **Breaking Changes**: None - all methods remain the same
- **Service Locator**: Updated to use unified service

The migration maintains backward compatibility while providing a cleaner, more maintainable architecture.
