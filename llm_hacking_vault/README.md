# LLM Hacking & AI Security Research Vault

A comprehensive, curated repository indexing full disclosed bug bounty reports, technical writeups, practical PoC patterns, and competition challenges focused on **LLM & AI Security, Prompt Injection, and Autonomous Agent Exploitation**.

---

## 📂 Vault Architecture & Directory Map

```text
llm_hacking_vault/
│
├── 01_hackerone_disclosed_reports/       # Full unabridged HackerOne reports with complete PoCs
│   ├── [21 verified complete disclosed reports including full reproduction steps]
│   └── INDEX.md                          # Comprehensive index sorted by community upvotes
│
├── 02_telegram_writeups_and_articles/    # Curated technical writeups & research papers (44 articles)
│   ├── prompt_injection/                 # Direct, indirect & invisible prompt injection guides
│   ├── agent_and_mcp_security/           # Autonomous agent risks, MCP server bugs & tool abuse
│   ├── rag_and_vector_dbs/               # Vector database vulnerabilities & RAG context attacks
│   ├── tools_and_training/               # Pen-testing toolkits and security labs (e.g., YoloLLM)
│   └── INDEX.md                          # Master index with author attribution & source links
│
├── 03_huntr_and_bounty_challenges/       # Targeted AI competitions & bounties
│   ├── huntr_ai_challenges.md            # Active challenges on the Huntr platform ($15k rewards)
│   └── ai_bounty_programs.md             # Dedicated AI bug bounty programs & VDPs
│
└── 04_cheatsheet_and_methodology/        # Technical frameworks & attack patterns
    ├── owasp_llm_top10_guide.md          # OWASP Top 10 for LLMs mapped to real disclosed CVEs
    ├── testing_methodology.md            # Step-by-step pentesting methodology for AI systems
    └── poc_reference_patterns.md         # Ready-to-use PoC templates for prompt extraction & SSRF
```

---

## 🚀 Quick Navigation & Highlights

| Section | Description | Verified Count | Direct Link |
| :--- | :--- | :--- | :--- |
| **Disclosed Reports** | Unabridged HackerOne reports with complete PoCs | **21 Full Reports** | [`INDEX.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/01_hackerone_disclosed_reports/INDEX.md) |
| **Curated Writeups** | Full articles on Prompt Injection, RAG, and MCP | **44 Full Articles** | [`INDEX.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/02_telegram_writeups_and_articles/INDEX.md) |
| **Huntr Challenges** | $15,000 AI Agent competitions on Huntr | **Curated Challenges** | [`huntr_ai_challenges.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/03_huntr_and_bounty_challenges/huntr_ai_challenges.md) |
| **AI Bug Bounties** | Live scopes rewarding LLM & Jailbreak bugs | **Active Programs** | [`ai_bounty_programs.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/03_huntr_and_bounty_challenges/ai_bounty_programs.md) |
| **OWASP LLM Top 10** | Detailed vulnerability mapping with real examples | **10 Categories** | [`owasp_llm_top10_guide.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/04_cheatsheet_and_methodology/owasp_llm_top10_guide.md) |
| **Testing Methodology**| Practical guide for hunting bugs in AI applications | **6 Testing Phases** | [`testing_methodology.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/04_cheatsheet_and_methodology/testing_methodology.md) |
| **PoC Patterns** | Functional payloads for extraction, exfil & tool abuse | **Production Payloads** | [`poc_reference_patterns.md`](file:///c:/Users/medoo/Desktop/llm/llm_hacking_vault/04_cheatsheet_and_methodology/poc_reference_patterns.md) |

---

## 🎯 Quality Standards & Content Filtering
All materials in this repository have been strictly vetted:
- **Zero Ads or Spam:** Promotional feature releases and subscription marketing have been fully removed.
- **Full Unabridged Content:** Reports include original steps to reproduce, full PoC payloads (including invisible unicode tag characters), and vendor disclosure notes.
- **Pure AI & LLM Focus:** Covers prompt injection, MCP servers, autonomous agent tool abuse, RAG context poisoning, and model guardrail bypasses.
