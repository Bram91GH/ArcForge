import time
from bs4 import BeautifulSoup
import requests
import pandas as pd

"""
GenericScraper Tool
-------------------

A flexible and reusable web scraper class designed to extract structured data from listing pages and enrich it
with detail content by visiting individual item links.

Supports scraping e-commerce products, blog articles, news feeds, etc. by defining your own CSS selectors
for fields like title, link, image, and inner page content.

Example use cases are included for:
- Bol.com laptops
- The Guardian sport articles

Dependencies:
- requests
- BeautifulSoup (bs4)
- pandas
"""

def main():
    """Main entry point of the script. Modify the called function here to switch between examples."""
    example_sport_articles()


class GenericScraper:
    """
    A generic web scraper to extract structured data from paginated listing pages and enrich each entry
    by visiting detail pages.

    Attributes:
        base_url (str): The base URL of the listing page.
        start_page (int): The page number to start scraping from.
        end_page (int): The page number to end scraping.
        page_param (str): The pagination query format.
        link_base (str): A prefix to prepend to relative URLs for full navigation.
        headers (dict): HTTP headers used for requests.
        pagination_enabled (bool): Whether to paginate or just scrape a single page.
    """

    def __init__(self, base_url, start_page=1, end_page=1, page_param='?page=', link_base='', pagination_enabled=True):
        self.base_url = base_url.rstrip('/')
        self.start_page = start_page
        self.end_page = end_page
        self.page_param = page_param
        self.link_base = link_base.rstrip('/')
        self.pagination_enabled = pagination_enabled
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

    def request_page(self, url):
        """
        Sends a GET request to the specified URL and returns a BeautifulSoup object of the HTML.

        Args:
            url (str): The URL to fetch.

        Returns:
            BeautifulSoup: Parsed HTML content or None if request fails.
        """
        try:
            print(f"Requesting: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            time.sleep(1)  # rate limiting
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Request failed: {url} - {e}")
            return None

    def scrape_listing_data(self, field_selectors: dict):
        """
        Scrapes field data from listing pages (paginated or single) using the provided CSS selectors.

        Args:
            field_selectors (dict): A dictionary where keys are field names and values are CSS selectors.

        Returns:
            dict: A dictionary containing lists of extracted field data.
        """
        field_data = {key: [] for key in field_selectors}

        if self.pagination_enabled:
            pages = range(self.start_page, self.end_page + 1)
        else:
            pages = [None]  # Single iteration, no page number appended

        for page_num in pages:
            if page_num is None:
                url = self.base_url
            else:
                url = f"{self.base_url}{self.page_param}{page_num}"

            soup = self.request_page(url)
            if not soup:
                continue

            raw_data = {}
            for key, selector in field_selectors.items():
                elements = soup.select(selector)
                if '[href]' in selector:
                    raw_data[key] = [el.get('href') for el in elements]
                elif '[src]' in selector:
                    raw_data[key] = [el.get('src') for el in elements]
                else:
                    raw_data[key] = [el.get_text(strip=True) for el in elements]

            min_len = min(len(lst) for lst in raw_data.values())
            if any(len(lst) != min_len for lst in raw_data.values()):
                print(f"[Warning] Truncating mismatched field lengths on page {page_num}")

            for key in field_data:
                field_data[key].extend(raw_data[key][:min_len])

        return field_data

    def create_dataframe(self, data_dict):
        """
        Converts a dictionary of scraped data into a Pandas DataFrame.

        Args:
            data_dict (dict): Dictionary with keys as column names and values as lists of data.

        Returns:
            pd.DataFrame: DataFrame with aligned fields.
        """
        return pd.DataFrame(data_dict)

    def get_value_from_product_page(self, url, selectors, attr=None):
        """
        Retrieves the first matching value from a product or article detail page.

        Args:
            url (str): The link to the detail page.
            selectors (list): A list of CSS selectors to try in order.
            attr (str, optional): The HTML attribute to extract. Defaults to text content.

        Returns:
            str or None: Extracted value or None if not found.
        """
        full_url = url if url.startswith('http') else self.link_base + url
        soup = self.request_page(full_url)
        if not soup:
            return None

        for selector in selectors:
            tag = soup.select_one(selector)
            if tag:
                return tag.get(attr) if attr else tag.get_text(strip=True)
        return None

    def enrich_dataframe_column_from_pages(self, df, column_name, selectors, attr=None, link_column='link'):
        """
        Enriches a column in the DataFrame by fetching data from each link in another column.

        Args:
            df (pd.DataFrame): DataFrame containing a link column.
            column_name (str): Name of the new column to add.
            selectors (list): CSS selectors to locate content on detail pages.
            attr (str, optional): HTML attribute to extract. Defaults to text content.
            link_column (str): Name of the column containing URLs.

        Returns:
            pd.DataFrame: Updated DataFrame with new column.
        """
        df[column_name] = df[link_column].apply(
            lambda url: self.get_value_from_product_page(url, selectors, attr=attr)
        )
        return df



# --------------------------------------------------------------------------------
# Example Use Cases
# --------------------------------------------------------------------------------

def example_electronics():
    """
    Example: Scrape laptops from bol.com and enrich with product price.
    """
    base_url = "https://www.bol.com/nl/nl/l/laptops/4770/"
    fields = {
        "title": "div.product-item__info",
        "link": "a.product-title.px_list_page_product_click.list_page_product_tracking_target[href]",
        "image_src": "img.skeleton-image__img[src]"
    }

    scraper = GenericScraper(base_url, start_page=1, end_page=2, link_base="https://www.bol.com")
    data = scraper.scrape_listing_data(fields)
    df = scraper.create_dataframe(data)

    df = scraper.enrich_dataframe_column_from_pages(
        df,
        column_name="price",
        selectors=["span.promo-price"]
    )

    print(df.head())


def example_sport_articles():
    """
    Example: Scrape recent sport articles from The Guardian and enrich with full article content.
    """
    base_url = "https://www.theguardian.com/uk/sport"
    fields = {
        "title": "a.dcr-2yd10d[aria-label]",
        "link": "a.dcr-2yd10d[href]"
    }

    scraper = GenericScraper(base_url, start_page=1, end_page=1, link_base="https://www.theguardian.com")

    print("Scraping listing page...")
    data = scraper.scrape_listing_data(fields)
    df = scraper.create_dataframe(data)

    print("Scraping content for each article...")
    df = scraper.enrich_dataframe_column_from_pages(
        df,
        column_name="content",
        selectors=["article p"],
        attr=None
    )

    print(df[["title", "link", "content"]].head(5))

    print("\n", df["title"][0])
    print("\n", df["content"][0])


if __name__ == '__main__':
    main()
