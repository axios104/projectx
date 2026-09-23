"""Helper utility functions for the scraper."""

import re
import unicodedata
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime, timezone


def clean_text(text: str | None) -> str:
    """
    Strip, collapse multiple whitespace to single space, and normalize unicode.
    
    Args:
        text: The string to clean.
        
    Returns:
        The cleaned string, or empty string if input is None.
    """
    if text is None:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Replace multiple whitespaces with single space and strip
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def to_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Convert a relative URL to an absolute URL using the base URL.
    
    Args:
        base_url: The base absolute URL.
        relative_url: The relative URL.
        
    Returns:
        The resolved absolute URL.
    """
    if not relative_url:
        return base_url
    return urljoin(base_url, relative_url)


def extract_price(text: str | None) -> float | None:
    """
    Extract numeric price from strings like '$29.99', '€15,50', 'USD 100'.
    
    Args:
        text: The string containing the price.
        
    Returns:
        The extracted price as a float, or None if no price found.
    """
    if not text:
        return None
    # Match numbers with optional decimal separators
    match = re.search(r'[\d]+(?:[.,]\d+)?', text)
    if match:
        # Standardize decimal separator
        price_str = match.group(0).replace(',', '.')
        try:
            return float(price_str)
        except ValueError:
            return None
    return None


def extract_rating(text: str | None) -> float | None:
    """
    Extract rating number from strings like '4.5 out of 5', '4.5/5', '4.5 stars'.
    
    Args:
        text: The string containing the rating.
        
    Returns:
        The extracted rating as a float, or None if no rating found.
    """
    if not text:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def safe_css_get(response, selector: str, default: str = '') -> str:
    """
    Safely get the first CSS match or default.
    
    Args:
        response: The Scrapy response or selector object.
        selector: The CSS selector string.
        default: The default value to return if no match.
        
    Returns:
        The text content of the match or the default string.
    """
    try:
        result = response.css(selector).get()
        return result if result is not None else default
    except Exception:
        return default


def safe_xpath_get(response, xpath: str, default: str = '') -> str:
    """
    Safely get the first XPath match or default.
    
    Args:
        response: The Scrapy response or selector object.
        xpath: The XPath selector string.
        default: The default value to return if no match.
        
    Returns:
        The text content of the match or the default string.
    """
    try:
        result = response.xpath(xpath).get()
        return result if result is not None else default
    except Exception:
        return default


def normalize_url(url: str) -> str:
    """
    Remove tracking parameters (utm_*, ref, etc.) from URL.
    
    Args:
        url: The URL to normalize.
        
    Returns:
        The normalized URL without tracking parameters.
    """
    if not url:
        return ""
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Filter out common tracking parameters
    filtered_params = {
        k: v for k, v in query_params.items() 
        if not k.startswith('utm_') and k not in ('ref', 'fbclid', 'gclid', 'msclkid')
    }
    
    # Reconstruct URL
    new_query = urlencode(filtered_params, doseq=True)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )


def timestamp_now() -> str:
    """
    Return the current time as an ISO 8601 timestamp string.
    
    Returns:
        The timestamp string.
    """
    return datetime.now(timezone.utc).isoformat()
