import asyncio
import sys
import re
import os
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import DialogFilter, DialogFilterChatlist

sys.stdout.reconfigure(encoding='utf-8')

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

BASE_VAULT = Path("auth_bypass_vault")
DIR_TG = BASE_VAULT / "02_telegram_writeups_and_articles"

DIR_OAUTH = DIR_TG / "oauth_and_sso"
DIR_IDOR = DIR_TG / "idor_and_bac"
DIR_2FA = DIR_TG / "2fa_and_mfa_bypass"
DIR_JWT = DIR_TG / "jwt_and_session_attacks"

for d in [DIR_OAUTH, DIR_IDOR, DIR_2FA, DIR_JWT]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

KEYWORDS = [
    r"\boauth\b",
    r"\bidor\b",
    r"\bbac\b",
    r"\bbroken access control\b",
    r"\baccount takeover\b",
    r"\bato\b",
    r"\b2fa\b",
    r"\bmfa\b",
    r"\bjwt\b",
    r"\bsession fixation\b",
    r"\bprivilege escalation\b",
    r"\bauthentication bypass\b",
    r"\bauthorization bypass\b"
]

REGEX = re.compile("|".join(KEYWORDS), re.IGNORECASE)

def sanitize(name: str) -> str:
    name = name or "article"
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r'\s+', "_", name)
    clean = name.strip("._")[:80]
    return clean or "item"

def fetch_full_article(url: str):
    if not url or "t.me" in url or "youtube.com" in url or "youtu.be" in url:
        return "", ""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return "", ""
        soup = BeautifulSoup(resp.text, "html.parser")
        h1 = soup.find("h1")
        title = h1.get_text().strip() if h1 else ""
        
        article_tag = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile("post-content|article-content|entry-content", re.I))
        if not article_tag:
            article_tag = soup.body

        elements = article_tag.find_all(["h1", "h2", "h3", "h4", "p", "pre", "blockquote", "li"])
        md_lines = []
        for elem in elements:
            tag = elem.name.lower()
            text = elem.get_text().strip()
            if not text:
                continue
            if tag in ["h1", "h2"]:
                md_lines.append(f"\n## {text}\n")
            elif tag in ["h3", "h4"]:
                md_lines.append(f"\n### {text}\n")
            elif tag == "pre":
                md_lines.append(f"\n```\n{text}\n```\n")
            elif tag == "blockquote":
                md_lines.append(f"\n> {text}\n")
            elif tag == "li":
                md_lines.append(f"- {text}")
            else:
                md_lines.append(f"\n{text}\n")
        return title, "\n".join(md_lines).strip()
    except Exception:
        return "", ""

async def crawl_auth_writeups():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        filters = await client(GetDialogFiltersRequest())
        target_peers = []
        for f in filters.filters:
            if isinstance(f, (DialogFilter, DialogFilterChatlist)):
                title = getattr(f, 'title', None)
                if hasattr(title, 'text'):
                    title = title.text
                if title and "bug_bounty" in title.lower():
                    target_peers = list(f.pinned_peers) + list(f.include_peers)
                    break

        print(f"[*] Scanning {len(target_peers)} Telegram channels for Auth Bypass writeups...")
        seen_urls = set()
        saved_articles = []

        for p in target_peers:
            entity = await client.get_entity(p)
            ch_name = getattr(entity, 'title', getattr(entity, 'first_name', 'Unknown'))
            print(f"[*] Scanning channel: {ch_name}")

            async for msg in client.iter_messages(entity, limit=800):
                if not msg.text:
                    continue
                text = msg.text
                if not REGEX.search(text):
                    continue

                # Filter out promotional spam or simple challenges
                if "try it:" in text.lower() or "available now on all paid" in text.lower() or "obsidian" in text.lower():
                    continue

                url_match = re.search(r'https?://[^\s<>"\')]+', text)
                url = url_match.group(0).rstrip('.)]') if url_match else ""
                
                if url in seen_urls or not url:
                    continue
                seen_urls.add(url)

                date_str = msg.date.strftime("%Y-%m-%d")

                # Fetch full article if possible
                scraped_title, scraped_body = fetch_full_article(url)
                
                title = scraped_title
                if not title:
                    title_match = re.search(r'\*\*(?:Title)?[:\s]*(.*?)\*\*', text, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else ""
                if not title:
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    title = lines[0][:75] if lines else "Auth Bypass Writeup"
                title = re.sub(r'[*_`#▎]', '', title).strip()

                # Content check: ignore stubs
                body_content = scraped_body if len(scraped_body) > 400 else text
                if len(body_content) < 300:
                    continue

                combined_lower = f"{title.lower()} {body_content.lower()}"
                
                if "oauth" in combined_lower or "sso" in combined_lower or "openid" in combined_lower:
                    cat_dir = DIR_OAUTH
                    category = "OAuth & SSO Vulnerabilities"
                    sub_folder = "oauth_and_sso"
                elif "2fa" in combined_lower or "mfa" in combined_lower or "otp" in combined_lower:
                    cat_dir = DIR_2FA
                    category = "2FA & MFA Bypass"
                    sub_folder = "2fa_and_mfa_bypass"
                elif "jwt" in combined_lower or "session" in combined_lower or "cookie" in combined_lower:
                    cat_dir = DIR_JWT
                    category = "JWT & Session Flaws"
                    sub_folder = "jwt_and_session_attacks"
                else:
                    cat_dir = DIR_IDOR
                    category = "IDOR & Broken Access Control"
                    sub_folder = "idor_and_bac"

                filename = f"{date_str}_{sanitize(title)}.md"
                filepath = cat_dir / filename

                md_doc = f"""# {title}

- **Category:** {category}
- **Publication Date:** {date_str}
- **Source Channel:** {ch_name}
- **Original Source URL:** [{url}]({url})

---

## Detailed Writeup & Technical Breakdown

{body_content}

---
*Archived in Auth Bypass Vault from verified bug bounty community intelligence.*
"""
                filepath.write_text(md_doc, encoding="utf-8")
                print(f"[+] Saved writeup: {filename} ({len(md_doc)} bytes)")

                saved_articles.append({
                    "title": title,
                    "date": date_str,
                    "category": category,
                    "sub_folder": sub_folder,
                    "filename": filename,
                    "url": url,
                    "channel": ch_name
                })

        saved_articles.sort(key=lambda x: x["date"], reverse=True)

        index_md = f"""# Curated Authentication & Authorization Bypass Writeups Index

Total Curated In-Depth Writeups: **{len(saved_articles)} Articles**

Every document below has been sourced directly from security researchers, Medium publications, and bug bounty blogs with full technical analysis and functional exploit flows.

| Date | Article Title | Category | Channel | Reference Link |
| :--- | :--- | :--- | :--- | :--- |
"""
        for a in saved_articles:
            local_path = f"./{a['sub_folder']}/{a['filename']}"
            ext_link = f"[Source Link]({a['url']})" if a['url'] else "Telegram"
            index_md += f"| {a['date']} | [{a['title'][:60]}](./{local_path}) | `{a['category']}` | {a['channel']} | {ext_link} |\n"

        (DIR_TG / "INDEX.md").write_text(index_md, encoding="utf-8")
        print(f"[+] Successfully generated INDEX.md for {len(saved_articles)} writeups.")

if __name__ == "__main__":
    asyncio.run(crawl_auth_writeups())
