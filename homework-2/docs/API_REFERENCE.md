# 📋 API Reference — Support Ticket System

> **For API Users / Integrators**
> 
> This guide explains how to use the Support Ticket System's APIs. All examples use simple language and include real copy-paste examples.
> 
> **Base URL:** `http://localhost:8000`

---

## 📌 Quick Start

All communication happens over HTTP using JSON. Responses always come back as JSON too.

**Check if the system is running:**
```bash
curl http://localhost:8000/health
```

You should see: `{"status": "healthy"}`

---

## 🎫 Understanding Tickets

A ticket is a customer support request. Each ticket contains:

| Field | Meaning | Example |
|-------|---------|---------|
| **id** | Unique identifier (auto-created) | `123e4567-e89b-12d3-a456-426614174000` |
| **customer_id** | Customer identifier | `CUST-12345` |
| **customer_email** | Customer's email | `john@example.com` |
| **customer_name** | Customer's name | `John Smith` |
| **subject** | Short description (1–200 characters) | `Cannot log in to account` |
| **description** | Detailed explanation (10–2000 characters) | `I tried my password three times...` |
| **category** | Type of issue | `account_access`, `technical_issue`, `billing_question`, `feature_request`, `bug_report`, `other` |
| **priority** | How urgent | `low`, `medium`, `high`, `urgent` |
| **status** | Current state | `new`, `in_progress`, `waiting_customer`, `resolved`, `closed` |
| **created_at** | When ticket was created (auto) | `2026-07-04T10:30:00Z` |
| **updated_at** | When ticket was last changed (auto) | `2026-07-04T10:30:00Z` |
| **resolved_at** | When marked as resolved (optional) | `2026-07-05T14:20:00Z` |
| **assigned_to** | Which team member handles it (optional) | `jane@company.com` |
| **tags** | Labels for organization | `["urgent", "production"]` |

### Where the ticket came from (Metadata)

Each ticket remembers how it was submitted:

| Field | Meaning | Options |
|-------|---------|---------|
| **source** | How was it submitted | `web_form`, `email`, `api`, `chat`, `phone` |
| **browser** | Browser used (if web) | `Chrome`, `Firefox`, etc. (optional) |
| **device_type** | Type of device | `desktop`, `mobile`, `tablet` (optional) |

### Smart classification (optional)

When the system analyzes a ticket, it provides:

| Field | Meaning | Example |
|-------|---------|---------|
| **category** | What category the system thinks it is | `account_access` |
| **priority** | How urgent the system thinks it is | `urgent` |
| **confidence** | How sure the system is (0 = not sure, 1 = very sure) | `0.85` |
| **reasoning** | Why the system thinks this | `Matched keywords: "can't access", "account"` |
| **keywords_found** | Words that helped classify it | `["can't access", "account", "login"]` |
| **manual_override** | Was this changed by a human | `false` |

---

## 📝 Create a Single Ticket

**What it does:** Add one ticket to the system.

**Endpoint:** `POST /tickets`

### Request

```bash
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "customer_email": "alice@company.com",
    "customer_name": "Alice Johnson",
    "subject": "Cannot reset my password",
    "description": "I clicked the forgot password link but never received an email. I have tried 3 times.",
    "category": "account_access",
    "priority": "high",
    "status": "new",
    "assigned_to": "support@company.com",
    "tags": ["urgent", "email_issue"],
    "metadata": {
      "source": "web_form",
      "browser": "Chrome",
      "device_type": "desktop"
    }
  }'
```

**What each field means:**
- `customer_id` — Required. Your internal customer ID (1–100 characters).
- `customer_email` — Required. Valid email address.
- `customer_name` — Required. Customer's full name (1–200 characters).
- `subject` — Required. Brief title (1–200 characters).
- `description` — Required. Full details (10–2000 characters).
- `category` — Optional. Pick one from the list above (defaults to `other`).
- `priority` — Optional. Pick one from the list above (defaults to `medium`).
- `status` — Optional. Pick one from the list above (defaults to `new`).
- `assigned_to` — Optional. Who should handle this.
- `tags` — Optional. List of labels.
- `metadata` — Optional. Where the ticket came from.

