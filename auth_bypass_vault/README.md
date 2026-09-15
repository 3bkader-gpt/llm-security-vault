# 🛡️ Authentication & Authorization Bypass Vault (Auth Bypass Vault)

A curated, comprehensive knowledge base and technical intelligence repository dedicated to **Authentication Bypasses**, **Broken Access Control (BAC)**, **Insecure Direct Object References (IDOR)**, **OAuth/SSO Flaws**, **Two-Factor Authentication (2FA) Bypasses**, **SAML 2.0 Exploitation**, **GraphQL Auth Vulnerabilities**, **Reverse Proxy Evasion**, and **JWT/Session Exploitation**.

Every document in this vault is **100% in English**, fully unabridged, strictly technical, and audited to eliminate noise, promotional digests, and superficial summaries.

---

## 📊 Vault Intelligence Summary

| Section | Description | Item Count | Status |
| :--- | :--- | :--- | :--- |
| [📁 01 HackerOne Disclosed Reports](./01_hackerone_disclosed_reports/INDEX.md) | High-impact disclosed H1 reports with full PoCs & vendor notes | **27 Reports** | Verified & Unabridged |
| [📁 02 Bug Bounty Writeups & Articles](./02_telegram_writeups_and_articles/INDEX.md) | In-depth technical articles & real-world exploit breakdowns | **34 Writeups** | Curated & De-noised |
| [📁 03 Methodology & Cheatsheets](./03_cheatsheet_and_methodology/INDEX.md) | Tactical testing workflows, exploit payloads & bypass patterns | **7 Deep Guides** | Battle-Tested |
| [📁 04 Payloads & Wordlists](./04_payloads_and_wordlists/README.md) | Ready-to-use dictionaries for Burp Intruder & ffuf | **4 Wordlists** | Production Ready |
| **Total Artifacts** | **Complete Auth & Access Control Arsenal** | **74 Assets** | **100% Coverage** |

---

## 🗂️ Vault Structure & Architecture

```text
auth_bypass_vault/
├── 01_hackerone_disclosed_reports/       # Real-world disclosed reports from HackerOne (27 Reports)
│   ├── INDEX.md                          # Interactive index with severity, bounties & upvotes
│   ├── 791775_Email_Confirmation_Bypass_in_myshopify_SSO_Privilege_Escalation.md (1,917 Upvotes)
│   ├── 745324_Account_takeover_via_leaked_session_cookie.md ($20,000 Bounty)
│   ├── 1342088_Flickr_Account_Takeover_using_AWS_Cognito_API.md (Critical Flickr ATO)
│   ├── 489146_Confidential_data_of_users_accessible_via_GraphQL.md (1,033 Upvotes)
│   ├── 219205_Authentication_bypass_on_auth.uber.com_via_subdomain_takeover.md
│   ├── 2831902_[CRITICAL]_0-Click_Account_Takeover_via_Password_Reset.md
│   ├── 1698316_Cache_Deception_Allows_Account_Takeover.md
│   ├── 226659_Password_Reset_link_hijacking_via_Host_Header_Poisoning.md
│   └── ... (27 full reports with step-by-step reproduction flows)
│
├── 02_telegram_writeups_and_articles/    # Real-world intelligence from top bounty hunters (34 Writeups)
│   ├── INDEX.md                          # Full classified index of all articles
│   ├── oauth_and_sso/                    # 14 writeups (OAuth misconfigs, SSO leaks, redirect flaws)
│   ├── jwt_and_session_attacks/          # 9 writeups (Algorithm confusion, secret tampering, fixation)
│   ├── idor_and_bac/                     # 6 writeups (Mass assignment, race conditions, UUID bypasses)
│   └── 2fa_and_mfa_bypass/               # 5 writeups (AiTM session theft, response manipulation, timing)
│
├── 03_cheatsheet_and_methodology/        # Practical, actionable exploitation resources (7 Deep Guides)
│   ├── INDEX.md                          # Index of all technical methodologies
│   ├── auth_testing_methodology.md       # 5-phase systematic authentication testing workflow
│   ├── oauth_jwt_session_cheatsheet.md   # Exploit payload matrix for OAuth, JWT, and Sessions
│   ├── idor_access_control_patterns.md   # Practical guide to IDOR parameter manipulation & BAC
│   ├── saml_sso_exploitation_guide.md    # XML Signature Wrapping (XSW 1-8), Comment Injection & Stripping
│   ├── graphql_auth_bypass_patterns.md   # Query batching (2FA brute-force), Relay IDs & @auth directives
│   ├── reverse_proxy_header_auth_bypass.md # Spring Boot /..;/, URL normalization, Hop-by-hop & IP spoofing
│   └── web_cache_deception_and_host_header_ato.md # Cache rule exploitation & Host Header ATO poisoning
│
└── 04_payloads_and_wordlists/            # Ready-to-use fuzzing wordlists (4 Toolkits)
    ├── README.md                         # Instructions for Burp Intruder & ffuf integration
    ├── auth_bypass_headers.txt           # 45+ IP spoofing and gateway identity override headers
    ├── path_normalization_payloads.txt   # URL normalization and matrix variable traversal payloads
    ├── idor_parameters_wordlist.txt      # Comprehensive parameter names list for IDOR & BOLA
    └── mass_assignment_parameters.txt    # High-value JSON keys for privilege escalation
```

