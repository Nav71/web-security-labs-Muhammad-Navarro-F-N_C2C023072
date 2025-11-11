Secure App (simple mitigations)
================================
Differences and mitigations used:
- SQL Injection: parameterized queries (sqlite3 placeholders) instead of string concatenation.
- XSS: simple sanitization and template auto-escaping (no use of '|safe').
- Upload: allowed extension whitelist, save to outside folder, randomize filename, verify image signatures for images.
- Access Control: require login and verify session user id == requested profile id. Return 403 otherwise.

Notes:
- These mitigations are intentionally minimal and meant for demonstration only.
- Real production apps must use strong password hashing (bcrypt), CSRF protection, robust input validation, CSP headers, stricter file scanning, and comprehensive authz systems.
