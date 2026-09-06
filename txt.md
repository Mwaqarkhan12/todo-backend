




Absolutely. These are mostly **web application authentication and security concepts**. I’ll explain them from beginner level, with examples and how they connect together.

---

## 1. Password Policy

A **password policy** defines the rules users must follow when creating a password.

For example:

* Minimum 8–12 characters
* At least one uppercase letter
* At least one lowercase letter
* At least one number
* At least one special character
* Password cannot be the same as the email
* Prevent commonly used passwords

### Example

Bad:

```text
password
12345678
qwerty
john123
```

Better:

```text
Blue!River92Moon
```

### Why?

Weak passwords are easy to guess or crack. A password policy makes account compromise harder.

**Important:** Password complexity is only one part of password security. You should also use secure password hashing such as **Argon2id**, **bcrypt**, or **scrypt**, rather than storing passwords directly.

---

# 2. OTP Expires / Resend

**OTP = One-Time Password.**

You commonly see this when:

```text
Enter the 6-digit code sent to your email.
```

For example:

```text
OTP: 481293
Expires in 5 minutes.
```

### OTP expiration

An OTP should have a short lifetime.

For example:

```text
OTP created: 7:00 PM
Expires:     7:05 PM
```

After that:

```text
481293 → INVALID
```

This prevents someone from using an old OTP.

### Resend OTP

If the user doesn't receive the OTP, they can request another one.

But you shouldn't allow:

```text
Resend
Resend
Resend
Resend
Resend
...
```

without limits.

Instead:

```text
Resend OTP → wait 30 seconds
```

and perhaps limit the number of OTPs per hour/day.

### Good OTP system

```text
Generate random OTP
       ↓
Store hashed OTP + expiry time
       ↓
Send OTP
       ↓
User enters OTP
       ↓
Check expiry
       ↓
Check attempts
       ↓
Verify
       ↓
Invalidate OTP
```

Once successfully used, the OTP should no longer work.

---

# 3. Email Template — Jinja2

**Jinja2** is a templating engine commonly used with Python applications.

Instead of creating every email manually, you create a template.

For example:

```html
Hello {{ name }},

Your OTP is {{ otp }}.

This code expires in {{ expiry_minutes }} minutes.
```

Then your Python application provides:

```python
name = "Ali"
otp = "481293"
expiry_minutes = 5
```

Jinja2 generates:

```text
Hello Ali,

Your OTP is 481293.

This code expires in 5 minutes.
```

### Why use templates?

You might have:

```text
Welcome email
OTP email
Password reset email
Account verification email
Login alert email
```

Instead of constructing HTML in Python code, keep the presentation in templates.

For example:

```text
templates/
    welcome.html
    otp.html
    password_reset.html
```

Then your backend supplies the dynamic values.

### Important security point

Don't put untrusted user input into templates in an unsafe way. Jinja2's autoescaping should generally be enabled for HTML templates.

---

# 4. H Cases

I'm assuming by **"H cases"** you mean **edge/hard cases (corner cases)** in authentication.

These are situations developers often forget to handle.

For example, OTP verification:

### Normal case

```text
User requests OTP
        ↓
Receives OTP
        ↓
Enters correct OTP
        ↓
Success
```

But what happens if:

### Case 1 — OTP expired

```text
OTP = 481293
Time = 10 minutes later
```

Result:

```text
OTP expired
```

### Case 2 — Wrong OTP

```text
Actual: 481293
Entered: 123456
```

Result:

```text
Invalid OTP
```

### Case 3 — Too many attempts

```text
Attempt 1 → wrong
Attempt 2 → wrong
Attempt 3 → wrong
Attempt 4 → wrong
...
```

Eventually:

```text
Too many attempts
```

### Case 4 — User requests multiple OTPs

```text
OTP 1 → 123456
OTP 2 → 987654
OTP 3 → 555222
```

You need to decide which OTP remains valid. Usually, **only the latest OTP should be valid**.

### Case 5 — User clicks resend repeatedly

Rate-limit the resend operation.

### Case 6 — Two browser tabs

The user might request OTP in one tab and another OTP in a second tab.

Your backend must handle this consistently.

These unusual situations are often where authentication bugs appear.

---

# 5. Brute-Force Attack

A **brute-force attack** means repeatedly trying credentials until something works.

Imagine an attacker knows:

```text
email = ali@example.com
```

They might try:

```text
password123
123456
qwerty
admin123
password
...
```

Or for an OTP:

```text
000000
000001
000002
000003
...
```

The attacker is essentially guessing.

### Why OTPs need protection

A 6-digit OTP has:

```text
000000 → 999999
```

That's **1,000,000 possibilities**.

If your API lets someone make unlimited attempts, that's dangerous.

### Protection

You can combine:

```text
Rate limiting
      +
Attempt limits
      +
Temporary lockout
      +
Strong password hashing
      +
MFA
      +
Monitoring
```

---

# 6. Rate Limiter

A **rate limiter** controls how frequently someone can perform an operation.

For example:

```text
Login API
5 attempts / minute
```

If someone tries:

```text
1 → allowed
2 → allowed
3 → allowed
4 → allowed
5 → allowed
6 → blocked
```

You might return something like:

```text
Too many requests. Try again later.
```

### Where to use rate limiting

Especially important for:

