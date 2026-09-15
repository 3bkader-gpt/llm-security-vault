#!/usr/bin/env python3
"""
Fetch disclosed HackerOne reports (High/Critical severity) via GraphQL API
and save as individual Markdown files in reports/ folder.
"""

import requests
import json
import os
import re
import time
from pathlib import Path

GRAPHQL_ENDPOINT = "https://hackerone.com/graphql"

# New HackerOne Search API (replaces deprecated hacktivity_items)
QUERY_TEMPLATE = """
query HacktivitySearchQuery($queryString: String!, $from: Int, $size: Int, $sort: SortInput!) {
  search(
    index: CompleteHacktivityReportIndex
    query_string: $queryString
    from: $from
    size: $size
    sort: $sort
  ) {
    __typename
    total_count
    nodes {
      __typename
      ... on HacktivityDocument {
        id
        _id
        reporter {
          id
          username
          name
          __typename
        }
        cve_ids
        cwe
        severity_rating
        public
        report {
          id
          databaseId: _id
          title
          substate
          url
          disclosed_at
          report_generated_content {
            id
            hacktivity_summary
            __typename
          }
          __typename
        }
        votes
        team {
          id
          handle
          name
          url
          currency
          __typename
        }
        total_awarded_amount
        latest_disclosable_action
        latest_disclosable_activity_at
        submitted_at
        disclosed
        has_collaboration
        collaborators {
          id
          username
          name
          __typename
        }
        __typename
      }
    }
  }
}
"""


FILTERS = [
    {
        "name": "backend_ssrf_rce",
        "label": "Backend Beast (SSRF & RCE)",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:SSRF OR cwe:"Code Injection" OR SSRF) AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "logic_idor_auth",
        "label": "Logic King (IDOR & Auth Bypass)",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:IDOR OR cwe:"Insecure Direct Object Reference" OR cwe:"Improper Authorization" OR IDOR) AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "xss",
        "label": "XSS Hunter",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:XSS OR cwe:"Cross-site Scripting" OR XSS) AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "advanced_injection_rce",
        "label": "Modern Injections (SSTI, Cmd, Deserialization)",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:Template OR cwe:Command OR cwe:Deserialization OR SSTI OR "Command Injection" OR Deserialization) AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "race_condition",
        "label": "Race Condition & Timing",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:Race OR "race condition" OR TOCTOU OR "concurrent execution") AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "request_smuggling",
        "label": "Request Smuggling & Desync",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:Smuggling OR "Request Smuggling" OR "HTTP Request Smuggling" OR H2C OR "CL.TE" OR "TE.CL" OR Desync) AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "oauth_sso",
        "label": "Identity & OAuth",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (cwe:OAuth OR cwe:Authentication OR OAuth OR SSO OR "access token" OR "OpenID") AND total_awarded_amount:>=200 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "complex_chains_privesc",
        "label": "Chains & Privilege Escalation",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND (chain OR "privilege escalation" OR "directory traversal" OR "path traversal" OR "account takeover") AND total_awarded_amount:>=500 AND disclosed_at:[2019-01-01 TO *]',
        "max": 200
    },
    {
        "name": "general_high_critical_massive",
        "label": "Massive General High/Critical",
        "query": 'severity_rating:(High OR Critical) AND substate:Resolved AND disclosed:true AND disclosed_at:[2019-01-01 TO *]',
        "sort": {"field": "votes", "direction": "DESC"},
        "min_votes": 20,
        "max": 500
    }
]


