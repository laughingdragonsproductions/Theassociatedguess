# AdSense — manual steps for Brandon (The Associated Guess)

Publisher ID: **ca-pub-7048606415692002** (shared with Laughing Dragons portfolio).

**Automated check:** `powershell -File G:\LocalAIagent\desktop-agent\scripts\check-adsense-readiness.ps1 -Site tag`  
State file: `G:\openclaw\business\jarvis\state\adsense-readiness.json`

## Matrix score path (Sep 2026)

| Milestone | Actions | TAG scored rows |
|-----------|---------|-----------------|
| **Code shipped (Sep 18)** | 63 indexable, section pages, newsroom, RSS, consent defaults | **100%** scanner |
| **After console §0–§3** | Auto ads off + EU CMP publish + Sites review | **Matrix 99%+** |
| **Full board** | + Sites review (A3) + Search Console (T7) + LV8 spot-check | 33/33 Done |

---

## Compliance matrix

| Requirement | Status | Notes |
|-------------|--------|-------|
| ads.txt | **Ready** | Root `ads.txt` → `pub-7048606415692002` (live verified) |
| Privacy policy | **Ready** | `/privacy.html` — AdSense, cookies, opt-out, third parties |
| Terms | **Ready** | `/terms.html` |
| About page | **Ready** | `/about.html` — editorial voice + **Laughing Dragons Productions** publisher block |
| Contact | **Ready** | `/contact.html` — tips + studio email + link to laughing-dragons.com/contact/ |
| Footer legal links | **Ready** | Privacy, Terms, About, Contact |
| Original content | **Ready** | 81 articles, 63+ indexable (≥75%), ON008 pipeline, footer disclaimer |
| Publisher script scope | **Ready** | `adsbygoogle.js` on editorial/article pages only; **omitted** on privacy, terms, search |
| Legal pages ad-free | **Ready** | No ad slots and no `adsense.js` on privacy, terms, or search |
| robots + sitemap | **Ready** | `/robots.txt`, `/sitemap.xml` |
| Ad units configured | **Ready** | Header `2936560577`, multiplex `7102817128`, footer `4852277474` in `config.js` |
| Auto ads disabled | **You** | AdSense dashboard before manual slots go live (§0 below) |
| EU consent (CMP) | **You** | AdSense → Privacy & messaging → European regulations (§2) |
| Search Console | **Recommended** | Verify `theassociatedguess.com`, submit sitemap (§4) |
| Add site + review | **You** | AdSense → Sites → add domain → request review (§3) |

---

## §0. Disable Auto ads (do this first)

AdSense → **Ads** → **Auto ads** → **Off** for `theassociatedguess.com`

Prevents auto placements on thin/static routes while manual units are being set up.

---

## §1. Create ad units → closes matrix **T6**

AdSense → **Ads** → **By ad unit** → **Display ads**

| Unit name | Format | `config.js` key | Placement |
|-----------|--------|-----------------|-----------|
| TAG Header Banner | Display (`auto`) | `header` | `2936560577` — below nav on editorial pages |
| TAG Multiplex | Multiplex (`autorelaxed`) | `inContent` | `7102817128` — below hero on articles |
| TAG Footer Banner | Leaderboard 728×90 | `footer` | `4852277474` — sitewide footer |

Copy each **data-ad-slot** into `assets/js/config.js`:

```javascript
adsense: {
  publisherId: "ca-pub-7048606415692002",
  slots: {
    header: "2936560577",
    inContent: "7102817128",
    footer: "4852277474",
  },
},
```

Homepage and static pages use header + footer only. Article pages also load `inContent` below the hero — never inside body text or the sidebar.

No rebuild required for slot changes — `config.js` is static. **Push** after editing:

```powershell
cd G:\LocalAIagent\Theassociatedguess
git add assets/js/config.js
git commit -m "TAG: AdSense display slot IDs"
git push origin main
```

**One-command apply** (paste your three slot IDs):

