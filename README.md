# 🌸 Floranova (فلورانوا)

> **Artisan Floral Operations & High-End E-Commerce Platform**  
> *Production-grade asynchronous floral atelier engine built with Python 3.13, FastAPI, Async SQLAlchemy 2.0, Jalali delivery slot scheduling, and a corporate operations dashboard.*

---

## 📌 Overview

**Floranova** is a specialized e-commerce and workshop management system tailored for the delicate domain of artisan floristry and luxury flower delivery. Unlike generic e-commerce stores, floristry requires handling **perishable living stock**, **strictly scheduled delivery slots**, **bespoke card and ribbon personalization**, and **multi-stage craftsmanship quality checks** before courier dispatch.

Floranova provides:
1. **Customer Boutique Storefront**: Interactive bouquet customizer, greeting card calligraphy authoring, surprise gift flags, and Jalali delivery slot selection.
2. **Real-time Order Tracker**: Transparent public tracking timeline (`/track/{tracking_code}`) with masked recipient identity and florist QA arrangement photos.
3. **Corporate Atelier Admin Dashboard**: Silent-refresh operations board, real-time KPI metrics, finite state machine order transitions, and cold storage batch freshness monitoring.
4. **Complete Asynchronous REST API**: Documented under `/docs` with JWT RBAC authentication, Pydantic v2 validation, and transactional integrity.

---

## 🏛️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT / STOREFRONT INTERFACE                   │
│   • Boutique Catalog Browsing       • Bespoke Bouquet Customizer      │
│   • Surprise Gift Flags & Cards     • Jalali Delivery Slot Picker     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       FASTAPI APPLICATION CORE                         │
│  ┌─────────────────────────┬─────────────────────────┬──────────────┐  │
│  │ Catalog & Customization │ Slot Capacity Engine    │ Order FSM    │  │
│  │ (/api/v1/catalog)       │ (/api/v1/slots)         │ (/api/v1/..) │  │
│  └─────────────────────────┴─────────────────────────┴──────────────┘  │
│  ┌─────────────────────────┬─────────────────────────┬──────────────┐  │
│  │ JWT Security & RBAC     │ Cold Storage Freshness  │ Silent Admin │  │
│  │ (Admin/Florist/Client)  │ (/api/v1/inventory)     │ Dashboard    │  │
│  └─────────────────────────┴─────────────────────────┴──────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Async Sessions (SQLAlchemy 2.0)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  DATABASE LAYER (SQLite WAL / PostgreSQL)              │
│   • users              • categories           • products               │
│   • addon_items        • delivery_slots       • flower_batches         │
│   • orders             • order_items          • order_addons           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Domain Features

### 1. 🌿 Perishable Stock & Cold Storage Freshness Tracking
Flowers degrade every hour. The inventory subsystem tracks incoming flower shipments as distinct freshness batches (`FlowerFreshnessBatch`):
- Received date, stem count, unit cost.
- Shelf-life countdown in days (`max_freshness_days`).
- Automated status flags: `FRESH` (سالم و شاداب) ➔ `NEEDS_ROTATION` (نزدیک به افت کیفیت) ➔ `EXPIRED_WASTED` (ضایعات).
- Real-time Spoilage Risk metric computed across atelier storage.

### 2. 🕒 Jalali Delivery Slot Capacity Engine
Floral deliveries are time-critical (anniversaries, celebrations, surprise moments).
- Dynamic date availability in Persian Solar Hijri (`jdatetime`).
- Time window booking (`09:00 - 13:00`, `13:00 - 17:00`, `17:00 - 21:00`).
- Strict slot capacity bounds (`max_capacity=8` per window) to prevent florist overload and late deliveries.

### 3. 💌 Bespoke Gifting Suite
- **Surprise Delivery Toggle (`is_surprise`)**: Prohibits courier from calling the recipient before arriving at the address.
- **Greeting Card & Ribbon Customizer**: Stores custom calligraphy text and sender pseudonym.
- **Curated Add-ons**: Belgian artisan chocolates, hand-crafted ceramic vases, helium celebration balloons.