```text
/login
/register
/forgot-password
/send-otp
/verify-otp
/resend-otp
```

### Example

Suppose:

```text
POST /login
```

You could have a limit such as:

```text
5 attempts per minute per IP
```

But **IP-only rate limiting isn't enough**. Attackers can rotate IP addresses, and many legitimate users may share an IP.

For authentication, you can consider multiple dimensions:

```text
IP address
+
Account/email
+
Device/session
```

while being careful not to make the system easy to abuse for account enumeration or denial of service.

---

# 7. Google Login

Google Login is an example of **OAuth 2.0 / OpenID Connect (OIDC)** based authentication.

Instead of asking your application for:

```text
Email
Password
```

the user clicks:

```text
Continue with Google
```

Your application sends the user to Google.

Conceptually:

```text
Your website
     ↓
Google
     ↓
User logs in
     ↓
Google authenticates user
     ↓
Google sends authorization information
     ↓
Your backend verifies it
     ↓
User gets logged into your application
```

### Why is this useful?

Your application doesn't need to handle the user's Google password.

Google handles the authentication.

Your application receives identity information such as an authenticated Google account identifier and, depending on scopes, profile information.

### Important distinction

OAuth is primarily about **authorization**.

For logging a user in based on their identity, **OpenID Connect** is the relevant identity layer built on OAuth 2.0.

---

# 8. Password Complexity

Password complexity is the specific set of requirements for password contents.

For example:

```text
Minimum length: 12
Uppercase: required
Lowercase: required
Number: required
Special character: required
```

A simplistic validation might look like:

```text
Password
   ↓
At least 12 characters?
   ↓
Contains uppercase?
   ↓
Contains lowercase?
   ↓
Contains number?
   ↓
Contains special character?
   ↓
Accept
```

However, modern password security generally emphasizes **length and blocking compromised/common passwords** rather than forcing lots of arbitrary character rules.

For example:

```text
correct-horse-battery-staple
```

can be stronger and easier to remember than a short complicated password.

---

# How All These Concepts Connect

Imagine you're building:

> **A website with email/password login, OTP verification, password reset, and Google login.**

Your architecture could look like this:

```text
                    Authentication System
                           │
             ┌─────────────┴─────────────┐
             │                           │
       Email/Password                 Google Login
             │                           │
      Password Policy                 OIDC
             │                           │
      Password Complexity              Google
             │                           │
      Password Hashing                  │
             │                           │
             └─────────────┬─────────────┘
                           │
                     Authentication
                           │
                     Rate Limiter
                           │
                    Abuse Protection
                           │
              ┌────────────┴────────────┐
              │                         │
             OTP                  Password Reset
              │                         │
       Expiration                     Email
              │                         │
       Resend limits                Jinja2
              │
       Attempt limits
```

---

# A Real Login Example

Suppose a user enters:

```text
Email: ali@example.com
Password: MyPassword123!
```

Your backend might do:

### Step 1 — Rate limit

```text
Has this account/IP exceeded login limits?
```

If yes:

```text
Reject
```

Otherwise continue.

### Step 2 — Find user

```text
ali@example.com
       ↓
Database
```

### Step 3 — Verify password

The stored password should be a secure hash, not:

```text
MyPassword123!
```

The server verifies the supplied password against the stored hash.

### Step 4 — MFA/OTP if required

```text
Send OTP
```

Jinja2 can generate the email:

```text
Hello Ali,

Your verification code is 481293.

It expires in 5 minutes.
```

### Step 5 — OTP verification

Backend checks:

```text
Correct?
Not expired?
Not already used?
Attempt limit not exceeded?
```

### Step 6 — Create authenticated session

```text
User authenticated
       ↓
Session / secure authentication cookie
       ↓
User enters application
```

---

# Password Reset Example

A secure password reset might work like this:

```text
User clicks "Forgot Password"
             ↓
Enters email
             ↓
Rate limiter
             ↓
Generate random reset token
             ↓
Store token securely + expiration
             ↓
Jinja2 email template
             ↓
Send email
             ↓
User clicks reset link
             ↓
Verify token + expiry
             ↓
User creates new password
             ↓
Hash password
             ↓
Invalidate reset token
             ↓
Done
```

Notice how several of your concepts work together:

**Rate limiter + OTP/token expiration + Jinja2 + password policy + password complexity + brute-force protection.**

---

## The most important distinction

These terms are related but **not the same thing**:

| Concept             | Main purpose                                       |
| ------------------- | -------------------------------------------------- |
| Password Policy     | Rules for acceptable passwords                     |
| Password Complexity | Requirements such as length/characters             |
| OTP Expiration      | Makes temporary codes stop working                 |
| OTP Resend          | Allows requesting another code                     |
| Jinja2              | Generates dynamic email templates                  |
| Edge/Hard Cases     | Handles unusual situations safely                  |
| Brute Force         | Attack involving repeated guessing                 |
| Rate Limiter        | Limits how frequently requests can happen          |
| Google Login        | External identity authentication using Google/OIDC |

If you're learning **backend authentication**, I'd recommend learning them in this order:

**1. Password hashing → 2. Password policy → 3. Login → 4. Sessions/JWT → 5. OTP → 6. Password reset → 7. Rate limiting → 8. Brute-force protection → 9. Email/Jinja2 → 10. Google OAuth/OIDC → 11. Edge cases.**






