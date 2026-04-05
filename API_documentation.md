# Finance Management Dashboard - API Documentation

## Base URL
```
http://localhost:8000/api
```

## Interactive API Testing
**Postman Collection:** [Finance Management API - Postman Documentation](https://bold-desert-872591.postman.co/workspace/705bce77-0211-42ae-8f76-18e04ebf790c/documentation/40456623-6890b617-93a8-4782-bd2f-b75498a947fb)

Use the Postman collection above for interactive API testing with pre-built requests and examples.

## Authentication
All endpoints (except login) require JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer {access_token}
```

---

## Table of Contents
1. [Authentication](#authentication)
2. [Financial Records](#financial-records)
3. [Dashboard Analytics](#dashboard-analytics)
4. [Error Codes](#error-codes)

---

## Authentication

### Login (Obtain JWT Token)

**Endpoint:** `POST /authentication/`

**Description:** Authenticate user with email and password. Returns JWT access and refresh tokens.

**Request Body:**
```json
{
  "email": "demo.admin@gmail.com",
  "password": "demo@admin2026"
}
```

**Response (200 OK):**
```json
{
  "Status": true,
  "Message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "uuid": "238b76d3-98a1-4908-9b78-09f72b319b0d",
      "email": "demo.admin@gmail.com",
      "role": "admin"
    }
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "Status": false,
  "Message": "Invalid email or password"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/authentication/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo.admin@gmail.com",
    "password": "demo@admin2026"
  }'
