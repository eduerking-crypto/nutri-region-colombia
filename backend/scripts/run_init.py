"""Aisla: ¿importar app.config rompe sqlite, o la URL de config es distinta?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


HARDCODED = "sqlite:///C:/nutri-region-colombia/backend/nutriregion.db"


def probe(label: str, url: str) -> None:
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        print(f"{label}: OK ({url!r})")
    except Exception as error:  # noqa: BLE001
        print(f"{label}: FAIL ({url!r}) -> {type(error).__name__}")


probe("1_sin_import_config", HARDCODED)

from app import config  # noqa: E402

print("config.DB_URL == HARDCODED:", config.DB_URL == HARDCODED)
print("len config:", len(config.DB_URL), "| len hard:", len(HARDCODED))
for index, (char_a, char_b) in enumerate(zip(config.DB_URL, HARDCODED)):
    if char_a != char_b:
        print(f"diff pos {index}: config={hex(ord(char_a))} hard={hex(ord(char_b))}")
extra = config.DB_URL[len(HARDCODED):] if len(config.DB_URL) > len(HARDCODED) else HARDCODED[len(config.DB_URL):]
if extra:
    print("sobrante:", [hex(ord(ch)) for ch in extra])
probe("2_tras_import_config_url_hardcodeada", HARDCODED)
probe("3_tras_import_config_url_de_config", config.DB_URL)
