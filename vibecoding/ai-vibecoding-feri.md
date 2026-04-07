## Hardware / OS / kliens

- **MacMini** (otthoni stúdió, fő gép) — Brave + Google Chrome, OneDrive sync
- **MacBook Pro** (mobil) — ugyanaz a setup, ugyanaz a OneDrive-mappa
- **iPhone** — Claude mobilapp, Dispatch tab → távolról is tudok feladatokat indítani a gépen
- **Claude Cowork** desktop appban (Sonnet 4.5/4.6 + Opus 4.6 1M kontextus) — ez a fő interfész
- **Claude Code** CLI — kódszerkesztésre, repo-műveletekre

## Skill réteg

Self-hosted skill-mappám van egy **privát GitHub repóban** (`ferenckovacs85/claude-config`), és symlinkkel kötöttem a `~/.claude/skills/`-be. Egy óránként futó scheduled task `git pull`-ozza, így ha bármelyik gépről változtatok, a másik 1 órán belül látja.

A repóban most ezek élnek (rajtuk kívül a beépített xlsx/pptx/docx/pdf/yt-transcript/skill-creator/schedule):

- **mentor** — személyes tanácsadó testület (Tony Robbins, Simon Sinek, James Clear, Ray Dalio, GaryVee). Üzleti dilemma → 5 nézőpont, prioritás, akció.
- **health-board** — egészségügyi/táplálkozási board (Peter Attia, Huberman, Gabrielle Lyon, Mark Hyman, Layne Norton).
- **fat-loss-planner** — szakértői táplálkozási tervező, makrók + heti menü.
- **design-system** — Coinbase + Stripe + 5 másik referencia design system, prezentáció/HTML építéshez.
- **vlog-kit** — videó-átiratból blog/social posztok generálása (work in progress).
- **(referenciák)** thinkers/, NVK kvantum-elemzés stb.

## MCP integrációk (élő, csatlakoztatva)

| Rendszer | Mire használom |
|---|---|
| **Notion** | Bitcoin Vision 21 dokumentációk, jogi meeting jegyzetek, projekt-hubok |
| **Gmail / Outlook** | Email keresés, tervezet írás, soha nem küld magától |
| **Google Calendar / Outlook Calendar** | Esemény keresés, létrehozás, szabad idő |
| **SharePoint / OneDrive (Graph)** | Dokumentum keresés/olvasás céges drive-ban |
| **Google Drive** | Doc keresés/olvasás privát Drive-ban |
| **Notion** | Adatbázisok, oldalak, kommentek (lent részletezve) |
| **Netlify** | Saját ferenckovacs.com deploy-ok, env változók |
| **Desktop Commander** | Lokális Mac fájlrendszer, shell, build scriptek, edit_block surgical edits |
| **PowerPoint** | .pptx létrehozás, szerkesztés, PDF export |
| **PDF tools** | PDF olvasás, űrlap kitöltés, csv extract |
| **Claude in Chrome** | Brave/Chrome böngésző távirányítása, screenshotok, JS exec |
| **Computer Use** | Mac asztal vezérlése, native appok (Mail, Notes, Finder, System Settings) |
| **Control Chrome** | Direkt Chrome tab műveletek |
| **iMessage** | Olvasás, küldés (otthon, családi koordinációhoz) |
| **Circleback** | Meeting transcript+notes integráció (X bookmarks, calendar, emails) |
| **Trivago, Kiwi flights** | Utazás kereséshez |
| **Three.js** | 3D scene rendering inline |
| **Plugins / MCP registry** | Új MCP-k felfedezése |
| **Scheduled tasks** | Cron-szerű feladatok (lent) |
| **Dispatch** | Mobilról távoli session indítás a gépen |

## Scheduled tasks (cron-szerű)

A Claude saját scheduled-task rendszerét használom, ezek futnak most:

- **`skills-sync`** — óránként `git pull` a `claude-config` repóra (multi-gép sync)
- **`cb-transcript-processor`** — Circleback meeting transcriptek napi feldolgozása (akció pontok kinyerése)
- **`outlook-contact-sync`** — Outlook kontaktok napi rendezése
- **`x-bookmarks-sync`** — X bookmarks lokális mentése (fieldtheory CLI-vel)

Az infrastruktúra teszi lehetővé, hogy reggel ne kelljen kézzel triggerelni semmit — a friss dolgok már a Notion-ban, MD-kben, OneDrive-ban várnak.

## Productivity CLI tools (helyileg telepítve, MCP-ből hívható)

- **fieldtheory** — X bookmarks → lokális JSON (Brave/Chrome session-höz csatlakozik)
- **Feynman** — research agent, mély témakutatás
- **llm-wiki** — saját tudásbázis-szerkesztő
- **Graphify** — graph-alapú jegyzetkezelés
- **yt-dlp** — YouTube transcript letöltő (a yt-transcript skill ezt használja)

## Multi-gép / multi-felhő szinkron pattern

A **OneDrive** a központi lemez, ezen keresztül látja a két Mac ugyanazt:

```
~/Library/CloudStorage/OneDrive-K.VÉpítőipariKft/
└── Bitcoin/Előadások/2026/
    ├── 01-megnyito/
    ├── 02-mi-a-bitcoin/
    ├── 03-szamok-analogiak/
    └── ELOADASOK_STATUS.md   ← a két Cowork session ezen keresztül "beszélget"
```

A `STATUS.md` egy megosztott "munkafüzet" — amelyik gépen dolgozom, annak Claude session-je olvassa-frissíti, így a másik napra már látja, hol állok. Ezzel megoldottam azt, hogy a két Cowork session amúgy nem ismeri egymást.