def fetch_reports(query_string: str, max_reports=200, sort=None, min_votes=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    if sort is None:
        sort = {
            "field": "latest_disclosable_activity_at",
            "direction": "DESC"
        }

    reports = []
    offset = 0
    page_size = 25

    while len(reports) < max_reports:
        payload = {
            "operationName": "HacktivitySearchQuery",
            "variables": {
                "queryString": query_string,
                "from": offset,
                "size": page_size,
                "sort": sort
            },
            "query": QUERY_TEMPLATE
        }

        print(f"[+] Fetching page (offset={offset})...")
        try:
            resp = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except Exception as err:
            print(f"[-] Request error at offset={offset}: {err}")
            break

        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")

        search_result = data.get("data", {}).get("search", {})
        nodes = search_result.get("nodes", [])

        if not nodes:
            print("[-] No more nodes returned.")
            break

        for node in nodes:
            if not isinstance(node, dict) or node.get("__typename") != "HacktivityDocument":
                continue

            sev = (node.get("severity_rating") or "").lower()
            if sev not in ("high", "critical"):
                continue

            votes = node.get("votes") or 0
            if min_votes is not None and votes < min_votes:
                continue

            report = node.get("report") or {}
            team = node.get("team") or {}

            rep_id = report.get("databaseId") or node.get("_id")
            if not rep_id:
                continue

            bounty_val = node.get("total_awarded_amount")
            bounty_str = str(bounty_val) if bounty_val is not None else "N/A"

            reports.append({
                "id": str(rep_id),
                "title": report.get("title") or f"Report {rep_id}",
                "severity_rating": node.get("severity_rating", "N/A"),
                "cwe": node.get("cwe", "N/A"),
                "substate": report.get("substate", "N/A"),
                "bounty": bounty_str,
                "currency": (team.get("currency") or "USD").upper(),
                "team": team.get("handle", "unknown"),
                "disclosed_at": report.get("disclosed_at", "N/A"),
                "votes": votes,
                "url": report.get("url") or f"https://hackerone.com/reports/{rep_id}",
                "summary": (report.get("report_generated_content") or {}).get("hacktivity_summary", ""),
            })

            if len(reports) >= max_reports:
                break

        if len(nodes) < page_size:
            break

        offset += page_size
        time.sleep(0.5)

    return reports[:max_reports]


def sanitize_filename(name: str) -> str:
    """Remove/replace characters unsafe for Windows filenames."""
    if not name:
        return "Untitled"
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r'\s+', "_", name)
    sanitized = name.strip("._")[:120]
    return sanitized if sanitized else "report"


def save_report_md(report: dict, reports_dir: Path):
    safe_title = sanitize_filename(report.get("title", "Untitled"))
    filename = f"{report['id']}_{safe_title}.md"
    filepath = reports_dir / filename

    md = f"""# {report['title']}

- **Report ID:** [{report['id']}]({report['url']})
- **Severity:** {report['severity_rating']}
- **CWE:** {report['cwe']}
- **Substate:** {report['substate']}
- **Bounty:** {report['bounty']} {report['currency']}
- **Program:** {report['team']}
- **Disclosed:** {report['disclosed_at']}
- **Votes:** {report['votes']}

## URL
{report['url']}

## Summary
{report['summary'] or 'No summary available.'}

## Notes
> Use this report for training your bug-hunting agent.
> Study the vulnerability type, impact, and proof-of-concept details.
"""
    filepath.write_text(md, encoding="utf-8")
    print(f"[+] Saved: {filepath}")


def main():
    base_dir = Path("reports")
    base_dir.mkdir(exist_ok=True)
    seen_ids = set()

    for f in FILTERS:
        folder = base_dir / f["name"]
        folder.mkdir(exist_ok=True)
        print(f"\n=== {f['label']} ({f['name']}) ===")
        print(f"[*] Query: {f['query']}")

        reports = fetch_reports(
            query_string=f["query"],
            max_reports=f["max"],
            sort=f.get("sort"),
            min_votes=f.get("min_votes")
        )
        print(f"[*] Fetched {len(reports)} reports.")

        saved = 0
        skipped = 0
        for r in reports:
            rid = r["id"]
            if rid in seen_ids:
                skipped += 1
                continue
            seen_ids.add(rid)
            save_report_md(r, folder)
            saved += 1

        print(f"[*] Saved {saved} new, skipped {skipped} duplicates.")

    print(f"\n[*] All filters processed. Total unique reports: {len(seen_ids)}. Done.")


if __name__ == "__main__":
    main()
