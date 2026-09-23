"""
Site4 Spider: Real Estate Directory Spider (JSON API)

Demonstrates JSON API parsing, API pagination, and extracting the 5 target fields:
- Name of the client
- Name of organisation
- Designation
- Phone no
- Location
"""

import scrapy
import json
from projectx.scraper.items import DirectoryItem
from projectx.scraper.utils.helpers import clean_text


class Site4Spider(scrapy.Spider):
    """
    Spider for scraping real estate directory data from a JSON API.

    HOW TO CUSTOMIZE:
    1. Update `allowed_domains` and `start_urls` with the real API endpoint.
    2. Update the JSON key paths in `parse()` to match the real API response structure.
    3. Add any required API headers/keys in `custom_settings` or `start_requests()`.
    4. Run: scrapy crawl site4
    """
    name = 'site4'
    allowed_domains = ['api.example-directory4.com']  # TODO: Replace with real domain
    start_urls = ['https://api.example-directory4.com/v1/agents?page=1']  # TODO: Replace

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        """Override to add any API-specific headers or authentication."""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                headers={
                    'Accept': 'application/json',
                    # 'Authorization': 'Bearer YOUR_API_KEY',  # Uncomment if needed
                },
            )

    def parse(self, response):
        """Parse JSON API response and extract the 5 target fields."""
        self.logger.info(f"Parsing API response: {response.url}")

        # Rate limit check
        if response.status == 429:
            self.logger.warning(f"Rate limited on {response.url}")
            return

        try:
            data = response.json()

            # ── Extract the items array ──
            # Adjust the key to match the real API structure
            # Common patterns: data['results'], data['data'], data['items'], data['agents']
            items = data.get('results', data.get('data', data.get('items', [])))

            if not items:
                self.logger.info(f"No more items at {response.url}. Stopping.")
                return

            for record in items:
                item = DirectoryItem()

                # ── Map API fields to our 5 target fields ──
                # Replace these keys with the actual JSON keys from the API response

                # Name of the client (try common API field names)
                item['name_of_the_client'] = (
                    record.get('name')
                    or record.get('agent_name')
                    or record.get('full_name')
                    or record.get('first_name', '') + ' ' + record.get('last_name', '')
                ).strip()

                # Name of organisation
                item['name_of_organisation'] = (
                    record.get('agency')
                    or record.get('organisation')
                    or record.get('company')
                    or record.get('agency_name')
                    or ''
                )

                # Designation
                item['designation'] = (
                    record.get('designation')
                    or record.get('title')
                    or record.get('role')
                    or record.get('position')
                    or 'Director'
                )

                # Phone number
                item['phone_no'] = (
                    record.get('phone')
                    or record.get('phone_number')
                    or record.get('mobile')
                    or record.get('contact_number')
                    or ''
                )

                # Location
                item['location'] = (
                    record.get('location')
                    or record.get('suburb')
                    or record.get('city')
                    or record.get('area')
                    or ''
                )

                yield item

            # ── Handle API pagination ──
            next_page = data.get('next_page', data.get('next', data.get('next_url')))
            if next_page:
                yield response.follow(next_page, callback=self.parse)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON from {response.url}: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing API response {response.url}: {e}")