```

---

## Financial Records

### Get All Records (with Filtering)

**Endpoint:** `GET /financial-records/records/`

**Authentication:** Required (Viewer+)

**Description:** Retrieve financial records with advanced filtering, sorting, and pagination.

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by category (case-insensitive) | `?category=salary` |
| `type` | string | Filter by type (income/expense) | `?type=income` |
| `date_from` | date | Start date filter (YYYY-MM-DD) | `?date_from=2026-01-01` |
| `date_to` | date | End date filter (YYYY-MM-DD) | `?date_to=2026-04-03` |
| `amount_min` | decimal | Minimum amount filter | `?amount_min=5000` |
| `amount_max` | decimal | Maximum amount filter | `?amount_max=100000` |
| `search` | string | Text search (category/notes/type) | `?search=salary` |
| `sort_by` | string | Sort field (date/amount/created_at) | `?sort_by=date` |
| `order` | string | Sort order (asc/desc) | `?order=desc` |
| `page` | integer | Page number (default: 1) | `?page=1` |
| `limit` | integer | Records per page (default: 10) | `?limit=10` |

**Response (200 OK):**
```json
{
  "Status": true,
  "Message": "Financial Records Retrieved",
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_count": 45,
    "total_pages": 5
  },
  "data": [
    {
      "uuid": "238b76d3-98a1-4908-9b78-09f72b319b0d",
      "created_by": "admin-uuid",
      "type_of_record": "income",
      "category": "salary",
      "amount": "85000.00",
      "date": "2026-01-05",
      "notes": "January salary credit",
      "is_deleted": false,
      "created_at": "2026-01-05T10:30:00Z",
      "updated_at": "2026-01-05T10:30:00Z"
    },
    {
      "uuid": "456c89d2-ab12-4908-9b78-09f72b319b0e",
      "created_by": "admin-uuid",
      "type_of_record": "expense",
      "category": "food",
      "amount": "3500.00",
      "date": "2026-01-07",
      "notes": "Weekly grocery run",
      "is_deleted": false,
      "created_at": "2026-01-07T14:20:00Z",
      "updated_at": "2026-01-07T14:20:00Z"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/financial-records/records/?category=salary&type=income&sort_by=amount&order=desc&page=1&limit=10" \
  -H "Authorization: Bearer {access_token}"
```

---

### Search Records (Advanced)

**Endpoint:** `GET /financial-records/search/`

**Authentication:** Required (Viewer+)

**Description:** Dedicated endpoint for advanced search with all filter capabilities. Same parameters as `/records/` but with detailed filter documentation.

**Query Parameters:** Same as `/records/` endpoint above.

**Response (200 OK):**
```json
{
  "Status": true,
  "Message": "Search Results Retrieved",
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_count": 15,
    "total_pages": 2
  },
  "filters_applied": {
    "category": "salary",
    "type": "income",
    "date_from": "2026-01-01",
    "date_to": "2026-04-03",
    "amount_min": "50000",
    "amount_max": null,
    "search": null,
    "sort_by": "date",
    "order": "desc"
  },
  "data": [
    {
      "uuid": "238b76d3-98a1-4908-9b78-09f72b319b0d",
      "created_by": "admin-uuid",
      "type_of_record": "income",
      "category": "salary",
      "amount": "85000.00",
      "date": "2026-01-05",
      "notes": "January salary credit",
      "is_deleted": false,
      "created_at": "2026-01-05T10:30:00Z",
      "updated_at": "2026-01-05T10:30:00Z"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/financial-records/search/?type=expense&amount_min=1000&amount_max=5000&sort_by=date&order=desc" \
  -H "Authorization: Bearer {access_token}"
```

---

### Add New Record

**Endpoint:** `POST /financial-records/add-record/`

**Authentication:** Required (Admin only)

**Permission:** `IsAdminOrNot`

**Description:** Create a new financial record. Only admin users can add records.

**Request Body:**
```json
{
  "type_of_record": "income",
  "category": "salary",
  "amount": "85000.00",
  "date": "2026-04-03",
  "notes": "April salary payment",
  "created_by": "238b76d3-98a1-4908-9b78-09f72b319b0d"
}
```

**Required Fields:**
- `type_of_record` (string): "income" or "expense"
- `category` (string): salary, food, rent, investment, other
- `amount` (decimal): Positive number with up to 2 decimal places
- `date` (date): YYYY-MM-DD format
- `created_by` (UUID): UUID of the user creating the record

**Optional Fields:**
- `notes` (string): Additional notes or description

**Response (201 Created):**
```json
{
  "Status": true,
  "Message": "Financial Record Added",
  "data": {
    "uuid": "789a12b3-cd45-4908-9b78-09f72b319b0f",
    "created_by": "238b76d3-98a1-4908-9b78-09f72b319b0d",
    "type_of_record": "income",
    "category": "salary",
    "amount": "85000.00",
    "date": "2026-04-03",
    "notes": "April salary payment",
    "is_deleted": false,
    "created_at": "2026-04-03T12:00:00Z",
    "updated_at": "2026-04-03T12:00:00Z"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "Status": false,
  "Message": {
    "amount": ["Ensure this value is greater than or equal to 0.01"],
    "category": ["Invalid category"]
  }
}
```

**Response (403 Forbidden):**
```json
{
  "Status": false,
  "Message": "You do not have permission to perform this action."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/financial-records/add-record/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "type_of_record": "income",
    "category": "salary",
    "amount": "85000.00",
    "date": "2026-04-03",
    "notes": "April salary payment",
    "created_by": "238b76d3-98a1-4908-9b78-09f72b319b0d"
  }'
```

---

### Update Record

**Endpoint:** `PATCH /financial-records/update-record/`

**Authentication:** Required (Admin only)

**Permission:** `IsAdminOrNot`

**Description:** Update an existing financial record. UUID must be sent in request body (not URL).

**Request Body:**
```json
{
  "uuid": "789a12b3-cd45-4908-9b78-09f72b319b0f",
  "type_of_record": "income",
  "category": "salary",
  "amount": "90000.00",
  "date": "2026-04-03",
  "notes": "Updated April salary",
  "created_by": "238b76d3-98a1-4908-9b78-09f72b319b0d"
}
```

**Required Fields:**
- `uuid` (UUID): UUID of the record to update
- At least one field to update (all fields are optional except uuid)

**Response (200 OK):**
```json
{
  "Status": true,
  "Message": "Financial Record Updated",
  "data": {
    "uuid": "789a12b3-cd45-4908-9b78-09f72b319b0f",
    "created_by": "238b76d3-98a1-4908-9b78-09f72b319b0d",
    "type_of_record": "income",
    "category": "salary",
    "amount": "90000.00",
    "date": "2026-04-03",
    "notes": "Updated April salary",
    "is_deleted": false,
    "created_at": "2026-04-03T12:00:00Z",
    "updated_at": "2026-04-03T14:30:00Z"
  }
}
```

**Response (404 Not Found):**
```json
{
  "Status": false,
  "Message": "Financial Record Not Found"
}
```

**Response (403 Forbidden):**
```json
{
  "Status": false,
  "Message": "You do not have permission to perform this action."
}
```

**cURL Example:**
```bash
curl -X PATCH http://localhost:8000/api/financial-records/update-record/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "789a12b3-cd45-4908-9b78-09f72b319b0f",
    "amount": "90000.00",
    "notes": "Updated April salary"
  }'
```

---

### Delete Record

**Endpoint:** `DELETE /financial-records/delete-record/`

**Authentication:** Required (Admin only)

**Permission:** `IsAdminOrNot`

**Description:** Soft delete a financial record (marks as deleted, not permanently removed).

**Request Body:**
```json
{
  "uuid": "789a12b3-cd45-4908-9b78-09f72b319b0f"
}
```

**Required Fields:**
- `uuid` (UUID): UUID of the record to delete

**Response (200 OK):**
```json
{
  "Status": true,
  "Message": "Financial Record Deleted"
}
```

**Response (404 Not Found):**
```json
{
  "Status": false,
  "Message": "Financial Record Not Found"
}
```

**Response (403 Forbidden):**
```json
{
  "Status": false,
  "Message": "You do not have permission to perform this action."
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/financial-records/delete-record/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "789a12b3-cd45-4908-9b78-09f72b319b0f"
  }'
```

---

## Dashboard Analytics

### Get Dashboard KPIs

**Endpoint:** `GET /financial-records/dashboard-kpi/`

**Authentication:** Required (Viewer+)

**Permission:** `IsAuthenticated`, `IsViewerOrAbove`

**Description:** Retrieve comprehensive dashboard analytics including KPIs, category breakdown, trends, and statistics.

**Response (200 OK):**
```json
{
  "Status": true,
  "Message": "Dashboard Summary Retrieved",
  "data": {
    "kpis": {
      "total_income": 250000.00,
      "total_expense": 65000.00,
      "net_balance": 185000.00,
      "current_month_income": 85000.00,
      "current_month_expense": 12000.00,
      "current_month_balance": 73000.00
    },
    "category_breakdown": [
      {
        "category": "salary",
        "type": "income",
        "count": 3,
        "amount": 240000.00
      },
      {
        "category": "food",
        "type": "expense",
        "count": 12,
        "amount": 35000.00
      },
      {
        "category": "rent",
        "type": "expense",
        "count": 3,
        "amount": 30000.00
      }
    ],
    "top_categories": [
      {
        "category": "salary",
        "amount": 240000.00
      },
      {
        "category": "investment",
        "amount": 10000.00
      },
      {
        "category": "rent",
        "amount": 30000.00
      },
      {
        "category": "food",
        "amount": 35000.00
      },
      {
        "category": "other",
        "amount": 5000.00
      }
    ],
    "recent_transactions": [
      {
        "date": "2026-04-03",
        "category": "salary",
        "type": "income",
        "amount": 85000.00,
        "notes": "April salary payment"
      },
      {
        "date": "2026-04-02",
        "category": "food",
        "type": "expense",
        "amount": 3500.00,
        "notes": "Grocery shopping"
      }
    ],
    "ratios": {
      "income_percentage": 79.36,
      "expense_percentage": 20.64
    },
    "statistics": {
      "total_transactions": 45,
      "average_transaction_amount": 7.11,
      "most_frequent_category": "food"
    }
  }
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/financial-records/dashboard-kpi/ \
  -H "Authorization: Bearer {access_token}"
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful. Data returned. |
| 201 | Created | Resource created successfully. |
| 400 | Bad Request | Invalid input, missing fields, or validation error. |
| 401 | Unauthorized | Missing or invalid JWT token. |
| 403 | Forbidden | Authenticated but insufficient permissions (e.g., non-admin trying to create record). |
| 404 | Not Found | Record doesn't exist or has been soft-deleted. |
| 500 | Server Error | Unexpected server error. |

### Error Response Format

All error responses follow this format:
```json
{
  "Status": false,
  "Message": "Error description or validation errors"
}
```

### Common Error Scenarios

**1. Missing Authentication Token**
```json
{
  "Status": false,
  "Message": "Authentication credentials were not provided."
}
```

**2. Invalid Token**
```json
{
  "Status": false,
  "Message": "Given token is invalid for any token type"
}
```

**3. Insufficient Permissions**
```json
{
  "Status": false,
  "Message": "You do not have permission to perform this action."
}
```

**4. Validation Error**
```json
{
  "Status": false,
  "Message": {
    "amount": ["Ensure this value is greater than or equal to 0.01"],
    "date": ["Invalid date format"]
  }
}
```

**5. Record Not Found**
```json
{
  "Status": false,
  "Message": "Financial Record Not Found"
}
```

---

## Rate Limiting & Performance Notes

- Current implementation: No rate limiting (can be added in future)
- Pagination: Default 10 records per page, max configurable via `limit` parameter
- Soft deletes: All queries automatically exclude deleted records
- Large datasets: Use `limit` parameter to optimize response time

---

## Demo Accounts

Test the API with these demo accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | demo.admin@gmail.com | demo@admin2026 |
| Analyst | demo.analyst@gmail.com | demo@analyst2026 |
| Viewer | demo.viewer@gmail.com | demo@viewer2026 |

---

## Testing Workflow

1. **Login** to get JWT token
2. **Use token** in headers for subsequent requests
3. **Try filtering** with different parameters
4. **Test permissions** with different role accounts
5. **Verify errors** with invalid data

---

**Last Updated:** April 3, 2026 | **API Version:** v1 (Stable)
