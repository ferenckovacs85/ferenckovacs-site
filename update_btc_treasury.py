#!/usr/bin/env python3
"""
Bitcoin Treasury frissítő script
---------------------------------
Lekéri a KV Cégcsoport aktuális BTC egyenlegét a bitcointreasuries.net oldalról
és frissíti az index.html-ben a satoshi értéket.

Használat:
    python3 update_btc_treasury.py

Függőségek:
    pip install requests beautifulsoup4

Ütemezés (havonta 1x):
    - Manuálisan: python3 update_btc_treasury.py
    - Cron: 0 9 1 * * cd /path/to/site && python3 update_btc_treasury.py
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
INDEX_HTML = Path(__file__).parent / "index.html"
LOG_FILE = Path(__file__).parent / "btc_update.log"

# Regex minta az aktuális sat érték megtalálásához az index.html-ben
# Illeszkedik pl. "122M sat", "186M sat", "186.5M sat" stb.
SAT_PATTERN = re.compile(r'(\d+(?:\.\d+)?M\s*sat)')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def fetch_btc_holdings() -> float:
    """Lekéri a BTC egyenleget a bitcointreasuries.net oldalról."""
    log.info(f"Lekérdezés: {TREASURY_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; KVCegcsoport-BTC-Updater/1.0)"
    }

    resp = requests.get(TREASURY_URL, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1. módszer: JSON-LD schema keresése
    for script_tag in soup.find_all("script", type="application/ld+json"):
        text = script_tag.string or ""
        # "currently report to hold 1.865 BTC"
        match = re.search(r'hold\s+([\d.]+)\s*BTC', text)
        if match:
            btc = float(match.group(1))
            log.info(f"JSON-LD-ből kinyerve: {btc} BTC")
            return btc

    # 2. módszer: oldal szövegében keresés
    page_text = soup.get_text()

    # "1.865 BTC" vagy "1.865BTC" minta keresése
    match = re.search(r'([\d,]+\.?\d*)\s*BTC', page_text)
    if match:
        btc_str = match.group(1).replace(",", "")
        btc = float(btc_str)
        log.info(f"Oldal szövegéből kinyerve: {btc} BTC")
        return btc

    # 3. módszer: táblázat cellákban keresés
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)
        match = re.match(r'^([\d,]+\.?\d*)\s*$', text)
        if match:
            val = float(match.group(1).replace(",", ""))
            if 0.001 < val < 1000:  # ésszerű BTC tartomány egy kisvállalatnál
                btc = val
                log.info(f"Táblázat cellából kinyerve: {btc} BTC")
                return btc

    raise ValueError("Nem sikerült kinyerni a BTC egyenleget az oldalról.")


def btc_to_sat_display(btc: float) -> str:
    """
    BTC-t satoshira konvertál és formázza megjelenítésre.

    Példák:
        1.865     -> "186M sat"
        0.35      -> "35M sat"
        1.225     -> "122M sat"  (kerekítve)
        2.5       -> "250M sat"
    """
    sats = int(round(btc * 1e8))       # 1 BTC = 100,000,000 sat
    millions = sats / 1e6               # millió satoshi

    # Kerekítés: ha egész szám, nincs tizedes, egyébként 1 tizedesig
    if millions == int(millions):
        return f"{int(millions)}M sat"
    else:
        # Ha a tizedes rész nulla lenne kerekítés után, elhagyjuk
        rounded = round(millions, 1)
        if rounded == int(rounded):
            return f"{int(rounded)}M sat"
        return f"{rounded}M sat"


def update_index_html(new_sat_value: str) -> bool:
    """Frissíti az index.html-ben a satoshi értéket."""
    log.info(f"index.html frissítése: {INDEX_HTML}")

    html = INDEX_HTML.read_text(encoding="utf-8")

    # Megkeressük a "vállalati bitcoin készlet" közelében lévő sat értéket
    # A HTML struktúra: <div class="val">122M sat</div>
    pattern = re.compile(
        r'(<div\s+class="val">)'   # nyitó tag
        r'(\d+(?:\.\d+)?M\s*sat)'  # régi érték
        r'(</div>)'                # záró tag
    )

    match = pattern.search(html)
    if not match:
        log.error("Nem találtam a sat értéket az index.html-ben!")
        return False

    old_value = match.group(2)

    if old_value.replace(" ", "") == new_sat_value.replace(" ", ""):
        log.info(f"Nincs változás, az érték már {old_value}")
        return True

    new_html = pattern.sub(
        lambda m: f'{m.group(1)}{new_sat_value}{m.group(3)}',
        html,
        count=1,
    )

    INDEX_HTML.write_text(new_html, encoding="utf-8")
    log.info(f"Frissítve: {old_value} → {new_sat_value}")
    return True


def main():
    log.info("=" * 50)
    log.info("Bitcoin Treasury frissítés indítása")
    log.info(f"Dátum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        btc = fetch_btc_holdings()
        sat_display = btc_to_sat_display(btc)
        log.info(f"Aktuális: {btc} BTC = {sat_display}")

        success = update_index_html(sat_display)

        if success:
            log.info("Frissítés sikeres!")
        else:
            log.error("Frissítés sikertelen!")
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
