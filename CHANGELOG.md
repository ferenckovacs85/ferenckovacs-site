# CHANGELOG

A ferenckovacs.com változásnaplója. A formátum a [Keep a Changelog](https://keepachangelog.com/)
irányelveit követi. A git commit történet a teljes forrás; itt csak a szembetűnő felhasználói
változások vannak összegyűjtve.

## [2026-04-21] — Előadás archívum publikus élesítése

### Added — új tartalom
- **`/eloadasok/`** — magyar nyilvános előadás-archívum (6 deck):
  - Mi a Bitcoin? (kapudeck, 14 slide)
  - Bitcoin — számok és analógiák (11 slide)
  - Merre megy az árfolyam? (17 slide, videókkal, 65 MB)
  - A magyar Bitcoin Bárka (záró, 9 slide)
  - KV Homes Workshop Megnyitó (16 slide, interaktív timeline)
  - Kolor Garden projektbemutató (15 slide)
- **`/en/talks/`** — angol változat, mind a 6 deck teljes fordítással
  - Hungary-specifikus referenciák (pengő, Paks II, Kazincbarcika) kontextussal megtartva
  - Lyn Alden és Lawrence Lepard idézetek valós hivatkozott forrásokkal
- **Főoldal szekció** mindkét nyelven (Bitcoin után, Kapcsolat előtt):
  - 3 preview kártya + link a teljes archívumra
- **Navigáció** — "Előadások" / "Talks" link mindkét `hu/` és `en/` főoldalra

### Fixed
- **EN `/kvhomes/` link** a főoldalon: a magyar KV Homes oldalra mutatott, átjavítva
  a létező angol `/kvhomes/details/` oldalra
- **KV Homes Megnyitó deck** — 15 kép hiányzott (hotel fotók, timeline képek) az első
  szűrés után, pótolva
- **Árfolyam (EN) Power Law kártya** detail szöveg angolra (smart-quote escape miatt kimaradt)
- **Bárka (EN) + Árfolyam (EN) idézetek** — magyar parafrázisok helyett valós Lyn Alden és
  Lepard idézetek, forrás-attribúcióval

### Technical
- Repo migráció: primary location most `~/Library/CloudStorage/OneDrive-K.VÉpítőipariKft/ferenckovacs-site/`
- `WORKFLOW.md` (OneDrive-local) létrehozva — setup + git-OneDrive sync figyelmeztetés
- `.gitignore` bővítés: `WORKFLOW.md`, `SITE_STATUS.md`, OneDrive conflict fájlok

### Relevant commits
- `e016e6f` — feat: /eloadasok/ + 4 Bitcoin deck élesbe
- `a8667d7` — feat: KV Homes 2 deck élesbe
- `f47d3d5` — fix: KV Homes Megnyitó hiányzó képek pótlása
- `adc79dc` — feat: /en/talks/ + Bitcoin 02 fordítás
- `95672bc`, `8739f77`, `f9e2563`, `f4681f4`, `cc6773e` — Bitcoin 03, 07, 06, KV Homes, Kolor Garden fordítás
- `4e66000` — fix: Power Law kártya
- `03b890e` — fix: valós Alden + Lepard idézetek
- `7637b11` — feat: Talks szekció főoldalakon + EN KV Homes link fix

---

## Megjegyzés

A részletes "hol tartunk éppen" belső állapotot az `/SITE_STATUS.md` tartalmazza
(nem commit-olt, OneDrive-szinkronban a dolgozó gépek között).
