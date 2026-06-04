import asyncio
import os
import urllib.parse
import re
import json
import random
import aiohttp
from playwright.async_api import async_playwright
from dotenv import load_dotenv
# Copyright © 2026 NZ0. Released under the MIT License.
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(SCRIPT_DIR, "crawled-apps.json")
SLUGS_FILE = os.path.join(SCRIPT_DIR, "app_slugs.txt")

VERBOSE = True

GITHUB_APP_URL_PATTERN = re.compile(r'github\.com/apps/([a-zA-Z0-9-]+)', re.IGNORECASE)


TARGET_KEYWORDS = [
    "download", "installer", "setup", "crack", "patch", 
    "keygen", "activator", "serial key", "full version", 
    "free plugin", "update agent", "secure check", "verification"
]


DOWNLOAD_PATTERNS = {
    "executable_payload": re.compile(r'https?://[^\s"\'><,\\#]+\.(?:exe|msi|bat|cmd|ps1|vbs|scr|lnk)', re.IGNORECASE),
    "compressed_archive": re.compile(r'https?://[^\s"\'><,\\#]+\.(?:zip|rar|7z|tar|gz|iso|img)', re.IGNORECASE),
    "cloud_storage_bucket": re.compile(r'https?://(?:[^\s"\'><,\\]+\.)?(?:s3\.amazonaws\.com|storage\.googleapis\.com|sharepoint\.com|onedrive\.live\.com|mediafire\.com|mega\.nz|dropbox\.com)/[^\s"\'><,\\]*', re.IGNORECASE),
    "github_raw_delivery": re.compile(r'https?://raw\.githubusercontent\.com/[^\s"\'><,\\]+', re.IGNORECASE)
}


IOC_PATTERNS = {
    "suspicious_tld": re.compile(r'https?://(?:[a-zA-Z0-9-]+\.)*(?:xyz|top|site|online|click|space|biz|live|pw|cc|icu|gq|cf|tk|ml)/[^\s"\'><,\\]*'),
    "discord_webhook": re.compile(r'https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[a-zA-Z0-9-_]+'),
    "telegram_bot": re.compile(r'https://api\.telegram\.org/bot\d+:[a-zA-Z0-9-_]+'),
    "ngrok_tunnel": re.compile(r'https://[a-zA-Z0-9-]+\.ngrok-free\.app'),
    "crypto_wallet": re.compile(r'\b(?:0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{26,33}|bc1[a-zA-Z0-9]{39,59})\b')
}

def log(msg):
    if VERBOSE:
        print(msg, flush=True)

