"""ProjectX CLI - Web Scraper & Data Formatter

Usage:
    python run.py scrape <spider_name> [--output-dir DIR]
    python run.py format <input> <output> [--schema SCHEMA]
    python run.py list-spiders
    python run.py list-schemas
"""
import sys
import argparse
from pathlib import Path

def cmd_scrape(args):
    try:
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
    except ImportError:
        print("Scrapy is not installed. Please install it to use the scraper.")
        sys.exit(1)
        
    settings = get_project_settings()
    
    if args.output_dir:
        output_path = Path(args.output_dir) / f"{args.spider_name}_output.json"
        settings.set('FEEDS', {
            str(output_path): {'format': 'json'}
        })
        
    process = CrawlerProcess(settings)
    process.crawl(args.spider_name)
    process.start()

def cmd_format(args):
    from projectx.formatter.cli import main as formatter_main
    # Mock sys.argv for the sub-CLI parser
    sys.argv = ['formatter'] + sys.argv[2:]
    formatter_main()

def cmd_list_spiders(args):
    try:
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
    except ImportError:
        print("Scrapy is not installed.")
        sys.exit(1)
        
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    spider_loader = process.spider_loader
    print("Available spiders:")
    for name in spider_loader.list():
        print(f"  - {name}")

def cmd_list_schemas(args):
    from projectx.formatter.schemas import SchemaRegistry
    registry = SchemaRegistry()
    print("Available schemas:")
    for name in registry.list_schemas():
        schema = registry.get(name)
        print(f"  - {name}: {schema.description}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    
    # Add src dir to path dynamically to ensure projectx module is found
    src_dir = str(Path(__file__).parent.parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        
    if command == 'scrape':
        parser = argparse.ArgumentParser(prog="run.py scrape")
        parser.add_argument('spider_name', help='Name of the spider to run')
        parser.add_argument('--output-dir', help='Output directory for scraped data')
        args = parser.parse_args(sys.argv[2:])
        cmd_scrape(args)
        
    elif command == 'format':
        cmd_format(None)
        
    elif command == 'list-spiders':
        cmd_list_spiders(None)
        
    elif command == 'list-schemas':
        cmd_list_schemas(None)
        
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
