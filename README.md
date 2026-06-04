# AppScan
A helpful python tool for tracking SEO poisoning across google. In response to malware being distrubuted via rouge github apps.
![Running instance of appscan](https://github.com/Net-Zer0/AppScan/blob/main/appscan-running.png?raw=true)



### Enviroment Setup
python -m venv .venv
source .venv/bin/activate
create .env
inside add
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx

### Installing Dependencies
pip install aiohttp playwright python-dotenv
playwright install chromium

After installing these in the venv playright needs a browser and browser dependencies for your system, the commands below will help you with this!

### For apt based systems
sudo playwright install-deps chromium

### For RPM/DNF based systems
sudo dnf install -y nss atk at-spi2-atk cups-libs libdrm gtk3 libXcomposite libXdamage libXfixes libXrandr mesa-libgbm pango alsa-lib

### Test the Install
python -c "import aiohttp, dotenv, playwright; print('OK')"

### Running the Crawler
Inside the venv env you just created simply
`python appscan.py`
### About
This was a tiny little poc heavily speed up with the help of llms in tracking malicous sites being hosted off github to help analyst track malware campaigns 

## Configurations
Inside the script there are sections for setting keywords, your own regex and custom iocs or slugs in context of this script.

## Output
appscan will output all the scrapped queries and app sites into a .json file!
![Output from appscan](https://github.com/Net-Zer0/AppScan/blob/main/output-json.png?raw=true)
