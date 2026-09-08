# AdSense — manual steps for Brandon (The Associated Guess)

Publisher ID: **ca-pub-7048606415692002** (shared with Laughing Dragons portfolio).

**Automated check:** `powershell -File G:\LocalAIagent\desktop-agent\scripts\check-adsense-readiness.ps1 -Site tag`  
State file: `G:\openclaw\business\jarvis\state\adsense-readiness.json`

## Matrix score path (Sep 2026)

| Milestone | Actions | TAG scored rows |
|-----------|---------|-----------------|
| **Now (code shipped)** | Satire footer + conditional script on legal/search | **93%** (28/30) — C9 + LV6 Done |
| **After console §1–3** | Slot IDs + EU CMP | **100%** (30/30) |
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
| Original content | **Ready** | 78 satire articles, daily vault pipeline, per-article satire footer |
| Publisher script scope | **Ready** | `adsbygoogle.js` on editorial/article pages only; **omitted** on privacy, terms, search |
| Legal pages ad-free | **Ready** | No ad slots and no `adsense.js` on privacy, terms, or search |
| robots + sitemap | **Ready** | `/robots.txt`, `/sitemap.xml` |
| Ad units configured | **You** | Paste slot IDs in `assets/js/config.js` (§1 below) |
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

| Unit name | `config.js` key | Placement |
|-----------|-----------------|-----------|
| TAG Header Banner | `header` | Below nav on editorial pages |
| TAG Article Banner | `inContent` | Below hero on articles only |
| TAG Footer Banner | `footer` | Sitewide footer |

Copy each **data-ad-slot** into `assets/js/config.js`:

```javascript
adsense: {
  publisherId: "ca-pub-7048606415692002",
  slots: {
    header: "PASTE_HEADER_SLOT",
    inContent: "PASTE_ARTICLE_SLOT",
    footer: "PASTE_FOOTER_SLOT",
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

**Code-side (Dave) — done:**

- [x] ads.txt + publisher script on monetized pages
- [x] Privacy/terms/about/contact
- [x] Empty-slot-safe `adsense.js`
- [x] No ads and no `adsbygoogle.js` on legal/search pages
- [x] 78 articles + sitemap
- [x] Per-article satire disclaimer footer
- [x] Dolly redirect stubs excluded from sitemap

**Console-side (Brandon) — pending:**

- [ ] §0 Disable Auto ads
- [ ] §1 Create TAG display ad units + fill `config.js` + push
- [ ] §2 Enable EU CMP
- [ ] §3 Add site in AdSense → Sites → request review
- [ ] §4 (Optional) Search Console verify + submit sitemap
- [ ] §5 (After go-live) Spot-check content/ad ratio for LV8

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
