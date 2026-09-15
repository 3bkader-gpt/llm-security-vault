# Practical Payloads & Wordlists for Authentication Testing

A tactical toolkit of fuzzing wordlists, header dictionaries, and parameter payloads configured for automated and manual authentication auditing.

---

## Wordlists Inventory

| Wordlist | File | Description | Recommended Tool |
| :--- | :--- | :--- | :--- |
| **Auth Bypass Headers** | [`auth_bypass_headers.txt`](./auth_bypass_headers.txt) | 45+ headers for IP spoofing, gateway identity overrides, and 401/403 bypasses | Burp Intruder / Match & Replace |
| **Path Normalization Payloads** | [`path_normalization_payloads.txt`](./path_normalization_payloads.txt) | Traversal, semicolon matrix variables, and URL encoding variations | `ffuf` / Turbo Intruder |
| **IDOR Parameters** | [`idor_parameters_wordlist.txt`](./idor_parameters_wordlist.txt) | Common user/tenant/entity identifier query and JSON keys | Burp Param Miner / `ffuf` |
| **Mass Assignment Keys** | [`mass_assignment_parameters.txt`](./mass_assignment_parameters.txt) | Privilege escalation and role assignment parameters | Burp Repeater / Postman |

---

## 🚀 Tool Integration Examples

### 1. ffuf: Path Normalization Fuzzing
```bash
ffuf -u "https://target.com/FUZZ/users" -w path_normalization_payloads.txt -mc 200,302
```

### 2. ffuf: IP Spoofing & Header Injection
```bash
ffuf -u "https://target.com/admin" -H "FUZZ" -w auth_bypass_headers.txt -mc 200,302,500
```

### 3. Burp Suite: Match & Replace Rule
1. Navigate to **Proxy** -> **Proxy Settings** -> **Match and Replace**.
2. Add a rule to inject headers automatically on every request:
   - **Type:** Request Header
   - **Match:** `^Host: .*$`
   - **Replace:** `Host: target.com\r\nX-Forwarded-For: 127.0.0.1\r\nX-Original-URL: /admin`

---
*Archived in Auth Bypass Vault from verified bug bounty community intelligence.*
