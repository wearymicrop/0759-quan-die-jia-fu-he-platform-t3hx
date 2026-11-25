import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "券叠加复核台"
RULE_VERSION = "retail-promo-1.0"
SOURCES = ('events', 'rules')


def db_path():
    return Path(os.environ.get("DB_PATH", ROOT / "instance/ledger.sqlite3"))