### Response (Success)

**Status Code:** `201 Created`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "customer_id": "CUST-001",
  "customer_email": "alice@company.com",
  "customer_name": "Alice Johnson",
  "subject": "Cannot reset my password",
  "description": "I clicked the forgot password link but never received an email. I have tried 3 times.",
  "category": "account_access",
  "priority": "high",
  "status": "new",
  "created_at": "2026-07-04T10:30:00Z",
  "updated_at": "2026-07-04T10:30:00Z",
  "resolved_at": null,
  "assigned_to": "support@company.com",
  "tags": ["urgent", "email_issue"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome",
    "device_type": "desktop"
  },
  "classification": null
}
```

### Auto-Classify When Creating

Add `?auto_classify=true` to have the system analyze and classify the ticket automatically.

```bash
curl -X POST "http://localhost:8000/tickets?auto_classify=true" \
  -H "Content-Type: application/json" \
  -d '{ ... same as above ... }'
```

The response will include a `classification` field:

```json
{
  "...": "all ticket fields...",
  "classification": {
    "category": "account_access",
    "priority": "urgent",
    "confidence": 0.92,
    "reasoning": "Matched keywords: 'password reset', 'cannot access', 'email'",
    "keywords_found": ["password reset", "cannot access", "email"],
    "manual_override": false
  }
}
```

### Error Responses

**Bad request (missing or invalid fields):**
```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "customer_email"],
      "msg": "Input should be a valid email address",
      "input": "not-an-email"
    }
  ]
}
```
Status: `422 Unprocessable Entity`

**Field too short or too long:**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "description"],
      "msg": "String should have at least 10 characters",
      "input": "too short"
    }
  ]
}
```
Status: `422 Unprocessable Entity`

---

## 📥 Upload Tickets in Bulk

**What it does:** Add many tickets at once from a file (CSV, JSON, or XML).

**Endpoint:** `POST /tickets/import`

### Prepare Your File

Choose one format:

#### CSV Format (`tickets.csv`)
```csv
customer_id,customer_email,customer_name,subject,description,category,priority,status
CUST-001,alice@example.com,Alice Johnson,Cannot login,Password not working anymore,account_access,high,new
CUST-002,bob@example.com,Bob Smith,Billing error,Charged twice this month,billing_question,medium,new
CUST-003,carol@example.com,Carol Davis,Feature request,Add dark mode,feature_request,low,new
```

#### JSON Format (`tickets.json`)
```json
[
  {
    "customer_id": "CUST-001",
    "customer_email": "alice@example.com",
    "customer_name": "Alice Johnson",
    "subject": "Cannot login",
    "description": "Password not working anymore",
    "category": "account_access",
    "priority": "high",
    "status": "new"
  },
  {
    "customer_id": "CUST-002",
    "customer_email": "bob@example.com",
    "customer_name": "Bob Smith",
    "subject": "Billing error",
    "description": "Charged twice this month",
    "category": "billing_question",
    "priority": "medium",
    "status": "new"
  }
]
```

#### XML Format (`tickets.xml`)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<tickets>
  <ticket>
    <customer_id>CUST-001</customer_id>
    <customer_email>alice@example.com</customer_email>
    <customer_name>Alice Johnson</customer_name>
    <subject>Cannot login</subject>
    <description>Password not working anymore</description>
    <category>account_access</category>
    <priority>high</priority>
    <status>new</status>
  </ticket>
  <ticket>
    <customer_id>CUST-002</customer_id>
    <customer_email>bob@example.com</customer_email>
    <customer_name>Bob Smith</customer_name>
    <subject>Billing error</subject>
    <description>Charged twice this month</description>
    <category>billing_question</category>
    <priority>medium</priority>
    <status>new</status>
  </ticket>
