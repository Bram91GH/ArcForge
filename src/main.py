import argparse
import yaml
import os

from tools.scraper.generic_scraper import GenericScraper
from tools.core.save_strategy import CsvStrategy, JsonStrategy, XmlStrategy  # Extendable

def main():
    config_path = parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Always look in the config folder
    full_path = os.path.join(base_dir, "..", "config", config_path)
    full_path = os.path.normpath(full_path)

    print(f"Loading config from: {full_path}")
    config = load_config(full_path)


    # Scraper setup
    scraper = GenericScraper(
        base_url=config["base_url"],
        start_page=config["start_page"],
        end_page=config["end_page"],
        link_base=config["link_base"],
        pagination_enabled=config.get("pagination", False)
    )

    print("📰 Scraping listing page...")
    data = scraper.scrape_listing_data(config["field_selectors"])
    df = scraper.create_dataframe(data)

    if config.get("enrich", False):
        print("📄 Enriching with full article content...")
        df = scraper.enrich_dataframe_column_from_pages(
            df,
            column_name=config.get("enrich_column", "content"),  # Use YAML value, fallback to "content"
            selectors=config["enrich_selectors"],
            attr=None
        )

    print(f"✅ Extracted {len(df)} records")

    saver = get_saver(config["save_strategy"])
    saver.save(df, config["output_name"])

def parse_args():
    parser = argparse.ArgumentParser(description="Run a scraping session with a specified YAML config.")
    parser.add_argument("-c", "--config", type=str, required=True, help="Path to the config YAML file.")
    args = parser.parse_args()
    return args.config

def load_config(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)

def get_saver(strategy: str):
    if strategy == "csv":
        return CsvStrategy()
    elif strategy == "json":
        return JsonStrategy()
    elif strategy == "xml":
        return XmlStrategy()
    else:
        raise ValueError(f"Unsupported save strategy: {strategy}")

if __name__ == "__main__":
    main()