Yes. The best way is to implement these as **one authentication module**, rather than treating each concept as a separate feature.

Assuming you're using **Python + FastAPI/Django/Flask**, the architecture would look like this:

```text
project/
├── auth/
│   ├── routes.py
│   ├── service.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── otp.py
│   ├── rate_limit.py
│   └── google.py
│
├── templates/
│   ├── otp_email.html
│   ├── welcome_email.html
│   └── password_reset.html
│
└── config.py
```

### 1. Start with the database

You'd typically have a user table like:

```text
User
----------------------
id
email
password_hash
is_verified
google_id
created_at
updated_at
```

For OTPs:

```text
OTP
----------------------
id
user_id
otp_hash
expires_at
attempts
used
created_at
```

For password reset:

```text
PasswordReset
----------------------
id
user_id
token_hash
expires_at
used
created_at
```

---

## 2. Implement password hashing

Never store:

```text
password = "Ali12345!"
```

Store a secure password hash instead.

Conceptually:

```python
password_hash = hash_password(password)
```

When logging in:

```python
if verify_password(password, user.password_hash):
    # password is correct
```

Use a well-established password-hashing library rather than implementing the algorithm yourself.

---

## 3. Implement password validation

Create something like:

```python
def validate_password(password):
    if len(password) < 12:
        raise ValueError("Password is too short")

    # Check additional policy requirements
    # Check common/compromised passwords
```

Then during registration:

```text
POST /register
        ↓
Validate email
        ↓
Validate password
        ↓
Hash password
        ↓
Create user
        ↓
Send verification OTP
```

---

# 4. Implement OTP

Create a function:

```python
def generate_otp():
    # cryptographically secure random 6-digit code
    ...
```

When the user requests an OTP:

```text
POST /auth/send-otp
        ↓
Rate limit
        ↓
Generate OTP
        ↓
Hash OTP
        ↓
Store hash + expiration
        ↓
Send email
```

For example:

```text
OTP: 481293
Expires: 5 minutes
```

**Don't store the OTP as plaintext if you can avoid it.**

---

# 5. OTP verification

Create:

```text
POST /auth/verify-otp
```

The backend checks:

```text
Is OTP valid?
       ↓
Is it expired?
       ↓
Has it already been used?
       ↓
Has the user exceeded attempts?
       ↓
Does the hash match?
       ↓
Mark OTP as used
       ↓
Verify account
```

A simplified example:

```python
if otp.expires_at < now:
    return "OTP expired"

if otp.used:
    return "OTP already used"

if otp.attempts >= 5:
    return "Too many attempts"

if not verify_otp(code, otp.otp_hash):
    otp.attempts += 1
    return "Invalid OTP"

otp.used = True
user.is_verified = True
```

---

# 6. OTP resend

Create:

```text
POST /auth/resend-otp
```

Don't simply generate another OTP every time.

Use a cooldown:

```text
First request → send OTP
       ↓
30 seconds
       ↓
Resend allowed
```

And an overall limit:

```text
Maximum 5 OTP requests/hour
```

The exact numbers depend on your application's threat model and user experience.

---

# 7. Jinja2 email

Create:

```text
templates/
    otp_email.html
```

For example:

```html
<h2>Hello {{ name }}</h2>

<p>Your verification code is:</p>

<h1>{{ otp }}</h1>

<p>This code expires in {{ expiry_minutes }} minutes.</p>
```

Your Python code supplies:

```python
context = {
    "name": user.name,
    "otp": otp,
    "expiry_minutes": 5
}
```

Then Jinja2 renders the HTML.

You can use the same approach for:

```text
Welcome email
OTP email
Password reset email
Email verification
Security alert
```

---

# 8. Rate limiter

This is extremely important.

You want rate limiting around endpoints such as:

```text
POST /login
POST /register
POST /send-otp
POST /verify-otp
POST /forgot-password
POST /reset-password
```

For example:

```text
/login
       ↓
Rate limiter
       ↓
Allowed?
   ↓       ↓
 Yes       No
   ↓       ↓
Login    429
```

In a production application, a shared store such as **Redis** is commonly used for distributed rate limiting.

---

# 9. Brute-force protection

Rate limiting is one part of brute-force protection.

For login:

```text
Attacker
   ↓
POST /login
   ↓
Wrong password
   ↓
POST /login
   ↓
Wrong password
   ↓
POST /login
   ↓
...
```

You need controls that make repeated guessing difficult.

For example:

```text
Per-IP rate limit
+
Per-account protection
+
Progressive delays/temporary lockouts
+
Strong password hashing
+
Monitoring
```

Be careful with permanent account lockouts: an attacker could intentionally lock someone else's account.

---

# 10. Google Login

Add:

```text
GET /auth/google
```

User clicks:

```text
Continue with Google
```

Then:

```text
Your application
       ↓
Google authorization
       ↓
User signs in
       ↓
Google redirects back
       ↓
Your callback endpoint
       ↓
Validate OIDC response
       ↓
Find/create user
       ↓
Create your application's session
```

You should use a maintained OAuth/OIDC library rather than manually constructing the protocol.

---

# 11. Password reset

Add:

```text
POST /auth/forgot-password
```

Flow:

