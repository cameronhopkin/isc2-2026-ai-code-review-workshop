
## Detailed Vulnerability Findings

The following findings were identified by Qwen 3.8 27B FP8 during the ISC2 Security Congress 2026 workshop.

### 1. Broken Object Level Authorization (BOLA / IDOR)

**Severity:** High  
**Classification:** CWE-639  
**Files:** `target-app/auth.py:33-45`, `target-app/app.py:47-57`  
**Detection:** Scanner-free review

**Explanation:** The `require_order_access` decorator verifies that a user is authenticated but does not verify ownership of the requested order. The `get_order` endpoint retrieves orders by ID without restricting access to the authenticated user.

**Impact:** An authenticated attacker could access another user's order by changing the order ID.

**Remediation:** Enforce object-level authorization and restrict order queries to resources owned by or explicitly accessible to the authenticated user.

### 2. SQL Injection

**Severity:** High  
**Classification:** CWE-89  
**File:** `target-app/models.py:59-60`  
**Detection:** Scanner-assisted and scanner-free reviews

**Explanation:** The `search_orders` function interpolates user-controlled search text directly into an SQL statement using Python string formatting.

**Impact:** An attacker could manipulate the SQL query to access unauthorized data or potentially modify database contents, depending on database permissions.

**Remediation:** Replace string interpolation with parameterized SQL queries.

### 3. Hardcoded Application Secrets

**Severity:** High  
**Classification:** CWE-798  
**Files:** `target-app/app.py:15`, `target-app/app.py:17`  
**Detection:** Scanner-assisted and scanner-free reviews

**Explanation:** The application contains a hardcoded Flask session-signing key and a reporting API token. The token resembles a live credential, but its operational validity was not established.

**Impact:** Exposure of a valid Flask signing key could permit session forgery. Exposure of a valid API token could permit unauthorized access to the associated service.

**Remediation:** Remove embedded secrets, load credentials from a secure secret store or environment, and rotate any credentials that have been exposed.

### 4. OS Command Injection

**Severity:** Critical (scanner-free); High (scanner-assisted)  
**Classification:** CWE-78  
**File:** `target-app/storage.py:37-43`  
**Detection:** Scanner-assisted and scanner-free reviews

**Explanation:** The `generate_report` function interpolates the user-controlled `report_format` parameter into a command string executed using `subprocess.run(..., shell=True)`.

**Impact:** An attacker could inject shell metacharacters and execute operating-system commands with the application's privileges.

**Remediation:** Avoid shell execution. Use argument arrays with `shell=False` and validate report formats against an explicit allowlist.

### 5. Path Traversal

**Severity:** High  
**Classification:** CWE-22  
**File:** `target-app/storage.py:25-28`  
**Detection:** Scanner-free review

**Explanation:** The `read_upload` function combines an untrusted filename with the upload directory without verifying that the resolved path remains inside the permitted directory.

**Impact:** An authenticated attacker could potentially read files outside the upload directory.

**Remediation:** Validate filenames and enforce that resolved file paths remain within the designated upload directory.

### 6. Hardcoded Universal Password

**Severity:** High  
**Classification:** CWE-798  
**File:** `target-app/auth.py:55-57`  
**Detection:** Scanner-assisted and scanner-free reviews

**Explanation:** The `verify_password` function accepts the literal password `password123` when the user's stored password hash matches the predictable demonstration format.

**Impact:** An attacker who knows the hardcoded password could authenticate as accounts using the demonstration credential scheme.

**Remediation:** Remove the hardcoded password comparison and implement proper salted password hashing and verification.

## Detection Observations

The scanner-free review independently identified all six planted vulnerability categories.

The scanner-assisted review identified SQL injection, hardcoded secrets, command injection, and the hardcoded password, but did not report the BOLA or path traversal vulnerabilities.

Both reviews also identified a separate hardcoded reporting API token.

The scanner-assisted review classified several additional scanner alerts as informational or false positives.

## Evaluation Summary

**Final score: 60/60**

- Six of six planted vulnerability categories identified.
- Zero unmatched findings according to the workshop evaluation harness.
- All reported source locations were cross-referenced against the workshop application.
- Severity ratings reflect model output and have not been independently validated through exploitation.

These results demonstrate successful detection on this specific workshop benchmark, not a generalized vulnerability-detection accuracy rate.
