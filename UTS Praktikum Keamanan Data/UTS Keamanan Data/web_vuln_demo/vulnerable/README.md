Vulnerable App
==============
This app intentionally contains insecure coding patterns:
- Login builds SQL queries by concatenation (SQL Injection possible).
- Comments render user input with '|safe' (stored XSS possible).
- Upload accepts any file and saves with original name in uploads/ (insecure).
- Profile shows user by id param with NO authorization checks (broken access control).

Do NOT expose this app to the internet. Use locally for testing/learning only.
