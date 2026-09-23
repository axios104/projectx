"""
Site2 Spider: Real Estate Directory Spider (XPath Selectors)

Demonstrates XPath selectors, multi-level crawling, and extracting the 5 target fields:
- Name of the client
- Name of organisation
- Designation
- Phone no
- Location
"""

import scrapy
from projectx.scraper.items import DirectoryItem
from projectx.scraper.utils.helpers import clean_text


class Site2Spider(scrapy.Spider):
    """
    Spider for scraping real estate directory listings.
    Uses XPath selectors for data extraction.

    HOW TO CUSTOMIZE:
    1. Update `allowed_domains` and `start_urls` with the real website.
    2. Update XPath selectors in `parse()` and `parse_listing()` to match the real HTML.
    3. Run: scrapy crawl site2
    """
    name = 'site2'
    allowed_domains = ['example-directory2.com']  # TODO: Replace with real domain
    start_urls = ['https://example-directory2.com/agents']  # TODO: Replace with real URL

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    }

    def parse(self, response):
        """Parse the listing/category page to find agent profile links."""
        self.logger.info(f"Parsing listing page: {response.url}")
        try:
            # ── Extract links to individual agent profiles ──
            # Replace XPath with the actual path for agent profile links
            listing_links = response.xpath(
                '//div[contains(@class, "agent-card")]//a/@href'
            ).getall()
            for link in listing_links:
                yield response.follow(link, callback=self.parse_listing)

            # ── Pagination ──
            # Replace XPath with the actual path for next page link
            next_page = response.xpath(
                '//a[contains(@class, "pagination-next")]/@href'
            ).get()
            if next_page:
                self.logger.info(f"Following next page: {next_page}")
                yield response.follow(next_page, callback=self.parse)

        except Exception as e:
            self.logger.error(f"Error parsing listing page {response.url}: {e}")

    def parse_listing(self, response):
        """Extract the 5 required fields using XPath selectors."""
        self.logger.info(f"Parsing listing: {response.url}")
        try:
            item = DirectoryItem()

            # ── Name of the client ──
            item['name_of_the_client'] = response.xpath(
                '//h1[@class="agent-name"]/text()'
            ).get(default='')

            # ── Name of organisation ──
            item['name_of_organisation'] = response.xpath(
                '//span[@class="agency-name"]/text()'
            ).get(default='')

            # ── Designation ──
            item['designation'] = response.xpath(
                '//span[@class="agent-role"]/text()'
            ).get(default='Director')

            # ── Phone number ──
            item['phone_no'] = response.xpath(
                '//a[contains(@class, "phone")]/@href'
            ).get(default='')

            # ── Location ──
            item['location'] = response.xpath(
                '//span[@class="location"]/text()'
            ).get(default='')

            yield item

        except Exception as e:
            self.logger.error(f"Error parsing listing {response.url}: {e}")