```text
User enters email
       ↓
Rate limit
       ↓
Generate random reset token
       ↓
Store token hash + expiration
       ↓
Send Jinja2 email
       ↓
User clicks link
       ↓
Validate token
       ↓
Enter new password
       ↓
Validate password policy
       ↓
Hash password
       ↓
Update password
       ↓
Invalidate token
```

Importantly, the "forgot password" response should generally not reveal whether an email address is registered.

For example, return something like:

```text
If an account exists for that email,
we've sent password-reset instructions.
```

That helps prevent account enumeration.

---

# 12. Handle edge cases

Before calling your authentication system "finished", test cases like:

```text
Correct password
Wrong password
Expired OTP
Wrong OTP
Used OTP
Too many OTP attempts
Repeated resend
Expired reset token
Used reset token
Invalid reset token
Google account already exists
Email already registered
Two simultaneous login requests
Two OTP requests
Very long password
Common/compromised password
Rate limit exceeded
```

This is where **"H cases" / edge cases** become important.

---

# Recommended project flow

If you're implementing this for a real project, build it in this order:

```text
                    AUTH SYSTEM
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
   Registration         Login          Google Login
       │                 │                 │
 Password Policy     Password Hash       OIDC
       │                 │                 │
      OTP          Brute-force           User
       │             protection          Session
       │                 │
   Verification     Rate Limiter
       │
     Email
    (Jinja2)
       │
       └──────── Password Reset
```

### API endpoints

A clean starting API might be:

```text
POST /auth/register
POST /auth/login
POST /auth/logout

POST /auth/send-otp
POST /auth/verify-otp
POST /auth/resend-otp

POST /auth/forgot-password
POST /auth/reset-password

GET  /auth/google
GET  /auth/google/callback
```

Then put the actual security logic in services rather than putting everything directly inside the route handlers.

---

If you tell me **what framework you're using (FastAPI, Django, Flask, Node/Express, Laravel, Spring Boot, etc.) and what database (PostgreSQL, MySQL, MongoDB)**, I can show you the actual implementation structure and code for this authentication system.





Yes. With your stack—**FastAPI + SQLModel + Neon/PostgreSQL + Argon2**—I would implement the password policy at the **schema/validation layer**, and keep Argon2 responsible only for hashing.

There are also a couple of important problems in your current `register_user()` that we should fix:

1. Your `except Exception` catches your own `HTTPException` and turns it into a `500`.
2. `"@" in email` and `".com" in email` is not proper email validation.
3. You're storing the OTP directly in the database.
4. Your model has `email_verification_otp`, but your function uses `email_verification_token`.
5. Your password field is called `password_hash` in the registration request, although the client should actually send a **plain password**, which your backend then hashes.
6. `302 FOUND` isn't appropriate for "user already exists"; normally use `409 CONFLICT`.
7. Returning `new_user` can expose fields you don't want to return.

Let's build this properly.

---

# 1. Recommended project structure

I'd organize it like this:

```text
app/
├── main.py
├── database.py
│
├── models/
│   └── user.py
│
├── schemas/
│   └── user.py
│
├── services/
│   └── auth.py
│
├── security/
│   ├── password.py
│   └── otp.py
│
└── data/
    └── common_passwords.py
```

The important separation is:

```text
User input
    ↓
Pydantic validation
    ↓
Password policy
    ↓
Business logic
    ↓
Argon2 hashing
    ↓
Database
```

---

# 2. Install the required packages

You already have FastAPI, SQLModel, etc.

For password hashing and email validation:

```bash
pip install argon2-cffi email-validator
```

If you're using Pydantic's `EmailStr`, `email-validator` is required.

---

# 3. Create your password policy

Create:

```text
security/password.py
```

Use Argon2 for hashing and a separate function for the policy.

```python
import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError


password_hasher = PasswordHasher()


COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "123456789",
    "qwerty",
    "qwerty123",
    "1234567890",
    "admin",
    "admin123",
    "letmein",
    "welcome",
    "welcome123",
    "iloveyou",
    "monkey",
    "dragon",
    "football",
    "abc123",
    "password1",
    "passw0rd",
}


def validate_password_policy(password: str, email: str) -> None:
    """
    Raises ValueError if the password does not satisfy
    the application's password policy.
    """

    # 1. Minimum 8 characters
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    # 2. Maximum 12 characters
    if len(password) > 12:
        raise ValueError("Password must not exceed 12 characters.")

    # 3. Uppercase
    if not re.search(r"[A-Z]", password):
        raise ValueError(
            "Password must contain at least one uppercase letter."
        )

    # 4. Lowercase
    if not re.search(r"[a-z]", password):
        raise ValueError(
            "Password must contain at least one lowercase letter."
        )

    # 5. Number
    if not re.search(r"\d", password):
        raise ValueError(
            "Password must contain at least one number."
        )

    # 6. Special character
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError(
            "Password must contain at least one special character."
        )

    # 7. Password cannot equal email
    if password.casefold() == email.casefold():
        raise ValueError(
            "Password cannot be the same as your email."
        )

    # 8. Common password check
    if password.casefold() in {
        common.casefold() for common in COMMON_PASSWORDS
    }:
        raise ValueError(
            "This password is too common. Please choose a stronger password."
        )


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against an Argon2 hash.
    """
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False
```

---

# 4. Important point about your 8–12 requirement

You said:

> Minimum 8–12 characters

This is ambiguous.

