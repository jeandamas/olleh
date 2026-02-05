# OLLEH – Layaway, Savings & Profile APIs

This document describes the APIs added to support the OLLEH Rules Charter and Membership & Layaway Agreement.

**Base URL:** `/api/`  
**Authentication:** JWT (same as memberships). Include header: `Authorization: JWT <token>`  
**Public:** `GET /api/policies/` does not require authentication.

---

## 1. Policies (public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/policies/` | Returns OLLEH policy constants: layaway min/max days, cooling-off hours, service fee rules, penalties, savings-to-layaway limits. No auth required. |

---

## 2. Savings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/savings/balance/` | Get current savings balance (RWF). |
| POST | `/api/savings/deposit/` | Record a deposit. Body: `{ "amount_rwf": <int>, "reference": "<optional>" }`. |
| GET | `/api/savings/transactions/` | List recent savings transactions. |
| GET | `/api/savings/refund-requests/` | List my refund requests. |
| POST | `/api/savings/refund-requests/` | Request a refund (withdrawal). Processed within 7 working days. Body: `{ "amount_rwf": <int>, "reason": "<optional>" }`. |

---

## 3. Layaways

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/layaways/eligibility/` | Get layaway eligibility: active membership, savings balance, layaway limit, current usage, `can_request`, message. |
| GET | `/api/layaways/` | List my layaways. |
| POST | `/api/layaways/` | Create a layaway request. Body: `{ "item_value_rwf": <int>, "item_description": "<optional>", "collection_type": "pickup"|"delivery", "delivery_fee_rwf": 0 }`. Service fee is computed automatically (5,000 RWF if item ≤50k, 10% above). |
| GET | `/api/layaways/{id}/` | Get layaway details. |
| DELETE | `/api/layaways/{id}/` | Cancel layaway. No penalty if within 48h cooling-off; otherwise 10,000 RWF cancellation penalty. |

**Layaway limits (by savings balance):**

- 0 RWF → 30,000 RWF
- 1–30,000 RWF → 2× savings
- 30,001–60,000 RWF → 80,000 RWF
- 60,001+ RWF → 120,000 RWF

**Service & protection fee:**

- Item ≤ 50,000 RWF → 5,000 RWF flat  
- Item > 50,000 RWF → 10%

---

## 4. Profile & measurements

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/me/profile/` | Get my OLLEH profile (olleh_code, reputation, full_name, phone, national_id). |
| PATCH | `/api/me/profile/` | Update full_name, phone, national_id (olleh_code and reputation are read-only). |
| GET | `/api/me/measurements/` | Get my measurements (optional fit assistance). |
| POST | `/api/me/measurements/` | Create or update my measurements. Body: `{ "height_cm", "chest_cm", "waist_cm", "hip_cm", "shoe_size_eu", "notes" }` (all optional). |

---

## 5. Admin-only (Django Admin)

- **Layaway:** Confirm (starts cooling-off), Activate (set 14–30 days), Mark completed, Mark defaulted.
- **Savings:** View/edit accounts and transactions; approve/reject refund requests.
- **Member profile:** Edit OLLEH code, reputation (Starter / Trusted / Elite).

---

## Running migrations

From project root with your virtualenv activated:

```bash
python manage.py migrate users
python manage.py migrate orders
python manage.py migrate savings
```

If using `uv`:

```bash
uv run python manage.py migrate
```

Schema and docs: `/api/schema/`, `/api/docs/`, `/api/redoc/`.
