# Production-Ready Rate Limiter Middleware

## Problem
Web applications are vulnerable to Denial of Service (DoS) attacks, brute-forcing, and API abuse. Rate limiting is essential to protect infrastructure, but implementing it safely in a multi-threaded environment without race conditions is non-trivial.

## Solution
A plug-and-play WSGI middleware implementing the **Token Bucket algorithm**. It uses SQLite with `BEGIN IMMEDIATE` transactions to guarantee atomicity and prevent race conditions under heavy concurrent load.

## Features
- **Algorithm:** Token Bucket (allows for burst traffic while enforcing a sustained rate).
- **Atomicity:** Thread-safe via SQLite write locks.
- **Standard Compliance:** Returns `429 Too Many Requests` with a correct `Retry-After` header.
- **Zero Dependencies:** Pure Python standard library.

## Setup
```bash
python app.py
```
Open `http://localhost:8000` and click the button rapidly to trigger the limit.

## Usage
Wrap any WSGI application with the middleware:
```python
from middleware import RateLimitMiddleware

app = RateLimitMiddleware(your_wsgi_app, capacity=10, refill_rate=1.0)
```

## Architectural decisions
- **SQLite over In-Memory:** While in-memory is faster, SQLite allows the rate limit state to persist across process restarts and provides a centralized state if multiple workers are running (when using WAL mode).
- **BEGIN IMMEDIATE:** We explicitly acquire a write lock before reading the token count to prevent TOCTOU (Time-of-Check to Time-of-Use) race conditions where multiple threads read the same token count simultaneously.
- **Token Bucket vs Fixed Window:** The Token Bucket avoids the "thundering herd" problem of fixed-window limiters (where a user can burst 2x the limit at the window boundary).