If you mean:

> **At least 8 characters and maximum 12 characters**

then the code above is correct:

```text
8 <= password length <= 12
```

But I would personally recommend:

```text
Minimum: 12
Maximum: much higher
```

rather than maximum 12.

For example:

```text
Blue!River92Moon
```

is a much better password than forcing users to stay below 12 characters.

If your project specification specifically says **8–12**, keep the current implementation.

---

# 5. Improve your User registration schema

You currently have something like:

```python
class User_register:
    ...
    password_hash
```

This should be changed.

The frontend should send:

```text
password
```

not:

```text
password_hash
```

The client should **never be responsible for creating the Argon2 hash**.

Create:

```text
schemas/user.py
```

```python
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=12)
```

Now FastAPI automatically validates the basic shape of the request.

Example request:

```json
{
    "name": "Muhammad Ali",
    "email": "ali@example.com",
    "password": "Ali@12345X"
}
```

---

# 6. Why use EmailStr?

Your current code:

```python
if "@" not in user.email or ".com" not in user.email:
```

isn't reliable.

For example:

```text
abc@something.com
```

looks okay.

But email addresses don't necessarily have to end in `.com`.

Instead:

```python
from pydantic import EmailStr
```

and:

```python
email: EmailStr
```

Pydantic performs proper email syntax validation.

---

# 7. Keep your database model separate

Your SQLModel should represent the database.

For example:

```python
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(
        min_length=5,
        max_length=50
    )

    email: str = Field(
        max_length=255,
        unique=True,
        index=True
    )

    password_hash: str = Field(
        max_length=255
    )

    email_verification_otp: Optional[str] = Field(
        default=None,
        max_length=255
    )

    email_verified: bool = Field(
        default=False
    )

    todos: List["Todo"] = Relationship(
        back_populates="user",
        cascade_delete=True
    )
```

Notice:

```python
password_hash
```

is still in your **database model**.

But your registration schema has:

```python
password
```

That's the correct separation.

---

# 8. Implement the registration service

Now your registration function becomes much cleaner.

```python
from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.user import User
from schemas.user import UserRegister
from security.password import (
    validate_password_policy,
    hash_password,
)
from security.otp import generate_otp


def register_user(
    user: UserRegister,
    session: Session
):
    # Normalize email
    email = user.email.strip().lower()

    # ---------------------------------
    # 1. Password policy
    # ---------------------------------

    try:
        validate_password_policy(
            password=user.password,
            email=email
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # ---------------------------------
    # 2. Check existing user
    # ---------------------------------

    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create account."
        )

    # ---------------------------------
    # 3. Generate OTP
    # ---------------------------------

    otp = generate_otp()

    # ---------------------------------
    # 4. Hash password
    # ---------------------------------

    password_hash = hash_password(
        user.password
    )

    # ---------------------------------
    # 5. Create user
    # ---------------------------------

    new_user = User(
        name=user.name.strip(),
        email=email,
        password_hash=password_hash,
        email_verification_otp=otp,
        email_verified=False
    )

    # ---------------------------------
    # 6. Save
    # ---------------------------------

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # ---------------------------------
    # 7. Send verification email
    # ---------------------------------

    send_email_verification(
        receiver_email=email,
        otp=otp
    )

    # Don't return password hash!
    return {
        "message": "Registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "email_verified": new_user.email_verified
        }
    }
```

---

# 9. Very important: fix your `try/except`

Your original code has:

```python
try:
    ...
    raise HTTPException(...)
    
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=str(e)
    )
```

This is a problem.

Suppose you intentionally do:

```python
raise HTTPException(
    status_code=409,
    detail="User exists"
)
```

Your:

```python
except Exception
```

catches it.

Then it becomes:

```text
500 Internal Server Error
```

That's not what you want.

If you really need a catch-all, do:

```python
except HTTPException:
    raise

except Exception:
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

But for this service, you can avoid the broad `try/except` entirely and handle database errors separately.

---

# 10. Generate OTP securely

Don't generate OTP using something predictable like:

```python
random.randint(...)
```

Use Python's cryptographically secure `secrets`.

Create:

```text
security/otp.py
```

```python
import secrets


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"
```

This generates:

```text
481293
```

or:

```text
003827
```

etc.

---

# 11. Your current OTP implementation needs one more improvement

Currently you're doing:

```python
email_verification_otp=otp
```

That means the database contains:

```text
481293
```

in plaintext.

A better design is:

```text
User enters OTP
       ↓
Hash OTP
       ↓
Store OTP hash
       ↓
Send plaintext OTP through email
       ↓
User submits OTP
       ↓
Hash/verify
       ↓
Mark verified
```

Also add expiration.

Your model could become:

```python
email_verification_otp_hash: Optional[str] = None

email_verification_otp_expires_at: Optional[datetime] = None

email_verification_attempts: int = 0
```

For example:

```python
from datetime import datetime
from typing import Optional

from sqlmodel import Field


email_verification_otp_hash: Optional[str] = Field(
    default=None,
    max_length=255
)

email_verification_otp_expires_at: Optional[datetime] = None

email_verification_attempts: int = Field(
    default=0
)
```

That gives you the foundation for:

* OTP expiration
* OTP attempt limits
* OTP resend
* brute-force protection

---

# 12. Your password policy now works like this

Suppose user sends:

```json
{
    "name": "Muhammad Ali",
    "email": "ali@gmail.com",
    "password": "password"
}
```

The policy checks:

```text
password
   ↓
