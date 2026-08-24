# AdSense — manual steps for Brandon

Publisher ID: **ca-pub-7048606415692002** (shared with Laughing Dragons portfolio).

**Automated check:** `powershell -File G:\LocalAIagent\desktop-agent\scripts\check-adsense-readiness.ps1 -Site tag`  
State file: `G:\openclaw\business\jarvis\state\adsense-readiness.json`

## Compliance matrix (Aug 2026)

| Requirement | Status | Notes |
|-------------|--------|-------|
| ads.txt | **Ready** | Root `ads.txt` → `pub-7048606415692002` (live verified) |
| Privacy policy | **Ready** | `/privacy.html` — AdSense, cookies, opt-out, third parties |
| Terms | **Ready** | `/terms.html` |
| About page | **Ready** | `/about.html` — editorial voice + **Laughing Dragons Productions** publisher block |
| Contact | **Ready** | `/contact.html` — tips + studio email + link to laughing-dragons.com/contact/ |
| Footer legal links | **Ready** | Privacy, Terms, About, Contact |
| Original content | **Ready** | 72 satire articles, daily vault pipeline |
| Publisher script | **Ready** | `adsbygoogle.js` in every page `<head>` via build |
| Legal pages ad-free | **Ready** | No ad slots on privacy, terms, or search (build enforces) |
| robots + sitemap | **Ready** | `/robots.txt`, `/sitemap.xml` (72 article URLs) |
| Ad units configured | **You** | Paste slot IDs in `assets/js/config.js` |
| Auto ads disabled | **You** | AdSense dashboard until manual slots are set |
| EU consent (CMP) | **You** | AdSense → Privacy & messaging → European regulations |
| Search Console | **Recommended** | Verify `theassociatedguess.com`, submit sitemap |
| Add site + review | **You** | AdSense → Sites → add domain → request review |

## 1. Create ad units

AdSense → **Ads** → **By ad unit** → **Display ads**

| Unit name | Placement |
|-----------|-----------|
| TAG Header Banner | Below main nav on editorial pages (`header`) |
| TAG Article Banner | Below hero image on every article (`inContent`) |
| TAG Footer Banner | Sitewide footer (`footer`) |

Copy each **data-ad-slot** into `assets/js/config.js`:

```javascript
adsense: {
  publisherId: "ca-pub-7048606415692002",
  slots: {
    header: "YOUR_HEADER_SLOT",
    inContent: "YOUR_ARTICLE_SLOT",
    footer: "YOUR_FOOTER_SLOT",
  },
},
```

Homepage and static pages use header + footer only. All 72+ article pages also load the inContent unit below the hero image — never inside body text or the sidebar.

Rebuild is optional for slot changes — `config.js` is static. Push to GitHub after editing.

## 2. Add site in AdSense

1. AdSense → **Sites** → **Add site** → `theassociatedguess.com`
2. Confirm **ads.txt** is detected
3. View source on an article — confirm `adsbygoogle.js` loads
4. Request review when checklist above is green

## 3. Deploy path (Dave ON004)

```powershell
powershell -File G:\LocalAIagent\desktop-agent\scripts\build-associated-pressed-site.ps1 -PublishOne
cd G:\LocalAIagent\Theassociatedguess
git add .
git commit -m "Publish Associated Guess site updates."
git push origin main
```

Rebuild-only (no publish):

```powershell
powershell -File G:\LocalAIagent\desktop-agent\scripts\build-associated-pressed-site.ps1
```

Site repo: `G:\LocalAIagent\Theassociatedguess`  
Live: https://theassociatedguess.com

## 4. Review-ready checklist (TAG)

Code-side (Dave) — **done**:

- [x] ads.txt + publisher script
- [x] Privacy/terms/about/contact
- [x] Empty-slot-safe `adsense.js`
- [x] No ads on legal/search pages
- [x] 72+ articles + sitemap

Console-side (Brandon) — **pending**:

- [ ] Create TAG display ad units
- [ ] Fill slot IDs in `config.js` and push
- [ ] Enable EU CMP for `theassociatedguess.com`
- [ ] Add site in AdSense → Sites
- [ ] (Optional) Search Console verify + submit sitemap
- [ ] Request review