```powershell
powershell -File G:\LocalAIagent\Theassociatedguess\scripts\apply-tag-adsense-slots.ps1 `
  -Header "PASTE_HEADER_SLOT" `
  -InContent "PASTE_ARTICLE_SLOT" `
  -Footer "PASTE_FOOTER_SLOT"
```

---

## §2. EU CMP → closes matrix **P3**

AdSense → **Privacy & messaging** → **European regulations** → create/enable message for `theassociatedguess.com` linking to https://theassociatedguess.com/privacy.html

Verify with AdSense preview or EEA VPN: consent banner appears before ads load.

---

## §3. Add site + request review → closes matrix **A3**

1. AdSense → **Sites** → **Add site** → `theassociatedguess.com`
2. Confirm **ads.txt** detected (`pub-7048606415692002`)
3. View-source an article — confirm:
   - `adsbygoogle.js` loads
   - Three `<ins class="adsbygoogle">` with real slot IDs (header, inContent, footer)
4. Confirm `/privacy.html` and `/terms.html` have **no** `adsbygoogle.js` and no ad units
5. **Request review**

---

## §4. Search Console (optional) → closes matrix **T7**

1. Add property `theassociatedguess.com` in Google Search Console
2. Verify (DNS TXT or HTML file upload)
3. Submit sitemap URL from `/robots.txt` (https://theassociatedguess.com/sitemap.xml)

---

## §5. Content vs ad ratio (after slots live) → closes matrix **LV8**

After §1 slot IDs are live:

1. Spot-check 3 articles — body word count should dwarf 3 display units
2. House ads (`houseAds` promos) are labeled **Promoted** — publisher content, not Google ads
3. Mark LV8 Done in readiness matrix

Sample article layout: `article/ghost-parking/index.html` — ads outside body text (header, below hero, footer).

---

## Deploy path (Dave / rebuild)

Rebuild-only (no vault publish):

```powershell
py -3 G:\LocalAIagent\Theassociatedguess\scripts\build_from_vault.py
cd G:\LocalAIagent\Theassociatedguess
git add .
git commit -m "TAG: rebuild from vault"
git push origin main
```

Publish one article from vault + rebuild:

```powershell
powershell -File G:\LocalAIagent\desktop-agent\scripts\build-associated-pressed-site.ps1 -PublishOne
```

Site repo: `G:\LocalAIagent\Theassociatedguess`  
Live: https://theassociatedguess.com

---

## Review-ready checklist

**Code-side — done (Sep 18 push):**

- [x] ads.txt + publisher script on monetized pages
- [x] Privacy/terms/about/contact/newsroom/reprints
- [x] Empty-slot-safe `adsense.js` + Consent Mode defaults in `<head>`
- [x] No ads and no `adsbygoogle.js` on legal/search pages
- [x] 81 articles, 63+ indexable, sitemap + RSS + 8 section pages
- [x] Disclaimer in footer (not header); article notes at bottom
- [x] Slot IDs in `config.js` (header, inContent, footer)

**Console-side (Brandon) — do after push:**

- [ ] §0 Disable Auto ads
- [x] §1 Slot IDs in config.js (push to live)
- [ ] §2 Enable EU CMP in AdSense (links to privacy.html)
- [ ] §3 Add site in AdSense → Sites → request review
- [ ] §4 Search Console verify + submit sitemap
- [ ] §5 Spot-check content/ad ratio for LV8

**Pre-review verification:**

```powershell
powershell -File G:\LocalAIagent\desktop-agent\scripts\check-adsense-readiness.ps1 -Site tag
```

Manual live checks:

- [ ] https://theassociatedguess.com/ads.txt → `pub-7048606415692002`
- [ ] Article page → 3 filled `<ins class="adsbygoogle">` with slot IDs
- [ ] `/privacy.html` and `/terms.html` → no ad units, no `adsbygoogle.js`
- [ ] `/search.html` → no ad units, no `adsbygoogle.js`
- [ ] EU consent banner from EEA test or AdSense preview
- [ ] Auto ads **disabled**
