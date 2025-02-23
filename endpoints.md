# API Documentation

## Admin Routes

### Approve User
**URL:** `/approve-user`

**Method:** `POST`

**Auth Required:** Yes (Role: admin)

**Description:** Approves a user.

#### Request Body:
```json
{
  "email": "user@example.com"
}
```

#### Responses:
- `200 OK`: User approved
- `404 Not Found`: User not found
- `401 Unauthorized`: Invalid token or insufficient permissions

---

## Auth Routes

### Register
**URL:** `/register`

**Method:** `POST`

**Auth Required:** No

**Description:** Registers a new user.

#### Request Body:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Responses:
- `201 Created`: User registered successfully
- `400 Bad Request`: User already exists

### Login
**URL:** `/login`

**Method:** `POST`

**Auth Required:** No

**Description:** Logs in a user.

#### Request Body:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Responses:
- `200 OK`: Returns a JWT token
- `401 Unauthorized`: Invalid credentials or user not approved

---

## Confirmation Routes

### Confirm Participation
**URL:** `/<token>`

**Method:** `GET`

**Auth Required:** No

**Description:** Confirms participation in an event.

#### Responses:
- `200 OK`: Renders confirmation form
- `404 Not Found`: Event not found
- `400 Bad Request`: Invalid token or event has already started

### Submit Confirmation
**URL:** `/submit-confirmation`

**Method:** `POST`

**Auth Required:** No

**Description:** Submits the confirmation status for an event.

#### Request Body:
```json
{
  "token": "token",
  "status": "confirmed",
  "justification": "optional justification"
}
```

#### Responses:
- `200 OK`: Renders success page
- `400 Bad Request`: Invalid token or other error

---

## Event Routes

### Create Event
**URL:** `/`

**Method:** `POST`

**Auth Required:** Yes (Roles: user, admin)

**Description:** Creates a new event.

#### Request Body:
```json
{
  "name": "Event Name",
  "description": "Event Description", (Optional)
  "location": "Event Location", (Optional)
  "confirmation_deadline" : "2023-11-01T10:00:00", (Optional),
  "confirmation_change_deadline" : "2023-11-15T10:00:00", (Optional),
  "start_datetime": "2023-12-01T10:00:00",
  "end_datetime": "2023-12-01T12:00:00",
  "template_id": "template_id"
}
```

#### Responses:
- `201 Created`: Event created successfully
- `400 Bad Request`: Error creating event

### Send Invitations
**URL:** `/<event_id>/send-invitations`

**Method:** `POST`

**Auth Required:** Yes (Roles: user, admin)

**Description:** Sends invitations for an event.

#### Request Body:
```json
{
  "emails": ["invitee1@example.com", "invitee2@example.com"]
}
```

#### Responses:
- `200 OK`: Invitations sent successfully
- `400 Bad Request`: Emails list is required
- `404 Not Found`: Event not found

### Get Events
**URL:** `/`

**Method:** `GET`

**Auth Required:** Yes (Roles: user, admin)

**Description:** Retrieves all events.

#### Responses:
- `200 OK`: Returns a list of events

---

## Mail Template Routes

### Create Mail Template
**URL:** `/`

**Method:** `POST`

**Auth Required:** No

**Description:** Creates a new mail template.

#### Request Body:
```json
{
  "name": "Template Name",
  "subject": "Template Subject",
  "template_body_file": "HTML content of the template"
}
```

#### Responses:
- `201 Created`: Template created successfully
- `400 Bad Request`: Missing required fields

---

## Responses Routes

### Get Responses
**URL:** `/<event_id>`

**Method:** `GET`

**Auth Required:** Yes (Roles: user, admin)

**Description:** Retrieves responses for an event.

#### Responses:
- `200 OK`: Returns a list of responses
