# Framework-specific review guide

## Django
Review DEBUG, ALLOWED_HOSTS, SECRET_KEY handling, CSRF, SECURE_* and SESSION_COOKIE_* settings, middleware, permissions on views and DRF viewsets, queryset object scoping, unsafe raw SQL, template escaping, file uploads, signed cookies, and admin exposure. Verify authorization per object and tenant, not only authentication.

## Flask
Review session signing and SECRET_KEY, debug mode, blueprint authorization, CSRF protection on state-changing endpoints, Jinja autoescaping, SQLAlchemy query construction, file paths and uploads, CORS and security headers.

## Node.js / Express
Review middleware ordering, authorization, JWT validation (algorithm, issuer, audience, expiry), cookie security, request validation, prototype pollution, injection, SSRF, dependency advisories, and exception handling.

## ASP.NET Core
Review `[Authorize]` coverage and policy checks, resource-based authorization, antiforgery, Identity configuration, Data Protection key persistence, EF Core query parameterization, secrets, logging and CORS.

## General verification
For each suspected issue trace user-controlled input, boundary, sink, existing guards and whether a realistic precondition exists. Avoid assuming a missing control without checking global middleware and infrastructure layers.
