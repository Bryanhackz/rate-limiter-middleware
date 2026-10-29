# Security Policy

## Supported Versions
Currently, only the latest `main` branch is supported.

## Scope
This is a WSGI middleware designed to protect backend applications from Denial of Service (DoS) and brute-force attacks. The primary security focus is on concurrency safety (preventing race conditions during token consumption) and atomic database transactions (SQLite `BEGIN IMMEDIATE`).

## Reporting a Vulnerability
Please do not report security vulnerabilities through public GitHub issues. Send an email to **br4yangil006@gmail.com**. You should receive a response within 48 hours.

Please include:
- Type of issue (e.g., race condition, rate-limit bypass, DoS)
- Full paths of source file(s) related to the issue
- Step-by-step instructions to reproduce the issue
- Impact of the issue
