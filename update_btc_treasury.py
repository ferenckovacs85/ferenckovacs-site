#!/usr/bin/env python3
"""
Bitcoin Treasury frissítő script
---------------------------------
Lekéri a KV Cégcsoport aktuális BTC egyenlegét és unrealized P/L értékét
a bitcointreasuries.net oldalról és frissíti a hu/index.html és en/index.html fájlokat.

Megjelenítés: a készlet BTC-ben ("1.865 BTC"), nem satoshiban.
A P/L a "BTC Value" és a "Total Cost Basis" hányadosából számolódik,
NEM az oldal első százalék-találatából (az korábban hibás értéket adott).

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
TREASURY_URL = "https://bitcointreasuries.net/private-companies/kv-cegcsoport"
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


def _num(s: str) -> float:
    """Szám parse-olása ezres elválasztó vesszőkkel."""
    return float(s.replace(",", ""))


def fetch_treasury_data() -> dict:
    """Lekéri a BTC egyenleget és kiszámolja a P/L-t a bitcointreasuries.net oldalról."""
    log.info(f"Lekérdezés: {TREASURY_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; KVCegcsoport-BTC-Updater/1.0)"
    }
    resp = requests.get(TREASURY_URL, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    data = {}

    # --- BTC egyenleg ---
    # 1. módszer: meta description ("track its 1.865 BTC balance")
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        m = re.search(r"([\d,]+\.?\d*)\s*BTC balance", meta["content"])
        if m:
            data["btc"] = _num(m.group(1))
            log.info(f"Meta description-ből: {data['btc']} BTC")

    # 2. módszer: "₿1.865" minta az oldal szövegében
    if "btc" not in data:
        m = re.search(r"₿\s*([\d,]+\.?\d*)", page_text)
        if m:
            data["btc"] = _num(m.group(1))
            log.info(f"₿ mintából: {data['btc']} BTC")

    if "btc" not in data:
        raise ValueError("Nem sikerült kinyerni a BTC egyenleget.")

    # Épségellenőrzés — korábban egy rossz regex 2025 BTC-t olvasott ki
    if not (0 < data["btc"] < 1000):
        raise ValueError(f"Gyanús BTC érték: {data['btc']} — frissítés kihagyva.")

    # --- P/L számítás: BTC Value / Total Cost Basis ---
    vm = re.search(r"BTC Value\s*\$?\s*([\d,]+\.?\d*)", page_text)
    cm = re.search(r"Total Cost Basis\s*\$?\s*([\d,]+\.?\d*)", page_text)
    if vm and cm:
        value = _num(vm.group(1))
        cost = _num(cm.group(1))
        if cost > 0:
            pl = (value / cost - 1) * 100
            if -100 <= pl <= 1000:
                data["pl_pct"] = pl
                log.info(f"P/L számítva: value ${value:,.0f} / cost ${cost:,.0f} = {pl:.1f}%")
            else:
                log.warning(f"Gyanús P/L érték ({pl:.1f}%), kihagyva.")
    else:
        log.warning("BTC Value / Total Cost Basis nem található, P/L kihagyva.")

    return data


def btc_to_display(btc: float) -> str:
    """BTC értéket formáz megjelenítésre, pl. 1.865 → '1.865 BTC'."""
    s = f"{btc:.8f}".rstrip("0").rstrip(".")
    return f"{s} BTC"


def pl_to_display(pl_pct: float) -> str:
    """P/L százalékot formázza megjelenítésre."""
    rounded = round(pl_pct)
    if rounded >= 0:
        return f"+{rounded}%"
    return f"{rounded}%"


def update_html_file(filepath: Path, data: dict) -> bool:
    """Frissíti egy HTML fájlban a BTC készletet és a P/L-t (id-alapú, robusztus minták)."""
    log.info(f"Fájl frissítése: {filepath}")

    if not filepath.exists():
        log.warning(f"Fájl nem található: {filepath}")
        return False

    html = filepath.read_text(encoding="utf-8")
    changed = False

    # --- BTC készlet frissítése (id="btc-holdings") ---
    btc_pattern = re.compile(
        r'(<div\s+class="val"\s+id="btc-holdings">)([^<]+)(</div>)'
    )
    if "btc" in data:
        new_btc = btc_to_display(data["btc"])
        match = btc_pattern.search(html)
        if match and match.group(2).strip() != new_btc:
            html = btc_pattern.sub(
                lambda m: f"{m.group(1)}{new_btc}{m.group(3)}",
                html, count=1,
            )
            log.info(f"  BTC készlet frissítve: {match.group(2).strip()} → {new_btc}")
            changed = True
        elif match:
            log.info(f"  BTC készlet nem változott: {new_btc}")
        else:
            log.warning('  Nem található id="btc-holdings" elem!')

    # --- P/L frissítése (id="btc-pl") ---
    pl_pattern = re.compile(
        r'(<div\s+class="val"\s+id="btc-pl">)([^<]+)(</div>)'
    )
    if "pl_pct" in data:
        new_pl = pl_to_display(data["pl_pct"])
        match = pl_pattern.search(html)
        if match and match.group(2).strip() != new_pl:
            html = pl_pattern.sub(
                lambda m: f"{m.group(1)}{new_pl}{m.group(3)}",
                html, count=1,
            )
            log.info(f"  P/L frissítve: {match.group(2).strip()} → {new_pl}")
            changed = True
        elif match:
            log.info(f"  P/L nem változott: {new_pl}")
        else:
            log.warning('  Nem található id="btc-pl" elem!')

    if changed:
        filepath.write_text(html, encoding="utf-8")

    return True


def main():
    log.info("=" * 50)
    log.info("Bitcoin Treasury frissítés indítása")
    log.info(f"Dátum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        data = fetch_treasury_data()

        log.info(f"Aktuális: {btc_to_display(data['btc'])}")
        if "pl_pct" in data:
            log.info(f"P/L: {pl_to_display(data['pl_pct'])}")

        all_success = True
        for html_file in HTML_FILES:
            if not update_html_file(html_file, data):
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
