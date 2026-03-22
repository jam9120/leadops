from contextlib import contextmanager

import duckdb

from app.core.config import DB_PATH, ensure_directories


@contextmanager
def get_connection():
    ensure_directories()
    conn = duckdb.connect(str(DB_PATH))
    try:
        yield conn
    finally:
        conn.close()