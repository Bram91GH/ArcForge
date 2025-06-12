# tools/core/port_scraper.py

from abc import ABC, abstractmethod

class PortScraper(ABC):
    @abstractmethod
    def scrape_listing_data(self, fields: dict):
        pass

    @abstractmethod
    def create_dataframe(self, data: list):
        pass

    @abstractmethod
    def enrich_dataframe_column_from_pages(self, df, column_name: str, selectors: list, attr: str = None):
        pass