### 4. 🔄 Strict Finite State Machine (Order FSM)
Orders transition deterministically through operations:
$$\text{PENDING} \longrightarrow \text{CONFIRMED} \longrightarrow \text{ARRANGING} \longrightarrow \text{QUALITY\_APPROVED} \longrightarrow \text{OUT\_FOR\_DELIVERY} \longrightarrow \text{DELIVERED}$$
- Florists upload or attach quality inspection photos before dispatch.
- Every state shift is recorded into `status_history` JSON with Persian timestamps and actor attribution.

### 5. 🖥️ Silent Operations Admin Dashboard
Adheres strictly to modern design standards:
- White corporate theme (`#ffffff` / `#f8fafc`) with slate typography.
- High-density KPI cards: Daily Revenue, Pending Studio Arrangements, Cold Storage Stems, Spoilage Risk %.
- Quick status advance buttons in live orders table.
- Non-disruptive background polling every 15 seconds (no noisy toasts).

---

## 🚀 Quickstart

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or standard Python `venv`
- Docker (optional)

### 1. Installation with `uv`

```bash
git clone https://github.com/mdy79/floranova.git
cd floranova

# Install all dependencies including dev tools
uv sync

# Run database schema migrations & sample seed catalog
uv run python -m floranova.scripts.seed_data
```

### 2. Run Application

```bash
# Start ASGI server
uv run uvicorn floranova.main:app --host 0.0.0.0 --port 8000 --reload
```

Navigate to:
- **Storefront**: [http://localhost:8000/](http://localhost:8000/)
- **Order Tracker**: [http://localhost:8000/track/FN-819241](http://localhost:8000/track/FN-819241)
- **Atelier Admin Dashboard**: [http://localhost:8000/admin](http://localhost:8000/admin)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔐 Default Seed Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Admin** | `admin@floranova.ir` | `Floranova@2026!` | Full atelier & financial controls |
| **Florist** | `florist@floranova.ir` | `Florist@2026!` | Order status transitions & inventory |
| **Customer** | `mehrad@floranova.ir` | `Mehrad@2026!` | Storefront & personal order tracking |

---

## 🧪 Test Suite

Run the full asynchronous test suite with `pytest`:

```bash
uv run pytest -v
```

Output:
```text
tests/test_auth.py::test_register_and_login_flow PASSED                  [ 14%]
tests/test_auth.py::test_duplicate_email_registration_rejected PASSED    [ 28%]
tests/test_auth.py::test_invalid_login_credentials PASSED                [ 42%]
tests/test_catalog.py::test_catalog_categories_and_products PASSED       [ 57%]
tests/test_inventory.py::test_inventory_batches_and_summary PASSED       [ 71%]
tests/test_inventory.py::test_unauthorized_inventory_access_blocked PASSED [ 85%]
tests/test_orders.py::test_checkout_and_lifecycle_flow PASSED            [100%]
============================== 7 passed in 5.14s ===============================
```

---

## 🐳 Docker Deployment

Run with Docker Compose:

```bash
docker compose up -d --build
```

---

## 📡 API Reference Summary

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new customer account | Public |
| `POST` | `/api/v1/auth/login` | Obtain OAuth2 JWT bearer token | Public |
| `GET` | `/api/v1/catalog/products` | Browse flower arrangements with filters | Public |
| `GET` | `/api/v1/slots/dates` | Get available Jalali delivery dates | Public |
| `GET` | `/api/v1/slots/windows` | Check time slot capacity for a date | Public |
| `POST` | `/api/v1/orders/checkout` | Submit order with slot reservation | Public/User |
| `GET` | `/api/v1/orders/track/{code}` | Public order tracking with masked data | Public |
| `GET` | `/api/v1/orders/manage/list` | Admin/Florist order management board | Staff |
| `POST` | `/api/v1/orders/manage/{id}/transition` | Advance order state in FSM | Staff |
| `GET` | `/api/v1/inventory/batches` | List cold storage flower batches | Staff |
| `GET` | `/api/v1/admin/stats` | Retrieve live operations & revenue KPIs | Admin |

---

## 📜 License

Open source under the [MIT License](LICENSE).
