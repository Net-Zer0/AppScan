# AppScan

A helpful Python tool for tracking SEO poisoning across Google. In response to malware being distributed via rogue GitHub apps, AppScan works by using a lightweight browser through Playwright to query select keywords in a search engine. This allows it to crawl search results and collect data on GitHub apps potentially being used to distribute malware.

It runs with a visible browser window to allow users to solve CAPTCHAs presented by Google and continue automated scanning.

Furthermore, it is designed with modularity in mind by allowing you to specify your own regex detections, indicators, and search keywords within the script.

![Running instance of AppScan](https://github.com/Net-Zer0/AppScan/blob/main/appscan-running.png?raw=true)

---

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
```

Create a `.env` file for storing your GitHub token for API requests.

Add the following variable:

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx
```

You can create a token by navigating to:

**GitHub Profile → Settings → Developer Settings → Personal Access Tokens**

A classic token with no additional permissions is sufficient. The token is only used for querying the GitHub API for information related to GitHub Apps.

---

## Installing Dependencies

```bash
pip install aiohttp playwright python-dotenv
playwright install chromium
```

After installing the Python packages, Playwright also requires browser dependencies.

### For apt-based systems

```bash
sudo playwright install-deps chromium
```

### For RPM/DNF-based systems

```bash
sudo dnf install -y nss atk at-spi2-atk cups-libs libdrm gtk3 libXcomposite libXdamage libXfixes libXrandr mesa-libgbm pango alsa-lib
```

---

## Test the Installation

```bash
python -c "import aiohttp, dotenv, playwright; print('OK')"
```

---

## Running the Crawler

Inside the virtual environment you just created:

```bash
python appscan.py
```

You will more than likely encounter a CAPTCHA while querying Google. This is expected due to Google's anti-automation protections.

Playwright runs in a visible browser window, allowing you to solve the CAPTCHA manually and continue scraping results without restarting the scan.

---

## About

This was a small proof-of-concept project heavily accelerated with the help of LLMs to assist analysts in tracking malicious sites hosted through GitHub and identifying malware distribution campaigns.

---

## Configuration

Several variables can be customized to fit your research requirements.

### General Configuration

```python
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(SCRIPT_DIR, "crawled-apps.json")
SLUGS_FILE = os.path.join(SCRIPT_DIR, "app_slugs.txt")

VERBOSE = True

GITHUB_APP_URL_PATTERN = re.compile(
    r'github\.com/apps/([a-zA-Z0-9-]+)',
    re.IGNORECASE
)

TARGET_KEYWORDS = [
    "keyword",
    "etc"
]
```

### Download Detection Patterns

```python
DOWNLOAD_PATTERNS = {
    "executable_payload": re.compile(...),
    "compressed_archive": re.compile(...),
    "cloud_storage_bucket": re.compile(...),
    "github_raw_delivery": re.compile(...)
}
```

### IOC Detection Patterns

```python
IOC_PATTERNS = {
    "suspicious_tld": re.compile(...),
    "discord_webhook": re.compile(...),
    "telegram_bot": re.compile(...),
    "ngrok_tunnel": re.compile(...),
    "crypto_wallet": re.compile(...)
}
```

These patterns can be modified or expanded to support your own research objectives and detection logic.

> **Note:** It is strongly recommended to use the `.env` file for storing your GitHub token rather than hardcoding credentials directly into the script.

### Search Scope Configuration

The number of search results processed is controlled by:

```python
RESULTS_PER_PAGE = 100  # Request up to 100 results per page
PAGES_TO_HUNT = 2       # Number of pages to scrape per keyword
```

For example:

* `RESULTS_PER_PAGE = 100`
* `PAGES_TO_HUNT = 2`

Would allow up to **200 search results per keyword**.

---

## Output

AppScan outputs all discovered queries, GitHub App references, and collected findings into a JSON file:

```text
crawled-apps.json
```

Example output:

![Output from AppScan](https://github.com/Net-Zer0/AppScan/blob/main/output-json.png?raw=true)

---

## License

Released under the MIT License.

Copyright © 2026 NZ0