8+ characters?             YES
12 or fewer?               YES
uppercase?                 NO
lowercase?                 YES
number?                    NO
special character?         NO
same as email?             NO
common password?           YES
```

Result:

```text
400 Bad Request
```

---

# 13. Example valid password

For your current 8–12 character requirement:

```text
Ali@12345X
```

Check:

```text
Length          → 10 ✅
Uppercase       → A, X ✅
Lowercase       → li ✅
Number          → 12345 ✅
Special         → @ ✅
Same as email   → No ✅
Common password → No ✅
```

So it passes.

Another example:

```text
Blue!92Moon
```

Length:

```text
11
```

and it satisfies all the requirements.

---

# 14. One problem with "common passwords"

Don't stop at this:

```python
COMMON_PASSWORDS = {
    "password",
    "12345678",
    ...
}
```

That's useful for learning, but a production application should use a **much larger compromised/common-password list**.

Your logic should conceptually be:

```text
User password
      ↓
Basic policy
      ↓
Is it common/compromised?
      ↓
Yes → reject
No  → continue
      ↓
Argon2 hash
```

You can eventually maintain a large list of known breached passwords rather than manually maintaining ten or twenty entries.

Also consider checking whether the password contains obvious pieces of the user's identity, e.g. their name or email local part.

---

# 15. Don't validate only on the frontend

You might eventually have:

```text
React / Next.js frontend
        ↓
Password validation
        ↓
FastAPI backend
        ↓
Password validation AGAIN
```

The backend validation is mandatory.

A malicious user can completely bypass frontend JavaScript and call:

```text
POST /register
```

directly.

So:

```text
Frontend validation → UX
Backend validation  → Security
```

---

# 16. Complete registration flow

Your final architecture should be:

```text
                 POST /register
                       │
                       ▼
              Pydantic validation
                       │
                       ▼
                  Email valid?
                       │
                       ▼
                Password policy
                       │
          ┌────────────┼────────────┐
          │            │            │
       Length       Complexity    Common?
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                Existing user?
                       │
                       ▼
                  Generate OTP
                       │
                       ▼
                  Argon2 hash
                       │
                       ▼
                 Create User
                       │
                       ▼
                    Neon DB
                       │
                       ▼
                Send OTP email
                       │
                       ▼
                  Registration
                    complete
```

---

# 17. What your database should eventually look like

I'd recommend evolving your `User` model toward:

```python
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(
        min_length=5,
        max_length=50
    )

    email: str = Field(
        max_length=255,
        unique=True,
        index=True
    )

    password_hash: str = Field(
        max_length=255
    )

    email_verified: bool = Field(
        default=False
    )

    email_verification_otp_hash: Optional[str] = Field(
        default=None,
        max_length=255
    )

    email_verification_otp_expires_at: Optional[datetime] = None

    email_verification_attempts: int = Field(
        default=0
    )

    todos: List["Todo"] = Relationship(
        back_populates="user",
        cascade_delete=True
    )
```

This is much more useful for the authentication features you want to implement next.

---

# 18. One more important thing: database migrations

Because you're using **Neon PostgreSQL**, when you change:

```text
email_verification_otp
```

to:

```text
email_verification_otp_hash
email_verification_otp_expires_at
email_verification_attempts
```

don't just change the Python model and assume the existing Neon table changes automatically.

You should use a migration system such as **Alembic**.

Your workflow becomes:

```text
Change SQLModel
      ↓
Create migration
      ↓
Review migration
      ↓
Run migration against Neon
      ↓
Database updated
```

---

## Your first implementation milestone

I'd implement it in this exact order:

```text
1. ✅ UserRegister schema
2. ✅ EmailStr validation
3. ✅ Password policy
4. ✅ Common-password check
5. ✅ Argon2 hashing
6. ✅ Clean registration service
7. ✅ Secure OTP generation
8. ⬜ OTP hashing
9. ⬜ OTP expiration
10. ⬜ OTP verification
11. ⬜ OTP resend + cooldown
12. ⬜ OTP attempt limit
13. ⬜ Rate limiting
14. ⬜ Password reset
15. ⬜ Google OIDC login
```

**One correction I'd make immediately in your existing code:** rename the request field from `password_hash` to `password`. The user sends a password; **your backend creates the Argon2 hash**. Never ask the frontend to send something called `password_hash` unless you're deliberately designing a client-side cryptographic protocol.

If you show me your current **`User_register` schema, `password_hasher()` function, `generate_otp()` function, and your FastAPI `/register` route**, I can adapt the code exactly to your existing project instead of making you restructure everything.




Great. Now let's implement **OTP expiration + resend** properly on top of your existing FastAPI + SQLModel + Neon setup.

The clean flow should be:

```text
Register
   ↓
Generate OTP
   ↓
Save OTP hash + expiry time
   ↓
Send email
   ↓
User enters OTP
   ↓
Verify OTP
   ↓
If expired → reject
   ↓
If correct → verify email
```

For resend:

```text
POST /auth/resend-otp
        ↓
Find user
        ↓
Check resend cooldown
        ↓
Generate NEW OTP
        ↓
Invalidate old OTP
        ↓