A kritikus fájlok három helyen vannak (mind byte-azonos):
1. Working master a `0X-*/` mappában
2. `vegleges/...FINAL.html`
3. `~/ferenckovacs-site/bitcoin-2026-Q2/[név].html` (deployolva)

## Konkrét use case-ek (példák az elmúlt hetekből)

**1. Bitcoin Miskolc 2026 előadások építése**
- 3 előadás kész (Megnyitó, Mi a Bitcoin?, Számok és analógiák) — egyenként ~15-30 dia, önálló offline HTML, base64 képek, 16:9 fix arány, billentyűzet/swipe nav
- Branded QR kódok lokálisan generálva (Python `qrcode[pil]` + StyledPilImage + Telegram airplane overlay)
- Hetente több iteráció: tartalmi átfogalmazás, design polish, projektor-szabályok (felső 2/3, alsó nem látszik), Full HD átnézés a deployolt verzión
- Hidden Q2 hub: `ferenckovacs.com/bitcoin-2026-Q2/` (noindex/nofollow, robots.txt blokkolva, csak az URL ismerője éri el)

**2. Bitcoin Vision 21 dokumentációk (Notion)**
- One-pager, koordinációs doc, meeting prep oldalak Hagya Szabolcs ügyvédnek
- Email-integráció: Léránt Gergely + Siposs Attila levelekből származó info beépítése (BTCPay setup)
- MiCA / 2024. évi VII tv. / Btk. 408/A jogi referenciák ellenőrzése — itt többször ki kellett szólni, hogy a források ütköznek és emberi verifikáció kell

**3. Mentor board konzultációk**
- Üzleti dilemma → mentor skill → 5 mentor (Robbins/Sinek/Clear/Dalio/GaryVee) szempontjából elemzés → összegzés + akciópontok
- Ugyanígy health-board étkezés/edzés döntésekhez

**4. Tartalomkészítés**
- YouTube vlog átirat → vlog-kit skill → magyar nyelvű blog/SoMe poszt
- Egy konkrét példa: precast betonelem-gyártásról szóló vlog → magyar LinkedIn poszt

**5. Mobil távirányítás**
- iPhone-ról Dispatch tab-on át üzenek a Cowork-nek, az meg a MacMini-n elindít egy code task-ot vagy átnézi a OneDrive-ot → mire haza érek, kész

## Mi működik nagyon jól

- **Skill + scheduled task + multi-gép sync** kombináció: nincs napi triggerelés, minden a háttérben fut
- **Edit_block (Desktop Commander)** sebészi precizitású szövegcserékhez — nagy HTML/MD fájlokat tudok regex nélkül módosítani
- **Computer Use + Claude in Chrome kombináció** — natív app + böngésző + lokális build script egy folyamatban
- **Mentor / health-board "personae" skillek** — különböző nézőpontokat kapok azonnal, nem kell ChatGPT/Claude/Perplexity-t külön nyitogatni
- **Notion MCP** — strukturált jogi/üzleti dokumentációhoz nagyon jó
- **OneDrive STATUS.md mintázat** — a két Cowork session "üzenőfala"

## Hol van fehér folt / hol kérnék segítséget

- **Több párhuzamos kontextus kezelése** — most a STATUS.md a köztes nyelv két Mac között, de skálázódik-e? Van-e jobb minta?
- **Voice / dictate workflow** — főleg autóban szeretnék hangból feladatot indítani; jelenleg Wispr Flow + Dispatch, de nem zökkenőmentes
- **Költségkontroll** — Opus 4.6 1M kontextussal komoly tokenforgalom van, nincs jó dashboard arra, hogy lássam, melyik task mennyibe került
- **Verifikáció / tesztek hosszú HTML build-eken** — minden iteráció után kézzel screenshot-olok Brave-ben Full HD-ban; kéne erre egy jobb visual regression mintázat
- **Plugin / marketplace stratégia** — most ad-hoc telepítgetek; van-e tapasztalatod arról, mi éri meg "fizetős MCP" szintre menni?
- **Több ügyfélnek vagy nézőnek a megosztás** — most a `ferenckovacs.com/bitcoin-2026-Q2/` privát hub a megoldás. Skálázhatóbb minta?
- **Code session vs. task session határa** — mikor érdemes Claude Code-ot külön spawn-olni, és mikor maradni a Cowork-ön belül? Még mindig ízlés alapján döntök.

## Repók / linkek

- **Skills repo (privát GitHub):** `ferenckovacs85/claude-config`
- **Web repo (privát GitHub):** `ferenckovacs85/ferenckovacs-site` (Netlify deploy)
- **Privát Q2 hub:** `https://ferenckovacs.com/bitcoin-2026-Q2/` (URL ismerővel elérhető)
- **Ez a doksi:** `https://ferenckovacs.com/vibecoding/` (szintén rejtett, neked készült)

## Mit várnék tőled

Ha bármi ebből megpattant a fejedben — akár egy MCP-t ismersz, amit nem használok, akár egy skill mintát, akár egy egész workflow-t —, **érdekel**. Nem kell formálisan, egy hangüzenet vagy egy bekezdés is teljesen jó.

Külön érdekel:
1. Hogy szervezed a saját AI-stacked, ha párhuzamosan sok kliens-projekted van
2. Költségkontroll / observability tippek
3. Milyen MCP-ket / pluginekat látsz "must have"-nek 2026 Q2-ben, amikre én nem gondoltam

Köszi, hogy ránézel.

— Feri
