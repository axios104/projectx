import os
import json
import logging
from datetime import datetime, timezone
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter

from projectx.scraper.utils.helpers import clean_text


class CleaningPipeline:
    """Pipeline for cleaning and normalizing item fields."""

    def process_item(self, item, spider):
        """Clean all string fields — strip whitespace, normalize text."""
        adapter = ItemAdapter(item)

        for field_name in adapter.field_names():
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = clean_text(value)

        # Normalize phone number format: ensure it starts with 'tel:' prefix
        phone = adapter.get('phone_no')
        if phone:
            # Strip any existing prefix and whitespace
            phone_clean = phone.replace('tel:', '').replace('tel.', '').strip()
            # Remove spaces, dashes, parentheses from phone
            phone_clean = phone_clean.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            adapter['phone_no'] = f'tel:{phone_clean}' if phone_clean else ''

        return item


class ValidationPipeline:
    """Pipeline for validating required fields and deduplicating."""

    def __init__(self):
        """Initialize with empty set for seen entries."""
        self.seen = set()

    def process_item(self, item, spider):
        """Validate that essential fields exist and item is not duplicate."""
        adapter = ItemAdapter(item)

        # Must have at least a client name or organisation name
        client = adapter.get('name_of_the_client', '').strip()
        org = adapter.get('name_of_organisation', '').strip()

        if not client and not org:
            raise DropItem("Missing both client name and organisation name")

        # Deduplicate by (client_name, organisation) tuple
        key = (client.lower(), org.lower())
        if key in self.seen:
            raise DropItem(f"Duplicate entry: {client} / {org}")
        self.seen.add(key)

        return item


class JsonExportPipeline:
    """Pipeline for exporting items to a JSON array file."""

    # The 5 fields in exact column order for the final Excel
    FIELD_ORDER = [
        'name_of_the_client',
        'name_of_organisation',
        'designation',
        'phone_no',
        'location',
    ]

    def __init__(self, output_dir):
        """Initialize pipeline with output directory."""
        self.output_dir = output_dir
        self.file = None
        self.first_item = True

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline from crawler settings."""
        return cls(
            output_dir=crawler.settings.get('OUTPUT_DIR', 'output')
        )

    def open_spider(self, spider):
        """Called when spider opens. Setup file and directory."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"{spider.name}_{timestamp}.json"
        self.filepath = os.path.join(self.output_dir, filename)

        self.file = open(self.filepath, 'w', encoding='utf-8')
        self.file.write("[\n")
        self.first_item = True
        spider.logger.info(f"Exporting JSON to {self.filepath}")

    def close_spider(self, spider):
        """Called when spider closes. Close file properly."""
        if self.file:
            self.file.write("\n]\n")
            self.file.close()
            spider.logger.info(f"Finished exporting JSON to {self.filepath}")

    def process_item(self, item, spider):
        """Write item to JSON file with only the 5 required fields in order."""
        adapter = ItemAdapter(item)

        # Build ordered dict with only the 5 target fields
        ordered = {}
        for field in self.FIELD_ORDER:
            ordered[field] = adapter.get(field, '')

        line = json.dumps(ordered, ensure_ascii=False, indent=2)

        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False

        # Indent each line for proper JSON array formatting
        indented = '\n'.join('  ' + l for l in line.split('\n'))
        self.file.write(indented)
        return item