Save new OTP + new expiry
        ↓
Send email
```

## 1. Update your `User` model

Since you're using SQLModel, add expiration and resend-related fields.

```python
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(min_length=5, max_length=50)

    email: str = Field(
        max_length=255,
        unique=True,
        index=True
    )

    password_hash: str = Field(max_length=255)

    email_verification_otp_hash: Optional[str] = Field(
        default=None,
        max_length=255
    )

    email_verification_otp_expires_at: Optional[datetime] = None

    email_verification_otp_attempts: int = Field(
        default=0
    )

    email_verification_last_sent_at: Optional[datetime] = None

    email_verified: bool = Field(default=False)
```

The important fields are:

```text
email_verification_otp_hash
email_verification_otp_expires_at
email_verification_otp_attempts
email_verification_last_sent_at
```

---

# 2. Generate OTP

Use Python's `secrets` module.

```python
import secrets


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"
```

This produces:

```text
482193
```

or:

```text
004821
```

Always keep it as a string because leading zeros are valid.

---

# 3. Hash the OTP

Since you're already using Argon2, you can use it for the OTP hash too.

```python
from argon2 import PasswordHasher

otp_hasher = PasswordHasher()


def hash_otp(otp: str) -> str:
    return otp_hasher.hash(otp)


def verify_otp(otp: str, otp_hash: str) -> bool:
    try:
        return otp_hasher.verify(otp_hash, otp)
    except Exception:
        return False
```

Your database should contain something like:

```text
email_verification_otp_hash
    ↓
$argon2id$v=19$m=...
```

not:

```text
481293
```

---

# 4. Set OTP expiration

Let's say your OTP should expire after **5 minutes**.

```python
from datetime import datetime, timedelta, timezone


OTP_EXPIRATION_MINUTES = 5


def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(
        minutes=OTP_EXPIRATION_MINUTES
    )
```

So:

```text
10:00:00
   +
5 minutes
   ↓
10:05:00
```

---

# 5. Generate everything together

I recommend creating a helper:

```python
def create_otp():

    otp = generate_otp()

    otp_hash = hash_otp(otp)

    expires_at = get_otp_expiry()

    return otp, otp_hash, expires_at
```

Now registration/resend can simply do:

```python
otp, otp_hash, expires_at = create_otp()
```

---

# 6. Modify your registration

Your registration currently does something like:

```python
otp = generate_otp()
```

Change it to:

```python
otp, otp_hash, expires_at = create_otp()
```

Then:

```python
new_user = User(
    name=user.name.strip(),
    email=email,
    password_hash=password_hash,

    email_verification_otp_hash=otp_hash,
    email_verification_otp_expires_at=expires_at,

    email_verification_otp_attempts=0,
    email_verification_last_sent_at=datetime.now(timezone.utc),

    email_verified=False
)
```

Then send the **original OTP**:

```python
send_email_verification(
    receiver_email=email,
    otp=otp
)
```

Remember:

```text
Database → OTP hash
Email    → actual OTP
```

---

# 7. Create OTP verification endpoint

You'll need something like:

```text
POST /auth/verify-otp
```

Request:

```json
{
    "email": "ali@gmail.com",
    "otp": "482193"
}
```

Create a schema:

```python
from pydantic import BaseModel, EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
```

---

# 8. Verify OTP

Your endpoint/service should do these checks **in this order**:

```text
Find user
   ↓
Already verified?
   ↓
OTP exists?
   ↓
OTP expired?
   ↓
Too many attempts?
   ↓
OTP correct?
   ↓
Mark email verified
```

Example:

```python
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select


MAX_OTP_ATTEMPTS = 5


def verify_email_otp(
    data: VerifyOTPRequest,
    session: Session
):
    email = data.email.strip().lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to verify account."
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified."
        )

    if not user.email_verification_otp_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active OTP. Please request a new OTP."
        )

    # Check attempts
    if user.email_verification_otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. Please request a new OTP."
        )

    # Check expiration
    now = datetime.now(timezone.utc)

    if (
        not user.email_verification_otp_expires_at
        or user.email_verification_otp_expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new OTP."
        )

    # Verify OTP
    if not verify_otp(
        data.otp,
        user.email_verification_otp_hash
    ):
        user.email_verification_otp_attempts += 1

        session.add(user)
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP."
        )

    # Success
    user.email_verified = True

    # Invalidate OTP
    user.email_verification_otp_hash = None
    user.email_verification_otp_expires_at = None
    user.email_verification_otp_attempts = 0

    session.add(user)
    session.commit()

    return {
        "message": "Email verified successfully."
    }
```

---

# 9. Why invalidate the OTP?

Suppose the correct OTP is:

```text
482193
```

User enters it correctly.

If you leave it in the database, they could potentially use:

```text
482193
```

again.

Instead:

```python
user.email_verification_otp_hash = None
user.email_verification_otp_expires_at = None
```

So:

```text
482193
   ↓
Used successfully
   ↓
INVALID
```

This makes it a **true one-time password**.

---

# 10. Now implement resend

Create:

```text
POST /auth/resend-otp
```

Request:

```json
{
    "email": "ali@gmail.com"
}
```

Schema:

```python
class ResendOTPRequest(BaseModel):
    email: EmailStr
