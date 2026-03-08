#!/usr/bin/env python3
"""
Bitcoin Treasury frissítő script
---------------------------------
Lekéri a KV Cégcsoport aktuális BTC egyenlegét és P/L értékét
a bitcointreasuries.net oldalról és frissíti a hu/index.html és en/index.html fájlokat.

Használat:
    python3 update_btc_treasury.py

Függőségek:
    pip install requests beautifulsoup4

Ütemezés (naponta 1x):
    - Manuálisan: python3 update_btc_treasury.py
    - GitHub Actions: lásd .github/workflows/update-btc.yml
"""

import re
import sys
import logging
from pathlib import Path
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Hiányzó függőségek. Telepítsd:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

# --- Konfiguráció ---
TREASURY_URL = "https://bitcointreasuries.net/private-companies/kv-cgcsoport"
BASE_DIR = Path(__file__).parent
HTML_FILES = [
    BASE_DIR / "hu" / "index.html",
    BASE_DIR / "en" / "index.html",
]
LOG_FILE = BASE_DIR / "btc_update.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def fetch_treasury_data() -> dict:
    """Lekéri a BTC egyenleget és P/L értéket a bitcointreasuries.net oldalról."""
    log.info(f"Lekérdezés: {TREASURY_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; KVCegcsoport-BTC-Updater/1.0)"
    }

    resp = requests.get(TREASURY_URL, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text()
    data = {}

    # --- BTC egyenleg kinyerése ---

    # 1. módszer: JSON-LD schema keresése
    for script_tag in soup.find_all("script", type="application/ld+json"):
        text = script_tag.string or ""
        match = re.search(r'hold\s+([\d.]+)\s*BTC', text)
        if match:
            data["btc"] = float(match.group(1))
            log.info(f"JSON-LD-ből kinyerve: {data['btc']} BTC")
            break

    # 2. módszer: oldal szövegében keresés
    if "btc" not in data:
        match = re.search(r'([\d,]+\.?\d*)\s*BTC', page_text)
        if match:
            data["btc"] = float(match.group(1).replace(",", ""))
            log.info(f"Oldal szövegéből kinyerve: {data['btc']} BTC")

    if "btc" not in data:
        raise ValueError("Nem sikerült kinyerni a BTC egyenleget.")

    # --- P/L % kinyerése ---
    # Keresés: "-23.22%" vagy "+15.5%" minta
    pl_match = re.search(r'([+-]?\d+\.?\d*)%', page_text)
    if pl_match:
        data["pl_pct"] = float(pl_match.group(1))
        log.info(f"P/L kinyerve: {data['pl_pct']}%")
    else:
        log.warning("Nem sikerült kinyerni a P/L értéket, kihagyva.")

    return data


def btc_to_sat_display(btc: float) -> str:
    """BTC-t satoshira konvertál és formázza megjelenítésre."""
    sats = int(round(btc * 1e8))
    millions = sats / 1e6

    if millions == int(millions):
        return f"{int(millions)}M sat"
    else:
        rounded = round(millions, 1)
        if rounded == int(rounded):
            return f"{int(rounded)}M sat"
        return f"{rounded}M sat"


def pl_to_display(pl_pct: float) -> str:
    """P/L százalékot formázza megjelenítésre."""
    rounded = round(pl_pct)
    if rounded >= 0:
        return f"+{rounded}%"
    return f"{rounded}%"


def update_html_file(filepath: Path, data: dict) -> bool:
    """Frissíti egy HTML fájlban a satoshi értéket és a P/L-t."""
    log.info(f"Fájl frissítése: {filepath}")

    if not filepath.exists():
        log.warning(f"Fájl nem található: {filepath}")
        return False

    html = filepath.read_text(encoding="utf-8")
    changed = False

    # --- Satoshi érték frissítése ---
    sat_pattern = re.compile(
        r'(<div\s+class="val">)'
        r'(\d+(?:\.\d+)?M\s*sat)'
        r'(</div>)'
    )
    if "btc" in data:
        new_sat = btc_to_sat_display(data["btc"])
        match = sat_pattern.search(html)
        if match and match.group(2).replace(" ", "") != new_sat.replace(" ", ""):
            html = sat_pattern.sub(
                lambda m: f'{m.group(1)}{new_sat}{m.group(3)}',
                html, count=1,
            )
            log.info(f"  Satoshi frissítve: {match.group(2)} → {new_sat}")
            changed = True
        elif match:
            log.info(f"  Satoshi nem változott: {new_sat}")

    # --- P/L frissítése ---
    pl_pattern = re.compile(
        r'(<div\s+class="val"\s+id="btc-pl">)'
        r'([^<]+)'
        r'(</div>)'
    )
    if "pl_pct" in data:
        new_pl = pl_to_display(data["pl_pct"])
        match = pl_pattern.search(html)
        if match and match.group(2).strip() != new_pl:
            html = pl_pattern.sub(
                lambda m: f'{m.group(1)}{new_pl}{m.group(3)}',
                html, count=1,
            )
            log.info(f"  P/L frissítve: {match.group(2).strip()} → {new_pl}")
            changed = True
        elif match:
            log.info(f"  P/L nem változott: {new_pl}")

    if changed:
        filepath.write_text(html, encoding="utf-8")

    return True


def main():
    log.info("=" * 50)
    log.info("Bitcoin Treasury frissítés indítása")
    log.info(f"Dátum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        data = fetch_treasury_data()

        sat_display = btc_to_sat_display(data["btc"])
        log.info(f"Aktuális: {data['btc']} BTC = {sat_display}")
        if "pl_pct" in data:
            log.info(f"P/L: {pl_to_display(data['pl_pct'])}")

        all_success = True
        for html_file in HTML_FILES:
            success = update_html_file(html_file, data)
            if not success:
                all_success = False

        if all_success:
            log.info("Frissítés sikeres!")
        else:
            log.error("Néhány fájl frissítése sikertelen!")
            sys.exit(1)

    except requests.RequestException as e:
        log.error(f"Hálózati hiba: {e}")
        sys.exit(1)
    except ValueError as e:
        log.error(f"Feldolgozási hiba: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Váratlan hiba: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
