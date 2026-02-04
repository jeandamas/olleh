# Membership Management System

This directory contains the complete membership management system for client users, allowing them to request memberships and wait for admin approval.

## Overview

The system provides a complete workflow for membership management:

1. **Client users** can browse membership tiers and submit requests with payment information
2. **Admin users** can review, approve, and activate membership requests
3. **Automatic status tracking** manages the lifecycle of memberships

## Files Created

### Core Files
- **`models.py`** - Contains `Membership` and `UserMembership` models
- **`serializers.py`** - REST API serializers for client endpoints
- **`views.py`** - ViewSets for handling API requests
- **`permissions.py`** - Custom permissions for client/admin access
- **`urls.py`** - URL routing for API endpoints
- **`admin.py`** - Enhanced Django admin interface with actions

### Management Commands
- **`management/commands/create_sample_memberships.py`** - Creates sample membership tiers

### Documentation
- **`API_GUIDE.md`** - Complete API documentation for client endpoints
- **`README.md`** - This file

## Quick Start

### 1. Run Migrations

First, ensure your database is up to date:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Sample Membership Tiers

Create some test membership tiers:

```bash
python manage.py create_sample_memberships
```

This creates 4 tiers: Bronze, Silver, Gold, and Platinum.

**Note:** All prices are in RWF (Rwandan Francs) and are stored as integers (no decimal places).

### 3. Create Users for Testing

Create a regular user and an admin user:

```bash
# Create superuser (admin)
python manage.py createsuperuser

# Create regular users via API or Django shell
python manage.py shell
```

In the shell:
```python
from users.models import User
user = User.objects.create_user(email='client@example.com', password='testpass123')
user.first_name = 'John'
user.last_name = 'Doe'
user.save()
```

### 4. Start the Development Server

```bash
python manage.py runserver
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/api/docs
- **Django Admin**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

## API Endpoints

### Client Endpoints

All endpoints require JWT authentication. Get a token first:

```bash
# Register a new user
curl -X POST http://localhost:8000/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "re_password": "securepass123"
  }'

# Login and get JWT token
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Membership Tiers

```bash
# List all available membership tiers
GET /api/memberships/

# Get specific membership tier
GET /api/memberships/{id}/
```

### User Memberships

```bash
# List user's membership requests
GET /api/user-memberships/

# Create new membership request
POST /api/user-memberships/
{
  "membership": 1,
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": "50000.00"
}

# Get specific membership request
GET /api/user-memberships/{id}/

# Update payment info (pending only)
PATCH /api/user-memberships/{id}/
{
  "payment_reference": "MTN987654321"
}

# Cancel membership request
DELETE /api/user-memberships/{id}/

# Get active membership
GET /api/user-memberships/active/

# Get pending requests
GET /api/user-memberships/pending/

# Get membership history
GET /api/user-memberships/history/
```

## Admin Workflow

### Via Django Admin Panel

1. Login to admin panel: http://localhost:8000/admin/
2. Navigate to **User Memberships**
3. You'll see all pending requests with payment information
4. Select one or more pending requests
5. Choose action from dropdown:
   - **Mark selected as PAID** - Confirms payment
   - **Activate selected memberships** - Activates and sets dates
   - **Cancel selected memberships** - Cancels requests

### Status Flow

```
pending → paid → active → expired
   ↓                ↓
canceled        canceled
```

1. **pending** - User submitted request with payment info
2. **paid** - Admin confirmed payment (optional)
3. **active** - Admin activated membership (sets start/end dates)
4. **expired** - Membership reached end date
5. **canceled** - User or admin canceled

## Testing Examples

### Complete User Flow Example

```bash
# 1. Get JWT token (after registration)
TOKEN="your-jwt-token-here"

# 2. Browse available memberships
curl -H "Authorization: JWT $TOKEN" \
  http://localhost:8000/api/memberships/

# 3. Request a membership
curl -X POST \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "membership": 1,
    "payment_mode": "mobile_money",
    "payment_reference": "MTN123456789",
    "amount_paid": 25000
  }' \
  http://localhost:8000/api/user-memberships/

# 4. Check pending requests
curl -H "Authorization: JWT $TOKEN" \
  http://localhost:8000/api/user-memberships/pending/

# 5. Update payment info if needed
curl -X PATCH \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_reference": "MTN999888777"
  }' \
  http://localhost:8000/api/user-memberships/1/

# 6. Admin approves in Django admin...

# 7. Check active membership
curl -H "Authorization: JWT $TOKEN" \
  http://localhost:8000/api/user-memberships/active/
```

## Key Features

### For Clients
✅ Browse available membership tiers  
✅ Request membership with payment info  
✅ Update payment information (pending only)  
✅ View membership status in real-time  
✅ Cancel pending/paid requests  
✅ View membership history  
✅ Check active membership  

### For Admins
✅ View all membership requests  
✅ Filter by status, payment mode, tier  
✅ Bulk actions (mark paid, activate, cancel)  
✅ View payment details  
✅ Track who approved what  
✅ Color-coded status badges  

### Security
✅ JWT authentication required  
✅ Users can only view their own memberships  
✅ Admins can view all memberships  
✅ Only admins can approve/activate  
✅ Proper permission checks  

### Validation
✅ Amount must match tier price  
✅ Payment reference required for mobile/bank  
✅ Only one active membership per user  
✅ Only one pending per user per tier  
✅ Status transition validation  

## Model Constraints

### UserMembership Constraints

1. **One active membership per user** - A user can only have one active membership at a time
2. **One pending per tier** - A user can't have multiple pending requests for the same tier
3. **Proper status transitions** - Status changes follow business logic
4. **Date validation** - End date must be after start date

## Payment Modes

- **mobile_money** - Mobile Money (MTN, Airtel, etc.) - requires `payment_reference`
- **cash** - Cash payment - `payment_reference` optional
- **bank** - Bank Transfer - requires `payment_reference`

## Common Issues & Solutions

### Issue: "User already has an active membership"
**Solution**: Only one active membership is allowed. Previous membership must expire or be canceled.

### Issue: "Only pending memberships can be updated"
**Solution**: Once admin approves, payment info is locked. Only pending requests can be updated.

### Issue: "Amount paid must match the membership price"
**Solution**: The amount paid must exactly match the tier price. Use integers only (no decimals) for RWF amounts.

### Issue: "Authentication credentials were not provided"
**Solution**: Include JWT token in Authorization header: `Authorization: JWT <token>`

## Database Indexes

The system includes optimized indexes for:
- User lookups
- Status filtering
- Active membership queries
- Payment reference searches
- Expiration checks

## Future Enhancements

Consider adding:
- Email notifications on status changes
- Automatic payment gateway integration
- Membership renewal reminders
- Proration for upgrades/downgrades
- Gift memberships
- Family/team plans
- Referral codes

## API Documentation

For complete API documentation with request/response examples, see [`API_GUIDE.md`](./API_GUIDE.md).

You can also view interactive documentation at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Support

For issues or questions, refer to:
1. `API_GUIDE.md` - Complete API reference
2. Django Admin - View and manage all data
3. API docs at `/api/docs` - Interactive testing

---

**Created**: January 2026  
**Django Version**: 6.0.1  
**DRF Version**: 3.16.1
