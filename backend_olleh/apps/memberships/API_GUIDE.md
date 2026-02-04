# Membership API Guide for Client Users

This guide explains how client users can interact with the membership API to request and manage their memberships.

## Authentication

All endpoints require JWT authentication. Include the JWT token in the Authorization header:

```
Authorization: JWT <your-token-here>
```

To get a JWT token, users must first register and login using the Djoser authentication endpoints:
- Register: `POST /auth/users/`
- Login: `POST /auth/jwt/create/`

---

## API Endpoints Overview

### Base URL
All membership endpoints are prefixed with `/api/`

### Available Endpoints

1. **Membership Tiers** (Available Plans)
   - `GET /api/memberships/` - List all available membership tiers
   - `GET /api/memberships/{id}/` - Get details of a specific tier

2. **User Memberships** (User's Membership Requests)
   - `GET /api/user-memberships/` - List user's membership requests
   - `POST /api/user-memberships/` - Request a new membership
   - `GET /api/user-memberships/{id}/` - Get details of a specific request
   - `PATCH /api/user-memberships/{id}/` - Update payment info (pending only)
   - `DELETE /api/user-memberships/{id}/` - Cancel a membership request

3. **Custom Actions**
   - `GET /api/user-memberships/active/` - Get current active membership
   - `GET /api/user-memberships/pending/` - Get all pending requests
   - `GET /api/user-memberships/history/` - Get expired/canceled memberships

---

## Detailed Endpoint Usage

### 1. List Available Membership Tiers

**Endpoint:** `GET /api/memberships/`

**Description:** Get all available membership plans that users can subscribe to.

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Basic",
    "price": 50000,
    "max_order_price": 100000,
    "description": "Basic membership with standard benefits",
    "duration_days": 365,
    "is_available": true,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Premium",
    "price": 100000,
    "max_order_price": 500000,
    "description": "Premium membership with enhanced benefits",
    "duration_days": 365,
    "is_available": true,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  }
]
```

**Query Parameters:**
- `ordering=price` - Order by price (ascending)
- `ordering=-price` - Order by price (descending)
- `ordering=duration_days` - Order by duration

---

### 2. Get Membership Tier Details

**Endpoint:** `GET /api/memberships/{id}/`

**Description:** Get detailed information about a specific membership tier.

**Response Example:**
```json
{
  "id": 1,
  "name": "Basic",
  "price": 50000,
  "max_order_price": 100000,
  "description": "Basic membership with standard benefits",
  "duration_days": 365,
  "is_available": true,
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

---

### 3. Request a New Membership

**Endpoint:** `POST /api/user-memberships/`

**Description:** Create a new membership request with payment information.

**Request Body:**
```json
{
  "membership": 1,
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": 50000
}
```

**Payment Modes:**
- `mobile_money` - Mobile Money (requires payment_reference)
- `cash` - Cash payment (payment_reference optional)
- `bank` - Bank Transfer (requires payment_reference)

**Validation Rules:**
- `amount_paid` must match the membership tier price exactly
- `payment_reference` is required for `mobile_money` and `bank` payments
- User can only have one pending membership per tier
- User can only have one active membership at a time

**Response Example:**
```json
{
  "membership": 1,
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": 50000
}
```

**Status after creation:** `pending` (waiting for admin approval)

**Note:** All amounts are in RWF (Rwandan Francs) and must be integers (no decimal places).

---

### 4. List User's Membership Requests

**Endpoint:** `GET /api/user-memberships/`

**Description:** Get all membership requests for the authenticated user.

**Response Example:**
```json
[
  {
    "id": 1,
    "membership": 1,
    "membership_name": "Basic",
    "membership_price": 50000,
    "status": "pending",
    "start_date": null,
    "end_date": null,
    "payment_mode": "mobile_money",
    "payment_reference": "MTN123456789",
    "amount_paid": 50000,
    "is_active": false,
    "created_at": "2026-01-20T14:30:00Z",
    "updated_at": "2026-01-20T14:30:00Z"
  }
]
```

**Query Parameters:**
- `status=pending` - Filter by status (pending, paid, active, expired, canceled)
- `membership=1` - Filter by membership tier ID
- `ordering=-created_at` - Order by creation date (newest first)
- `ordering=start_date` - Order by start date

---

### 5. Get Membership Request Details

**Endpoint:** `GET /api/user-memberships/{id}/`

**Description:** Get detailed information about a specific membership request.

**Response Example:**
```json
{
  "id": 1,
  "user": 5,
  "user_email": "user@example.com",
  "membership": 1,
  "membership_details": {
    "id": 1,
    "name": "Basic",
    "price": 50000,
    "max_order_price": 100000,
    "description": "Basic membership with standard benefits",
    "duration_days": 365,
    "is_available": true,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  },
  "status": "pending",
  "start_date": null,
  "end_date": null,
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": 50000,
  "payment_confirmed_by": null,
  "confirmed_by_email": null,
  "payment_confirmed_at": null,
  "is_active": false,
  "created_at": "2026-01-20T14:30:00Z",
  "updated_at": "2026-01-20T14:30:00Z"
}
```

---

### 6. Update Payment Information

**Endpoint:** `PATCH /api/user-memberships/{id}/`

**Description:** Update payment information for a pending membership request.

**Note:** Only pending memberships can be updated. Once approved by admin, payment info cannot be changed.

**Request Body:**
```json
{
  "payment_mode": "bank",
  "payment_reference": "BANK987654321",
  "amount_paid": 50000
}
```

**Response Example:**
```json
{
  "payment_mode": "bank",
  "payment_reference": "BANK987654321",
  "amount_paid": 50000
}
```

---

### 7. Cancel Membership Request

**Endpoint:** `DELETE /api/user-memberships/{id}/`

**Description:** Cancel a pending or paid membership request.

**Note:** Only pending or paid memberships can be canceled. Active memberships cannot be canceled via this endpoint.

**Response Example:**
```json
{
  "detail": "Membership request canceled successfully."
}
```

---

### 8. Get Active Membership

**Endpoint:** `GET /api/user-memberships/active/`

**Description:** Get the user's currently active membership.

**Response Example:**
```json
{
  "id": 2,
  "user": 5,
  "user_email": "user@example.com",
  "membership": 1,
  "membership_details": {
    "id": 1,
    "name": "Basic",
    "price": 50000,
    "max_order_price": 100000,
    "description": "Basic membership with standard benefits",
    "duration_days": 365,
    "is_available": true,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  },
  "status": "active",
  "start_date": "2026-01-21T09:00:00Z",
  "end_date": "2027-01-21T09:00:00Z",
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": 50000,
  "payment_confirmed_by": 1,
  "confirmed_by_email": "admin@example.com",
  "payment_confirmed_at": "2026-01-21T09:00:00Z",
  "is_active": true,
  "created_at": "2026-01-20T14:30:00Z",
  "updated_at": "2026-01-21T09:00:00Z"
}
```

**If no active membership:**
```json
{
  "detail": "No active membership found."
}
```

---

### 9. Get Pending Memberships

**Endpoint:** `GET /api/user-memberships/pending/`

**Description:** Get all pending membership requests waiting for admin approval.

**Response Example:**
```json
[
  {
    "id": 3,
    "membership": 2,
    "membership_name": "Premium",
    "membership_price": 100000,
    "status": "pending",
    "start_date": null,
    "end_date": null,
    "payment_mode": "bank",
    "payment_reference": "BANK123456",
    "amount_paid": 100000,
    "is_active": false,
    "created_at": "2026-01-22T10:00:00Z",
    "updated_at": "2026-01-22T10:00:00Z"
  }
]
```

---

### 10. Get Membership History

**Endpoint:** `GET /api/user-memberships/history/`

**Description:** Get all expired and canceled memberships.

**Response Example:**
```json
[
  {
    "id": 1,
    "membership": 1,
    "membership_name": "Basic",
    "membership_price": 50000,
    "status": "expired",
    "start_date": "2025-01-20T09:00:00Z",
    "end_date": "2026-01-20T09:00:00Z",
    "payment_mode": "mobile_money",
    "payment_reference": "MTN987654321",
    "amount_paid": 50000,
    "is_active": false,
    "created_at": "2025-01-19T14:30:00Z",
    "updated_at": "2026-01-20T09:01:00Z"
  }
]
```

---

## Membership Status Flow

1. **pending** - User creates a membership request and provides payment info
2. **paid** - Admin confirms the payment (optional intermediate step)
3. **active** - Admin activates the membership (sets start/end dates)
4. **expired** - Membership reaches its end date
5. **canceled** - User or admin cancels the request

---

## Common Use Cases

### Use Case 1: User Requests a Membership

1. User browses available tiers: `GET /api/memberships/`
2. User selects a tier and makes payment via mobile money
3. User submits membership request: `POST /api/user-memberships/`
4. User waits for admin approval
5. Admin confirms payment and activates membership
6. User can now see active membership: `GET /api/user-memberships/active/`

### Use Case 2: User Corrects Payment Information

1. User submitted wrong payment reference
2. User checks pending requests: `GET /api/user-memberships/pending/`
3. User updates payment info: `PATCH /api/user-memberships/{id}/`
4. Admin can now see correct payment reference

### Use Case 3: User Cancels Request

1. User decides not to proceed with membership
2. User cancels the request: `DELETE /api/user-memberships/{id}/`
3. Membership status changes to "canceled"

---

## Error Responses

### 400 Bad Request
```json
{
  "amount_paid": ["Amount paid must match the membership price of 50,000 RWF."]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Admin Workflow

While this guide focuses on client endpoints, here's how admins interact with membership requests:

1. Admin views pending requests in Django Admin
2. Admin verifies payment (checks mobile money transaction, bank transfer, etc.)
3. Admin marks membership as "paid" (optional) or directly activates it
4. Admin activates membership - this sets start/end dates and status to "active"
5. User can now use their active membership

---

## Testing the API

You can test these endpoints using:
- **Swagger UI**: Navigate to `/api/docs` in your browser
- **ReDoc**: Navigate to `/api/redoc` in your browser
- **Postman/Insomnia**: Import the OpenAPI schema from `/api/schema/`
- **cURL**: Use command-line requests

### Example cURL Request

```bash
# Get available memberships
curl -H "Authorization: JWT your-token-here" \
  http://localhost:8000/api/memberships/

# Request a new membership
curl -X POST \
  -H "Authorization: JWT your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "membership": 1,
    "payment_mode": "mobile_money",
    "payment_reference": "MTN123456789",
    "amount_paid": 50000
  }' \
  http://localhost:8000/api/user-memberships/
```

---

## Notes

- Users can only view and manage their own memberships
- Admins can view and manage all memberships
- Payment confirmation and activation are admin-only actions
- Users cannot activate their own memberships
- Once a membership is active, it cannot be canceled (only expires naturally)
- A user can only have one active membership at a time
- Previous active memberships are automatically expired when a new one is activated
