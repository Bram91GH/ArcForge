# tools/core/pipeline_factory.py

class ToolPipeline:
    def __init__(self, scrape_func_and_scraper, strategy):
        self.scrape_func, self.scraper = scrape_func_and_scraper
        self.strategy = strategy

    def run(self, enrich=False, name="output"):
        data = self.scrape_func()
        df = self.scraper.create_dataframe(data)

        if enrich:
            df = self.scraper.enrich_dataframe_column_from_pages(
                df,
                column_name="content",
                selectors=["article p"]
            )

        self.strategy.save(df, name)


class ToolPipelineFactory:
    def create_pipeline(self, scraper, fields: dict, strategy):
        return ToolPipeline(
            scrape_func_and_scraper=(lambda: scraper.scrape_listing_data(fields), scraper),
            strategy=strategy
        )
