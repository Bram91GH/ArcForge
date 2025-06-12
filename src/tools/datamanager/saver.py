# tools/datamanager/saver.py

from tools.core.save_strategy import SaveStrategy, CsvStrategy, JsonStrategy, SqliteStrategy, XmlStrategy
import pandas as pd

class DataSaver:
    def __init__(self, strategy: SaveStrategy):
        self.strategy = strategy

    def save(self, df: pd.DataFrame, name: str):
        self.strategy.save(df, name)

# Optional factory/helper if you want simplified creation
def create_saver(format: str = "csv") -> DataSaver:
    strategy_map = {
        "csv": CsvStrategy(),
        "json": JsonStrategy(),
        "sqlite": SqliteStrategy(),
        "xml": XmlStrategy()
    }
    strategy = strategy_map.get(format)
    if not strategy:
        raise ValueError(f"Unknown save format: {format}")
    return DataSaver(strategy)
