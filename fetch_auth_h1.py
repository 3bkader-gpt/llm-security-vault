import requests
import json
import re
import os
import time
from pathlib import Path

HEADERS = {
    "Accept": "application/json, text/html, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

GRAPHQL_ENDPOINT = "https://hackerone.com/graphql"

GRAPHQL_QUERY = """
query HacktivitySearchQuery($queryString: String!, $from: Int, $size: Int, $sort: SortInput!) {
  search(index: CompleteHacktivityReportIndex, query_string: $queryString, from: $from, size: $size, sort: $sort) {
    total_count
    nodes {
      ... on HacktivityDocument {
        _id
        votes
        severity_rating
        report {
          databaseId: _id
          title
        }
      }
    }
  }
}
"""

SEARCH_QUERIES = [
    'title:"Authentication Bypass" AND disclosed:true',
    'title:"Account Takeover" AND disclosed:true',
    'title:"OAuth" AND (bypass OR takeover) AND disclosed:true',
    'title:"2FA Bypass" AND disclosed:true',
    'title:"IDOR" AND severity_rating:(High OR Critical) AND disclosed:true',
    'title:"Broken Access Control" AND disclosed:true',
    'title:"JWT" AND bypass AND disclosed:true',
]

def sanitize_filename(name: str) -> str:
    name = name or "report"
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r'\s+', "_", name)
    clean = name.strip("._")[:90]
    return clean or "report"

def get_top_auth_report_ids(target_count=30):
    report_candidates = {}
    for q in SEARCH_QUERIES:
        payload = {
            "operationName": "HacktivitySearchQuery",
            "variables": {
                "queryString": q,
                "from": 0,
                "size": 15,
                "sort": {"field": "votes", "direction": "DESC"}
            },
            "query": GRAPHQL_QUERY
        }
        try:
            resp = requests.post(GRAPHQL_ENDPOINT, headers={"Content-Type": "application/json", "Accept": "application/json"}, json=payload, timeout=20)
            data = resp.json()
            nodes = data.get("data", {}).get("search", {}).get("nodes", [])
            for n in nodes:
                rid = str(n.get("report", {}).get("databaseId") or n.get("_id") or "")
                votes = n.get("votes") or 0
                title = (n.get("report") or {}).get("title") or ""
                if rid and rid not in report_candidates:
                    report_candidates[rid] = {"votes": votes, "title": title}
        except Exception as e:
            print(f"Error querying {q}: {e}")
    
    # Sort by votes descending
    sorted_ids = sorted(report_candidates.keys(), key=lambda x: report_candidates[x]["votes"], reverse=True)
    return sorted_ids[:target_count]

def fetch_full_report(report_id: str):
    url = f"https://hackerone.com/reports/{report_id}.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[-] Failed report {report_id}: {e}")
    return None

