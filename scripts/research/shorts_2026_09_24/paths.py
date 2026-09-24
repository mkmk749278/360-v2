"""Where the research data lives. Nothing here is committed: `fetch.py`
rebuilds it from the public Binance archive (data.binance.vision)."""
import os

DATA = os.environ.get("SHORTS_DATA_DIR", os.path.expanduser("~/shorts_research_data"))
os.makedirs(DATA, exist_ok=True)