---

## 🎯 Highlighted Case Studies

### 1. Zero-Click & 1-Click Account Takeovers (ATO)
- **Shopify [Report #791775](./01_hackerone_disclosed_reports/791775_Email_Confirmation_Bypass_in_myshop.myshopify.com_that_Leads_to_Full_Privilege_Escalation_.md):** Email confirmation bypass leading to full privilege escalation across all store owners using Shopify SSO (1,917 upvotes).
- **Remitly [Report #2831902](./01_hackerone_disclosed_reports/2831902_[CRITICAL]_0-Click_Account_Takeover_via_Password_Reset_[AUTH-3243]__orchestrator_v1_passwo.md):** 0-click account takeover via unauthenticated password reset endpoint misconfiguration.
- **Flickr [Report #1342088](./01_hackerone_disclosed_reports/1342088_Flickr_Account_Takeover_using_AWS_Cognito_API.md):** Account takeover using misconfigured AWS Cognito identity pool APIs.

### 2. Modern MFA / 2FA Bypasses
- **BigBear 2.0 AiTM Campaign [Writeup](./02_telegram_writeups_and_articles/2fa_and_mfa_bypass/2026-09-11_BigBear_2.0__The_Phishing_Kit_That_Beats_MFA_Without_a_Password.md):** Evilginx2-based adversary-in-the-middle session cookie theft capturing post-MFA credentials across Microsoft 365.
- **Race Condition in OTP Verification [Writeup](./02_telegram_writeups_and_articles/2fa_and_mfa_bypass/2026-08-25_The_art_of_Race_Condition_how_a_simple_race_condition_can_leads_to_ATO!.md):** Bypassing single-use 6-digit OTP rate limits via concurrent thread synchronization.

### 3. JWT Cryptographic & Implementation Flaws
- **VaultDesk $8,500 Algorithm Confusion [Writeup](./02_telegram_writeups_and_articles/jwt_and_session_attacks/2026-09-09_I_Forged_My_Own_Admin_Token_by_Exploiting_JWT_Algorithm_Confusion_($8,500_Bounty.md):** Forging superadmin tokens by switching RS256 to HS256 using the publicly exposed JWKS RSA public key as HMAC secret.
- **JWT Security Complete Walkthrough [Writeup](./02_telegram_writeups_and_articles/oauth_and_sso/2026-07-26_JWT_Security_TryHackMe_Room_Walkthrough.md):** Deep technical dive into `none` algorithm, header parameter injection (`jwk`, `jku`, `kid`), and dictionary attacks.

### 4. GraphQL & Enterprise SSO
- **HackerOne [Report #489146](./01_hackerone_disclosed_reports/489146_Confidential_data_of_users_and_limited_metadata_of_programs_and_reports_accessible_via_Gra.md):** Confidential user data, session information, and OTP backup codes exposed via unauthenticated GraphQL queries (1,033 upvotes).
- **SAML 2.0 Exploitation Guide [Guide](./03_cheatsheet_and_methodology/saml_sso_exploitation_guide.md):** Deep-dive into XML Signature Wrapping (XSW 1-8), assertion stripping, and XML comment injection in enterprise IdPs.

---

## 🛠️ Testing Methodology & Quick Reference

For day-to-day bug hunting and web application penetration testing, refer to the guides in `03_cheatsheet_and_methodology/`:

1. [Authentication Testing Methodology](./03_cheatsheet_and_methodology/auth_testing_methodology.md): Follow the 5-phase testing checklist (Recon -> Auth Bypass -> 2FA Bypass -> OAuth/SSO Analysis -> Session Management).
2. [OAuth, JWT & Session Cheatsheet](./03_cheatsheet_and_methodology/oauth_jwt_session_cheatsheet.md): Ready-to-use cheat tables for `redirect_uri` manipulation, JWT header tampering, and session cookie flags.
3. [IDOR & Access Control Patterns](./03_cheatsheet_and_methodology/idor_access_control_patterns.md): Concrete parameter mutation patterns, method overrides, and multi-tenant privilege escalation flows.
4. [SAML 2.0 & Enterprise SSO Guide](./03_cheatsheet_and_methodology/saml_sso_exploitation_guide.md): Auditing SAML assertions, XML Signature Wrapping, and SAML Raider workflows.
5. [GraphQL Auth Bypass Patterns](./03_cheatsheet_and_methodology/graphql_auth_bypass_patterns.md): Query batching, alias multiplexing for 2FA bypass, and Relay Global ID decoding.
6. [Reverse Proxy & Header Bypasses](./03_cheatsheet_and_methodology/reverse_proxy_header_auth_bypass.md): Spring Boot semicolon matrix `/..;/`, hop-by-hop headers, and IP spoofing.
7. [Web Cache Deception & Host ATO](./03_cheatsheet_and_methodology/web_cache_deception_and_host_header_ato.md): Static extension confusion, delimiter tricks, and password reset poisoning.

---
*Maintained in the Auth Bypass Vault — strictly technical, comprehensive, and updated with real-world intelligence.*