</tickets>
```

### Upload the File

```bash
curl -X POST http://localhost:8000/tickets/import \
  -F "file=@tickets.csv"
```

Or with auto-classification:

```bash
curl -X POST "http://localhost:8000/tickets/import?auto_classify=true" \
  -F "file=@tickets.csv"
```

### Response (Success)

**Status Code:** `200 OK`

```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "errors": [],
  "created_ticket_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234e5678-e89b-12d3-a456-426614174001",
    "345e6789-e89b-12d3-a456-426614174002"
  ]
}
```

**What it means:**
- `total` — How many tickets were in the file.
- `successful` — How many were created successfully.
- `failed` — How many had problems.
- `errors` — Details about any problems.
- `created_ticket_ids` — IDs of the new tickets.

### Example with Some Errors

```json
{
  "total": 3,
  "successful": 2,
  "failed": 1,
  "errors": [
    {
      "record_index": 2,
      "identifier": "CUST-003",
      "message": "Invalid email address: not-an-email"
    }
  ],
  "created_ticket_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234e5678-e89b-12d3-a456-426614174001"
  ]
}
```

### Error Responses

**File too large:**
```json
{
  "detail": "File exceeds maximum size of 10485760 bytes"
}
```
Status: `400 Bad Request`

**Bad file format:**
```json
{
  "detail": "Invalid CSV structure: missing required columns"
}
```
Status: `400 Bad Request`

---

## 📖 Get a List of Tickets

**What it does:** Get all tickets (with optional filtering).

**Endpoint:** `GET /tickets`

### Basic Request

```bash
curl http://localhost:8000/tickets
```

### Filter by Category

```bash
curl "http://localhost:8000/tickets?category=account_access"
```

### Filter by Priority

```bash
curl "http://localhost:8000/tickets?priority=urgent"
```

### Filter by Status

```bash
curl "http://localhost:8000/tickets?status=new"
```

### Combine Filters

```bash
curl "http://localhost:8000/tickets?category=account_access&priority=urgent&status=new"
```

### Response

**Status Code:** `200 OK`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "customer_id": "CUST-001",
    "customer_email": "alice@company.com",
    "customer_name": "Alice Johnson",
    "subject": "Cannot reset my password",
    "description": "I clicked the forgot password link but never received an email.",
    "category": "account_access",
    "priority": "high",
    "status": "new",
    "created_at": "2026-07-04T10:30:00Z",
    "updated_at": "2026-07-04T10:30:00Z",
    "resolved_at": null,
    "assigned_to": "support@company.com",
    "tags": ["urgent"],
    "metadata": {
      "source": "web_form",
      "browser": "Chrome",
      "device_type": "desktop"
    },
    "classification": null
  }
]
```

---

## 🔍 Get One Ticket

**What it does:** Get detailed information about a single ticket.

**Endpoint:** `GET /tickets/{id}`

```bash
curl http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000
```

### Response (Success)

**Status Code:** `200 OK`

Same format as the ticket shown above.

### Error Response

**Ticket not found:**
```json
{
  "detail": "Ticket not found"
}
```
Status: `404 Not Found`

---

## ✏️ Update a Ticket

**What it does:** Change information about a ticket (status, assigned person, etc).

**Endpoint:** `PUT /tickets/{id}`

### Update Just the Status

```bash
curl -X PUT http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

### Update Assignment

```bash
curl -X PUT http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_to": "jane@company.com"
  }'
```

### Mark as Resolved

```bash
curl -X PUT http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved"
  }'
```

### Change Category or Priority

```bash
curl -X PUT http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "category": "billing_question",
    "priority": "urgent"
  }'
