# RWF Currency Update - Integer Implementation

## Overview

All RWF (Rwandan Franc) amounts have been updated to use **integers only** throughout the codebase. This is because RWF doesn't have subdivisions (no cents or decimals), so storing amounts as integers is more accurate and efficient.

## What Changed

### 1. **Models** (`models.py`)

**Before:**
```python
price = models.DecimalField(max_digits=10, decimal_places=2)
max_order_price = models.DecimalField(max_digits=10, decimal_places=2)
amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
```

**After:**
```python
price = models.PositiveIntegerField(help_text="Price in RWF (Rwandan Francs)")
max_order_price = models.PositiveIntegerField(help_text="Maximum order price in RWF")
amount_paid = models.PositiveIntegerField(null=True, blank=True, help_text="Amount paid in RWF (Rwandan Francs)")
```

### 2. **Serializers** (`serializers.py`)

**Before:**
```python
membership_price = serializers.DecimalField(source="membership.price", max_digits=10, decimal_places=2, read_only=True)
```

**After:**
```python
membership_price = serializers.IntegerField(source="membership.price", read_only=True)
```

### 3. **Sample Data** (`management/commands/create_sample_memberships.py`)

**Before:**
```python
"price": 25000.00,
"max_order_price": 50000.00,
```

**After:**
```python
"price": 25000,
"max_order_price": 50000,
```

### 4. **Tests** (`tests_api.py`)

**Before:**
```python
price=Decimal("25000.00")
amount_paid="25000.00"
```

**After:**
```python
price=25000
amount_paid=25000
```

### 5. **Display Formatting**

Added thousand separators for better readability:
```python
# In models
def __str__(self):
    return f"{self.name} ({self.price:,} RWF)"

# In management command
f"✓ Created membership: {membership.name} ({membership.price:,} RWF)"

# In error messages
f"Amount paid must match the membership price of {membership.price:,} RWF."
```

## Migration

A new migration has been created: `0002_convert_rwf_to_integer.py`

This migration will:
- Convert `Membership.price` from DecimalField to PositiveIntegerField
- Convert `Membership.max_order_price` from DecimalField to PositiveIntegerField
- Convert `UserMembership.amount_paid` from DecimalField to PositiveIntegerField

**To apply the migration:**
```bash
python manage.py migrate memberships
```

### Handling Existing Data

If you have existing data with decimal values (e.g., `25000.00`), Django will automatically convert them to integers during migration. Any fractional amounts will be truncated.

**Example conversions:**
- `25000.00` → `25000`
- `50000.50` → `50000` (fractional part dropped)
- `100000.99` → `100000` (fractional part dropped)

⚠️ **Important:** If you have existing data with fractional RWF amounts, review it before migrating as the decimal portion will be lost.

## API Changes

### Request Format

**Before:**
```json
{
  "membership": 1,
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": "25000.00"
}
```

**After:**
```json
{
  "membership": 1,
  "payment_mode": "mobile_money",
  "payment_reference": "MTN123456789",
  "amount_paid": 25000
}
```

### Response Format

**Before:**
```json
{
  "id": 1,
  "name": "Bronze",
  "price": "25000.00",
  "max_order_price": "50000.00"
}
```

**After:**
```json
{
  "id": 1,
  "name": "Bronze",
  "price": 25000,
  "max_order_price": 50000
}
```

## Benefits

### 1. **Accuracy**
- RWF doesn't have decimal subdivisions
- Integer representation is more accurate for RWF
- No rounding errors

### 2. **Performance**
- Integer operations are faster than decimal operations
- Less memory usage
- More efficient database storage

### 3. **Simplicity**
- Cleaner API responses (no `.00` decimals)
- Easier to work with in JavaScript/frontend
- More intuitive for users (no confusing decimals)

### 4. **Standards Compliance**
- Aligns with how RWF is actually used
- Matches banking and financial practices in Rwanda

## Important Notes

### ✅ DO
- Always use integers for RWF amounts (e.g., `25000`, not `25000.00`)
- Use thousand separators for display (e.g., `25,000 RWF`)
- Validate that amounts are positive integers

### ❌ DON'T
- Don't send decimal values (e.g., `"25000.50"`) - they will be rejected or truncated
- Don't use floats for calculations - use integers only
- Don't assume decimal places exist

## Testing

All tests have been updated to use integer values:

```python
# Old
price=Decimal("25000.00")

# New
price=25000
```

Run the test suite to verify:
```bash
python manage.py test apps.memberships.tests_api
```

## Frontend Integration

If you're building a frontend, ensure:

1. **Send integers in requests:**
```javascript
// Good
{ amount_paid: 25000 }

// Bad
{ amount_paid: "25000.00" }
{ amount_paid: 25000.50 }
```

2. **Display with formatting:**
```javascript
// Format for display
const formatRWF = (amount) => {
  return `${amount.toLocaleString()} RWF`;
};

// Example: 25000 → "25,000 RWF"
```

3. **Input validation:**
```javascript
// Ensure user inputs are integers
const validateAmount = (value) => {
  return Number.isInteger(Number(value)) && Number(value) > 0;
};
```

## Documentation Updates

All documentation has been updated:
- ✅ `API_GUIDE.md` - All examples use integers
- ✅ `README.md` - Updated with integer examples
- ✅ `MEMBERSHIP_IMPLEMENTATION_SUMMARY.md` - Updated references
- ✅ All code comments and docstrings

## Backwards Compatibility

⚠️ **Breaking Change**: This is a breaking change for existing API clients.

If you have existing clients:
1. Update them to send integers instead of decimal strings
2. Update response parsing to handle integers
3. Test thoroughly before deploying

## Rollback

If you need to rollback:

1. Revert the migration:
```bash
python manage.py migrate memberships 0001_initial
```

2. Revert code changes (checkout previous commit)

Note: Any data entered as integers will remain integers if you rollback.

## Questions?

### Q: What if I need to store cents/fractions?
**A:** RWF doesn't have subdivisions. If you absolutely need fractional amounts for other currencies, create separate fields or models for those currencies.

### Q: Will old API requests with decimals still work?
**A:** Django REST Framework will attempt to convert decimal strings to integers by truncating. However, you should update clients to send integers explicitly.

### Q: How do I display large amounts?
**A:** Use Python's format specification: `f"{amount:,} RWF"` which adds thousand separators (e.g., "1,000,000 RWF").

### Q: Can I still use `.00` in the database?
**A:** No, the database schema has changed to INTEGER type. Decimal places are no longer supported for RWF fields.

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Model Field | DecimalField | PositiveIntegerField |
| Python Type | Decimal | int |
| API Format | `"25000.00"` | `25000` |
| Database Type | DECIMAL(10,2) | INTEGER |
| Display Format | `25000.00 RWF` | `25,000 RWF` |

---

**Implementation Date:** January 29, 2026  
**Migration:** `0002_convert_rwf_to_integer.py`  
**Status:** ✅ Complete