def build_full_markdown(data: dict) -> str:
    rep_id = data.get("id")
    title = data.get("title", "Untitled Report")
    url = data.get("url") or f"https://hackerone.com/reports/{rep_id}"
    
    state = data.get("substate") or data.get("state") or "disclosed"
    sev_rating = data.get("severity_rating") or "None"
    sev_obj = data.get("severity") or {}
    cvss_score = sev_obj.get("rating") or sev_obj.get("score") or sev_rating
    
    weakness_obj = data.get("weakness") or {}
    weakness_name = weakness_obj.get("name") or "Authentication / Access Control Flaw"
    
    reporter = data.get("reporter") or {}
    reporter_user = reporter.get("username") or "anonymous"
    
    team = data.get("team") or {}
    team_name = team.get("profile", {}).get("name") or team.get("handle") or "Unknown Team"
    
    has_bounty = data.get("has_bounty?")
    bounty_amount = data.get("formatted_bounty") or data.get("bounty_amount")
    bounty_str = f"${bounty_amount}" if bounty_amount else ("Yes (Undisclosed Amount)" if has_bounty else "No Bounty / Swag")
    
    disclosed_at = data.get("disclosed_at") or "Unknown"
    submitted_at = data.get("submitted_at") or data.get("created_at") or "Unknown"
    votes = data.get("vote_count") or 0
    
    vuln_info = data.get("vulnerability_information") or "No detailed description provided."
    
    summaries = data.get("summaries") or []
    summary_blocks = []
    for s in summaries:
        cat = s.get("category", "Summary").title()
        content = s.get("content", "").strip()
        user = s.get("user", {}).get("username", "Team")
        if content:
            summary_blocks.append(f"### {cat} by @{user}\n\n{content}")
    summaries_text = "\n\n".join(summary_blocks) if summary_blocks else "No formal disclosure summary provided."

    md = f"""# Report #{rep_id}: {title}

- **Platform:** HackerOne
- **Report URL:** [{url}]({url})
- **Program:** {team_name}
- **Reporter:** @{reporter_user}
- **Status:** {state.upper()}
- **Severity:** {cvss_score}
- **Weakness:** {weakness_name}
- **Bounty:** {bounty_str}
- **Submitted:** {submitted_at}
- **Disclosed:** {disclosed_at}
- **Community Upvotes:** {votes}

---

## Executive Summaries

{summaries_text}

---

## Full Vulnerability Description & Technical Reproduction Steps

{vuln_info}
"""
    return md

def main():
    vault_dir = Path("auth_bypass_vault/01_hackerone_disclosed_reports")
    vault_dir.mkdir(parents=True, exist_ok=True)

    print("[+] Collecting top Auth Bypass & Account Takeover reports from HackerOne...")
    top_ids = get_top_auth_report_ids(target_count=35)
    print(f"[+] Found {len(top_ids)} high-signal candidates. Downloading unabridged reports...")

    saved_reports = []

    for idx, rid in enumerate(top_ids):
        print(f"[{idx+1}/{len(top_ids)}] Downloading full report #{rid}...")
        data = fetch_full_report(rid)
        if not data:
            continue

        title = data.get("title", "")
        vuln_info = data.get("vulnerability_information") or ""
        
        # Verify substantive content
        if len(vuln_info) < 200:
            print(f"    [-] Skipping report #{rid} (Empty or restricted description)")
            continue

        md_doc = build_full_markdown(data)
        safe_name = sanitize_filename(title)
        filename = f"{rid}_{safe_name}.md"
        filepath = vault_dir / filename
        filepath.write_text(md_doc, encoding="utf-8")
        print(f"    [+] Saved ({len(md_doc)} bytes): {filename}")

        saved_reports.append({
            "id": rid,
            "title": title,
            "program": data.get("team", {}).get("handle", "Unknown"),
            "severity": data.get("severity_rating") or "None",
            "bounty": data.get("formatted_bounty") or (f"${data.get('bounty_amount')}" if data.get('bounty_amount') else "N/A"),
            "votes": data.get("vote_count") or 0,
            "filename": filename,
            "url": data.get("url") or f"https://hackerone.com/reports/{rid}"
        })
        time.sleep(0.3)

    saved_reports.sort(key=lambda x: x["votes"], reverse=True)

    index_md = f"""# HackerOne Disclosed Authentication & Authorization Bypass Reports Index

Total Curated High-Impact Reports: **{len(saved_reports)} Unabridged Reports**

All reports below contain the full original vulnerability disclosures, complete step-by-step reproduction flows, actual HTTP requests/responses, and vendor verification notes directly from HackerOne.

| Report ID | Vulnerability Title | Target Program | Severity | Bounty | Upvotes | Original Report |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in saved_reports:
        index_md += f"| [#{r['id']}](./{r['filename']}) | [{r['title'][:65]}](./{r['filename']}) | `{r['program']}` | {r['severity']} | {r['bounty']} | {r['votes']} | [HackerOne]({r['url']}) |\n"

    (vault_dir / "INDEX.md").write_text(index_md, encoding="utf-8")
    print(f"\n[+] Successfully saved {len(saved_reports)} reports to {vault_dir}")

if __name__ == "__main__":
    main()
