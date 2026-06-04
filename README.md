# AppScan

A helpful Python tool for tracking SEO poisoning across Google. In response to malware being distributed via rogue GitHub apps, AppScan works by using a light headless browser through Playwright to query select keywords in a search engine. This allows it to crawl into these search results and fetch data on GitHub apps pushing malware.

Furthermore, it is designed with modularity by allowing you to specify your own regex detections and search keywords within the script.

![Running instance of appscan](https://github.com/Net-Zer0/AppScan/blob/main/appscan-running.png?raw=true)

---

## Enviroment Setup

```bash
python -m venv .venv
source .venv/bin/activate
```

Create a `.env` file for storing your GitHub token for API requests.

Inside add this variable:

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx
```

You can grab a token by heading to your profile, going to Developer Settings, and selecting Tokens. Use a classic token with no permissions added. We simply need the token for queries to the GitHub API for information on APPS.

---

## Installing Dependencies

```bash
pip install aiohttp playwright python-dotenv
playwright install chromium
```

After installing these in the virtual environment, Playwright needs a browser and browser dependencies for your system. The commands below will help you with this.

### For apt-based systems

```bash
sudo playwright install-deps chromium
```

### For RPM/DNF-based systems

```bash
sudo dnf install -y nss atk at-spi2-atk cups-libs libdrm gtk3 libXcomposite libXdamage libXfixes libXrandr mesa-libgbm pango alsa-lib
```

---

## Test the Install

```bash
python -c "import aiohttp, dotenv, playwright; print('OK')"
```

---

## Running the Crawler

Inside the virtual environment you just created, simply run:

```bash
python appscan.py
```

---

## About

This was a tiny little PoC heavily sped up with the help of LLMs in tracking malicious sites being hosted off GitHub to help analysts track malware campaigns.

---

## Configurations

Inside the script there are sections for setting keywords, your own regex, and custom IOCs or slugs in the context of this script. Furthermore, there is also a section for changing how many results to search per page and how many pages to search through.

---

## Output

AppScan will output all the scraped queries and app sites into a `.json` file.

![Output from appscan](https://github.com/Net-Zer0/AppScan/blob/main/output-json.png?raw=true)
