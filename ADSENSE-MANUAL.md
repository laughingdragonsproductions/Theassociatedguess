# AdSense — manual steps for Brandon

Publisher ID: **ca-pub-7048606415692002** (shared with Laughing Dragons portfolio).

## Compliance matrix (Aug 2026)

| Requirement | Status | Notes |
|-------------|--------|-------|
| ads.txt | **Ready** | Root `ads.txt` → `pub-7048606415692002` |
| Privacy policy | **Ready** | `/privacy.html` — AdSense, cookies, opt-out, third parties |
| Terms | **Ready** | `/terms.html` |
| About page | **Ready** | `/about.html` — editorial voice + **Laughing Dragons Productions** publisher block |
| Contact | **Ready** | `/contact.html` — tips + studio email + link to laughing-dragons.com/contact/ |
| Footer legal links | **Ready** | Privacy, Terms, About, Contact |
| Original content | **Ready** | 70+ satire articles, daily vault pipeline |
| Publisher script | **Ready** | `adsbygoogle.js` in every page `<head>` via build |
| robots + sitemap | **Ready** | `/robots.txt`, `/sitemap.xml` (rebuilt with articles) |
| Ad units configured | **You** | Paste slot IDs in `assets/js/config.js` |
| Auto ads disabled | **You** | AdSense dashboard until manual slots are set |
| EU consent (CMP) | **You** | AdSense → Privacy & messaging → European regulations |
| Search Console | **Recommended** | Verify `theassociatedguess.com`, submit sitemap |
| Add site + review | **You** | AdSense → Sites → add domain → request review |

## 1. Create ad units

AdSense → **Ads** → **By ad unit** → **Display ads**

| Unit name | Placement |
|-----------|-----------|
| TAG Article In-Content | Article body top (`inContent`) |
| TAG Sidebar | Homepage sidebar (`sidebar`) |
| TAG Footer | Sitewide footer (`footer`) |

Copy each **data-ad-slot** into `assets/js/config.js`:

```javascript
adsense: {
  publisherId: "ca-pub-7048606415692002",
  slots: {
    header: "",
    footer: "YOUR_FOOTER_SLOT",
    inContent: "YOUR_IN_CONTENT_SLOT",
    sidebar: "YOUR_SIDEBAR_SLOT",
  },
},
```

Rebuild is optional for slot changes — `config.js` is static. Push to GitHub after editing.

## 2. Add site in AdSense

1. AdSense → **Sites** → **Add site** → `theassociatedguess.com`
2. Confirm **ads.txt** is detected
3. View source on an article — confirm `adsbygoogle.js` loads
4. Request review when checklist above is green

## 3. Deploy path (Dave ON004)

```powershell
powershell -File G:\LocalAIagent\desktop-agent\scripts\build-associated-pressed-site.ps1 -ArchiveUsed
cd G:\LocalAIagent\Theassociatedguess
git add .
git commit -m "Publish Associated Guess site updates."
git push origin main
```

Site repo: `G:\LocalAIagent\Theassociatedguess`  
Live: https://theassociatedguess.com
