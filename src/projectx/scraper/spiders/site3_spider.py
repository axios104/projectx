"""
Site3 Spider: Real Estate Directory Spider (Mixed CSS + XPath)

Demonstrates mixed CSS/XPath selectors, 3-level crawling (categories → listings → detail),
and extracting the 5 target fields:
- Name of the client
- Name of organisation
- Designation
- Phone no
- Location
"""

import scrapy
from projectx.scraper.items import DirectoryItem
from projectx.scraper.utils.helpers import clean_text


class Site3Spider(scrapy.Spider):
    """
    Spider for scraping real estate directory with category-based navigation.
    Uses mixed CSS and XPath selectors.

    HOW TO CUSTOMIZE:
    1. Update `allowed_domains` and `start_urls` with the real website.
    2. Update selectors in all parse methods to match the real HTML.
    3. Run: scrapy crawl site3
    """
    name = 'site3'
    allowed_domains = ['example-directory3.com']  # TODO: Replace with real domain
    start_urls = ['https://example-directory3.com/']  # TODO: Replace with real URL

    def parse(self, response):
        """Parse the main page to find location/category links."""
        self.logger.info(f"Parsing main directory: {response.url}")
        try:
            # ── Follow location/region links ──
            # Replace with the actual CSS for location category links
            location_links = response.css('div.locations a::attr(href)').getall()
            for link in location_links:
                yield response.follow(link, callback=self.parse_location)

        except Exception as e:
            self.logger.error(f"Error parsing main page {response.url}: {e}")

    def parse_location(self, response):
        """Parse a location page to find agent listing links."""
        self.logger.info(f"Parsing location page: {response.url}")
        try:
            # ── Extract agent card links within this location ──
            agent_links = response.xpath(
                '//div[contains(@class, "agent-card")]//a/@href'
            ).getall()
            for link in agent_links:
                # Pass location as meta data so we have it on the detail page
                location = response.css('h1.location-title::text').get(default='')
                yield response.follow(
                    link,
                    callback=self.parse_agent,
                    cb_kwargs={'location': clean_text(location)},
                )

            # ── Pagination within the location ──
            next_page = response.css('a.next::attr(href)').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse_location)

        except Exception as e:
            self.logger.error(f"Error parsing location page {response.url}: {e}")

    def parse_agent(self, response, location=''):
        """Extract the 5 required fields from an agent detail page."""
        self.logger.info(f"Parsing agent page: {response.url}")
        try:
            item = DirectoryItem()

            # ── Name of the client ──
            item['name_of_the_client'] = response.css(
                'h1.agent-name::text'
            ).get(default='')

            # ── Name of organisation ──
            item['name_of_organisation'] = response.xpath(
                '//div[@class="agency-info"]//span[@class="name"]/text()'
            ).get(default='')

            # ── Designation ──
            item['designation'] = response.css(
                'span.role::text'
            ).get(default='Director')

            # ── Phone number ──
            # Try multiple selectors (some sites have phone in href, some in text)
            phone = response.css('a[href^="tel:"]::attr(href)').get()
            if not phone:
                phone = response.xpath(
                    '//span[contains(@class, "phone")]/text()'
                ).get(default='')
            item['phone_no'] = phone

            # ── Location ── (use the one passed from the location page, or extract)
            if location:
                item['location'] = location
            else:
                item['location'] = response.css(
                    'span.suburb::text'
                ).get(default='')

            yield item

        except Exception as e:
            self.logger.error(f"Error parsing agent {response.url}: {e}")
