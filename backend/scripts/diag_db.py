"""Prueba mínima de conexión SQLite con las variantes de URL."""
import os
import sqlite3
from pathlib import Path

target = Path(r"C:\nutri-region-colombia\backend\nutriregion.db")
print("exists:", target.exists(), "| size:", target.stat().st_size if target.exists() else None)
print("readable:", target.exists() and os.access(target, os.R_OK))
print("writable:", target.exists() and os.access(target, os.W_OK))

variants = [
    f"sqlite:///{target.as_posix()}",
    f"sqlite:///{target}",
    f"sqlite:///{str(target).replace(chr(92), '/')}",
]
from sqlalchemy import create_engine

for url in variants:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.exec_driver_sql("select 1")
        print("OK  :", url)
    except Exception as error:  # noqa: BLE001
        print("FAIL:", url, "->", type(error).__name__)

print("--- sqlite3 directo ---")
try:
    direct = sqlite3.connect(target)
    print("sqlite3 OK:", direct.execute("select count(*) from foods").fetchone())
    direct.close()
except Exception as error:  # noqa: BLE001
    print("sqlite3 FAIL:", type(error).__name__, error)
