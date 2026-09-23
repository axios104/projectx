BOT_NAME = 'projectx'
SPIDER_MODULES = ['projectx.scraper.spiders']
NEWSPIDER_MODULE = 'projectx.scraper.spiders'

# ═══════════════════════════════════════════════════════════════
# Playwright (headless browser) — required for JS-heavy sites
# ═══════════════════════════════════════════════════════════════
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-gpu",
    ],
}
# Max concurrent Playwright pages
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4

# ═══════════════════════════════════════════════════════════════
# Anti-detection
# ═══════════════════════════════════════════════════════════════
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 4
DOWNLOAD_DELAY_JITTER = 0.5  # Scrapy 2.19

# AutoThrottle (adaptive rate limiting)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 4
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 1
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# Cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Cache (useful during development)
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = 'httpcache'

# ═══════════════════════════════════════════════════════════════
# Middlewares
# ═══════════════════════════════════════════════════════════════
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # Disable these for Playwright to avoid fingerprint mismatch
    # 'projectx.scraper.middlewares.RandomUserAgentMiddleware': 400,
    # 'projectx.scraper.middlewares.CustomHeadersMiddleware': 401,
    # 'projectx.scraper.middlewares.ProxyRotationMiddleware': 610,
    # 'projectx.scraper.middlewares.BanDetectionMiddleware': 620,
}

# ═══════════════════════════════════════════════════════════════
# Pipelines
# ═══════════════════════════════════════════════════════════════
ITEM_PIPELINES = {
    'projectx.scraper.pipelines.CleaningPipeline': 100,
    'projectx.scraper.pipelines.ValidationPipeline': 200,
    'projectx.scraper.pipelines.JsonExportPipeline': 300,
}

# ═══════════════════════════════════════════════════════════════
# Request headers (mimicking real Chrome browser)
# ═══════════════════════════════════════════════════════════════
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Language': 'en-AU,en-US;q=0.9,en;q=0.8',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'none',
#     'Sec-Fetch-User': '?1',
#     'Cache-Control': 'max-age=0',
# }

# ═══════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# ═══════════════════════════════════════════════════════════════
# Output / Proxy paths
# ═══════════════════════════════════════════════════════════════
import os
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
PROXY_LIST_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'proxies.txt')
PROXY_ENABLED = False
