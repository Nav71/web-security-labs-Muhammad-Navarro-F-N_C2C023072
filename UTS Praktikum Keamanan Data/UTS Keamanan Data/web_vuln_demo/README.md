Web Vulnerability Demo (Vulnerable vs Secure)
============================================
This project contains two minimal Flask web apps demonstrating four common web vulnerabilities:
  1) SQL Injection (Login)
  2) Cross-Site Scripting (Comment form)
  3) Insecure File Upload (Upload form)
  4) Broken Access Control (Profile page)

Structure:
- vulnerable/   : intentionally vulnerable implementations
- secure/       : safer implementations with simple mitigations
- run_instructions.txt : how to run each app
- requirements.txt : python dependencies

SECURITY & ETHICS:
- These apps are purposely vulnerable for educational/testing on local machines only.
- Do NOT deploy vulnerable versions to the public internet.
- Use this code only in controlled, legal environments for learning and testing.

Quick Run (recommended in separate virtualenvs):
  1) cd /path/to/web_vuln_demo/vulnerable
     python3 -m venv venv && source venv/bin/activate
     pip install -r ../requirements.txt
     export FLASK_APP=app.py
     flask run --port 5001
  2) cd /path/to/web_vuln_demo/secure
     python3 -m venv venv && source venv/bin/activate
     pip install -r ../requirements.txt
     export FLASK_APP=app.py
     flask run --port 5002

Notes about differences (details are in each folder's README.md):
- SQL Injection: vulnerable uses string-concatenated SQL; secure uses parameterized queries.
- XSS (comments): vulnerable prints user input unescaped; secure uses template auto-escaping / sanitization.
- Upload: vulnerable accepts & saves any filename; secure restricts extensions, checks content-type, stores outside static.
- Broken Access Control: vulnerable allows viewing arbitrary profiles by id; secure enforces session ownership checks.
