import scrapy


class DirectoryItem(scrapy.Item):
    """Item representing a scraped directory entry.

    Exactly 5 fields matching the final Excel output format:
    - Name of the client (person name)
    - Name of organisation (company/business name)
    - Designation (job title)
    - Phone no (phone number)
    - Location (city/area)
    """
    name_of_the_client = scrapy.Field()
    name_of_organisation = scrapy.Field()
    designation = scrapy.Field()
    phone_no = scrapy.Field()
    location = scrapy.Field()
