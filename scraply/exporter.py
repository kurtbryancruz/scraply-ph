import json
import pandas as pd
from typing import List


def to_json(jobs: List[dict]) -> str:
    return json.dumps(jobs, ensure_ascii=False, indent=2)


def to_csv(jobs: List[dict]) -> str:
    if not jobs:
        return ""
    return pd.DataFrame(jobs).to_csv(index=False)


def to_dataframe(jobs: List[dict]) -> pd.DataFrame:
    return pd.DataFrame(jobs)
