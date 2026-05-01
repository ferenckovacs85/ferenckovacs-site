# CHANGELOG

A ferenckovacs.com változásnaplója. A formátum a [Keep a Changelog](https://keepachangelog.com/)
irányelveit követi. A git commit történet a teljes forrás; itt csak a szembetűnő felhasználói
változások vannak összegyűjtve.

## [2026-04-30] — KV Homes BNI Select Prime pitch deck (HU + EN)

### Added — új tartalom
- **`/eloadasok/kvhomes-bni/`** — KV Homes pitch a BNI Select Prime chapter-nek (2026. május 12.)
  - 15 dia / 20 perc · single-file HTML · click-reveal step-by-step
  - Slide 3 — Apple-style feature grid SVG ikonokkal (100 m², A+++, hőszivattyú, aktív szellőzés, 6 kW PV, 10 kWh akku) — egyenként pop-up
  - Slide 4 — Átlag/KV összehasonlító dashboard 6 sorral, soronként rise-animációval; energia-sor 2-fázisú: phase-1 (147 vs 12) → phase-2 (∞ AKTÍV HÁZ + negatív bar bekúszás)
  - Slide 8–10 — Kolor Garden projekt: helyszín / adatok (32 618 m² · 80 lakás · 37 családi ház · ~15 500 m² park) / filozófia (Miért + Hogyan)
  - Slide 13 — BNI ask: 4 konkrét referral-helyzet (építkező / fejlesztő / önkormányzat / generálkivitelező), trigger-mondatokkal
  - Full HD-re méretezve (4 m vászon, 10–25 m olvasási távolság), mobil-tap zónákkal és presenter-clicker keyboard-támogatással
- **`/en/talks/kvhomes-bni/`** — teljes angol fordítás
- **Új szekció a `/eloadasok/` és `/en/talks/` listákon:** „Üzleti hálózat / közösségi" / „Business networking / community" — első tényleges kártyával

### Technical
- `data-steps` engine kibővítve: a slide-on belüli step-state-en kívül `phase-2` toggle az energia-soron (∞ AKTÍV HÁZ climax)
- HUD step-dots — vizuális indikátor a dia-belüli pozícióhoz (lent középen)
- `?slide=N&step=M` deeplink (próbához)
- Pointer/touch dedupe (220 ms ablak) — a korábbi mobil dupla-click hiba ellen
- Negatív bar visszafelé-növekedés `position:absolute; right:82%` triggerrel, piros gradient + glow

### Convention
- Magyar + angol pár kötelező — mindkét nyelv készen, /en/talks/ index frissítve

### Relevant commits
- `(ez a commit)` — KV Homes BNI Select Prime deck élesbe (HU + EN) + index-kártyák

---

## [2026-04-22] — Interaktív bányászat-szimulátor

### Added
- **`/bitcoin-mining-dice.html`** — Proof-of-Work szimulátor dobókocka-analógiával (magyar UI)
  - 1920×1080 full-screen canvas, auto scale-to-fit
  - Bányászat-állapot, retarget folyamat-kijelzés, blokk-idő átlag vizualizáció
  - Hozzáadva a Kalkulátorok (`/kalkulatorok.html`) oldalra és mindkét főoldali sub-grid-be
  - OG meta tagek a social preview-hez, back-link a Kalkulátorok oldalra
- **`/en/bitcoin-mining-dice.html`** — ugyanaz angolul, back-link a `/en/napkin-math.html`-re
- **Kétféle szünet a mining dice-ban** (mindkét nyelvre) — az első verzió utáni finomítás
  - `Space` = **bányászat szünet** (idő megy tovább — hashrate-eltűnés szimulálása; jó retarget-hatás bemutatásához)
  - `Shift+Space` vagy `P` vagy új ikon-gomb = **teljes game pause** (minden áll, idő is)
  - Stats-kijelzés 3 állapota: 🟢 Élőben / ❚❚ Bányászat szünet (idő megy) / 🧊 Játék áll (idő is)
- **Link frissítés** — az EN napkin-math és EN főoldal linkjei most a `/en/bitcoin-mining-dice.html`-re mutatnak (a „Hungarian UI" figyelmeztetés eltávolítva)

### Technical
- `gameNow()` helper, `state.totalPausedMs` accumulator: block timestamps, runtime, retarget ablakok mind „játékidő"-n alapulnak
- Animáció-timingek (`justWon`, event `at`) valódi `Date.now()`-on maradtak a vizuális folyamatosság kedvéért
- Reset kimossa a pause-akkumulátorokat is

### Relevant commits
- `cb7e630` → `5531b26` (rebase) — mining dice integráció
- `0be6d8c` — kétféle szünet implementáció
- `(ez a commit)` — angol fordítás + linkek + log frissítés

### Convention (új)
- **Minden magyar nyelvű új anyag után** az angol változatot is elkészítjük alapesetben.
- Minden változást bejegyzünk a `CHANGELOG.md`-be (commit-olt) és a `SITE_STATUS.md`-be (OneDrive-local).

---

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