async def apply_stealth_mechanics(context):
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    """)

async def handle_captcha_interception(page):
    """
    Scans the DOM for Google verification indicators.
    Blocks program execution if a captcha is present, until it is solved.
    """
    while True:
        html_snapshot = await page.content()
        
        # Standard Google CAPTCHA indicators
        is_blocked = (
            "g-recaptcha" in html_snapshot or 
            "To continue, please type the characters" in html_snapshot or
            "captcha" in page.url.lower() or
            "sorry/index" in page.url.lower()
        )
        
        if not is_blocked:
            break
            
        log("[!] ACTION REQUIRED: Google threw a CAPTCHA challenge.")
        log("[!] Please focus the spawned Chromium window and solve the prompt manually...")
        
        # Sleep to allow the captcha to be solved
        await asyncio.sleep(4)
    

    await asyncio.sleep(1.5)

async def get_slugs_via_google():
    slugs = set()
    
    # --- Allow specification of search results and how many pages to search across ---
    RESULTS_PER_PAGE = 100  # Instructs Google to show 100 results per page
    PAGES_TO_HUNT = 2       # Number of pages to scrape per keyword (e.g., 2 pages = 200 max results)
    
    log(f"[*] Launching Interactive Crawling NZ0 (Max {RESULTS_PER_PAGE * PAGES_TO_HUNT} results per keyword)...")

    async with async_playwright() as p:
        # --- Make sure you keep this as headless set to false otherwise captchas will not be solveable!!
        browser = await p.chromium.launch(headless=False)
        
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        await apply_stealth_mechanics(context)
        page = await context.new_page()

        for keyword in TARGET_KEYWORDS:
            query_string = f'"github.com/apps/" "{keyword}"'
            encoded_query = urllib.parse.quote_plus(query_string)
            
            for page_idx in range(PAGES_TO_HUNT):
                start_offset = page_idx * RESULTS_PER_PAGE
                

                url = f"https://www.google.com/search?q={encoded_query}&num={RESULTS_PER_PAGE}&start={start_offset}"
                
                log(f"[*] Querying: {query_string} | Page {page_idx + 1} (Offset: {start_offset})")

                try:
                    # randomize sleep to attempt bypassing captchas or to look less automated
                    await asyncio.sleep(random.uniform(4.0, 7.5))
                    
                    await page.goto(url, timeout=45000, wait_until="domcontentloaded")
                    
                    # Intercept CAPTCHA if it prompts in the UI window
                    await handle_captcha_interception(page)

                    # Check if Google returned empty results or "did not match any documents" page
                    html_snapshot = await page.content()
                    if "did not match any documents" in html_snapshot or "Our systems have detected unusual traffic" in html_snapshot:
                        log(f"[-] No more valid results or soft-block hit for '{keyword}' at page {page_idx + 1}. Skipping remaining pages.")
                        break

                    hrefs = await page.locator("a").evaluate_all(
                        "elements => elements.map(el => el.href).filter(href => href)"
                    )
                    
                    page_finds = 0
                    for href in hrefs:
                        decoded_href = urllib.parse.unquote(href)
                        match = GITHUB_APP_URL_PATTERN.search(decoded_href)
                        if match:
                            slug = match.group(1).strip()
                            if slug and slug not in ["features", "marketplace", "settings", "search", "about", "privacy"]:
                                if slug not in slugs:
                                    slugs.add(slug)
                                    page_finds += 1
                                    log(f"   [+] Identified Target App: {slug}")
                    
                    log(f"[+] Harvested {page_finds} new targets from Page {page_idx + 1}.")
                    
                    # If a page returned absolutely zero apps, subsequent index pages are likely empty aswell
                    if page_finds == 0:
                        break

                except Exception as e:
                    log(f"[!] Target fetching failed for '{keyword}' on page {page_idx + 1}: {e}")
                    break

        log("[*] Closing Browser.")
        await browser.close()

    with open(SLUGS_FILE, "w", encoding="utf-8") as f:
        for slug in sorted(slugs):
            f.write(slug + "\n")

    log(f"[+] Total Endpoints: {len(slugs)}")
    return list(slugs)

async def analyze_app_metadata(session, slug):
    url = f"https://api.github.com/apps/{slug}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                owner = data.get("owner", {})
                raw_payload_text = json.dumps(data)
                
                detected_downloads = {}
                detected_iocs = {}
                is_malicious = False

                for category, regex in DOWNLOAD_PATTERNS.items():
                    matches = list(set(regex.findall(raw_payload_text)))
                    if matches:
                        detected_downloads[category] = matches
                        is_malicious = True  

                for ioc_type, regex in IOC_PATTERNS.items():
                    matches = list(set(regex.findall(raw_payload_text)))
                    if matches:
                        detected_iocs[ioc_type] = matches
                        is_malicious = True

                return {
                    "slug": slug,
                    "app_name": data.get("name"),
                    "creator": owner.get("login"),
                    "creator_id": owner.get("id"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "description": data.get("description"),
                    "external_url": data.get("external_url"),
                    "threat_hunting_metrics": {
                        "is_suspicious": is_malicious,
                        "collected_download_links": detected_downloads,
                        "infrastructure_iocs": detected_iocs
                    },
                    "status": "active"
                }
            elif response.status == 404:
                return {"slug": slug, "status": "deleted"}
            else:
                return {"slug": slug, "status": f"error_{response.status}"}
    except Exception as e:
        return {"slug": slug, "status": "failed", "error": str(e)}

async def main():
    log("=" * 60)
    log("[*] Scan Starting")
    log("=" * 60)

    slugs = await get_slugs_via_google()
    if not slugs:
        log("[!] aborted: No target profiles gathered via search index.")
        return

    log(f"[*] Preforming API lookups {len(slugs)} targets...")
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_app_metadata(session, slug) for slug in slugs]
        results = await asyncio.gather(*tasks)

    flagged_apps = [r for r in results if r.get("threat_hunting_metrics", {}).get("is_suspicious") is True]

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log(f"\n[+] Scanning complete. logs: {RESULTS_FILE}")
    log(f"[!] CRITICAL WARN: Found {len(flagged_apps)} GitHub apps acting as active payload delivery vectors.")

    if flagged_apps:
        print("\n=== Found regex matches or points of interest ===")
        print(json.dumps(flagged_apps, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
