import logging
import random
from urllib.parse import urlparse
from scrapy.exceptions import CloseSpider, IgnoreRequest

from projectx.scraper.utils.user_agents import USER_AGENTS

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware:
    """Middleware for assigning random User-Agent strings to requests."""

    def __init__(self, per_domain_mode=True):
        """Initialize middleware with optional per-domain pinning."""
        self.user_agents = USER_AGENTS
        self.per_domain_mode = per_domain_mode
        self.domain_uas = {}

    @classmethod
    def from_crawler(cls, crawler):
        """Create from crawler settings."""
        # Could read per_domain_mode from settings if desired
        return cls(per_domain_mode=True)

    def process_request(self, request, spider):
        """Assign random User-Agent to the request."""
        if self.per_domain_mode:
            domain = urlparse(request.url).netloc
            if domain not in self.domain_uas:
                self.domain_uas[domain] = random.choice(self.user_agents)
            ua = self.domain_uas[domain]
        else:
            ua = random.choice(self.user_agents)

        request.headers['User-Agent'] = ua
        spider.logger.debug(f"Assigned User-Agent {ua} to {request.url}")


class CustomHeadersMiddleware:
    """Middleware for assigning custom anti-detect headers."""

    @classmethod
    def from_crawler(cls, crawler):
        """Create from crawler settings."""
        return cls()

    def process_request(self, request, spider):
        """Assign headers based on the request."""
        domain = urlparse(request.url).netloc
        
        # Referer header
        if 'Referer' not in request.headers:
            request.headers['Referer'] = f'https://www.google.com/search?q={domain}'
            
        # SEC-CH headers mimicking modern Chrome
        ua = request.headers.get(b'User-Agent', b'').decode('utf-8')
        if 'Chrome' in ua:
            request.headers['sec-ch-ua'] = '"Google Chrome";v="128", "Chromium";v="128", "Not=A?Brand";v="24"'
            if 'Windows' in ua:
                request.headers['sec-ch-ua-platform'] = '"Windows"'
            elif 'Mac OS X' in ua:
                request.headers['sec-ch-ua-platform'] = '"macOS"'
            elif 'Linux' in ua:
                request.headers['sec-ch-ua-platform'] = '"Linux"'
                
        # DNT header
        request.headers['DNT'] = str(random.choice([0, 1]))


class ProxyRotationMiddleware:
    """Middleware for rotating proxies."""

    def __init__(self, proxy_file, proxy_enabled):
        """Initialize middleware."""
        self.proxy_file = proxy_file
        self.proxy_enabled = proxy_enabled
        self.proxies = []
        if self.proxy_enabled:
            self._reload_proxies()

    @classmethod
    def from_crawler(cls, crawler):
        """Create from crawler settings."""
        return cls(
            proxy_file=crawler.settings.get('PROXY_LIST_FILE'),
            proxy_enabled=crawler.settings.getbool('PROXY_ENABLED', False)
        )

    def _reload_proxies(self):
        """Reload proxies from file."""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")
        except FileNotFoundError:
            logger.error(f"Proxy file not found at {self.proxy_file}")
            self.proxies = []

    def process_request(self, request, spider):
        """Assign random proxy to the request if enabled."""
        if not self.proxy_enabled or not self.proxies:
            return

        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
        spider.logger.debug(f"Using proxy {proxy} for {request.url}")

    def process_exception(self, request, exception, spider):
        """Handle connection errors by marking proxies as dead."""
        if not self.proxy_enabled:
            return
            
        proxy = request.meta.get('proxy')
        if proxy and proxy in self.proxies:
            spider.logger.warning(f"Removing dead proxy {proxy} due to {exception}")
            self.proxies.remove(proxy)
            
            if not self.proxies:
                spider.logger.critical("All proxies are dead. Closing spider.")
                raise CloseSpider("all_proxies_dead")
                
            # Retry request with a new proxy (Scrapy RetryMiddleware handles this usually if we return None, 
            # but we can return request to retry immediately if preferred)
            return request


class BanDetectionMiddleware:
    """Middleware to detect bans and retries with new settings."""

    def __init__(self):
        """Initialize middleware tracking domains."""
        self.ban_counts = {}

    @classmethod
    def from_crawler(cls, crawler):
        """Create from crawler settings."""
        return cls()

    def process_response(self, request, response, spider):
        """Check response for ban indicators."""
        domain = urlparse(request.url).netloc
        
        is_banned = False
        if response.status in [403, 429, 503]:
            is_banned = True
        elif hasattr(response, 'text'):
            # Check response body for text indicators
            try:
                body = response.text.lower()
                ban_indicators = ['captcha', 'blocked', 'access denied', 'rate limit']
                if any(indicator in body for indicator in ban_indicators):
                    is_banned = True
            except Exception:
                pass

        if is_banned:
            self.ban_counts[domain] = self.ban_counts.get(domain, 0) + 1
            spider.logger.warning(f"Ban detected on {domain}. Ban count: {self.ban_counts[domain]}")
            
            if self.ban_counts[domain] > 10:
                spider.logger.warning(f"Too many bans on {domain}, you should increase delays.")
                
            # Create a new request to retry
            retry_req = request.copy()
            retry_req.dont_filter = True
            
            # If using proxies, clear the old one so a new one is selected
            if 'proxy' in retry_req.meta:
                del retry_req.meta['proxy']
                
            return retry_req

        return response