```

### Response

**Status Code:** `200 OK`

Returns the updated ticket with all fields.

### Error Responses

**Ticket not found:**
```json
{
  "detail": "Ticket not found"
}
```
Status: `404 Not Found`

**Invalid field value:**
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "status"],
      "msg": "Input should be 'new', 'in_progress', 'waiting_customer', 'resolved' or 'closed'",
      "input": "invalid_status"
    }
  ]
}
```
Status: `422 Unprocessable Entity`

---

## 🗑️ Delete a Ticket

**What it does:** Remove a ticket from the system (permanent).

**Endpoint:** `DELETE /tickets/{id}`

```bash
curl -X DELETE http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000
```

### Response

**Status Code:** `204 No Content` (no response body)

If successful, you get nothing back, which is normal.

### Error Response

**Ticket not found:**
```json
{
  "detail": "Ticket not found"
}
```
Status: `404 Not Found`

---

## 🤖 Let the System Classify a Ticket

**What it does:** The system analyzes a ticket's subject and description and suggests a category and priority level.

**Endpoint:** `POST /tickets/{id}/auto-classify`

```bash
curl -X POST http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000/auto-classify
```

### Response

**Status Code:** `200 OK`

```json
{
  "category": "account_access",
  "priority": "urgent",
  "confidence": 0.92,
  "reasoning": "Matched keywords: 'cannot access', 'account', 'password'",
  "keywords_found": ["cannot access", "account", "password"],
  "manual_override": false
}
```

**What it means:**
- `category` — What type of issue it is.
- `priority` — How urgent the system thinks it is.
- `confidence` — How sure the system is (0–1, higher is more confident).
- `reasoning` — Why the system made this decision.
- `keywords_found` — Words it found that helped it decide.
- `manual_override` — Whether a human changed this before (false = not changed).

### Error Response

**Ticket not found:**
```json
{
  "detail": "Ticket not found"
}
```
Status: `404 Not Found`

---

## 🔄 Status Codes Explained

| Code | Meaning | When You See This |
|------|---------|-------------------|
| **200** | Success | Your request worked. |
| **201** | Created | A new ticket was created. |
| **204** | No Content | Deletion succeeded (no response body). |
| **400** | Bad Request | Your file or request had an error (not JSON format, too large, etc.). |
| **404** | Not Found | Ticket ID doesn't exist. |
| **422** | Invalid Data | A field has the wrong type or value (wrong email format, text too short, unknown category, etc.). |

---

## 💡 Common Workflows

### Create a ticket and let the system classify it

```bash
curl -X POST "http://localhost:8000/tickets?auto_classify=true" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-005",
    "customer_email": "test@example.com",
    "customer_name": "Test User",
    "subject": "I cannot access my account",
    "description": "My password is not working and I cannot reset it",
    "metadata": {"source": "web_form"}
  }'
```

### Upload many tickets and classify them all

```bash
curl -X POST "http://localhost:8000/tickets/import?auto_classify=true" \
  -F "file=@tickets.csv"
```

### Find all urgent account access issues that are new

```bash
curl "http://localhost:8000/tickets?category=account_access&priority=urgent&status=new"
```

### Reassign a ticket and change its status

```bash
curl -X PUT http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_to": "support_team@company.com",
    "status": "in_progress"
  }'
```

### Classify an existing ticket

```bash
curl -X POST http://localhost:8000/tickets/123e4567-e89b-12d3-a456-426614174000/auto-classify
```

---

## 🎯 Tips for Success

1. **Email format:** Always use valid email addresses.
2. **Text length:** Subjects must be 1–200 characters; descriptions must be 10–2000.
3. **Empty categories:** The system defaults to `other` if you don't pick a category.
4. **File size:** Keep upload files under 10 MB.
5. **Try the test command:** Visit `http://localhost:8000/docs` in your browser to test all endpoints interactively.

---

## 📞 Need Help?

- Check that the system is running: `curl http://localhost:8000/health`
- Read the error message carefully — it usually explains what's wrong.
- Verify your JSON is valid (use an online JSON validator).
- Check that file formats match the samples above.
