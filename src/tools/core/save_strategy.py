from abc import ABC, abstractmethod
import pandas as pd
import os
import sqlite3
from datetime import datetime

class SaveStrategy(ABC):
    @abstractmethod
    def save(self, df: pd.DataFrame, name: str):
        pass

class CsvStrategy(SaveStrategy):
    def save(self, df, name):
        path = f"outputs/csv/{name}_{self._timestamp()}.csv"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"✅ Saved CSV to {path}")

    def _timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M")

class JsonStrategy(SaveStrategy):
    def save(self, df, name):
        path = f"outputs/json/{name}_{self._timestamp()}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_json(path, orient="records", lines=False)
        print(f"✅ Saved JSON to {path}")

    def _timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M")

class SqliteStrategy(SaveStrategy):
    def __init__(self, db_path="outputs/db/data.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def save(self, df, name):
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(name, conn, if_exists="append", index=False)
        print(f"✅ Saved to SQLite DB table '{name}' in {self.db_path}")

class XmlStrategy(SaveStrategy):
    def save(self, df, name):
        path = f"outputs/xml/{name}_{self._timestamp()}.xml"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Save DataFrame as XML
        # root_name: top-level tag, row_name: per record tag
        df.to_xml(path, root_name="records", row_name="record", index=False)

        print(f"✅ Saved XML to {path}")

    def _timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M")