```

---

# 11. Add resend cooldown

Don't let someone do:

```text
Resend
Resend
Resend
Resend
Resend
```

within a few seconds.

Let's use a **60-second cooldown**.

```python
RESEND_COOLDOWN_SECONDS = 60
```

Then:

```python
from datetime import datetime, timedelta, timezone


def resend_email_otp(
    data: ResendOTPRequest,
    session: Session
):
    email = data.email.strip().lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        # Don't reveal whether the account exists
        return {
            "message": "If the account exists, a new OTP has been sent."
        }

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified."
        )

    now = datetime.now(timezone.utc)

    # Check cooldown
    if user.email_verification_last_sent_at:

        elapsed = (
            now - user.email_verification_last_sent_at
        ).total_seconds()

        if elapsed < RESEND_COOLDOWN_SECONDS:

            remaining = int(
                RESEND_COOLDOWN_SECONDS - elapsed
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {remaining} seconds before requesting another OTP."
            )

    # Generate NEW OTP
    otp, otp_hash, expires_at = create_otp()

    # Replace old OTP
    user.email_verification_otp_hash = otp_hash

    user.email_verification_otp_expires_at = expires_at

    user.email_verification_otp_attempts = 0

    user.email_verification_last_sent_at = now

    session.add(user)
    session.commit()

    # Send NEW OTP
    send_email_verification(
        receiver_email=user.email,
        otp=otp
    )

    return {
        "message": "If the account exists, a new OTP has been sent."
    }
```

---

# 12. What happens to the old OTP?

This is very important.

Suppose:

```text
OTP #1
482193
expires 10:05
```

User clicks resend.

New OTP:

```text
OTP #2
719284
expires 10:10
```

Now:

```text
482193 → INVALID
719284 → VALID
```

Because you replaced:

```python
user.email_verification_otp_hash
```

with the new hash.

Therefore **only the newest OTP is valid**.

That's the behavior you want.

---

# 13. Add a resend limit

Cooldown alone isn't enough.

An attacker could do:

```text
10:00 → resend
10:01 → resend
10:02 → resend
...
```

for hours.

Eventually you want something like:

```text
60-second cooldown
+
maximum N resends within a time window
+
API rate limiting
```

For example, you could add:

```python
email_verification_resend_count: int = Field(default=0)
```

But for a production implementation, I would eventually move this kind of rate-limit state to **Redis**, rather than putting all rate-limit logic into your `User` table.

---

# 14. Your complete OTP lifecycle

After these changes, your system looks like:

```text
                    REGISTER
                       │
                       ▼
                 Generate OTP
                       │
              ┌────────┴────────┐
              │                 │
         OTP plaintext       OTP hash
              │                 │
              ▼                 ▼
           Email             Neon DB
                                │
                         Expiration = 5 min
                                │
                                ▼
                        User enters OTP
                                │
                   ┌────────────┴────────────┐
                   │                         │
                Expired?                  Valid?
                   │                         │
                  YES                       YES
                   │                         │
                   ▼                         ▼
              Reject                    Verify email
                                             │
                                             ▼
                                       Delete OTP
```

Resend:

```text
              RESEND OTP
                   │
                   ▼
             Check cooldown
                   │
             ┌─────┴─────┐
             │           │
           Too soon     Allowed
             │           │
             ▼           ▼
            429       Generate new OTP
                         │
                         ▼
                  Replace old OTP
                         │
                         ▼
                    Send email
```

---

# 15. One thing I'd change in your model

Your current field:

```python
email_verification_otp
```

should become:

```python
email_verification_otp_hash
```

And add:

```python
email_verification_otp_expires_at
email_verification_otp_attempts
email_verification_last_sent_at
```

So your relevant model section becomes:

```python
email_verification_otp_hash: Optional[str] = Field(
    default=None,
    max_length=255
)

email_verification_otp_expires_at: Optional[datetime] = None

email_verification_otp_attempts: int = Field(
    default=0
)

email_verification_last_sent_at: Optional[datetime] = None

email_verified: bool = Field(default=False)
```

Then run an **Alembic migration** so Neon gets the new columns.

---

## 16. Final endpoints

You should now have:

```text
POST /auth/register
```

Creates account + sends OTP.

```text
POST /auth/verify-otp
```

Verifies OTP.

```text
POST /auth/resend-otp
```

Generates and sends a new OTP.

The behavior should be:

| Situation                      | Result                |
| ------------------------------ | --------------------- |
| Correct OTP before 5 min       | ✅ Verify              |
| Wrong OTP                      | ❌ Invalid             |
| Correct OTP after 5 min        | ❌ Expired             |
| Correct OTP after already used | ❌ Invalid             |
| Resend before 60 sec           | ❌ 429                 |
| Resend after 60 sec            | ✅ New OTP             |
| Old OTP after resend           | ❌ Invalid             |
| 5 wrong OTP attempts           | ❌ Block until new OTP |
| Already verified               | ❌ No OTP needed       |

### One important security improvement

For your next step, **don't put the OTP endpoints behind only application-level checks**. Add a proper **rate limiter** around `/verify-otp` and `/resend-otp`. The attempt counter protects an individual OTP, while the rate limiter protects your API from someone hammering these endpoints.

If you paste your **current `User` model + `generate_otp()` + `send_email_verification()` + register route**, I can modify *your exact code* to add expiration and resend without changing your existing project structure.
