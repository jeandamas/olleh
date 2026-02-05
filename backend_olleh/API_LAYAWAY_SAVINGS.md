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
| POST | `/api/layaways/{id}/images/` | Upload an item image for this layaway. See **Image uploads** below. |
| GET | `/api/layaways/{id}/payments/` | List payments reported for this layaway (installments). |
| POST | `/api/layaways/{id}/payments/` | Report a payment (member). Body: `{ "amount_rwf": <int>, "reference": "<optional>" }`. Staff confirm separately; when confirmed, amount is applied and layaway may be marked completed if paid in full. |
| POST | `/api/layaways/{id}/payments/{payment_id}/confirm/` | **Staff only.** Confirm a reported payment. Applies amount to layaway; if paid in full, layaway status becomes completed. |

**Payments (installments)**

- Members report payments via `POST /api/layaways/{id}/payments/` (amount_rwf, optional reference). Payments have no status field; they are either unconfirmed (pending staff) or confirmed (confirmed_at set by staff).
- Staff confirm via `POST /api/layaways/{id}/payments/{payment_id}/confirm/`. On confirm: layaway `amount_paid_rwf` is increased; if total paid ≥ layaway total and layaway is active, the layaway is marked **completed**.

**Image uploads**

Use **multipart/form-data** for `POST /api/layaways/{id}/images/`:

| Field   | Type   | Required | Description |
|--------|--------|----------|-------------|
| `image` | file   | Yes      | Image file (JPEG, PNG, GIF, WebP). |
| `caption` | string | No    | Optional caption. |
| `order` | integer | No     | Display order (lower first). Default 0. |

Example with `curl`:

```bash
curl -X POST "https://your-api/api/layaways/1/images/" \
  -H "Authorization: JWT <token>" \
  -F "image=@/path/to/photo.jpg" \
  -F "caption=Front view"
```

Responses: `201 Created` with the new image object (`id`, `url`, `caption`, `order`, `created_at`). Image URLs are absolute.

**Layaway limits (by membership tier):**

- Basic: max 30,000 RWF per layaway
- Premium: max 50,000 RWF per layaway

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
